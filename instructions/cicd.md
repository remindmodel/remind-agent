# CI/CD instructions (applies to `.github/workflows/`, Makefile-related testing)

## Source of truth
- The main test entry point is `make test`. Prefer aligning workflows with this target.

## Change policy
- Do not change CI/CD workflows unless required for the task.
- Keep workflow changes minimal and explain the reason and the impact.
- Prefer consolidating logic in the Makefile rather than duplicating complex logic in workflow YAML.

## Output/log hygiene
- Avoid adding steps that upload or print massive logs by default.
- Prefer concise failure output with pointers to the relevant section.
