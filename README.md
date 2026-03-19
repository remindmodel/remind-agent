# remind-context

This repository contains GitHub Copilot context files for the REMIND codebase.

## What are context files?

Context files are Markdown files that instruct GitHub Copilot about a codebase - its
structure, conventions, and how to respond. VS Code picks them up automatically from
`.github/copilot-instructions.md` (repo-wide instructions), `.github/instructions/`
(topic-specific instruction files) and `.github/prompts/` (task specific typical use cases)

## Why a separate repository?

Git submodules would be the natural solution for keeping these files under independent
version control while having them available in the main codebase. However, two constraints
make this impossible:

1. VS Code requires Copilot context files to reside at the top level of the `.github/`
   directory (i.e. `.github/copilot-instructions.md` and `.github/instructions/`)
2. The `.github/` directory is already under version control in the main REMIND repository
   (CI/CD workflows, etc.)

A submodule cannot coexist with already-tracked files in the same directory, so the
files are instead copied manually into the target codebase using `copy-context.sh`.

## Usage

Copy context files to a REMIND codebase using `copy-context.sh`. The default target
is `/p/tmp/$USER/remind` (cluster scratch directory), but you can specify any path:

```bash
# Copy to default ../remind
./copy-context.sh

# Copy to a specific codebase
./copy-context.sh ~/code/some_specific_remind_version
```

To bring changes made in a REMIND codebase back to this repository:

```bash
# Reverse from default ../remind
./copy-context.sh -r

# Reverse from a specific codebase
./copy-context.sh -r ~/code/some_specific_remind_version
```

The copied files will be untracked in the target codebase, which is intentional.