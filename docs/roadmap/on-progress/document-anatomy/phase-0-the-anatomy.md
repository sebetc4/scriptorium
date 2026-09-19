# Phase 0: The Anatomy Of A Document

---

## Status

**Current Status:** 🟢 Done (100% — 6/6)
**Started:** 2026-09-19
**Completed:** 2026-09-19
**Blocked By:** —

---

## Before Starting This Phase

This is the first phase. Read this roadmap's `README.md` — in particular
*The Five Roles*, which this phase writes down — and `docs/architecture.md`,
which explains every directory of the repository and says nothing about the
inside of a document.

---

## Objective

Write down the five roles, so that the four phases after this one carry out a
contract instead of inventing one as they go.

---

## Overview

### Why This Phase Matters
A document's anatomy has never been declared. `core/doc.py` knows one fact —
`index.md` is the entry — and everything else is habit. Four skills write into
a document directory and none agrees with the others about what belongs where.

The cost is not tidiness. It is that nobody can say whether a given file may be
deleted, regenerated or edited, and so nothing ever is: 25 MB of review sheets
accumulate, a figure generator sits in `sources/` because there was nowhere else
to put it, and a user opening `sources/` cannot tell what they put there from
what a script left behind.

### What It Enables
Every phase after this one, and a `make clean` that can be trusted to run inside
user content.

### Out of Scope
Moving anything, changing any script. This phase produces two documents and
changes no behaviour.

---

## Tasks

- [x] Write the five roles into `docs/architecture.md`, one section each — `document/`, `sources/`, `study/`, `generators/`, `.work/` — stating for each who writes it, whether the build reads it, and what `make clean` does to it
- [x] State the cut that decides the rest: **the build reads `document/` and nothing else**, which is the only boundary a wrong answer makes visible
- [x] State the rule for `sources/`: it is the user's, they fill it with what they judge relevant, and no tool ever modifies what is in it
- [x] Draw the line the scripts blur today: a tool may *acquire* into `sources/` on the user's behalf — an imported PDF, a captured page — and may never *derive* into it
- [x] Say what makes a file durable rather than disposable, and check the rule against the awkward cases by name: `extracted.md`, `meta.json`, `NOTES.md`, `figures.py`, a hand-drawn SVG
- [x] Add the anatomy to `CLAUDE.md`'s repo map, in the few lines it deserves there

---

## Technical Details

### Files to Modify
```
docs/architecture.md    a section: the inside of a document
CLAUDE.md               the repo map
```

### Dependencies
None.

### Constraints
`library/` is user content and is not versioned. A contract written here governs
files that git will not protect, which is why it is written before anything
moves.

The anatomy has to survive the four skills that already write into a document:
`pdf` (`new`, `import`, `build`, `review`), `epub` (`epub`, `preview`), `fetch`,
`translate`. A rule one of them cannot follow will be broken in the first week.

Five directories, and none of them is a miscellany. If a file fits none, that is
a finding about the anatomy and it is recorded here, not absorbed by widening a
definition.

---

## Acceptance Criteria

- [x] `docs/architecture.md` answers, for any file in a document: who wrote it, may I edit it, does the build read it, will `make clean` remove it
- [x] The acquire / derive line is drawn in a sentence, not as a list of filenames
- [x] Each of the five awkward cases is placed, with its reason
- [x] `make test` passes, documentation test included

---

## Notes
