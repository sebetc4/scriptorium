# Phase 1: The Measurement

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/7)
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

Turn a slice of a transcript into the `measured:` block, and keep the honest
line between what is read and what is inferred visible in the output itself.

---

## Overview

### Why This Phase Matters
This is the phase that makes the whole thing worth building. A hand-written
review put four delegated review passes at "≈ 109,500 tokens"; the transcript
says 196,578 fresh and 727,020 cached. Every number this script prints replaces
a guess of roughly that quality.

### What It Enables
Phase 2's skill has something to explain, and thresholds that can oblige it to.

### Out of Scope
Any judgement. This script never writes prose, never names a cause, and never
decides that a number is bad.

---

## Tasks

### Bounding the slice
- [ ] Locate the transcript from `$CLAUDE_CODE_SESSION_ID`, and fail with a clear message rather than guessing when it is absent
- [ ] Resolve the slice: `from` defaults to the last review of this session, `to` to now, both overridable — and exclude every turn that ran the review tooling or wrote under `reviews/`

### What is read
- [ ] Count the exact measures: fresh and cached tokens for the main context and for each subagent separately, thinking tokens, turns, tool calls by name, images, subagent runs with their `agentType` and duration, skill spans, files written
- [ ] Count the friction: interruptions, permission denials, API errors — and degrade silently for any record shape this corpus could not confirm, writing nothing rather than a zero that looks measured

### What is inferred
- [ ] Compute the derived measures and print the rule beside each: active minutes with its idle threshold, build and review cycles, context peak, image carry, repeated Bash commands, files read twice

### The output
- [ ] Emit the `measured:` block with each measure's median beside it, plus `--timeline` truncated to sixty characters a line, and `--ledger` for Phase 3
- [ ] Write the suite on synthetic transcripts covering subagents, an idle gap, an interruption, a review tooling turn that must be excluded, and a corpus with no median yet

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/scripts/metrics.py    new
.claude/skills/session-review/tests/                synthetic transcript fixtures
```

### The Reference Transcript
Session `4c7bb3d0-7eec-4a1b-9587-e966e5703b8b`, 2026-09-17, 7.3 MB, in this
project's transcript directory. It is the one the hand-written review of
2026-09-17 covers, and the acceptance criteria above are checked against it.

| Measure | Expected |
|---|---|
| Fresh tokens, subagents | 196,578 |
| Cache reads, subagents | 727,020 |
| Images | 11 |
| Delegated passes (`pdf-reviewer`) | 4 |

It is written down here because that transcript is neither versioned nor
permanent: it lives outside the repository and rotates. If it is gone when this
phase runs, the criteria stand as a record of what the instrument was built to
reproduce, and the phase says so in its notes rather than quietly weakening
them. A figure that disagrees is a finding about the script or about this
table — it is resolved, not overwritten.

### Dependencies
`corpus.py` and the format, from Phase 0. The transcript layout recorded in the
roadmap's `README.md`.

### Constraints
The script reads the project's transcript directory and nothing else — never
`library/`, never another project. Prompt text leaves the script only through
`--timeline`, truncated. A measurement tool that reproduces the conversation
would rebuild inside `reviews/` what the `.gitignore` is there to protect.

The output stays around forty-five lines: the session that runs this pays for
every one of them.

---

## Acceptance Criteria

- [ ] Run on the transcript of 2026-09-17 session `4c7bb3d0`, the script reports the figures recorded under *The Reference Transcript* below
- [ ] A measure whose record shape is absent from the transcript is omitted, never written as zero
- [ ] Every derived measure prints its rule; no derived measure is presented as read
- [ ] Two consecutive reviews of the same session produce disjoint slices, and the review tooling's own turns appear in neither
- [ ] The whole output is under fifty lines
- [ ] The suite passes on a fresh clone, reading only synthetic fixtures

---

## Notes
