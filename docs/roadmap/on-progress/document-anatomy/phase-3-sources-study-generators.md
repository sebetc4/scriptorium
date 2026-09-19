# Phase 3: What Was Received, What Was Learned, What Makes

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/7)
**Started:**
**Completed:**
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. Phase 2's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Split what `sources/` holds today into the three roles it has always confused:
the received, the learned, and the code that makes.

---

## Overview

### Why This Phase Matters
`sources/` is the user's directory. Two scripts currently write derived files
into it: `ingest.py` puts `extracted.md`, `meta.json` and `pages/` beside the
PDF the user imported, and `fetch.py` puts `extracted.md` and `meta.json` beside
the `page.html.gz` it captured.

Both also put *received* material there, and that is not the same act. One is a
tool filling the user's directory on their behalf; the other is a tool using it
as scratch space. And a third thing hides in the same place: `figures.py`, the
generator that draws four of one document's SVGs, left there because nothing
said where a generator belongs — a finding raised in the review corpus and never
resolved for want of an answer.

### What It Enables
A directory the user can empty, refill and reorganise without breaking a build,
because nothing a tool needs lives there except what the user provided.

### Out of Scope
An investigation's received material. The images, threads, raw captures and
datasheets a `sourcing` session collected stay in `sources/`: a tool acquired
them, on the user's behalf, and they are as received as an imported PDF.

---

## Tasks

- [ ] Move `ingest.py`'s derivation — `extracted.md`, `meta.json` — to `study/`, and `pages/` to `.work/`, since page renders are regenerable and large
- [ ] Move `fetch.py`'s derivation to `study/`, leaving `page.html.gz` in `sources/` as received material
- [ ] Move the sourcing journal `NOTES.md` to `study/`, where written knowledge belongs beside what it was written from
- [ ] Move `figures.py` to `generators/`, and say in the `pdf` skill that a generator lives there and writes into `document/assets/`
- [ ] Make both derivations re-runnable from `sources/` alone, and add the command that does it
- [ ] Update every instruction that names `sources/extracted.md` — the four `SKILL.md`, `ingest.py`'s and `fetch.py`'s own notes — since a path in a skill is an instruction, not a comment
- [ ] Migrate the documents behind a dry run, then rebuild them all and compare

---

## Technical Details

### Files to Modify
```
.claude/skills/pdf/scripts/ingest.py     the derivation targets, and its notes
.claude/skills/fetch/scripts/fetch.py    the derivation targets, and its notes
.claude/skills/pdf/SKILL.md              where a generator lives
.claude/skills/*/SKILL.md                every path naming sources/extracted.md
Makefile                                 the re-derivation command
library/**                               the migration, behind a dry run
```

### Dependencies
Phases 1 and 2: the document root, and `.work/` for what is disposable.

### Constraints
`extracted.md` is called "an immutable reference" by both scripts and is read
during a translation to check that nothing was invented. It goes to `study/`,
which `make clean` never touches — but the re-derivation must still work, or a
lost `study/` costs a re-import.

If a derivation turns out not to be reproducible from `sources/` alone, this
phase stops and says so rather than moving a file somewhere it can be silently
destroyed.

---

## Acceptance Criteria

- [ ] After `make import` and `make fetch`, `sources/` holds only received material
- [ ] Deleting `study/` and re-running the derivation reproduces `extracted.md` byte for byte, or the phase records which script cannot and why
- [ ] `figures.py` lives in `generators/` and still produces the four SVGs of its document
- [ ] No `SKILL.md` names a path that no longer exists
- [ ] `make test` passes, fetch and import suites included

---

## Notes
