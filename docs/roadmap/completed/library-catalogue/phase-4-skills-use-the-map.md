# Phase 4: The Skills Use the Map

---

## Status

**Current Status:** 🟢 Done (100% — 7/7)
**Started:** 2026-09-26
**Completed:** 2026-09-26
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-3-library-mapped.md` and `phase-3-library-mapped-report.md` in
full before touching anything here: the decisions already taken, the
problems and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-4-skills-use-the-map-report.md` current as the work happens —
after each significant step, and before every commit, pause, or end of
session.

---

## Objective

Make the discussion, and the other skills that reach for material, find it
through the map, cite it by id, and read only what they need. Then prove it
in a real discussion session.

---

## Overview

### Why This Phase Matters
The user expects the largest gain here: the discussion agent, given the map
of the library. The gain is lost if searching becomes a reflex that fills the
context. So the rule is a distinction, not a habit. An explanation the agent
can give from its own knowledge is given that way. The library is searched
when the answer depends on what it holds, and only what the search points at
is read.

### What It Enables
A discussion that builds on the user's own material without the agent
knowing where it is in advance. Journals whose citations survive renames.
The transistor pilot of the discussion-and-illustration roadmap, whose
material is spread across three entries.

### Out of Scope
The illustration skill and the transistor pilot, which belong to the
discussion-and-illustration roadmap.

---

## Tasks

### `discussion`
- [x] Write the rule into `discussion`: answer from the agent's own knowledge when that suffices, as an agent's account; search the library when the answer depends on it — the user's own material, a claim the document will state as established, how a document of the library explains something; read only what the search points at, and only the part needed
- [x] Make the journal cite by id and open or resume with `links` on its entry, and remove the **Material** section from the skill, the index template and the suite
- [x] Replace the resume's comparison of `sources/` by hand with `sync` then `ls` on the entry
- [x] Migrate the notebook's journal: its path citations become `id:` citations, and its **Material** section goes

### The other skills
- [x] `sourcing`: its pieces become items, and `NOTES.md` cites them by id
- [x] `pdf` and `fetch`: look for related material through the map, and never write an id into `document/`; `pdf`'s description, which claims every repair `make check-library` reports, names `catalogue` for a `manifest`, `id` or `citation` defect, with `tests/test_triggers.py`'s neighbours to match

### Proof
- [x] Hold a notebook session with the map, and record how the agent found the material outside the notebook, what it read, and what it cost, against the baseline session of discussion-and-illustration Phase 0

---

## Technical Details

### Files to Modify
```
.claude/skills/discussion/SKILL.md, assets/index.md, tests/
.claude/skills/sourcing/SKILL.md
.claude/skills/pdf/SKILL.md
.claude/skills/fetch/SKILL.md
library/electronics/notebook/study/discussion/     the migration
docs/document.md, docs/architecture.md             what the skills now do
```

### Dependencies
Phase 3: the user's library mapped. The baseline: the discussion-and-
illustration roadmap's Phase 0 closes on a real notebook session held with
the three-layer journal. That session must happen before this phase changes
the `discussion` skill. The user's time for the proof session.

### Constraints
- Searching is not a reflex: the rule names when to search, and a search that
  was not needed counts against the proof.
- The migration of the notebook's journal changes its citations and removes
  one section; it changes nothing the user said, and no claim's status.
- Phase 3 renamed files the notebook's journal cites by path. Its `index.md`
  and topic files were repointed, but the session of 2026-09-24 still cites
  `sources/images/20260924_123413.jpg`, now `led-ring-solder-joints.jpg`; the
  manifest keeps each first name under `original:`, which is how the
  migration finds the id of a path that no longer exists.
- `electribe-2`'s pieces are already items — `sources/threads`, `raw`,
  `images`, `datasheets`, one item per directory (Phase 3) — while its
  `study/NOTES.md` cites single files inside them: the `sourcing` task
  decides whether a piece it cites alone gets its own item.

---

## Acceptance Criteria

- [x] `make test` and `make check-library` pass
- [x] In the proof session, the agent found the material outside the notebook through `find` or `links`, without listing the file system
- [x] In the same session, it answered from its own knowledge where the library added nothing, and read only what a search pointed at
- [x] The session's cost is recorded against the baseline
