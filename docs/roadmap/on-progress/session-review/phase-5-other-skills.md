# Phase 5: The Skills Nobody Has Used Yet

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/4)
**Started:**
**Completed:**
**Blocked By:** A real task under `translate`, `fetch` or `epub`. None exists in this project's transcripts, and a review cannot be written for work that was never done.

---

## Before Starting This Phase

**Read First:**
1. Phase 4's `## Notes` and its report — in particular the three strains on the
   format it recorded, which this phase either confirms or contradicts.
2. `references/format.md` and `references/findings.md`, which this phase is
   allowed to amend once.

---

## Objective

Find out whether a format designed around one PDF session survives a
translation, a capture and an e-reader build — on real tasks, when they happen.

---

## Overview

### Why This Phase Matters
The corpus holds five reviews: one `pdf` and four `roadmap`. Those two are the
extremes this repository produces — one spends its cost on looking at pages,
the other on editing text and delegating audits — and between them they already
strained the format three times. What they cannot say is whether `translate`,
`fetch` and `epub` strain it in some fourth way, because no session in this
project has ever run them.

This is the phase that would have been done in Phase 4 had the evidence
existed. It waits rather than inventing it: a review of work that was never
done is exactly the thing this roadmap was built to stop.

### What It Enables
A format amended once, on evidence, or left alone on evidence.

### Out of Scope
Doing a task under those skills in order to review it. A task run for the sake
of being measured is not a task, and its review would describe an experiment.

---

## Tasks

- [ ] Review one real task under `translate`, and record where the format strained — a `kind` that did not fit, a measure that meant nothing outside `pdf`
- [ ] Review one real task under `fetch`, and record the same
- [ ] Review one real task under `epub`, and record the same
- [ ] Decide on the amendment: `review: 2` with a migration of the corpus, or nothing — and say in the report which strains of Phase 4 these three confirmed

---

## Technical Details

### Files to Modify
```
reviews/                                              three reviews, on the working machine
.claude/skills/session-review/references/format.md    amended only if the evidence says so
.claude/skills/session-review/references/findings.md  likewise
```

### Dependencies
Three real tasks, one under each skill. This phase opens when they exist, not
before.

### Constraints
A format amended here is a format amended once: `review: 2` and a migration of
the five reviews already written, or nothing. The version field exists so that
the decision is cheap, not so that it is frequent.

The three strains Phase 4 recorded are the standing hypotheses, and each is
either confirmed or dropped here: that no `kind` fits a defect in the
instrument's own measurement; that `target` cannot name a file outside this
repository; that `carried:` cannot say a finding was resolved upstream rather
than in this repository, which is the same limit seen from the other end; and
that `document` and `images` mean nothing for a task that produces no document.

The third and fourth are one question asked twice: the format assumes a single
repository, and this tooling lives in two. A finding raised here may have its
target and its fix in the skill repository, and today neither field can say so.
Four reviews already carry the case, written into their `note:` for want of a
field.

---

## Acceptance Criteria

- [ ] Three reviews exist, one per skill, each of a task that was going to happen anyway
- [ ] Each strain on the format is recorded, or its absence is
- [ ] The amendment decision is taken and written down, whichever way it goes
- [ ] `aggregate.py` prints a baseline for each of the three skills

---

## Notes
