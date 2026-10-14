---
name: inspect-remind-gdx
description: Inspect a REMIND GDX file safely, or verify a GDX writer change — fulldata.gdx and other large gdx, the GAMS/R zero-squeezing boundary, execute_loadpoint round-trips. Use when reading or comparing gdx contents, or when changing a script that writes/reads a .gdx.
---

# Inspecting & verifying GDX

GDX files cross the GAMS↔R boundary. A model gdx (`fulldata.gdx`) has ~1700 symbols and tens of MB
— output must stay bounded regardless of file size.

## Native tools first
- `gdxdump <file>` — symbol inventory without records (cheap even on a model gdx).
- `dumpgdx <file> <symbol> "<regex>"` — a few filtered values; **always** a strong regex
  (unfiltered output is huge). Needs the piam module.
- R `readGDX()` / gamstransfer `Container$read(path, symbols = name)` — larger filtered analyses;
  compute in-script, print only the result.
- Escalate to `scripts/gdx_inspect.R` only for bounded structural analytics (per-dim extent,
  sparsity, triangularity) on a huge or `(tall,tall)` symbol.

## Guard rails (non-negotiable)
- **Never dump records.** Read metadata first (`records = FALSE`), then ONE symbol at a time.
- Lead with a class-count summary; list symbols only when filtered/small. Output ~O(1) in file size.
- `(tall, tall)` parameters (e.g. `pm_temperatureImpulseResponseCO2`) are annual, ~50k records,
  triangular — never dump; use the tool.

## Which gdx holds what (in a run folder)
`fulldata.gdx` final feasible data · `non_optimal.gdx` last non-optimal/infeasible state ·
`abort.gdx` state after an execution error · `input.gdx` starting data · `input_ref.gdx`
reference-run data fixing `t < cm_startyear` (when `cm_startyear > 2005`; check `cfg.txt`).

## What this skill covers
- **Inspect** a gdx too big to dump — `reference/gdx.md` (zero-squeezing semantics, gamstransfer
  access, the `tall` caveat) and `reference/verify-gdx.md §A`.
- **Verify a writer change** end-to-end (R round-trip → on-disk zeros → GAMS `execute_loadpoint`) —
  `reference/verify-gdx.md §B`.

## Reference
- `reference/gdx.md` — GDX-is-sparse / zero-squeezing, `execute_loadpoint` semantics, reading in R.
- `reference/verify-gdx.md` — the inspect + writer-verification playbook (tool: `scripts/gdx_inspect.R`).

## Related skills
- `edit-remind-code` — a gdx writer change is a code change; verify it compiles and reads back.
- `debug-remind-run` — reading `abort.gdx` / `non_optimal.gdx` while diagnosing an infeasibility.
