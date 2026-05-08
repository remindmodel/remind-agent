#!/usr/bin/env bash
# Bootstrap remind-context inside a REMIND checkout.
#
# - Adds remind-context as a git submodule at <remind>/remind-context
# - Writes two pointer files so Copilot and Claude Code pick up the context:
#     <remind>/AGENT.md                       -> @remind-context/AGENT.md
#     <remind>/.github/copilot-instructions.md -> @../remind-context/AGENT.md
#
# The submodule, .gitmodules, and the pointer files are intentionally NOT
# committed to REMIND. Add them to your local .git/info/exclude if needed.

set -euo pipefail

REPO_URL="${REMIND_CONTEXT_URL:-https://github.com/tonnrueter/remind-context.git}"
REMIND_PATH="${1:-$PWD}"

if [ ! -d "$REMIND_PATH/.git" ]; then
    echo "Error: '$REMIND_PATH' is not a git repository." >&2
    exit 1
fi

cd "$REMIND_PATH"

if [ ! -d "remind-context/.git" ] && [ ! -f "remind-context/.git" ]; then
    echo "Adding remind-context submodule from $REPO_URL ..."
    git submodule add "$REPO_URL" remind-context
    git submodule update --init --recursive
else
    echo "remind-context submodule already present — updating ..."
    git submodule update --init --recursive --remote remind-context
fi

mkdir -p .github

if [ ! -f AGENT.md ]; then
    echo '@remind-context/AGENT.md' > AGENT.md
    echo "Wrote AGENT.md"
fi

if [ ! -f .github/copilot-instructions.md ]; then
    echo '@../remind-context/AGENT.md' > .github/copilot-instructions.md
    echo "Wrote .github/copilot-instructions.md"
fi

cat <<EOF

Done.

Next steps:
  - Pull updates later:   git submodule update --remote remind-context
  - Edit context:         cd remind-context && git checkout main && \$EDITOR ...
  - Do NOT commit remind-context/, .gitmodules, AGENT.md, or
    .github/copilot-instructions.md to REMIND.
EOF
