# Phase 3: The Library Mapped

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/6)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-2-catalogue-skill.md` and `phase-2-catalogue-skill-report.md` in
full before touching anything here: the decisions already taken, the
problems and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-3-library-mapped-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Map the user's library: every topic and entry named and described, the
items of the documents already studied described, and the commands that
create an entry leaving it mapped.

---

## Overview

### Why This Phase Matters
At the roadmap's creation the library held 9 topics and 23 entries, 14 of
them waiting to be studied and invisible to every tool. This phase makes all
of them findable. It is also the first time the rules of Phase 2 meet the
user's material, with its generic file names and its documents in every
state.

### What It Enables
Phase 4 can change the skills to rely on the map, because the map exists.

### Out of Scope
Describing every item of the waiting entries: each gets its entry-level name
and description here, and its items are described as it is studied.
Reorganising the library.

---

## Tasks

### The rollout
- [ ] Run `sync` on the user's library: a manifest in every topic and entry, the standard files named
- [ ] Name and describe every topic and entry, then show the user the tree once (`ls -l` from the root) and apply their corrections
- [ ] Describe the items of the entries that have a `document/`, from what is already studied
- [ ] Propose a new file name for each flagrantly generic one (`Sans titre.jpg`, `licensed-image_002_aEns.jpg`…), and rename those the user accepts

### Keeping it mapped
- [ ] Make `make new`, `make fetch` and `make import` sync the entry they create, and list what is left to name

### Proof
- [ ] Run `make check-library` on the user's library, and hand its to-do counts to the user

---

## Technical Details

### Files to Modify
```
library/**/manifest.yaml                 new, through the tool
Makefile                                 new, fetch, import
.claude/skills/pdf/scripts/ingest.py     sync after an import
.claude/skills/fetch/scripts/fetch.py    sync after a capture
```

### Dependencies
Phase 2: the skill and the describing agent. The user's time for one review
of the named tree, and for the rename proposals.

### Constraints
- `library/` is user content: nothing is moved, and nothing renamed without
  the user's yes. No source's content changes.
- The tree is shown to the user once, with every name and description, not
  entry by entry.

---

## Acceptance Criteria

- [ ] `make check-library` reports no defect on the user's library
- [ ] The user has reviewed the named tree
- [ ] After `make new`, `make fetch` or `make import`, the new entry has its manifest
- [ ] `make test` passes
