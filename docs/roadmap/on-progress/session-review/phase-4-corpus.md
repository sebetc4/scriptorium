# Phase 4: The Corpus In Use

---

## Status

**Current Status:** 🟡 In Progress (0% — 0/5)
**Started:** 2026-09-18
**Completed:**
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

Put the corpus to work, and find out on real tasks whether a format designed
around one PDF session survives a translation, a capture and an investigation.

---

## Overview

### Why This Phase Matters
Four phases build an instrument. None of them proves it measures anything. The
test that matters is adversarial and available: session `4c7bb3d0` was reviewed
by hand on 2026-09-17 and its transcript is still on disk. Running the real
tooling over it says exactly how much a careful session gets wrong when it
counts by hand — and whether the findings it reached are the findings the
instrument surfaces.

### What It Enables
The first findings become roadmap entries, which is the only way anything in
`reviews/` reaches this repository.

### Out of Scope
Acting on the findings. Carrying one to `docs/roadmap/pending/` is this phase's
job; implementing it is that roadmap's.

---

## Tasks

### The reports
- [ ] Write `scripts/aggregate.py`: cost baselines per skill, findings ranked by recurrence and severity, findings never carried, coverage, and before-and-after around a date

### The proof
- [ ] Re-review session `4c7bb3d0` with the real tooling and write down the gap against the hand-written review — which numbers were wrong, which findings the instrument missed, which it found that the session did not
- [ ] Review one task under each of `translate`, `fetch` and `epub`, and record where the format strained — a `kind` that did not fit, a measure that meant nothing outside `pdf`

### The loop
- [ ] Carry the findings that survive into `docs/roadmap/pending/`, and fill their `carried:`
- [ ] Decide what becomes of `agent-reviews/2026-09-17-round-led-d4017-guide-pedagogique.md`: converted, kept as the origin document, or retired — and say why in this phase's notes

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/scripts/aggregate.py    new
.claude/skills/session-review/references/format.md    amended if a task strains it
docs/roadmap/pending/<new>/                           the findings that are carried
```

### Dependencies
A corpus. This phase cannot start on zero reviews, and its second task is what
produces the first ones.

### Constraints
`aggregate.py` prints text on stdout, in the idiom of `make list`. No HTML, no
artifact, no chart.

A format amended here is a format amended once: `review: 2` and a migration, or
nothing. The version field exists so that this decision is cheap, not so that
it is frequent.

---

## Acceptance Criteria

- [ ] The gap between the hand-written review and the measured one is written down, figure by figure
- [ ] At least one finding that the hand-written review did not reach comes out of the re-review — or its absence is recorded as a result, which would say the instrument adds accuracy but not insight
- [ ] Four skills have at least one review, and each strain on the format is recorded
- [ ] At least one finding carries a `carried:` pointing at a real roadmap file
- [ ] `aggregate.py --coverage` runs against the ledger and names uncovered slices

---

## Notes
