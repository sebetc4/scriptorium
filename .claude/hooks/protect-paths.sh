#!/usr/bin/env bash
# PreToolUse (Edit|Write|NotebookEdit): refuses the files the repository treats
# as generated, as the user's, or as immutable evidence. Scripts still write
# them through Bash — which is what keeps `make import` and `make fetch` able to
# acquire into `sources/` while this refuses an edit by hand.
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
  # The catalogue: a manifest is written through the tool, which keeps its
  # paths, kinds and digests true to the disk (core/catalogue.py).
  "$root/library/"*/manifest.yaml|"$root/library/manifest.yaml")
    deny "manifest.yaml is kept by the catalogue: python -m core.catalogue sync, or describe to name and describe. Never by hand." ;;
  # The anatomy of a document, docs/architecture.md §11. Two of its five
  # directories are not this agent's to write by hand.
  "$root/library/"*/sources/*)
    deny "sources/ belongs to the user: they fill it, and no tool modifies what is in it. Derived material goes to study/, the document to document/index.md." ;;
  "$root/library/"*/.work/*)
    deny ".work/ is remade by a command and removed by make clean: change what produces it, not the output." ;;
esac

# An investigation's pieces are proof, wherever the document keeps them. The
# journal marks one: `study/NOTES.md` since the document-anatomy roadmap, and
# `NOTES.md` at the root for a document written before it.
dir=$(dirname "$file")
while [ "$dir" != "/" ] && [ "$dir" != "." ]; do
  case "$(basename "$dir")" in
    raw|datasheets|images)
      up=$(dirname "$dir")
      { [ -f "$up/study/NOTES.md" ] || [ -f "$up/NOTES.md" ]; } &&
        deny "$(basename "$dir")/ holds pieces of an investigation, kept as received: never edited." ;;
  esac
  dir=$(dirname "$dir")
done
exit 0
