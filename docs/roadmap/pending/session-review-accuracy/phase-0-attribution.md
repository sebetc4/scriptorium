# Phase 0: What Belongs To The Task

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/5)
**Started:**
**Completed:**
**Blocked By:** —

---

## Before Starting This Phase

This is the first phase. Read this roadmap's `README.md`, and the review that
produced it: `reviews/2026-09-18-53a9d27e-roadmap-phase-1.md` on the working
machine, which carries the figures below in its `measured:` block.

---

## Objective

Make `metrics.py` tell a turn that **ran** the review tooling from a turn that
**worked on** it, so that a slice is measured whole.

---

## Overview

### Why This Phase Matters
The exclusion exists so the instrument does not measure itself: a review that
counted its own `metrics.py` call would report the cost of reviewing as part of
the cost of working. It is implemented as a substring match on the tool input —
`metrics.py`, `corpus.py`, `aggregate.py`, `session-review`, `reviews/` — and
every command that reads, writes or tests a file under
`.claude/skills/session-review/` matches it.

The four phases that built this instrument were therefore measured at 106 API
calls out of 147 and 43 Bash calls out of 125. The error has a direction: it
always makes a task look cheaper than it was.

### What It Enables
Reviews of any work on the review tooling itself, which is the one kind this
repository is certain to keep producing.

### Out of Scope
Re-measuring the four reviews already written. Their `measured:` blocks stay as
the instrument produced them; a corrected instrument produces corrected blocks
from the same transcript whenever anyone wants them.

---

## Tasks

- [ ] Decide the rule that separates running from editing — the command's shape rather than any path it mentions — and write it down where the current markers are
- [ ] Exclude a turn only when its tool call *invokes* the review tooling: `metrics.py`, `corpus.py` or `aggregate.py` run as a program, and a write under `reviews/`
- [ ] Keep excluding what must stay excluded, and test it: a review that runs `metrics.py --owed` does not count that turn
- [ ] Add the case that fails today: a turn that edits or tests a file under `.claude/skills/session-review/` is the task, and is counted
- [ ] Re-run the instrument over session `53a9d27e` and record the corrected figures in this phase's report, against 106/147 and 43/125

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/scripts/metrics.py     the TOOLING markers and is_tooling()
.claude/skills/session-review/tests/test_metrics.py  the two cases
```

### Dependencies
None.

### Constraints
The separation must be decidable from the transcript alone. A turn's intent is
not recorded anywhere, so the rule can only read the shape of the command —
which is why the current rule reached for paths in the first place.

---

## Acceptance Criteria

- [ ] A turn that runs the review tooling is excluded; a turn that edits or tests it is counted
- [ ] Session `53a9d27e` measures 147 API calls and 125 Bash calls across its four slices
- [ ] `test_a_review_tooling_turn_is_excluded` still passes, unchanged
- [ ] The suite passes on a fresh clone, reading only synthetic fixtures

---

## Notes
