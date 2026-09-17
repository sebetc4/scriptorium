#!/usr/bin/env bash
# PostToolUse (Edit|Write): brand/tokens.yaml is the single source of the art
# direction; tokens.css and the diagram-design profile follow it only through
# `make brand`, and forgetting that step fails silently.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(jq -r '.tool_input.file_path // empty')
[ "$file" = "$root/brand/tokens.yaml" ] || exit 0
if ! out=$(make -C "$root" --no-print-directory brand 2>&1); then
  printf 'make brand failed after editing brand/tokens.yaml:\n%s\n' "$out" >&2
  exit 2
fi
jq -n --arg out "$out" '{hookSpecificOutput: {hookEventName: "PostToolUse",
  additionalContext: ("make brand ran after the edit of brand/tokens.yaml: " + $out)}}'
