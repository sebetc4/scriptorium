# Phase 1: Skill Triggers in the Session Review

---

## Status

**Current Status:** 🟢 Done (100% — 6/6)
**Started:** 2026-09-25
**Completed:** 2026-09-25
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-0-library-free-suite.md` and `phase-0-library-free-suite-report.md`
in full before touching anything here: the decisions already taken, the
problems and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-1-trigger-review-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Make every session review account for the skills the session loaded. Each
skill loaded is justified by what it brought. A skill loaded without need,
or a job done without the skill that covers it, becomes a finding with a
target and a fix.

---

## Overview

### Why This Phase Matters
A skill that fires on a neighbour's job is worse than no skill
(`docs/architecture.md` §5). So far nothing measures it. The `discussion`
skill is the sharpest case, because every session is a conversation. The
user chose to check triggering through the reviews rather than wait to
notice it. `metrics.py` already counts the skills a session loaded, but no
obligation asks the review to use that count.

### What It Enables
Every review becomes a trigger test, at no extra cost. Phase 2's audit
starts from real data.

### Out of Scope
Rewriting skill descriptions: that is Phase 2.

---

## Tasks

### The obligation
- [x] Have `metrics.py --owed` print, for each skill loaded in the slice, an obligation to say what it brought to the task
- [x] Add the obligation to the skill's list in `SKILL.md`: a skill loaded without need is a finding; a job done without the skill that covers it is asked as a question, since no script can detect it
- [x] Add the finding kind `trigger` to `references/findings.md` and to the vocabulary `corpus.py` accepts, with a worked example

### Tests and proof
- [x] Test the printed obligation on a transcript fixture that loads two skills, one of them without need
- [x] Test that `corpus.py` accepts a `trigger` finding and still refuses an unknown kind
- [x] Run the new obligation on the transcripts of the `discussion` skill's real sessions (the notebook's opening and its fresh-session resume, 2026-09-24/25) and record what it prints

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/scripts/metrics.py
.claude/skills/session-review/scripts/corpus.py
.claude/skills/session-review/SKILL.md
.claude/skills/session-review/references/findings.md
.claude/skills/session-review/tests/
```

### Dependencies
Phase 0, so that `make test` is green when this phase closes.

### Constraints
The finding vocabulary is closed on purpose. `trigger` enters it through
`corpus.py`, like every other kind, never as free text.

---

## Acceptance Criteria

- [x] `metrics.py --owed` names every skill loaded in the slice
- [x] A review holding a `trigger` finding parses with `corpus.py`
- [x] `make test` passes
