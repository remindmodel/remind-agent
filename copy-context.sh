#!/bin/bash

CONTEXT_DIR="$(dirname "$0")"
DEFAULT_REMIND_PATH="/p/tmp/$USER/remind"
CONTEXT_FILES=("copilot-instructions.md" "instructions/" "prompts/")

usage() {
  echo "Usage: $0 [-r] [--force] [remind_path]"
  echo ""
  echo "  remind_path   Path to the REMIND codebase (default: $DEFAULT_REMIND_PATH)"
  echo "  -r            Reverse: copy from REMIND back to remind-context"
  echo "  --force       Skip diff check and overwrite without prompting"
  exit 1
}

diff_check() {
  local src=$1
  local dst=$2
  if [ -e "$dst" ] && ! diff -rq "$src" "$dst" > /dev/null 2>&1; then
    echo "Warning: '$dst' differs from source:"
    diff -r "$src" "$dst"
    echo ""
    read -r -p "Overwrite? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[yY]$ ]]; then
      echo "Aborted."
      exit 1
    fi
  fi
}

REVERSE=false
FORCE=false
while getopts "rh-:" opt; do
  case $opt in
    r) REVERSE=true ;;
    h) usage ;;
    -) [ "$OPTARG" = "force" ] && FORCE=true || usage ;;
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
  for f in "${CONTEXT_FILES[@]}"; do
    [ "$FORCE" = false ] && diff_check "$REMIND_PATH/.github/$f" "$CONTEXT_DIR/$f"
    cp -R "$REMIND_PATH/.github/$f" "$CONTEXT_DIR/"
  done
  echo "Done. Don't forget to commit and push your changes!"
else
  echo "Copying context files to $REMIND_PATH..."
  for f in "${CONTEXT_FILES[@]}"; do
    [ "$FORCE" = false ] && diff_check "$CONTEXT_DIR/$f" "$REMIND_PATH/.github/$f"
    cp -R "$CONTEXT_DIR/$f" "$REMIND_PATH/.github/"
  done
  echo "Done."
fi