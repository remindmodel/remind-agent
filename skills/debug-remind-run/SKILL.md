---
name: debug-remind-run
description: Diagnose a failed or non-converged REMIND run from its output folder — pre-processing/compilation/execution errors, pre-triangular and solver infeasibilities, non-convergence, and TIRF/climate corruption. Use when a run under output/ failed, aborted, hit the iteration ceiling, or produced climate-driven nonsense.
---

# Debugging a REMIND run

Assume you start from a run folder `output/<SCENARIO_TIMESTAMP>/`. Work *inside* it — `full.gms`,
the gdx files and `cfg.txt` there are what actually ran, which may differ from the repo source.

**Don't anchor on the bottom of the log.** A tail "infeasible"/"Execution error" is often a
*symptom*, not the root cause — treat it as confirmation, and look earlier (missing inputs,
environment, runtime/numeric errors, a bound conflict). Don't force a single root cause when the
diagnostics don't support one.

## Step 1 — Establish the problem type

Cross-check two sources; if they disagree, trust `log.txt`.

- **`rs -f <run>`** (piam module) summarizes status: `RunStatus` (GAMS ran? `full.log missing` =
  GAMS never started), `Conv` (converged? criteria in `modules/80_optimization/nash/postsolve.gms`),
  `Mif` (reporting produced, `sumErr` = summation errors).
- **`log.txt` keywords:** `Creating full.gms` (R pre-processing done, GAMS compiling — compile
  errors flagged just below) → `Starting REMIND...` (GAMS compiled & started) → `REMIND run
  finished!` (read the `Model summary` below it).
- **No piam module (not on the cluster):** the `Model summary` at the end of `log.txt` carries most
  of what `rs` shows. See "Without the piam tools" below.
- **First, scan the tail for `CANCELLED` / `SIGNAL Terminated`** — if present, GAMS was killed
  externally (walltime, OOM, node failure). Report as an infra/timeout issue; no further
  classification needed.

## Step 2 — Problem types

### Case A — Pre-processing bug (R)
`Creating full.gms` is **absent** from `log.txt`. Read the last lines of `log.txt` for the error.

### Case B — Compilation error (GAMS)
`Creating full.gms` present, but a later line says `Compiling ... failed, stopping.`
1. `grep -n "^\*\*\*\*" main.lst` — every `****` error line. Focus on the **first** `$XYZ` error;
   later ones usually cascade. A block looks like:
   ```
   9251:****            $187 $187
   9252:**** LINE    358 INCLUDE     /path/to/core/declarations.gms
   9254:**** 187  Assigned set used as domain
   ```
   The `LINE ... INCLUDE` chain gives the source file + line.
2. `sed -n '<line-10>,<line+5>p' main.lst` for context.
3. Check the executed `full.gms` first (it's what compiled), then map back to `core/`/`modules/`
   with `grep -rn "<symbol>" core/ modules/` and confirm before proposing a fix.

### Case C — Execution error (GAMS)
`Model summary` points to `*** Status: Execution error(s)`. `abort.gdx` holds the last state.
Note: `rs` may mislabel a persistent infeasibility (Case E) as execution error — cross-check the
`****` line and modelstat. Escalate the filter:
```
grep -n "^\*\*\*\*" full.lst | grep -i "exec"
grep -n "^\*\*\*\*" full.lst | grep -viE "SOLVER STATUS|MODEL STATUS|REPORT SUMMARY|FILE SUMMARY"
grep -n "^\*\*\*\*" full.lst
```
Skip `**** ERRORS/WARNINGS IN VARIABLE ...` (informational). Then `sed -n '<line-15>,<line+15>p'
full.lst` for the failing source line + indices; explain it with values from `abort.gdx` /
`input.gdx`.

### Case D — Pre-triangular infeasibility
Modelstat = 4 (also via `nashstat` or the Model summary). GAMS found conflicting bounds/constraints
before the solver. Search `Solution Report` in `full.lst` — the `hybrid` model should show
modelstat 4; read down to the `---- EQU` listing for the pre-triangular infeasible equations and
their indices (region, year). Check the offending variables/parameters in `non_optimal.gdx` — a
parameter or bound that is 0/NA where it shouldn't be is the usual culprit.

### Case E — Solver infeasibility
Modelstat = 5 (locally infeasible). Some infeasibilities are spurious and clear over Nash
iterations; if they persist the run stops and a `testOneRegi` run of an infeasible region
(`nashstat -a`) produces the full equation listing. Note: `rs` may show "Execution error" here too
— the abort (`maximum number of consecutive failures ...`) is the *consequence*, and `log.txt` may
warn `The error that stopped GAMS is probably not the actual reason to fail.`
1. In the run folder, `listinfes` prints the first infeasible equation, e.g.:
   ```
   regi OAS: q_smoothphaseoutCapEarlyReti
              LOWER   LEVEL    UPPER    MARGINAL
   2035.OAS.pc -INF   0.0001   .        -1024.0000 INFES
   ```
   LEVEL outside [LOWER, UPPER] ⇒ infeasible; MARGINAL ≈ sensitivity to relaxing it. `listinfes`
   may list several rows — ones pointing at the **same variable/index** pinpoint the culprit.
2. Find the equation in `core/`/`modules/`; read its formulation.
3. Inspect the involved variables' bounds and parameters in `non_optimal.gdx` (see the
   `inspect-remind-gdx` skill). Common cause: a parameter = 0 or a too-tight bound for exactly the
   failing index.
4. Check other equations constraining those variables; compare against `input.gdx` /
   `input_ref.gdx` and recent commits touching the equation/parameters.

### Case F — Non-convergence
Modelstat = 1/2 (solved) but `Conv = not_converged` — hit the iteration ceiling. Check
`p80_messageShow` in `fulldata.gdx` (or the per-iteration `Convergence diagnostics` in `full.lst`)
for which criterion is unmet. **Follow `reference/nonconvergence.md` + `scripts/nash_converge.py`**
for the full workflow (which market won't settle, oscillation vs stall, trade tension vs solver,
whether the price/SCC answer is stable anyway). Quick flag: CO2 prices > 1500 USD/tCO2eq often mean
the climate target is infeasible, which is the real reason the markets won't clear.

## Tools (piam module)
`rs -f <run>` (status) · `nashstat` / `nashstat -a` (modelstat per region, last iteration) ·
`listinfes` (first infeasible equation) · `dumpgdx` / `readGDX` for exact values.

## Without the piam tools (laptop, copied run folder)

| cluster tool | use instead |
|---|---|
| `rs -f <run>` | `grep -n -A25 "Model summary" log.txt`: run time, which gdx files exist, modelstat, `full.log` status, infeasibilities (`nashstat -F` output), failed markets and taxes. Missing if the run was killed before the end |
| `nashstat` | `gdxdump fulldata.gdx Symb=p80_repy Format=csv`: modelstat and solvestat per region, last iteration |
| `listinfes` | the infeasibility list in the `Model summary`. No summary: say this step needs the cluster |
| `dumpgdx <file> <symbol> "<regex>"` | `gdxdump <file> Symb=<symbol> Format=csv \| grep -E "<regex>"`, or `readGDX()` in R |

`gdxdump` comes with GAMS and must be on the PATH; if it isn't, ask the user where GAMS is installed.

A run copied from the cluster needs at least `log.txt`, `cfg.txt`, `main.lst` and whichever of
`fulldata.gdx`, `non_optimal.gdx`, `abort.gdx` exists. Add `full.lst` (large) for execution errors
and infeasibilities, `nash_info_convergence.csv` for non-convergence. Ask the user for a missing
file instead of guessing.

If a step in this guide doesn't work where you are (a missing tool, a different path), say so and
suggest a fix to this guide.

## Reference
- `reference/triage.md` — triage a failed HPC/Slurm run from `log.txt` excerpts.
- `reference/nonconvergence.md` — the full Case F playbook (tool: `scripts/nash_converge.py`).
- `reference/tirf.md` — corrupted climate impulse response / TIRF spike (tool: `scripts/tirf_lst.py`).
- `reference/climate-debugging.md` — `log_climate.txt` structure, MAGICC ↔ parset compatibility.
- REMIND's own `tutorials/10_DebuggingREMIND.md` for broader context.

## Related skills
- `inspect-remind-gdx` — pull values out of `abort.gdx` / `non_optimal.gdx` / `input.gdx` safely.
- `edit-remind-code` — once you've located the failing equation: the code-reading discipline and
  mapping `full.gms` back to source.
- `configure-remind-scenarios` — when a bad input/switch is suspected ("what did this run use?").
