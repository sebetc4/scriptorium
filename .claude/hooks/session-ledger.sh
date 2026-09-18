#!/usr/bin/env bash
# SessionStart: every session of this project leaves session-level numbers,
# whether or not anyone sat down to review it. Reviews are written on purpose
# and a purpose is selective; the ledger is what keeps the corpus from becoming
# a record of the tasks that went well.
#
# SessionEnd is not used on purpose: it does not fire for a session that
# crashed or was killed, which are the sessions whose cost is most worth
# knowing. The price is that a ledger is always written from outside the
# session it describes, one session late — so an entry is keyed by transcript
# and carries the size it was computed from, and the live session is skipped
# and swept whole by the next one.
#
# It must cost nothing perceptible and must never block a session start: it
# runs in the background and always exits zero.
set -u
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
sweep="$root/.claude/skills/session-review/scripts/metrics.py"
[ -x "$root/.venv/bin/python" ] || exit 0
[ -f "$sweep" ] || exit 0
("$root/.venv/bin/python" "$sweep" --sweep >/dev/null 2>&1 &) 
exit 0
