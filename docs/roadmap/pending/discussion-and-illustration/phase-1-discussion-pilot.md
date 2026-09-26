# Phase 1: Discussion Pilot — Transistor

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/9)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** the [library-catalogue](../../completed/library-catalogue/README.md) roadmap — the transistor's material is spread across three entries, and the pilot finds it through the map

---

## Before Starting This Phase

Read `phase-0-discussion-skill.md` and `phase-0-discussion-skill-report.md` in
full before touching anything here: the decisions already taken, the problems
and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-1-discussion-pilot-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Run the `discussion` skill on `electronics/components/transistor`. Start from
the two pasted excerpts, hold the repository's first live discussion, resume
it in a fresh session, and finish with a written document. Correct the skill
from what the pilot shows.

---

## Overview

### Why This Phase Matters
No discussion has been held in this repository yet. The skill's main case is
therefore written before any instance of it exists, and only this pilot can
test it. `transistor` exercises both ways in:
- two pasted excerpts, two agents' answers to the same question: a
  seventeen-chapter syllabus, and a course that points at a Gemini canvas.
  Both give the answers without the user's question, and many of their claims
  are dated or numerical;
- a live discussion to be held on top of them, since the document is still to
  be written.

### What It Enables
The `transistor` document, which Phase 4 illustrates. It also yields a measured
resume cost to set against `claude --resume`.

### Out of Scope
The document's figures beyond what `diagram-design` already draws: they are
Phase 4.

---

## Tasks

### The excerpts
- [ ] Digest `transistor-1.md` and `transistor-2.md` into the journal, `study/discussion/`: every claim marked as an agent's account, the overlap between the two excerpts merged, and the canvas and images they refer to noted as received material

### The live discussion
- [ ] Open the repository's first live discussion with the user: the document's goal, its reader and its scope, recorded as the user said them
- [ ] Carry the discussion into the content the excerpts leave thin or contradict each other on, keeping the journal during the session rather than after it
- [ ] Resume in a fresh session from the journal's `index.md` alone, and record what the resume cost in tokens and what it missed
- [ ] Hand at least one dated or numerical claim to `sourcing`, and record its outcome in the journal
- [ ] Agree the outline with the user and write it into the journal

### The document
- [ ] Write `document/index.md` with the `pdf` skill from the agreed outline
- [ ] Build and review the document in the theme the user chose

### Feedback
- [ ] Fold the pilot's findings back into the skill, adding a script only for a step the pilot showed to be mechanical and repeated

---

## Technical Details

### Files to Modify
```
library/electronics/components/transistor/study/discussion/    new, the journal: index.md, topics/, sessions/
library/electronics/components/transistor/document/              new, the document
.claude/skills/discussion/SKILL.md                               the pilot's findings
```

### Dependencies
- Phase 0's skill.
- The user's time: the live discussion, spread over at least two sessions, and
  agreeing the outline.

### Constraints
- `sources/` is never edited.
- The theme and the cover belong to the user, per the `pdf` skill.
- Nothing displayed is invented, per the `pdf` skill.

---

## Acceptance Criteria

- [ ] `library/electronics/components/transistor/sources/` is byte-for-byte what it was before the phase
- [ ] The fresh session resumed from the journal without asking again anything the user had already answered
- [ ] No claim marked unverified in the journal is stated as established in `index.md`
- [ ] The PDF leaves review with no open defect
- [ ] `make test` passes
