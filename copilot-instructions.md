# Copilot instructions (repo-wide)

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

## Data & outputs
- `input/` and `output/` can be vast and are intentionally messy.
- `output/` is gitignored. Each run creates `output/<SCENARIO_TIMESTAMP>/`.
- Diagnostics for a run live in that run folder:
  - `log.txt` (this is Slurm stdout/stderr for the job) ✅ primary debugging source
  - `full.log` (can be massive) — never request or paste the full file
  - `log_climate.txt` may exist and can be relevant

## R conventions (defaults)
- Prefer tidyverse.
- Avoid `data.table`. Prefer `tibble`/`dplyr`/`readr`.
- Base R is OK as a fallback if it reduces complexity.
- Respect `renv.lock` and existing dependency choices.

## How to respond (style contract)
- Be concise by default (aim for 5–12 bullets total).
- Provide **one** recommended approach. Optionally include **one** alternative only if there is a real tradeoff.
- Avoid “menu answers” and avoid being overly critical. Be direct and actionable.
- When unsure, ask at most **2** clarifying questions, then proceed with the best guess.

## Debugging protocol (failed runs)
Assume debugging starts from a failed run in `output/<SCENARIO_TIMESTAMP>/`.

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

// ...existing code...

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
