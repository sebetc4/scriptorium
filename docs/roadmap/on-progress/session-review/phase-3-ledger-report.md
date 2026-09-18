# Phase 3 Report: The Ledger

**Phase:** [phase-3-ledger.md](phase-3-ledger.md)
**Start Commit:** 584c06f

---

## Work Log

### 2026-09-18

Phase opened. Phase 2's file and report were read in full: 7/7 tasks, four of
six acceptance criteria met, two left unticked because they can only be
observed from a later session. No restructuring pending.

What this phase inherits:

- `metrics.py --ledger` already prints the session-level JSON this phase's hook
  writes: it ignores the review cursor, reads the whole transcript, and carries
  `bytes` — the size it was computed from, which makes the re-sweep decision
  `size on disk != size recorded` and nothing more.
- The rule on unconfirmed record shapes holds for the ledger too: a counter
  whose shape this corpus never showed is omitted, never written as zero.
- `metrics.scan()` deduplicates usage by `message.id`. Nothing in this phase
  sums usage itself.

The start commit is `584c06f` for the same reason as the two before it: the
phase was opened during the previous one's closure, before that work was
committed.

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
