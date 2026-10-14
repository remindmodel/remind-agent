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

## Working style for structural changes

### Ask clarifying questions before proposing solutions
Before proposing any structural change to the repo (adding submodules, moving files,
modifying the index), ask at most 2 targeted questions to establish:
- What already exists at the target location
- Whether the affected files/directories are tracked or untracked

A single `git ls-files <path>` or `ls <path>` question upfront can rule out entire
classes of broken approaches.

### Recognize dead ends early
If a proposed solution requires a workaround to function, question whether the solution
is correct in the first place. 

### Don't iterate on a broken approach
If the first two attempts at a solution fail, stop and restate the problem from scratch
before proposing a third option.