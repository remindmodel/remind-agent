# GDX instructions (GAMS <-> R data exchange via `.gdx`)

Applies whenever a `.gdx` file crosses the GAMS/R boundary — inspecting one,
or changing a script that writes/reads it. Companion playbook:
`remind-context/prompts/inspect-verify-gdx.md`; tool: `remind-context/scripts/gdx_inspect.R`.

## GDX is sparse — mind the zeros
- A GAMS parameter cell equal to 0 is normally **not stored**; 0 is the default on read.
- GAMS `execute_unload` (and solve output such as `fulldata.gdx`) **squeezes zeros**.
- `quitte::write.gdx` (gamstransfer) **does persist explicit 0 rows** when they are in the
  data frame — equivalent to the old `wgdx.lst(squeeze = FALSE)`.
- `quitte::read.gdx` **drops** zeros under its default `squeeze = TRUE`. This is a *read-side*
  effect only; GAMS reads the gdx directly and still sees any stored zeros. Pass
  `read.gdx(..., squeeze = FALSE)` to see them in R.

## `execute_loadpoint` semantics
- `execute_loadpoint 'file' target = source;` loads records of `source` from `file.gdx`
  into `target`, mapping by **dimension position + UEL label**, *not* by domain-set name.
- So the source's domain names and any extra Set symbols in the gdx are inert; only
  (a) column/dimension order and (b) label membership in the target's domain matter.
  A writer may relabel a domain (e.g. `tall,tall` -> `tall,tall1`) with no effect on the load.
- It does **not** re-initialise the target — cells with no record keep their current value.
  Corollary: writing squeezed (zero-less) data is safe only if no cell must flip
  nonzero -> zero between successive loads (the model does not re-zero between iterations).

## `tall` is annual
- `tall` = every year 1900-3000 (`core/sets.gms`). Parameters over `(tall, ...)` — especially
  `(tall, tall)` like `pm_temperatureImpulseResponseCO2` — are annual and can be huge
  (~50k records, triangular). Never dump them; use `remind-context/scripts/gdx_inspect.R`.

## Reading gdx in R (gamstransfer)
- The R6 `Container` has **no `[[` accessor**; use `container$getSymbols(name)[[1]]`.
- Metadata only: `container$read(path, records = FALSE)` (cheap even for a model gdx).
- One symbol's records: `container$read(path, symbols = name)`.
- A parameter over domain `(tall, tall)` yields record columns `tall_1`, `tall_2`.
