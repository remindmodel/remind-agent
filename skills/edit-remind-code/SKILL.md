---
name: edit-remind-code
description: Read, explain, or change REMIND GAMS/R model code in core/ and modules/ — the default-realization discipline, declared-vs-computed, units, verifying edits compile, plus the pik-piam package ecosystem and renv. Use when explaining or modifying model code, or developing a pik-piam package against a run.
---

# Reading & changing REMIND code

## Reading REMIND code (checks before you explain)
Each rule comes from a mistake graded answers made repeatedly.
- **Lead with the default.** A module's default realization is its `$setglobal <module>
  <realization>` line in `main.gms` (e.g. `carbonprice NPi2025`). Check the realization is the
  default and that its `$ifthen` / `if(cm_…)` / `$(…)` guards hold under the `main.gms` defaults.
  Describe everything else as an alternative and name the switch that enables it. **Most common
  mistake by far.**
- **Declared ≠ computed.** The module that declares an interface symbol often isn't the one that
  sets its value; find the assignment lines. E.g. `pm_taxCO2eqSum` is declared in
  `46_carbonpriceRegi` but a default run computes it in `core/presolve.gms`.
- **Equations:** the `$`-condition in an equation's domain decides whether GAMS generates it at all.
- **Units come from the declaration**, not intuition. E.g. `p33_fedem` is EJ/GtC (GJ per tonne
  carbon), not per tonne CO2.
- **Comments can be stale.** Check prose against the code. Read a realization's `abort`
  preconditions before recommending it (e.g. `45_carbonprice/temperatureNotToExceed` requires a
  `climate=magicc` realization that doesn't exist, so it can never run).
- **Don't accept the question's premise** unchecked; **verify every identifier exists**; cite only
  `path:line` you actually read.

### If the remind-rag tools are available
When the `remind-rag` MCP server is connected (`search`, `get_symbol`, `get_switch`, `get_module`,
`get_scenario`, `get_links`), use it for the checks above — its results mark whether code runs in a
default run and separate where a symbol is declared, assigned and used. Without it, grep `main.gms`
for defaults and the module's `realization.gms`. The rules apply either way.

## Change strategy
- Make the smallest, most localized change; no broad refactors unless asked. Avoid renaming symbols
  across modules unless asked. Follow local conventions.
- **R:** tidyverse-first (`dplyr`/`tidyr`/`purrr`/`stringr`/`glue`, native pipe); base R only where
  there's no equivalent. Respect the stack's R 4.3.2 (full conventions in `reference/r.md`).

## Check compilation after every code change
`gamscompile` / `gams main.gms -a=c` only compile code **activated by the current defaults** — a
non-default realization is silently skipped. So activate the realization you touched first:
1. From the path, find the realization. `core/` is always active; for
   `modules/<nn>_<name>/<realization>/`, find the `$setglobal` in `main.gms`
   (`grep -n "module_47" main.gms`) and note the current default.
2. Temporarily set that `$setglobal` to your realization (and the R-side switch in
   `config/default.cfg` if applicable).
3. Compile from the project root:
   ```bash
   gams main.gms -a=c -errmsg=1 -pw=200 -ps=0
   ```
   Success: `*** Status: Normal completion`. Failure: grep `main.lst` for `****` and fix.
   (`gamscompile` needs an interactive terminal via `tput cols`; use the `gams` form in
   non-interactive sessions.)
4. **Restore** the original default immediately.
5. `rm main.lst`.

## Reference
- `reference/gams.md` — GAMS change strategy & debugging pointers.
- `reference/r.md` — R execution model, tidyverse conventions, the R 4.3.2 trap, run-folder renv.
- `reference/cicd.md` — `make test`, workflow change policy, structural-change working style.
- `reference/renv.md` — REMIND's renv architecture + the workflow for developing a pik-piam package.
- `reference/pik-piam-deps.md` — the pik-piam package map + what to do when a traceback bottoms out
  in one.

## Related skills
- `configure-remind-scenarios` — switch defaults and scenario wiring.
- `debug-remind-run` — when a code change is being made to fix a failing run.
- `inspect-remind-gdx` — when the change touches a gdx read/write path.
