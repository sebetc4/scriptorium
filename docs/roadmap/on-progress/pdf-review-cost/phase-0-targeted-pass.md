# Phase 0: The Targeted Pass

---

## Status

**Current Status:** 🟢 Done (100% — 4/4)
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Blocked By:** —

---

## Before Starting This Phase

This is the first phase. Read this roadmap's `README.md`, and
`.claude/agents/pdf-reviewer.md` in full — the budget it already imposes is the
thing being extended, not replaced.

---

## Objective

Let a verification pass look at the pages that changed, instead of the document.

---

## Overview

### Why This Phase Matters
On session `4c7bb3d0` the second round of review read all fifteen pages of both
variants — 46,636 fresh tokens — to confirm fixes on six of them. The agent had
no way to do less: it takes a document and a variant, and reviews the document.

### What It Enables
An iteration costs what the iteration changed.

### Out of Scope
Deciding which pages changed. The conversation that made the fixes knows, and
passes them.

---

## Tasks

- [x] Add an optional page list to the agent's input, and say in its description that a verification pass takes one
- [x] Say what a targeted pass still does whole: the text-layer checks, which cost no image and would otherwise stop covering the document
- [x] Say what it must not do — report a page it was not given, or treat the absence of the rest as a finding
- [x] Record, in the phase report, what one targeted pass costs against one full pass on the same document

---

## Technical Details

### Files to Modify
```
.claude/agents/pdf-reviewer.md     the input, and one line of its description
.claude/skills/pdf/SKILL.md        when to ask for a targeted pass
```

### Dependencies
None.

### Constraints
The agent's budget is written in its own file and is the reason it is cheap.
A page list makes a pass cheaper; nothing here may make one more expensive.

---

## Acceptance Criteria

- [x] A pass given six pages reads six pages, and says so
- [x] A pass given no pages behaves exactly as it does today
- [x] The text-layer checks still run over the whole document
- [x] The cost of both shapes is recorded on one real document

---

## Notes
