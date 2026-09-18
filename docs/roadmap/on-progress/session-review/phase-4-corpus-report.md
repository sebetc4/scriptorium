# Phase 4 Report: The Corpus In Use

**Phase:** [phase-4-corpus.md](phase-4-corpus.md)
**Start Commit:** 0df5266

---

## Work Log

### 2026-09-18

Phase opened. Phase 3's file and report were read in full: 6/6 tasks, 6/6
acceptance criteria, no restructuring pending.

What this phase inherits:

- `metrics.py --sweep` and the `SessionStart` hook: the ledger of this project
  holds four sessions, and `corpus.py --coverage` reports 0/4 fully reviewed —
  the honest state of a corpus with no reviews in it.
- `corpus.coverage()` returns, per session, the spans no review covers, as
  timestamps. `aggregate.py --coverage` is a presentation of that, not a second
  computation.
- The obligations fire from `metrics.owed()`. This phase produces the first
  reviews that have a baseline, and is where the corpus stops widening the
  first obligation from three costs to five.

Per the convention Phase 2 wrote down, this phase's start commit is `0df5266`,
the commit that closed Phase 3.

---

## Decisions

---

## Files Changed

---

## Problems And Deviations

---

## Changes To Later Phases

---

## Assessment
