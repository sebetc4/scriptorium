# Phase 1 Report: The Measurement

**Phase:** [phase-1-measurement.md](phase-1-measurement.md)
**Start Commit:** f22aab0

---

## Work Log

### 2026-09-18

Phase opened. Phase 0's file and report were read in full: the format, the
finding vocabulary and `corpus.py` are settled, all five tasks done and all
five acceptance criteria met, and no restructuring was left pending.

What this phase inherits from it: `metrics.py` emits the `measured:` block and
nothing else, and **omits** any measure whose record shape it could not confirm
rather than writing a zero — `corpus.py` drops a review with a missing key from
a median's sample, so a zero written out of politeness corrupts every baseline
computed afterwards. The medians are asked for by dotted path
(`tokens.fresh`, `subagents.fresh`, `tools.<Name>`, `derived.<name>`), with
`subagents.<field>` summed across runs and `.value` implied under `derived`,
and a review comparing itself to the corpus it is about to join passes
`exclude=<its own path>`.

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
