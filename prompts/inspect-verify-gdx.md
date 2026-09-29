# Inspect a GDX / verify a GDX write-path change

Use when: (a) you need the structure of a `.gdx` too big to dump — especially
`fulldata.gdx` (~1700 symbols, tens of MB), or (b) an R script's gdx writer changed
and you must prove the GAMS side still loads it. Underlying facts: `remind-context/instructions/gdx.md`.

Shell prep: `source /p/system/modulefiles/defaults/piam/module_load_piam`
(confirm `LOADEDMODULES` is non-empty and `Rscript`/`gams` resolve; R is 4.3.2).

## Guard rails (context safety) — non-negotiable
- **Never** print records. Read metadata first (`records = FALSE`), then ONE symbol at a time.
- Bound output by **symbol count too**: a model gdx has ~1700 symbols. Lead with a
  class-count summary; list symbols only when filtered/small; never auto-deep-dive every
  parameter. Output size must be ~O(1) in file size.

## A. Inspect
`Rscript remind-context/scripts/gdx_inspect.R <file.gdx> [symbol] [--grep=<regex>] [--list]`
- Bare on a model gdx: class-count headline + "narrow it down" hints (safe on `fulldata.gdx`).
- `--grep=<re>` or an exact `symbol`: filtered inventory + per-symbol deep-dive — dims,
  per-dimension extent, value summary, fill/sparsity, triangularity, adaptive shape map.

## B. Verify a writer change — escalate confidence, cheapest first
1. **R round-trip**: `write.gdx()` then `read.gdx(..., squeeze = FALSE)`; confirm
   rows / labels / values match the source data frame.
2. **On-disk truth**: `Container$new(f)$getSymbols("<sym>")[[1]]$records` — check
   `sum(value == 0)` to confirm explicit zeros persisted on disk (step 1's `read.gdx`
   squeezes them by default — a read-side effect, not a writer bug; see gdx.md).
3. **GAMS contract**: re-write the real records via the new writer, then run the *exact*
   `execute_loadpoint` from the consuming postsolve into a pre-zeroed target and compare
   aggregates to the R ground truth. Template (adapt the target declaration/domain):
   ```gams
   set tall / 1900*3000 /; alias(tall, tA, tB);
   parameter tgt(tall,tall); tgt(tall,tall) = 0;            !! mirror datainput pre-init
   execute_loadpoint '<file-without-.gdx>' tgt = <sourceSymbol>;
   scalar nz, s, mx;
   nz = sum((tA,tB)$tgt(tA,tB), 1);
   s  = sum((tA,tB),  tgt(tA,tB));
   mx = smax((tA,tB), tgt(tA,tB));
   display nz, s, mx;
   ```
   Run: `gams verify.gms --gdxfile=<file-without-.gdx> o=<scratch>/x.lst lo=0`
   — do **not** pass `curdir=` (not a valid option; GAMS exits 6). Remove the `225*/`
   scratch dirs GAMS leaves in cwd afterwards. A base GAMS module (no solver/license) suffices.

## How to report (strict)
- **GAMS status** (Normal completion?) + a 3-row `nNonzero / sum / max` table
  (R ground truth vs. loaded), and **one sentence** on any behavioural delta
  (e.g. explicit-zero handling). No record dumps.
