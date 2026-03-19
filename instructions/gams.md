# GAMS instructions (applies to `main.gms`, `core/`, `modules/`)

## Scope & entry points
- GAMS entry point is `main.gms`.
- Core model logic lives in `core/` and `modules/`.
- Prefer minimal, localized changes over broad refactors unless explicitly requested.

## Change strategy
- Make the smallest change that addresses the issue.
- Avoid renaming symbols (sets/params/equations) across many modules unless asked.
- Prefer patterns already present in the codebase (follow local conventions).

## Debugging guidance (HPC-aware)
- Many failures show up first in `output/<run>/log.txt` (Slurm stdout/stderr).
- Use `full.log` only for surgical excerpts (last few hundred lines or the first error context).
- When interpreting failures, prioritize concrete log evidence over speculation.
- Infeasibility can be a valid outcome; treat it as such unless logs indicate solver crash, missing data, or runtime error.

## When suggesting fixes
- Provide one recommended fix (plus at most one alternative).
- If a fix depends on a hypothesis (e.g., infeasibility vs solver/license vs missing include), clearly label it and request one targeted log excerpt to confirm.
