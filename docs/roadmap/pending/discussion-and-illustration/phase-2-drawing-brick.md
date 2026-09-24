# Phase 2: The Drawing Brick

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/7)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-1-discussion-pilot.md` and `phase-1-discussion-pilot-report.md` in
full before touching anything here: the decisions already taken, the problems
and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-2-drawing-brick-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Extract what the hand-written figure generators share into one tested brick
that writes role-based SVG. Carry into it the rules the radio-fm review learned
the hard way.

---

## Overview

### Why This Phase Matters
The radio-fm review measured the cost of drawing without a brick. Its figure
generator took two thirds of the main context: 900 lines of coordinate
geometry, patched seven times. Every explanatory label in eight figures was
unreadable on dark paper, and a glyph fell outside the art direction's fonts.
The `radio-fm` and `round-led-d4017` generators both carry the same class `S`
and the same `wire`, `dot` and `text`, copied from one to the other.

### What It Enables
Phase 3's skill, which teaches how to compose a figure without also having to
teach how to write SVG by hand.

### Out of Scope
Rewriting the existing generators of `radio-fm` and `round-led-d4017` onto the
brick: they work, and their documents are built.

---

## Tasks

### The decision
- [ ] Compare the helpers of the two existing generators, and list what they share and where they diverge
- [ ] Confirm or overturn the core placement against `docs/architecture.md` §2, record the verdict in its borderline table, and name the module in `CLAUDE.md`'s repo map

### The brick
- [ ] Implement the canvas: dimensions, `title` and `desc` for accessibility, the element list, serialisation
- [ ] Implement the primitives both generators use — wire, dot, box, text, arrow with prefixed markers, label with a leader line — taking colour roles only and refusing a hexadecimal value
- [ ] Guard text against the glyphs the art direction's fonts lack, read from the fonts themselves rather than from a hand-kept list
- [ ] Implement a small-multiples layout: one subject in several states, in identical frames, each state labelled

### Tests
- [ ] Test the brick in the core suite: roles only, `title` and `desc` present, the glyph guard, prefixed identifiers

---

## Technical Details

### Files to Modify
```
core/<module>.py              new, the brick — named in the first task
tests/test_<module>.py        new, its suite
docs/architecture.md          §2 borderline table, §3
CLAUDE.md                     repo map, core modules
```

### Dependencies
None on Phase 1's output. The phase follows it so that one skill is finished
before the second is started.

### Constraints
- The brick writes `var(--role)` and nothing else. The build resolves the roles
  against the document's cascade, light or dark, because WeasyPrint does not
  resolve `var()` inside an SVG.
- The fonts are the art direction's three families: a fourth does not come in.
- `make test` stays offline.

---

## Acceptance Criteria

- [ ] One radio-fm figure, redrawn with the brick as a test fixture, takes fewer lines than the original and builds without a check finding
- [ ] No output of the brick contains a hexadecimal colour
- [ ] `make test` passes, including `test_claude_md_maps_the_core`
