# Phase 1: What A Check Can See Without An Eye

---

## Status

**Current Status:** 🟢 Done (100% — 5/5)
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. The previous phase's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Catch in the text layer what is currently caught by looking: a figure's printed
font size, text that overlaps text, a glyph the fonts do not have.

---

## Overview

### Why This Phase Matters
On session `4c7bb3d0`, 4.6 pt text in a hand-drawn schematic, three label
collisions and an `≈` set in a fallback font were all found by a delegated pass,
three steps and eleven images after they were written. Each is arithmetic on
the SVG and the font set. None of them needs an eye.

The printed size is the clearest case: a 760-unit viewBox placed at 170 mm
makes one unit 0.22 mm, and nothing in the build says so before the page exists.

### What It Enables
Fewer images, which is the one cost that repeats on every later turn.

### Out of Scope
Judging a figure's composition. A check points at a number; the look judges.

---

## Tasks

- [x] Compute a figure's printed font size from its viewBox and its placed width, and name every text node under the threshold `review.py` already uses
- [x] Report text boxes that overlap, with the two labels named
- [x] Report glyphs used by the document and absent from the art direction's fonts
- [x] Decide where the checks run — inside `make review`, or before the build where they would be cheaper still — and say why in the report
- [x] Add them to the suite with an SVG fixture that fails each check

---

## Technical Details

### Files to Modify
```
.claude/skills/pdf/scripts/review.py    the checks
.claude/skills/pdf/tests/               one fixture per check
```

### Dependencies
Nothing outside what the repository already installs.

### Constraints
A check points at a page and does not judge it — the idiom the existing checks
follow. A check that cries wolf costs more than the defect it names, which the
same session demonstrated three times over.

---

## Acceptance Criteria

- [x] A figure with text under the threshold is named, with the computed size in mm
- [x] Two overlapping labels are named; two adjacent ones are not
- [x] A missing glyph is named with the character and the font that was asked for
- [x] No check fires on the repository's existing figures

---

## Notes
