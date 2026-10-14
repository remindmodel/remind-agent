# List the non-default switches in a REMIND scenario config

Use when: you have a `config/scenario_config*.csv` and want to see, per scenario, **which switches
are actually set away from their default** — e.g. to review a colleague's run matrix, sanity-check an
SCC / damage setup, or diff "what did this scenario really change" without reading a 70-column CSV by
eye.

Background: a REMIND scenario config is `;`-separated, one column per switch, one row per scenario.
An **empty cell means "inherit the default"**; a non-empty cell **overrides** it. Defaults are NOT
in `scenario_config.csv` — they live in the checkout's `main.gms` (`$setGlobal <name> <val> !! def =
<default>` for module selections and `cm_*`/`c_*` macro switches; plain scalar assignments like
`cm_dr_scc_scen = 0;` for a few) and, for cfg-level settings, in `config/default.cfg`
(`cfg$... <- ...`). The tool reads defaults from the **same checkout the config lives in**, so
fork-only switches resolve correctly — a central code index (or the remind-rag MCP) will miss
switches a feature branch added, e.g. `cm_scc_weight_matrix`, `cm_dr_scc_scen`.

Shell prep: none — plain `python3`, standard library only.

## Tool
`python3 remind-context/scripts/scenario_switches.py CONFIG.csv [options]`
- (default) only rows with `start == 1`, listing each non-default switch as `name  value  (default: d)`.
- `--all` — every scenario row, not just the queued ones.
- `--scenario NAME` — only this scenario title (repeatable).
- `--remind-root DIR` — the checkout holding `main.gms` + `config/default.cfg`
  (default: two levels up from `CONFIG.csv`, i.e. `<root>/config/x.csv -> <root>`). Pass this if the
  config is a copy that lives outside its model tree.
- `--show-redundant` — also list cells that are set but **equal** the default (harmless clutter).
- `--unknown` — also list columns whose default could not be resolved (fork-only switch the parser
  missed, or a non-switch column); empty block = everything resolved.

## Reading it
- The header line reports how many defaults were parsed and which checkout they came from — if that
  count is ~0, the `--remind-root` is wrong (no `main.gms` found).
- A switch shown with `(default: <empty>)` has a default of empty string (e.g. an optional path);
  the config is setting it to a non-empty value.
- Run-identity / input-path columns (`title`, `start`, `description`, `path_gdx*`) are skipped —
  they are never "switches".
- Values compare numerically where possible, so `0` vs `0.0` is treated as equal (not an override).

## SCC / damage runs — what a correct one sets
A COACCH-damage SCC run (the `SSP2-Dam*-Disc*-Clim*-<coalition>` matrix) shows this override set:
`climate=magicc7_ar6`, `damages=COACCH`, `internalizeDamages=COACCHitr` (compute the SCC),
`cm_magicc_temperatureImpulseResponse=on` (the TIRF step — see `inspect-tirf.md`),
`cm_scc_weight_matrix=<coalition>` and `cm_dr_scc_scen=<0|1|2>` (fork-only), plus `carbonprice=none`
(the internalized SCC *is* the price). The Dam/Clim level rides on `cm_damage_COACCH_CIspec`
(p05/p5/p95) and the MAGICC parset (`.../parsets/RCP26_{10,50,90}.json`). Missing
`cm_magicc_temperatureImpulseResponse=on` with `internalizeDamages=COACCHitr` aborts the run
(`COACCHitr/datainput.gms` guard).
