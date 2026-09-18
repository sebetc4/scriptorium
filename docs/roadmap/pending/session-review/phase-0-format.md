# Phase 0: The Format

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

This is the first phase. Read the roadmap's `README.md` instead — in
particular *What Was Measured Before Opening*, whose facts the next phase
depends on.

---

## Objective

Fix the shape of a review before anything writes one, and build the reader that
turns the corpus into medians. A format decided after the first ten reviews is
a migration; a format decided now is a contract.

---

## Overview

### Why This Phase Matters
Everything downstream is either a writer or a reader of this one format. The
measurement script emits it, the skill fills it, the ledger is its poor
relation, and the medians that keep a session honest are computed from it. It
is also the only artefact a human reads directly.

### What It Enables
Phase 1 has something to emit, and a median to emit beside each measure.

### Out of Scope
Measuring anything. This phase writes no transcript parser. Its fixtures are
reviews written by hand.

---

## Tasks

### The format
- [ ] Write `references/format.md`: every front matter field, its type, who owns it — script or session — and one complete review as an example
- [ ] Write `references/findings.md`: the closed `kind` vocabulary, one worked example per kind, and the rule that a finding without a `target:` and a `fix:` is not written

### The reader
- [ ] Write `scripts/corpus.py`: read `reviews/*.md`, parse the front matter, refuse a malformed one by name, and expose the records
- [ ] Add the median API `corpus.py` owes Phase 1: per skill, per measure, and only across reviews sharing the same `review:` version

### The ground
- [ ] Create `reviews/`, replace `agent-reviews` with it in `.gitignore` — and give that file the trailing newline it currently lacks

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/references/format.md      new
.claude/skills/session-review/references/findings.md    new
.claude/skills/session-review/scripts/corpus.py         new
.claude/skills/session-review/tests/                    new — hand-written review fixtures
.gitignore                                              agent-reviews → reviews
```

### Dependencies
None. This phase reads no transcript.

### Constraints
Nothing is added to `requirements.txt`: the front matter is parsed with what
`core/doc` already uses for a document's own front matter. Look there before
reaching for a dependency.

---

## Acceptance Criteria

- [ ] A review can be written by hand from `references/format.md` alone, without reading any code
- [ ] `corpus.py` refuses a review carrying an unknown `kind` and names the file and the value
- [ ] A median is computed per skill, and never mixes two `review:` versions
- [ ] The median of an empty or single-review corpus is absent, not zero — Phase 2 must be able to tell "no baseline yet" from "baseline of nothing"
- [ ] The suite passes on a fresh clone, reading only its own fixtures

---

## Notes
