# Phase 5: The Documentation That Follows

---

## Status

**Current Status:** 🟢 Done (100% — 6/6)
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. Phase 4's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

And before writing a line: the `## Notes` of all five phases before this one.
This phase does not describe the contract Phase 0 wrote — it describes the
system that exists, and the difference between the two is exactly what those
notes recorded.

---

## Objective

Write the document a person reads to understand what a document *is* and how it
lives, and bring every other document in the repository back into agreement with
it.

---

## Overview

### Why This Phase Matters
Phase 0 wrote a contract before anything moved, which is the right order for
doing the work and the wrong order for reading about it. Five phases of doing it
will have found things the contract did not anticipate — that is what their
notes are for — and a rule written in advance is not a description of a system
that exists.

Three statements in this repository become false the moment Phase 1 runs, and
none of them is in a place anyone would think to look:

- `CLAUDE.md` opens with "One directory under `library/` = one document
  (`index.md`)".
- `docs/architecture.md` §1 lists `library/` as "user content — outside this
  roadmap's scope", which was true when it was written.
- `docs/architecture.md` §9 defines a document as "a directory holding an
  `index.md`", and *source material* as "what `sources/` holds".

`tests/test_documentation.py` opens with the reason this phase exists: *the
documentation follows the code — otherwise it lies.*

### What It Enables
Someone opening this repository in six months, or a session loading `CLAUDE.md`
at its start, placing any file of a document without reading a script.

### Out of Scope
Changing any behaviour. If this phase finds that the documentation cannot be
written truthfully, the defect is in the code and it is recorded, not smoothed
over in prose.

---

## Tasks

- [x] Write `docs/document.md`: what a document is made of, and its life — what `make new`, `make import`, `make fetch`, `make build`, `make review`, `make epub`, `make translate` and `make clean` each put where, and what is left after each
- [x] State in it, for every one of the five directories, the three answers a person actually needs: who writes it, does the build read it, may I delete it
- [x] Reconcile `docs/architecture.md`: §1's tree, where `library/` is no longer out of scope, and §9's glossary, where *document* and *source material* are both defined wrongly after this roadmap
- [x] Reconcile `CLAUDE.md`: its opening sentence, and the repo map — the few lines that make a session place a file correctly without opening `docs/document.md`
- [x] Check the four `SKILL.md` against the new anatomy, and point each at `docs/document.md` where it currently describes a document's parts itself
- [x] Add the documentation test, in the shape of `test_claude_md_maps_the_core`: the five directories named by `core/doc.py`'s layout are named in `docs/document.md` and in `CLAUDE.md`

---

## Technical Details

### Files to Modify
```
docs/document.md          new — the anatomy and the life of one document
docs/architecture.md      §1 the tree, §9 the glossary
CLAUDE.md                 the opening sentence, the repo map
.claude/skills/*/SKILL.md every description of a document's parts
tests/test_documentation.py   the layout is named where it is read
```

### Dependencies
Phases 0 to 4, and their notes. This phase is written last because it describes
what the others turned out to build.

### Constraints
`docs/architecture.md` is 613 lines and is titled *Target Architecture*: it
records decisions and the reasons for them, and it is not a reference manual.
`docs/document.md` is the manual. The boundary matters — a manual that argues
with itself is not consulted, and an architecture note that lists filenames goes
stale in a week.

The documentation test has to fail for the right reason. Pinning a filename in a
test buys nothing if the file is renamed in the same commit; what it pins is the
agreement between `core/doc.py`'s layout and the prose that claims to describe
it.

---

## Acceptance Criteria

- [x] A person who has never seen this repository can place any file of a document from `docs/document.md` alone
- [x] No document in the repository still says a document is a directory holding an `index.md`
- [x] The five directories are named in `CLAUDE.md`, briefly enough that it stays a map
- [x] A test fails when `core/doc.py`'s layout and the documentation disagree
- [x] `make test` passes, documentation test included

---

## Notes
