# Working in this REMIND checkout

REMIND is a GAMS + R integrated assessment model. This file is the always-on base; the deeper,
task-specific guidance lives in the `remind-*` skills (see the end). Four skills auto-load by task:
`debug-remind-run`, `inspect-remind-gdx`, `configure-remind-scenarios`, `edit-remind-code`.

## HPC environment

- **Load the piam module** before running most HPC workflows: `module load piam`. Required for
  `dumpgdx`, `rs`, `listinfes`, `nashstat`, and other REMIND/PIK utilities.
- Before suggesting any R/GAMS command, confirm the shell has the stack loaded — `module` is a
  shell *function*, not always inherited by child shells (VS Code remote terminals are a frequent
  offender). Cheap check (no `module` call): `echo "LOADEDMODULES=$LOADEDMODULES"` and
  `command -v Rscript gams`. Empty `LOADEDMODULES` ⇒ nothing loaded: prefix commands with
  `source /p/system/modulefiles/defaults/piam/module_load_piam`, or tell the user to open a fresh
  terminal (or reload the VS Code window). Don't debug a run from a broken shell.
- The stack pins **R 4.3.2** — avoid R 4.4+-only idioms in one-liners. The main trap is base `%||%`
  (4.4+): use `rlang::%||%` instead.

## General rules

- **Do not run git commits or fetches** (nor push/pull/merge/rebase). The user handles git.
  Read-only inspection (`git status`, `git diff`, `git log`) is fine.
- **Never install programs or libraries** (system packages, R/Python/npm, …). If a task needs a
  missing dependency, say so and let the user install it.
- **This is a shared remote server.** Don't modify anything outside the project directory, and
  avoid resource-heavy commands without asking.
- **Never submit or run batch jobs / model runs** (`sbatch`, `srun`, `Rscript start.R`,
  `Rscript output.R`). The user starts these. You may edit inputs and suggest the exact command.
- **Ask before editing or deleting files above the working directory.** Reading them is fine.
- **Never run `find`, `ls`, `du`, `locate`, or any recursive search above the working directory
  without explicit approval.** The HPC filesystem is enormous (`/p/tmp/`, `/p/projects/`, `/p/`,
  `/home/` hold millions of files) and an unscoped search will stall. Scope to `.` or a named
  subdirectory.

## Temporary files

Agent scratch, intermediate outputs, and scratch scripts go in `scratch/` (inside this context
dir; create it if absent). Delete temp files when the task is done; if the user asks to keep a
report, move it out of `scratch/` (it is gitignored). Never scatter temp files elsewhere or in
`/tmp`.

## Working with data files (filter first, never dump)

Reading large files whole — or pasting full tables — wastes context. Filter to the rows/columns
you need, compute in-script, print only the result.

- **Native tools before custom scripts.** For a gdx, `gdxdump <file>` (symbol inventory, no
  records) and `dumpgdx <file> <symbol> "<regex>"` (filtered values; always a strong regex) are
  the first reach; read into R with `readGDX()` for larger analyses. The `remind-*` skills' scripts
  are escalations for what the native tools can't do.
- **Never read `full.lst` / `full.log` / `log.txt` broadly** — grep for a status/error/iteration
  first (`grep -n "Status:" full.log`).
- Spreadsheets (`.xlsx`) need a script (binary); read one sheet, subset. Cell comments need Python
  `openpyxl` (R's `readxl` ignores them).
- Prefer `Grep` with `head_limit` over cat-style reads; `Read` with `offset`/`limit` for big text.
- When checking/comparing values, print a small result table (item, expected, actual, diff) — not
  the inputs. Sub-agents doing extraction should return computed numbers, not file contents.

## REMIND orientation

- **Entry points.** `main.gms` assembles the GAMS model; `Rscript start.R` runs a simulation,
  `Rscript output.R` builds the PDF report from a `*.mif`; tests are `make test`.
- **Code layout.** Core model in `core/`; per-module realizations in
  `modules/<nn>_<name>/<realization>/`. Execution order:
  `SETS → DECLARATIONS → DATAINPUT → EQUATIONS → PRELOOP → LOOP → OUTPUT` (the loop reads input
  gdx, applies bounds/presolve, solves in module 80, runs postsolve, writes output).
- **A run folder is self-contained.** Each `output/<SCENARIO_TIMESTAMP>/` has its own `cfg.txt`
  (resolved config = ground truth), own renv (`renv/library/`, auto-activated by `.Rprofile`),
  stage logs (`log.txt`, `log_renv.txt`, `log_climate.txt`, `full.log`, `full.lst`), gdx artifacts
  (`fulldata.gdx`, `non_optimal.gdx`, `abort.gdx`, `input.gdx`, `input_ref.gdx`), `*.mif`, and a
  copy of the GAMS source as submitted. Work *inside* the run folder — never compare against the
  repo root, which may have changed since the run started. `output/` and `input/` are vast; don't
  assume they can be scanned.
- **Config is layered** (later wins): `main.gms` switch defaults + `config/default.cfg` →
  `config/scenario_config*.csv` row → start-time R overrides → serialized to `output/<run>/cfg.txt`.
  To see what a run actually used, read its `cfg.txt`.
- **Cardinal code-reading rules** (full set in `edit-remind-code`): lead with the **default**
  realization (`$setglobal <module> <realization>` in `main.gms`) and check its guards hold;
  **declared ≠ computed** (find the assignment, not just the declaration); **units come from the
  declaration**; verify every identifier exists and cite only `path:line` you actually read.
- **Don't anchor on the bottom of a log.** A tail "infeasible" can be a legitimate outcome; root
  cause usually appears earlier. (Full debugging flow in `debug-remind-run`.)

## How to respond

Bottom line up front (BLUF). Apply to every response:

1. First sentence = the conclusion, recommendation, or direct answer. No preamble, no restating the
   question.
2. Add support only if needed: one short "Why" line, or at most 2 concise paragraphs.
3. Give **one** recommended approach. Add **one** alternative only if there is a real tradeoff. No
   menu answers.
4. Use plain words, one idea per sentence. No hedging unless the next sentence resolves it.
5. Be direct and actionable. Do not be overly critical.
6. If uncertain, say the bottom line is uncertain; don't force a single root cause the evidence
   doesn't support. Ask at most **2** clarifying questions, then proceed with the best guess.
7. Default to the shortest complete response. Fewer words win.

This governs communication only. It does not change how carefully you think, which tools you use,
or how thoroughly you verify. Be rigorous, then report BLUF.
