## What this repo is
- GAMS-based simulation model with R tooling around it.
- GAMS entry point: `main.gms`. Core model code lives in `core/` and `modules/`.
- R scripts live in `scripts/`. Main scripts:
  - Run simulations: `Rscript start.R`
  - Postprocess/reporting: `Rscript output.R` (reads `*.mif` report files; generates a PDF with plots based on user selection)

## Execution environment (important)
- Simulations typically run on an HPC cluster using Slurm batch scheduling.
- Runs are non-interactive, resource/time constrained, and heavy I/O can matter.
- `output/` and `input/` can be very large. Do **not** assume these directories can be scanned or summarized.

## Commands (source of truth)
- Tests / CI target: `make test`
- Run simulation: `Rscript start.R`
- Generate PDF report: `Rscript output.R`

### Shell sanity check (HPC)
Before suggesting any R/GAMS diagnostic command on the cluster, confirm the
shell has the PIAM module stack loaded. The `module` command is a shell
function, not a binary, and is not always inherited by child shells (VS Code
remote terminals are a frequent offender). Symptoms of an unprepared shell:
`Rscript`/`gams` not found (exit 127), `module list` reports nothing.

Quick check (cheap — pure shell, no `module` invocation needed):
```sh
echo "LOADEDMODULES=$LOADEDMODULES"
command -v Rscript && command -v gams
```
- `LOADEDMODULES` is set/exported by the module system itself; empty ⇒ nothing
  loaded in this shell tree.
- If empty / unresolved: instruct the user to open a fresh terminal (or
  reload the VS Code window when working remotely) so the login shell init
  re-runs. Do **not** attempt to debug a run from such a shell — every
  diagnostic will fail spuriously and obscure the real problem.

The PIAM stack pins **R 4.3.2**. Avoid R 4.4+-only idioms (e.g. base `%||%`)
in suggested one-liners.

## Data & outputs
- `input/` and `output/` can be vast and are intentionally messy.
- `output/` is gitignored. Each run creates `output/<SCENARIO_TIMESTAMP>/`.
- Diagnostics for a run live in that run folder:
  - `log.txt` (this is Slurm stdout/stderr for the job) ✅ primary debugging source
  - `full.log` (can be massive) — never request or paste the full file
  - `log_climate.txt` may exist and can be relevant

### Run folder = self-contained unit
Each `output/<SCENARIO_TIMESTAMP>/` is independent of the repo root:
- `cfg.txt` — resolved configuration (ground truth, see *Configuration resolution*)
- `renv.lock` + `renv/library/` — own renv, auto-activated by `.Rprofile`
- `log.txt`, `log_renv.txt`, `log_climate.txt`, `full.log` — stage-specific logs
- `*.gdx`, `*.mif`, `*.RData`, `climate-assessment-data/` — artefacts
- A copy of the GAMS source (`main_<scenario>.gms`) and scenario CSVs as used at submission time

To inspect what a run actually used, work *inside* its folder. Never compare
against the repo root's settings — they may have changed since the run started.

## Configuration resolution
REMIND's `cfg` is built by layering, later wins:
1. **Defaults** — `gms::readDefaultConfig()` reads the GAMS switches
   (`cfg$gms$<switch>`) from their `$setglobal` / `parameter` lines in
   **`main.gms`**, then overlays **`config/default.cfg`**, which holds the
   R/run settings (`cfg$title`, `cfg$regionmapping`, `cfg$inputRevision`, …) and
   no GAMS switch. A switch's default is therefore the value in `main.gms`.
2. **`config/scenario_config*.csv`** — one row per scenario; columns override
   individual fields. Multiple scenario configs exist (`_damages`,
   `_NGFS_v6c1`, `_ScenarioMIP`, …); only those referenced by the start
   command apply.
3. **Start-time R overrides** in `start.R` / `submit.R` (cascade `path_gdx_*`,
   `UseThisRenvLock`, etc.).
4. **Resolved result** is serialized to `output/<run>/cfg.txt` — single
   source of truth for both GAMS switches and the R ecosystem at runtime.

When a parameter looks wrong:
1. Read it in `output/<run>/cfg.txt` first — that's what was actually used.
2. If it disagrees with the default (`main.gms` for GAMS switches,
   `default.cfg` for the rest), find the overriding row:
   ```sh
   grep -n "<scenario_name>" config/scenario_config_*.csv
   ```
3. For structured / derived fields, reproduce the cfg construction inside the
   run folder so its renv activates. Example (climate stage):
   ```sh
   cd output/<run>
   Rscript -e 'cfg <- remindClimateAssessment::climateAssessmentConfig(getwd(), "iteration"); str(cfg)'
   ```

## R conventions (defaults)
- Tidyverse-first (`dplyr`/`tidyr`/`purrr`/`stringr`/`glue`); avoid `data.table`; base R
  only where no tidyverse equivalent exists. Respect `renv.lock`.
- Full conventions, incl. the R 4.3.2 cluster caveat, are in `instructions/r.md` (imported below).

## How to respond (style contract)
- Be concise by default (aim for 5–12 bullets total).
- Provide **one** recommended approach. Optionally include **one** alternative only if there is a real tradeoff.
- Avoid "menu answers" and avoid being overly critical. Be direct and actionable.
- When unsure, ask at most **2** clarifying questions, then proceed with the best guess.

## Reading REMIND code (checks before you explain)
Each rule below comes from a mistake that graded answers about REMIND made repeatedly.
- **Lead with the default.** A module's default realization is its `$setglobal <module> <realization>` line in
  `main.gms` (e.g. `carbonprice NPi2025`). Before explaining code, check that its realization is the default and
  that its `$ifthen` / `if(cm_…)` / `$(…)` guards hold under the `main.gms` switch defaults. Describe everything
  else as an alternative and name the switch that enables it. This was the most common mistake by far.
- **Declared ≠ computed.** The module that declares an interface symbol is often not the one that sets its value;
  find the assignment lines. Example: `pm_taxCO2eqSum` is declared in `46_carbonpriceRegi`, but a default run
  computes it in `core/presolve.gms:10`.
- **Equations:** the `$`-condition in an equation's domain decides whether GAMS generates it at all.
- **Units come from the declaration**, not from intuition. Example: `p33_fedem` is in EJ/GtC, i.e. GJ per tonne of
  carbon, not per tonne of CO2.
- **Comments and descriptions can be stale.** Check prose against the code it describes. Before recommending a
  realization, read its `abort` preconditions: `45_carbonprice/temperatureNotToExceed` requires `climate=magicc`,
  a realization that doesn't exist (`modules/15_climate/` has `magicc7_ar6` and `off`), so it can never run.
- **Don't accept the question's premise** without checking it; **verify that every identifier you use exists**;
  cite only `path:line` locations you actually read.

### If the `remind-rag` tools are available
When the `remind-rag` MCP server is connected (`search`, `get_symbol`, `get_switch`, `get_module`,
`get_scenario`, `get_links`), use it for the checks above: its results mark whether code runs in a default run
and separate where a symbol is declared, assigned and used. Without it, grep `main.gms` for defaults and the
module's `realization.gms` for its realizations. The rules apply either way.

## Debugging protocol (failed runs)
Assume debugging starts from a failed run in `output/<SCENARIO_TIMESTAMP>/`.

REMIND's own guide, written by its developers from experience, is `tutorials/10_DebuggingREMIND.md`. Read the
matching case there before giving REMIND-specific advice instead of improvising it: did not start, error
(compilation / execution / missing gdx), infeasibilities (`p80_repy` in `full.lst`, modelstat codes,
`cm_abortOnConsecFail`, infeasibility spreading between regions through trade), non-convergence, debug runs
(`--debug --testOneRegi`, `listinfes`), and watching CONOPT (`conoptspy`, `gmsgrid.log`). On the PIK cluster,
`rs` / `modelstats::loopRuns('.')` gives a run's state.

### Critical note: do not anchor on the bottom of the log
- The last lines often contain solver/model status such as "infeasible". This can be a legitimate model outcome.
- Treat the tail as **symptom confirmation**, not necessarily root cause.
- Root cause often appears earlier (missing inputs, environment issues, runtime errors, licensing/solver problems, numeric errors).

### What to ask for (in this order)
1) Which stage failed?
   - simulation (`Rscript start.R` / GAMS), or
   - reporting (`Rscript output.R` / `*.mif` -> PDF)

2) From `output/<run>/log.txt` (user will paste) — **always request all three parts before looking at any other file**:
   - Header: first ~60 lines (environment, git state, package versions)
   - **First anomaly block**: ~120 lines around the earliest suspicious message
     (e.g., ERROR/FATAL/Abort/Exception, missing file, NaN/Inf, "Killed", OOM, segfault)
   - Tail: last ~120 lines
   ⚠️ Do not request `full.log` or `log_climate.txt` until all three parts of `log.txt` are in hand and insufficient.

3) Only if `log.txt` is genuinely insufficient: request from `full.log` or `log_climate.txt`

### How to answer a failure report
Use this structure:
- **Most likely root cause:** (1 short paragraph; cite the log lines that imply it; explain why tail "infeasible" is or isn't decisive)
- **Next check:** (1 concrete thing to look for / 1 command / 1 file location)
- **Fix:** (1 recommended change)
- **If still ambiguous:** ask exactly 1 focused question

### Climate-assessment debugging (`log_climate.txt`)
Only consult `log_climate.txt` after `log.txt` has been triaged and points at
the climate stage. Typical wrapper error in `log.txt`:
`climateAssessmentInterimRun.R: Climate assessment output file not found`
— that's a *symptom*; the real traceback is in `log_climate.txt`.

Structure of `log_climate.txt`:
- **Config block at the top** echoes the resolved climate stage `cfg`:
  `mode`, `scenario`, `condaEnv`, `magiccBin`, `variablesFile`,
  `infillingDatabase`, **`probabilisticFile`**, emission file paths,
  `nSets`. Read this first — it shows which MAGICC binary and which parset
  the run *actually* used, regardless of what `default.cfg` says.
- **`condaRun` blocks** — for each Python sub-step (`run_harm_inf.py`,
  `runOpenSCM.py`) the log lists the exported env vars
  (`MAGICC_EXECUTABLE_7`, `MAGICC_WORKER_ROOT_DIR`, `MAGICC_WORKER_NUMBER`)
  and the full command line including `--probabilistic-file`. For fresh
  runs all relevant env vars are also dumped near the top. Cross-check these
  against the config block.
- **Pipeline order is fixed**: harmonize → infill → OpenSCM/MAGICC. Errors
  like `ValueError: No runs to append` from `openscm_runner` are aggregator
  symptoms — every MAGICC worker died, so there was nothing to concatenate.
  Root cause is upstream.
- **MAGICC failures** surface as `magicc run failed: b"…"` followed by a
  Fortran backtrace. The path inside that backtrace points at the MAGICC
  source tree the binary was built from — useful for telling stock vs. fork
  apart.

Binary ↔ parset compatibility caveat:
- A MAGICC fork that adds new CFG keys requires a matching parset variant.
  Pointing such a binary at a stock parset can leave keys unset and produce
  `Cannot open file ''` from `read_allcfg` (Fortran `open('')`). Always
  verify `magiccBin` and `probabilisticFile` line up — both are visible in
  the config block at the top of `log_climate.txt` and (resolved) in
  `cfg.txt`.

## pik-piam dependencies
REMIND depends on a family of R packages maintained at https://github.com/pik-piam/.
They are installed via `renv` — there are no local checkouts. Treat them as third-party libraries.
Non-pik-piam dependencies (e.g. `callr`, `ggplot2`, `testthat`) are standard CRAN packages — do not look for them on pik-piam.

Key packages and their roles:
| Package | Role | GitHub |
|---|---|---|
| `remind2` | R reporting layer — reads GDX, produces `.mif` | https://github.com/pik-piam/remind2 |
| `magclass` | Core array class for spatio-temporal data | https://github.com/pik-piam/magclass |
| `piamInterfaces` | Variable mapping / IIASA template handling | https://github.com/pik-piam/piamInterfaces |
| `piamenv` | Python/conda environment management | https://github.com/pik-piam/piamenv |
| `piamutils` | Shared utilities across piam packages | https://github.com/pik-piam/piamutils |
| `piamPlotComparison` | Scenario comparison plots | https://github.com/pik-piam/piamPlotComparison |
| `lucode2` | Run management, config, job submission | https://github.com/pik-piam/lucode2 |
| `mip` | Model intercomparison plots | https://github.com/pik-piam/mip |
| `magpie4` | MAgPIE output reporting helpers | https://github.com/pik-piam/magpie4 |
| `magpiesets` | Regional/sectoral set definitions | https://github.com/pik-piam/magpiesets |
| `edgeTransport` | Transport sector input data | https://github.com/pik-piam/edgeTransport |
| `reporttransport` | Transport sector reporting | https://github.com/pik-piam/reporttransport |
| `gdx` / `gdxrrw` | GDX file I/O bridge between GAMS and R | https://github.com/pik-piam/gdx |
| `gdxdt` | GDX to data.table helpers | https://github.com/pik-piam/gdxdt |
| `GDPuc` | GDP unit conversion | https://github.com/pik-piam/GDPuc |
| `luplot` | Plotting utilities | https://github.com/pik-piam/luplot |
| `luscale` | Scaling/aggregation helpers | https://github.com/pik-piam/luscale |
| `lusweave` | PDF report generation | https://github.com/pik-piam/lusweave |
| `madrat` | Data preprocessing framework | https://github.com/pik-piam/madrat |
| `gms` | GAMS/R interface utilities | https://github.com/pik-piam/gms |
| `quitte` | Tidy data helpers for IAM data | https://github.com/pik-piam/quitte |
| `rmndt` | Transport data utilities | https://github.com/pik-piam/rmndt |
| `remindClimateAssessment` | Climate assessment / MAGICC integration | https://github.com/pik-piam/remindClimateAssessment |
| `modelstats` | Run statistics collection | https://github.com/pik-piam/modelstats |
| `lpjclass` | LPJmL data class | https://github.com/pik-piam/lpjclass |
| `goxygen` | GAMS code documentation | https://github.com/pik-piam/goxygen |

### When a traceback bottoms out in a pik-piam package
1. Ask the user to paste the relevant function source: `getAnywhere(<function>)` or browse `https://github.com/pik-piam/<package>/blob/main/R/<function>.R`.
2. Check the package's GitHub **Issues** and **Releases/Changelog** for the installed version.
3. Check whether the installed version in `renv.lock` is current — a newer version may have the fix.
4. Only escalate to assuming a REMIND-side bug if the package is behaving correctly per its own spec.
5. Do **not** suggest cloning these repos locally — reference GitHub URLs only.

## renv architecture (REMIND-specific)

- There is **no `renv.lock` in the repo root**. The main renv library lives at `renv/library/` but has no lockfile — it is managed manually.
- Lockfile snapshots are archived in `renv/archive/<timestamp>_renv.lock`.
- At run start, `scripts/start/submit.R` snapshots the current main library into `output/<run>/renv.lock`, then calls `renv::restore()` inside the run folder.
- Each run folder therefore has its **own self-contained renv** at `output/<run>/renv/library/`.
- To inspect what a run actually loaded, check `output/<run>/renv/library/` — not the main library.
- To open R with the run's renv: `renv::activate("<run_folder>")` or `cd` into the run folder (`.Rprofile` auto-activates).
- `cfg$UseThisRenvLock` propagates a lockfile across cascade runs.

### Debugging renv issues
- `log_renv.txt` in the run folder captures the full `renv::restore()` output. Check it when a package behaves as if the wrong version is installed.
- **"linked from cache"** means renv used a cached build at that SHA — if the branch was updated without pushing before the cache was populated, the cached copy is stale. Fix: push the branch, then `renv::install(..., rebuild = TRUE)`.

### Workflow for developing a pik-piam package and testing it in a REMIND run
1. Push your changes to a branch on GitHub (e.g. `tonnrueter/remindClimateAssessment@sealvl`) — **must be pushed before installing**.
2. From the REMIND repo root: `renv::install("tonnrueter/<package>@<branch>", rebuild = TRUE)` — `rebuild = TRUE` forces a fresh download even if renv has a cache entry at that SHA.
3. Do **not** run `renv::snapshot()` — this would create a `renv.lock` in the repo root that REMIND's workflow does not expect and may interfere with `submit.R`.
4. Verify the correct version is in the main library: `packageDescription("<package>")[c("RemoteRef", "RemoteSha")]`
5. Start the REMIND run normally. `submit.R` will snapshot the main library (including your dev version) into `output/<run>/renv.lock` and restore it into `output/<run>/renv/library/`.
6. Confirm the run used the right version: `grep RemoteSha output/<run>/renv/library/R-*/*/DESCRIPTION`

## Topic-specific instructions
@instructions/gams.md
@instructions/r.md
@instructions/cicd.md
@instructions/gdx.md

## Playbooks (prompts/)
Paths are relative to the REMIND root (this repo is deployed as `remind-context/`).
- `remind-context/prompts/triage-failed-run.md` — triage a failed HPC/Slurm run from its logs.
- `remind-context/prompts/inspect-verify-gdx.md` — inspect a large `.gdx` safely, or verify a gdx
  write-path change end-to-end (R round-trip -> on-disk zeros -> GAMS `execute_loadpoint`).
  Reusable tool: `remind-context/scripts/gdx_inspect.R`.
