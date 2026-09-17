#!/usr/bin/env bash
# PostToolUse (Edit|Write), async: after an edit under .claude/skills/<name>/,
# runs that skill's own suite in the background and wakes Claude on failure.
# Some tests read documents kept out of the repository: a failure may be a
# missing file, not a broken assertion.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(jq -r '.tool_input.file_path // empty')
case "$file" in
  "$root/.claude/skills/"*/scripts/*.py|"$root/.claude/skills/"*/tests/*.py) ;;
  *) exit 0 ;;
esac
skill=${file#"$root/.claude/skills/"}; skill=${skill%%/*}
[ -x "$root/.venv/bin/python" ] || exit 0
[ -d "$root/.claude/skills/$skill/tests" ] || exit 0
cd "$root" || exit 0
if ! out=$(.venv/bin/python -m pytest -q -x "$root/.claude/skills/$skill/tests" 2>&1); then
  printf 'The %s suite fails after editing %s:\n%s\n' "$skill" "${file#"$root/"}" "$(printf '%s\n' "$out" | tail -40)" >&2
  exit 2
fi
exit 0
