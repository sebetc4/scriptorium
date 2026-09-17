# Phase 0: Target Architecture

---

## Status

**Current Status:** 🟢 Done (100% — 9/9)
**Started:** 2026-09-12
**Completed:** 2026-09-12
**Blocked By:** —

---

## Before Starting This Phase

> Read the previous phase in full before touching anything here: its notes,
> its unchecked tasks, and its unmet acceptance criteria. Skip this section
> only for the roadmap's first phase, which has no predecessor.

This is the roadmap's first phase — there is no predecessor to read.

---

## Objective

Write down the repository we are aiming at, before a single file moves. One
document, `docs/architecture.md`, that answers three questions without
ambiguity: what each root directory is for, what earns a place in the shared
core rather than in a skill, and where each skill stops.

---

## Overview

### Why This Phase Matters

The repository grew by addition. Each new capability — EPUB, import, web
capture — landed in `lib/` because `lib/` was there, not because it belonged.
The result is a flat module directory whose only organising principle is that
everything is a Python file, and two skills that between them describe five
different jobs.

Restructuring without a written target reproduces the same accident in a new
shape. The eight phases that follow are all moves, and a move is only cheap
when the destination is already decided.

### What It Enables

Every later phase becomes mechanical. Phase 2 builds the layout this phase
specifies; Phases 3 to 7 each fill one slot in it; Phase 8 writes down what was
built. None of them has to relitigate a boundary.

### Out of Scope

No code moves, no file is renamed, no skill is created. This phase produces a
document and nothing else. Resist the urge to "just move one thing while we're
here" — the value of the document is that it is validated before anything
depends on it.

---

## Tasks

### The target tree
- [x] Write `docs/architecture.md` with the target tree: one entry per root directory and the reason that directory exists
- [x] Record the rule that decides between the shared core and a skill, and resolve the borderline cases by name rather than by principle
- [x] Decide the fate of `templates/`, `theme/` and `brand/`: shared, or owned by a skill — a `report` document produces both a PDF and an EPUB, so its preset cannot belong to only one of them

### Skill boundaries
- [x] Draw the `pdf` / `sourcing` boundary on PDF files, and record the escape hatch to a sixth `import` skill if the boundary leaks in practice
- [x] Draw the `fetch` / `sourcing` boundary, and name what each of the two refuses to do
- [x] Check that the five descriptions trigger on their own intent and on no other — a skill that fires on a neighbour's job is worse than no skill

### Mechanics and vocabulary
- [x] Decide how a skill holds its scripts, tests and assets: directory layout, import path, and how pytest collects a suite that lives inside `.claude/skills/`
- [x] Decide what remains of `make`: which targets stay as a facade over a skill's entry point, which move, which disappear
- [x] Write the English glossary of the repository's vocabulary, term by term — the Phase 1 translation will follow it, and an inconsistent glossary produces an inconsistent codebase

---

## Technical Details

### Files to Modify

```
docs/architecture.md    to be created
```

### Dependencies

None. This phase reads the repository and produces prose.

### Constraints

- The five skills are settled: `pdf`, `epub`, `translate`, `fetch`, `sourcing`.
  This phase draws their borders, it does not reopen their number.
- `library/` is outside the scope of the English migration and of the
  restructuring. It holds user content, in whatever language its author chose.
- `diagram-design` is installed as a plugin, outside the repository. It is
  consumed through the `.diagram-design` marker and the profile written by
  `brand/sync.py`. It is never modified, and nothing in this roadmap changes
  that.

---

## Acceptance Criteria

- [x] `docs/architecture.md` exists and shows the target tree of the whole repository
- [x] Every current root directory is either present in the target tree with a stated reason, or explicitly slated for removal
- [x] Every module currently in `lib/` has a named destination
- [x] Every test file currently in `tests/` has a named destination
- [x] The three boundaries — core/skill, pdf/sourcing, fetch/sourcing — are each stated as a rule that can be applied to a case not yet encountered
- [x] The glossary covers every term the current French codebase uses in a comment, a message or a test name
- [x] The target architecture has been read and validated before Phase 1 opens

---

## Notes

### What Phase 0 found while writing the document

Four decisions taken, each of which a later phase was waiting on:

- **The import mechanism is an installable package.** `pyproject.toml`, `lib/`
  becoming `doclib`, `pip install -e .` in `make setup`. This is the question
  Phase 2 defers here, and the deciding argument is that it is the only one of
  the three options that also works when a script is run by hand — which the ten
  `sourcing` tools are designed to invite. The cost is that `make setup` becomes
  mandatory on a fresh clone.
- **`templates/`, `theme/` and `brand/` all stay at the root**, under one rule:
  the document's substance stays at the root, the skills own the transformation.
  This settles Phase 4's open question — `theme/epub.css` stays in `theme/`.
- **The glossary settles two collisions.** `library/<topic>/<slug>` frees
  `theme:` for the light/dark sense, and "planche" becomes **contact sheet** and
  **style proof**. The second supersedes this roadmap's own prose, which says
  "plate" in places while Phase 6 already names its tool `contact-sheet`.
- **`make` keeps all sixteen targets and gains none.** A target exists when the
  subject is the library or a document in it; the `sourcing` tools are run
  directly.

Three findings that were not anticipated:

- **`theme/epub.css` is a self-contained sheet, not a concatenation of the
  paginated ones.** "Flattening" in the EPUB backbone means resolving `var()`
  and dropping `@page`. The reason `theme/` is indivisible is stronger and
  mechanical: `doc.PRESETS` derives the preset registry from the directory's
  listing, so the core already knows `epub.css` by name.
- **`fetch.py` and `ingest.py` have no tests** — 939 lines, and only
  `test_disposition.py` imports them, to check they point at `library/`. Phase 5
  expects to move a suite that does not exist; it writes one. `pdf` likewise
  starts with an empty `tests/` directory.
- **`.pytest_cache/` is not in `.gitignore`.** It has only ever appeared at the
  root, where it went unnoticed. A skill's suite will create one inside the
  skill, so Phase 2 adds the pattern.

Eleven of the sixteen test files go to `epub`, five stay at the root. The
imbalance is faithful: the EPUB work is the most recent and the best covered.

---

### The boundary that needed a decision

Importing a PDF appears in two different jobs, and the format is the wrong
thing to sort on. The distinction that holds is the **destination**:

- **`pdf`** — an external PDF becomes a document of the library. It is read in
  order to be rebuilt: text extracted, images carried over, pages rendered as a
  proofreading aid, then translated and given the repository's art direction.
  The output is an `index.md` under `library/`.
- **`sourcing`** — a PDF is a piece of evidence. It is read in order to be
  known: locate a term across a manual, detect the pages with no text layer,
  render a page at high resolution and crop it to read a silkscreen. No
  document is produced; the PDF stays a source.

The shared machinery — rendering a page with `pypdfium2`, cropping on
fractional coordinates, building a contact sheet — is the same in both cases,
and that is precisely why it belongs to the shared core rather than to either
skill. Each skill owns its intent; neither owns the brick.

The escape hatch: if in practice a request keeps landing between the two, a
sixth `import` skill is split out. That is a decision this phase records as
available, not one it takes.

### What the sourcing inventory already says about this

`sources/sourcing/outillage-sourcing.md` §4.1 and §5.3 note that the repository
already owns the contact-sheet brick twice — in `make preview` and in the PDF
review loop — and that it should be factored out. The core/skill rule written
here should make that conclusion follow automatically rather than be a
judgement call.
