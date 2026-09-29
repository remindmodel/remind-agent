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

## R ecosystem conventions — tidyverse-first
- Go **all in on the tidyverse**: `dplyr` / `tidyr` / `purrr` / `stringr` / `tibble`,
  `glue` for strings, and the native pipe `|>` (or `%>%`). Concretely prefer:
  - `purrr::map`/`walk` over `*apply`, `Filter`, and `for`-accumulate loops;
  - `stringr::str_*` over `grepl`/`sub`/`grep`;
  - `glue::glue()` over `sprintf`/`paste0`;
  - a built-and-`print()`ed `tibble` over hand-aligned `sprintf` columns;
  - `dplyr::summarise`/`count`/`n_distinct` + `tidyr::pivot_wider` over manual aggregation.
- Reach for base R only where no tidyverse equivalent exists — and note it in a comment.
- Avoid `data.table`. Respect `renv.lock` (the tidyverse core is already in the stack).

## Working with large data/logs
- Avoid printing large tables/logs.
- Prefer `glimpse()`, `count()`, `summarise()`, and targeted filtering/selecting.
- When diagnosing, ask for small, specific excerpts rather than entire files.

## How to propose code changes
- Keep diffs minimal.
- Propose one recommended implementation (plus at most one alternative if needed).
- Include how to validate the change using existing commands (`make test`, or rerun `Rscript ...`).

## Cluster R version
- Cluster runs use **R 4.3.2**; avoid R 4.4+-only constructs in diagnostic snippets. The
  main trap is the *base* `%||%` (4.4+), which fails with `could not find function "%||%"` —
  use `rlang::%||%` (load `rlang`, or a tidyverse package that attaches it) instead.

## Working inside a run folder
- A run's renv is self-contained at `output/<run>/renv/library/` with its own
  `.Rprofile` that auto-activates when R starts in that directory.
- To introspect a run's actual config or installed packages, `cd` into the
  run folder *before* invoking `Rscript`. Don't try to load run-specific
  state from the repo root — versions may have drifted since the run started.

Example — resolve a run's config from inside the run folder:
```sh
cd output/<run>
Rscript -e 'cfg <- gms::loadConfig("cfg.txt"); str(cfg[grep("<pattern>", names(cfg))])'
```