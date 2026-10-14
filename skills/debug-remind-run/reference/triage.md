# Triage a failed run (HPC/Slurm logs)

You are helping triage a failed run for a GAMS + R workflow on an HPC cluster (Slurm).
Logs are messy: the last lines often show "optimizer infeasible" which can be a legitimate model outcome.
Do NOT anchor on the bottom of the log; prioritize the earliest anomaly that explains later symptoms.

## Inputs I will provide
I will paste excerpts from:
- `output/<SCENARIO_TIMESTAMP>/log.txt` (Slurm stdout/stderr; primary)
  - **Required: header (~60 lines) + first anomaly block + tail (~120 lines)**
  - Do NOT skip to other files until all three parts are provided and insufficient.
Optionally:
- `output/<SCENARIO_TIMESTAMP>/full.log` (only small excerpts, only if log.txt is insufficient)

## Your task
1) Identify whether the run failed during:
   - simulation (`Rscript start.R` / GAMS), or
   - reporting (`Rscript output.R` / `.mif` -> PDF).
2) Find the **earliest meaningful anomaly** in the pasted excerpts (error/warning that plausibly triggers later failure).
3) Decide whether "infeasible" at the end is likely:
   - a legitimate model outcome, OR
   - a downstream symptom of an earlier runtime/config/data error.

## How to respond (strict)
- Keep it concise.
- Provide exactly:
  - **Likely root cause:** (1 short paragraph, reference exact log lines I pasted)
  - **Next check:** (1 concrete check; tell me what to paste next if needed)
  - **Fix:** (1 recommended fix)
- Optionally include **one** alternative fix only if there is a real tradeoff.
- Ask at most **1** clarifying question.

## Heuristics to use
Treat as high-signal anomalies (examples):
- file/path issues: "cannot open", "file not found", permissions
- environment issues: missing modules, missing solver, license errors
- runtime issues: OOM, "Killed", segfault, stacktrace, R error
- numeric/data issues: NaN/Inf, domain errors, invalid values
- GAMS/solver: compilation errors, "Abort", solver crash/termination, unexpected return codes

If you suspect the issue is earlier than what I pasted, ask me for a block around the first anomaly you think is missing (tell me what phrase to search for).