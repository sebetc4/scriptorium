# Phase 1: The Document, In Its Own Directory

---

## Status

**Current Status:** 🟢 Done (100% — 7/7)
**Started:** 2026-09-19
**Completed:** 2026-09-19
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. Phase 0's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Move `index.md`, `cover.md` and `assets/` into `<slug>/document/`, and teach
`core/doc.py` that a document's root is now the parent of that directory.

---

## Overview

### Why This Phase Matters
This is the change the other phases are shaped around, and the only one that
touches the core. Everything the build reads ends up behind one name, so that
every remaining directory can be defined by not being it.

`assets/` moves **with** the document rather than staying at the root, and that
is not a detail: every `index.md` links its images with a relative path of the
form `assets/img-001.jpg`. Moving both together leaves every relative path in every document exactly as it is. Moving
them apart would mean rewriting every document's links to gain nothing.

### What It Enables
A document root that holds only directories, each with one role.

### Out of Scope
`sources/`, `study/`, `generators/`, `.work/`. They are the phases after this
one; here they stay exactly where they are, however wrong that is.

---

## Tasks

- [x] Change discovery in `core/doc.py`: `find_docs` returns the parent of the directory holding `index.md`, and `load_doc` reads `<root>/document/index.md`
- [x] Fix what `d.name` and `d.relative_to(LIBRARY)` feed — the slug, the default title and `out_dir()` — all three of which would otherwise become `document`
- [x] Update `new.py` so a new document is created in the new shape, and check that `make new` then `make build` works on an empty document
- [x] Migrate the existing documents, behind a dry run that prints every move and touches nothing
- [x] Rebuild every document and compare each PDF and EPUB with the one built before the migration
- [x] Update every instruction that names a path inside a document — the four `SKILL.md`, `docs/architecture.md`, `CLAUDE.md`
- [x] Add the test that a document is discovered at its root, not at `document/`

---

## Technical Details

### Files to Modify
```
core/doc.py                          find_docs, load_doc, slug, title, out_dir
.claude/skills/pdf/scripts/new.py    the shape of a new document
.claude/skills/*/SKILL.md            every path that names index.md or assets/
library/**                           the migration, behind a dry run
tests/                               discovery at the root
```

### Dependencies
Phase 0's contract.

### Constraints
`d.name` is the slug and the default title, and `d.relative_to(LIBRARY)` is the
whole output path. All three break the moment `index.md` moves, and they break
silently — a build would succeed and write `out/pdf/…/<slug>/document/`. The
test comes before the migration, not after.

The documents are not versioned. A backup taken before the migration is worth
more than any amount of care in the script.

---

## Acceptance Criteria

- [x] A document is discovered at `<slug>/`, and its slug is `<slug>`
- [x] Every PDF and EPUB is byte-identical to the one built before the migration, or the difference is explained
- [x] No `index.md` had a relative link rewritten
- [x] `make new` produces the new shape and it builds
- [x] `make test` passes

---

## Notes
