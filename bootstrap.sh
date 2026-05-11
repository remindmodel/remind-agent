#!/usr/bin/env bash
# Bootstrap remind-context inside a REMIND checkout.
#
# remind-context is cloned as a plain (untracked) subdirectory of REMIND:
#
#   <remind>/remind-context/    <- this repo
#   <remind>/AGENT.md           <- pointer: @remind-context/AGENT.md
#   <remind>/.github/
#       copilot-instructions.md <- pointer: @../remind-context/AGENT.md
#
# Run once per REMIND checkout. To update: git -C remind-context pull

set -euo pipefail

REPO_URL="${REMIND_CONTEXT_URL:-https://github.com/tonnrueter/remind-context.git}"
REMIND_PATH="${1:-$PWD}"

if [ ! -d "$REMIND_PATH/.git" ]; then
    echo "Error: '$REMIND_PATH' is not a git repository." >&2
    exit 1
fi

cd "$REMIND_PATH"

if [ ! -d "remind-context/.git" ] && [ ! -f "remind-context/.git" ]; then
    echo "Cloning remind-context from $REPO_URL ..."
    git clone "$REPO_URL" remind-context
else
    echo "remind-context already present — pulling ..."
    git -C remind-context pull
fi

# Keep remind-context/ out of git status without touching committed .gitignore
exclude='.git/info/exclude'
if ! grep -qF 'remind-context/' "$exclude" 2>/dev/null; then
    echo 'remind-context/' >> "$exclude"
fi

mkdir -p .github

if [ ! -f AGENT.md ]; then
    printf '@remind-context/AGENT.md' > AGENT.md
    echo "Wrote AGENT.md"
fi

if [ ! -f .github/copilot-instructions.md ]; then
    printf '@../remind-context/AGENT.md' > .github/copilot-instructions.md
    echo "Wrote .github/copilot-instructions.md"
fi

cat <<'EOF'

Done.

Next steps:
  - Pull updates later:  git -C remind-context pull
  - Repeat bootstrap for each REMIND checkout you use.
  - Do NOT commit remind-context/, AGENT.md, or
    .github/copilot-instructions.md to REMIND.
EOF
