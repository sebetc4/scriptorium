#!/usr/bin/env bash
# PreToolUse (Bash): Python runs through .venv/bin/python, never the system
# interpreter — only there is the editable `core` package installed.
set -u
cmd=$(jq -r '.tool_input.command // empty')
# A python word in command position: start of a line, or after ; & | ( ` $( or
# a wrapper (env, time, xargs, exec, sudo, nohup) or a VAR=value prefix.
if printf '%s\n' "$cmd" | grep -qE '(^|[;&|(`]|\$\()[[:space:]]*((env|time|xargs|exec|sudo|nohup|[A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*)[[:space:]]+)*(/usr(/local)?/bin/)?python[0-9.]*([[:space:]]|$)'; then
  echo "Use .venv/bin/python, never the system python (CLAUDE.md). If .venv is missing, run make setup." >&2
  exit 2
fi
exit 0
