#!/bin/bash

CONTEXT_DIR="$(dirname "$0")"
DEFAULT_REMIND_PATH="/p/tmp/$USER/remind"

usage() {
  echo "Usage: $0 [-r] [remind_path]"
  echo ""
  echo "  remind_path   Path to the REMIND codebase (default: $DEFAULT_REMIND_PATH)"
  echo "  -r            Reverse: copy from REMIND back to remind-context"
  exit 1
}

REVERSE=false
while getopts "rh" opt; do
  case $opt in
    r) REVERSE=true ;;
    h) usage ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))

REMIND_PATH=${1:-"$DEFAULT_REMIND_PATH"}

if [ ! -d "$REMIND_PATH" ]; then
  echo "Error: REMIND path '$REMIND_PATH' does not exist"
  exit 1
fi

if [ "$REVERSE" = true ]; then
  echo "Copying context files from $REMIND_PATH back to remind-context..."
  cp "$REMIND_PATH/.github/copilot-instructions.md" "$CONTEXT_DIR/"
  cp -R "$REMIND_PATH/.github/instructions/" "$CONTEXT_DIR/"
  echo "Done. Don't forget to commit and push your changes!"
else
  echo "Copying context files to $REMIND_PATH..."
  cp "$CONTEXT_DIR/copilot-instructions.md" "$REMIND_PATH/.github/"
  cp -R "$CONTEXT_DIR/instructions/" "$REMIND_PATH/.github/"
  echo "Done."
fi