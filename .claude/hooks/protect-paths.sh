#!/usr/bin/env bash
# PreToolUse (Edit|Write|NotebookEdit): refuses the files the repository treats
# as generated or as immutable evidence. Scripts still write them through Bash.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
[ -n "$file" ] || exit 0

deny() { printf '%s\n' "$1" >&2; exit 2; }

case "$file" in
  "$root/brand/tokens.css")
    deny "brand/tokens.css is generated: edit brand/tokens.yaml, then make brand." ;;
  "$root/brand/icons/"*)
    deny "brand/icons/ is the pinned Lucide set: regenerate it with make icons." ;;
  "$HOME/.claude/plugins/"*diagram-design*|"$HOME/.diagram-design/"*)
    deny "diagram-design is never modified: change brand/sync.py and run make brand." ;;
  "$root/library/"*/sources/*)
    deny "sources/ is the immutable record of an import or a capture: edit index.md instead." ;;
esac

# A sourcing investigation is any folder holding NOTES.md; its pieces are proof.
dir=$(dirname "$file")
while [ "$dir" != "/" ] && [ "$dir" != "." ]; do
  case "$(basename "$dir")" in
    raw|datasheets|images)
      [ -f "$(dirname "$dir")/NOTES.md" ] &&
        deny "$(basename "$dir")/ holds pieces of an investigation, kept as received: never edited." ;;
  esac
  dir=$(dirname "$dir")
done
exit 0
