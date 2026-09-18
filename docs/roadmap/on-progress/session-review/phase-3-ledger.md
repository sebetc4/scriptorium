# Phase 3: The Ledger

---

## Status

**Current Status:** 🟢 Done (100% — 6/6)
**Started:** 2026-09-18
**Completed:** 2026-09-18
**Blocked By:** —

---

## Before Starting This Phase

> Read the previous phase in full before touching anything here: its notes,
> its unchecked tasks, and its unmet acceptance criteria. Skip this section
> only for the roadmap's first phase, which has no predecessor.

**Read First:**
1. The previous phase's `## Notes` section — what it found, decided, and
   left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Make sure no session escapes measurement, so that the corpus cannot quietly
become a record of the tasks that went well.

---

## Overview

### Why This Phase Matters
Reviews are written on purpose, and a purpose is selective. The ledger is
written by nobody's decision: every session leaves session-level numbers
whether or not anyone reviewed it. Its second job is the coverage figure —
how many tasks of this month carry a review, and which do not.

### What It Enables
Phase 4 can report coverage, and can price a kind of work from sessions nobody
sat down to review.

### Out of Scope
Judgement of any kind. The ledger holds numbers. It is never called a review,
never carries prose, and never attributes a slice to a task.

---

## Tasks

- [x] Write `.claude/hooks/session-ledger.sh` on `SessionStart`: sweep the project's transcripts, write a ledger for each one that has none, in the background
- [x] Bound the sweep: the top-level `*.jsonl` files and nothing else — never `memory/`, never a session's `subagents/` directory, which `metrics.py` reaches through its own session
- [x] Skip what is not worth recording — a session under three assistant turns, and the live session itself, whose transcript is a few lines old at `SessionStart` — and re-sweep a transcript that grew since its ledger was written, so a session is measured whole and once
- [x] Skip in silence when `.venv` or a tool is missing, always exiting zero
- [x] Wire it into `.claude/settings.json`, following the existing hooks' shape
- [x] Add coverage to `corpus.py`: which sessions of the ledger carry a review, and which slices do not

---

## Technical Details

### Files to Modify
```
.claude/hooks/session-ledger.sh    new — about twenty lines
.claude/settings.json              the SessionStart entry
.claude/skills/session-review/scripts/corpus.py    coverage
reviews/.ledger/                   written, never read by a human
```

### Dependencies
`metrics.py --ledger`, from Phase 1.

### Constraints
The hook fires at the start of every session in this repository. It must cost
nothing perceptible and must never block: a hook that breaks a session start is
worse than no hook. `skill-tests.sh` is the style to follow — narrow match,
early exit, silence unless something matters.

`SessionEnd` is not used, and the reason belongs in the script's comment: it
does not fire for a session that crashed or was killed, which are the sessions
whose cost is most worth knowing.

The price of that choice is that a ledger is always written from outside the
session it describes, one session late. A ledger entry is therefore keyed by
transcript, not by the sweep that wrote it, and carries the size it was
computed from, which is what makes the re-sweep decidable.

---

## Acceptance Criteria

- [x] A session started after a crashed one finds the crashed session in the ledger
- [x] The session running the hook writes no ledger for itself, and the next session writes its complete one
- [x] The two 97-byte transcripts of this project produce no ledger entry
- [x] Removing `.venv` makes the hook do nothing, print nothing, and exit zero
- [x] The ledger contains no prose and no text from any prompt
- [x] Coverage names the uncovered slices by time, not by content

---

## Notes
