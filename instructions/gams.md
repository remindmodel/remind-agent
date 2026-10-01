# GAMS instructions (applies to `main.gms`, `core/`, `modules/`)

Before explaining what GAMS code does, apply the checks in *Reading REMIND code* (`AGENT.md`): default
realization and switch guards, declared vs computed, equation conditions, units, preconditions.

## Change strategy
- Make the smallest, most localized change that addresses the issue; no broad refactors unless asked.
- Avoid renaming symbols (sets/params/equations) across many modules unless asked.
- Prefer patterns already present in the codebase (follow local conventions).

## Debugging
Follow the *Debugging protocol* in `AGENT.md`. If a fix depends on a hypothesis (e.g., infeasibility vs
solver/license vs missing include), label it and request one targeted log excerpt to confirm.
