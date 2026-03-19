# R instructions (applies to `scripts/`, `start.R`, `output.R`)

## Execution model
- Scripts are expected to run non-interactively (e.g., via `Rscript ...`), often on an HPC cluster under Slurm.
- Default run commands:
  - Simulation: `Rscript start.R`
  - Reporting: `Rscript output.R`

## Reporting pipeline
- `output.R` reads a `*.mif` report file (CSV-like with a specific structure) and generates a PDF with plots based on user selection.
- Failures may be:
  - upstream simulation/model (no/invalid `.mif` produced), or
  - downstream parsing/plotting/PDF generation.

## R ecosystem conventions
- Prefer tidyverse.
- Avoid `data.table`. Prefer `tibble` + `dplyr` + `readr`.
- Base R is acceptable as fallback.
- Respect `renv.lock` and avoid introducing new dependencies unless necessary.

## Working with large data/logs
- Avoid printing large tables/logs.
- Prefer `glimpse()`, `count()`, `summarise()`, and targeted filtering/selecting.
- When diagnosing, ask for small, specific excerpts rather than entire files.

## How to propose code changes
- Keep diffs minimal.
- Propose one recommended implementation (plus at most one alternative if needed).
- Include how to validate the change using existing commands (`make test`, or rerun `Rscript ...`).