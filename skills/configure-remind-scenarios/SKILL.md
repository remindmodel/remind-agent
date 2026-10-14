---
name: configure-remind-scenarios
description: Author or review a REMIND scenario config — which switches a scenario_config*.csv actually overrides vs. its checkout defaults, path_gdx chaining, SCC/damage setups. Use when reading or editing config/scenario_config*.csv or sanity-checking a run matrix.
---

# Working with scenario configs

Scenario configs live in `config/scenario_config*.csv` (`;`-separated): one **column** per switch /
flag / module realization, one **row** per scenario. An empty cell or missing column ⇒ the default
is used, so you only need columns that deviate.

- **Column names must match the switch name exactly.** Prefix with a dot (e.g. `.cm_startyear`) to
  disable a column without deleting it.
- **Every switch and its allowed values are declared in `main.gms`** (grep the name for its
  `$setglobal`/description and permitted values); R-side defaults live in `config/default.cfg`.
  Consult both before adding a column — do not invent switches or values.
- Cells hold realization names (e.g. `diffLin2Lin` for module 45) or parameter values; some accept
  comma-separated lists (e.g. `cm_emiMktTarget` in `47_regipol`).
- **Mandatory columns:** `title` (unique; letters/digits/`_`/`-`) and `start` (`1` = run by default,
  `0` = keep but don't start, or a group name run via `startgroup=<name>`).
- **Chained runs** use `path_gdx*` columns pointing to a gdx, an output folder, or another row's
  `title`: `path_gdx` (restart), `path_gdx_ref` (fixes `t < cm_startyear`), `path_gdx_bau` (BAU,
  e.g. NDC), `path_gdx_carbonprice`, `path_gdx_refpolicycost`. Pointing at a `start = 1` title waits
  for it; at a `start = 0`/absent title reuses the latest matching finished run in `output/`.

## See the non-default switches
`scripts/scenario_switches.py` lists, per scenario, which switches are set away from their default,
resolving each default from the **same checkout** (so fork-only switches resolve). Full usage + the
SCC/damage "what a correct run sets" checklist: `reference/scenario-switches.md`.

## How defaults resolve
Config is layered (`main.gms` + `default.cfg` → scenario_config row → start-time R overrides →
`cfg.txt`). The detail is in `reference/config-resolution.md`; to see what a run *actually* used,
read its `output/<run>/cfg.txt`.

## Reference
- `reference/config-resolution.md` — how `cfg` is layered and where a default comes from.
- `reference/scenario-switches.md` — the non-default-switch playbook (tool: `scripts/scenario_switches.py`).

## Related skills
- `edit-remind-code` — a switch's default is its `main.gms` `$setglobal` line; reading that is
  code-reading territory.
- `debug-remind-run` — when a scenario's inputs/switches are the suspected cause of a failure.
