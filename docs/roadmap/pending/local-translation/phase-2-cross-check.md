# Phase 2: Cross-Check in Practice

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/5)
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

Use the two engines together on real documents, and find out whether the
cross-check points a reviewer at the chunks that actually need reading.

---

## Overview

### Why This Phase Matters
`qc.cross_check` flags disagreements on numbers, structure and length. Whether
those are the disagreements that matter on real translations has never been
measured.

### What It Enables
A documented, trusted way to translate a document of the library with a second
opinion, and thresholds tuned on evidence.

### Out of Scope
Adding a third engine.

---

## Tasks

### In practice
- [ ] Translate two real documents of the library with both engines, and apply the better one
- [ ] Review the chunks the cross-check flagged and the ones it did not, and record what it missed and what it raised for nothing
- [ ] Tune the cross-check thresholds on that record, each change covered by a test

### Hand-over
- [ ] Write the two-engine procedure into the `translate` skill
- [ ] Record the results in `docs/local-translation.md`, and close what the notes left open

---

## Technical Details

### Files to Modify
```
.claude/skills/translate/scripts/qc.py
.claude/skills/translate/SKILL.md
docs/local-translation.md
```

### Dependencies
Phase 1's working `local` engine.

### Constraints
A threshold change is justified by a recorded case, not by taste.

---

## Acceptance Criteria

- [ ] Two real documents have been translated with both engines and reviewed
- [ ] The cross-check's misses and false alarms are recorded
- [ ] The skill documents the two-engine procedure

---

## Notes

