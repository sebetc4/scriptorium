# Phase 4: Illustration Pilot — Transistor

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/8)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-3-illustration-skill.md` and `phase-3-illustration-skill-report.md`
in full before touching anything here: the decisions already taken, the
problems and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-4-illustration-pilot-report.md` current as the work happens —
after each significant step, and before every commit, pause, or end of
session.

---

## Objective

Illustrate the `transistor` document with the `illustration` skill: a cover,
and the explanatory figures its outline calls for. Measure the figure work
against radio-fm.

---

## Overview

### Why This Phase Matters
The skill and the brick are claims about cost and quality until a document
proves them. `transistor` asks for exactly what `diagram-design` cannot draw:
a junction, a channel that forms as a voltage rises, a wafer under exposure.
radio-fm gives a measured baseline to beat.

### What It Enables
The roadmap's closure, and a decision on the next document to illustrate that
rests on measurements.

### Out of Scope
Reproducing the Gemini canvas, whether interactive or as a screenshot. What it
shows is redrawn, never copied.

---

## Tasks

### Figures
- [ ] Make one attempt to capture the Gemini canvas with Playwright, already the optional renderer of `make fetch RENDER=1`, by reading the document of the frame that holds the canvas rather than the page's network traffic. Save what it gets into `sources/` as acquired material
- [ ] List the states and views worth carrying to paper, from the capture or, failing it, from the images already in `sources/` and any screenshots the user takes
- [ ] Propose the figure list to the user from the outline: the idea each figure states, and which skill draws it
- [ ] Draw the figures the list retained, one generator per figure on the brick
- [ ] Draw one varying phenomenon as small multiples — the MOSFET channel forming as V_GS rises, unless the list retained another
- [ ] Propose a cover illustration, and apply the user's verdict

### Review and measure
- [ ] Build and review every variant through the delegated reviewer, until no defect is open
- [ ] Review the pilot with `session-review`, and fold its skill-gap findings into the skill

---

## Technical Details

### Files to Modify
```
library/electronics/components/transistor/generators/       new, one generator per figure
library/electronics/components/transistor/document/assets/  the figures
library/electronics/components/transistor/document/         index.md, cover.md
.claude/skills/illustration/SKILL.md                        the pilot's findings
```

### Dependencies
- Phase 1's document and Phase 3's skill.
- None on the Gemini canvas. The user cannot export it, and the figures are
  designed from the outline, with the canvas as inspiration. If the capture
  fails, the phase goes on without it.

### Constraints
- The cover is proposed, never decided.
- Every figure passes the proof command before it enters the build.

---

## Acceptance Criteria

- [ ] No figure label is unreadable on the dark variant, the radio-fm defect class
- [ ] Every figure passes the proof command's checks with no finding
- [ ] No figure image was read in the main conversation
- [ ] The session review puts the figure work's share of the main context below radio-fm's two thirds
- [ ] `make test` passes
