# Phase 0: Verify and Benchmark

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/6)
**Started:**
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

Choose the main local engine on measurements taken on this library's documents,
and find out, before writing any engine code, whether the candidates can carry
the placeholders and the context the contract requires.

---

## Overview

### Why This Phase Matters
The figures in `docs/local-translation.md` were copied from model pages and
never re-verified, and nobody knows yet whether a translation model returns
`⟦12⟧` intact. An engine built on either assumption can be finished and still
unusable.

### What It Enables
Phase 1 implements one engine, on a runtime that is known to work, with a
placeholder strategy that has been measured.

### Out of Scope
Writing the `LocalEngine` class. This phase produces measurements and a choice.

---

## Tasks

### Facts
- [ ] Verify each model's size, coverage and runtime support, and record the dates and sources in `docs/local-translation.md`
- [ ] Record each model's licence, and what it allows for a translated document shared outside this machine

### Measurements
- [ ] Install the candidate runtime and models, and write down the exact procedure that worked
- [ ] Build a benchmark of about twenty passages taken from this library's documents, English ↔ French, with their reference translations
- [ ] Measure placeholder survival for each model, and try an alternative marker if `⟦n⟧` does not survive
- [ ] Score MADLAD 10B Q8, MADLAD 7B Q8 and NLLB 3.3B on fidelity, fluency, terminology and meaning errors, and choose the main and the comparison engine

---

## Technical Details

### Files to Modify
```
docs/local-translation.md     facts verified, procedure, benchmark results
docs/local-translation/       the benchmark passages and scores — to be created
```

### Dependencies
The `translate` skill as delivered by repo-overhaul Phase 7.

### Constraints
Nothing is added to `requirements.txt` in this phase.

---

## Acceptance Criteria

- [ ] Every figure in `docs/local-translation.md` carries a verification date and a source
- [ ] Both licences are recorded
- [ ] The benchmark, its scores and the choice are written down, with the reason
- [ ] The placeholder strategy for Phase 1 is measured, not assumed

---

## Notes

