# Phase 2: Everything Disposable, In One Place

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/6)
**Started:**
**Completed:**
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. Phase 1's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Move the review sheets, the EPUB proofs and the translation workspace out of
`out/` and into `<slug>/.work/`, so that `out/` holds finished documents and
nothing else.

---

## Overview

### Why This Phase Matters
`out/` is where a person goes to find the PDF they asked for. It holds five
directories and three are not documents: `review/` is 25 MB of page sheets
rendered four to an image for a reviewer's eye, `preview/` the EPUB contact
sheets, `translate/` a workspace of text chunks and engine answers — the working
state of a job, not an output of it.

They are also kept away from the document they describe, in a parallel tree
joined to it by nothing but a path convention.

### What It Enables
`out/` as an export folder a person can hand to someone else, and a document
that is one thing in one place.

### Out of Scope
`out/pdf/` and `out/epub/`. They hold the finished documents and do not move.

---

## Tasks

- [ ] Add `work_dir(root, kind)` beside `out_dir()` in `core/doc.py`, resolving to `<slug>/.work/<kind>/`, and make it the only place that knows the layout
- [ ] Move `review.py`'s sheets and zooms from `OUT / "review"` to `.work/review/<variant>/`
- [ ] Move `preview.py`'s sheets from `out_dir(d, "preview")` to `.work/preview/`
- [ ] Move `translate.py`'s workspace from `OUT / "translate"` to `.work/translate/`
- [ ] Make `make clean` safe: it removes `out/` and every `.work/` under `library/`, and nothing else — proven on a fixture tree holding a `sources/`, a `document/` and a `.work/`
- [ ] Add `make clean DOC=topic/slug`, since a clean that can only be total is a clean nobody runs

---

## Technical Details

### Files to Modify
```
core/doc.py                                    work_dir(), beside out_dir()
.claude/skills/pdf/scripts/review.py           OUT / "review" → work_dir
.claude/skills/epub/scripts/preview.py         out_dir(d, "preview") → work_dir
.claude/skills/translate/scripts/translate.py  WORKSPACES → work_dir
Makefile                                       clean, and clean DOC=
docs/architecture.md                           follows the change
```

### Dependencies
Phase 1's document root, which is what `.work/` sits beside.

### Constraints
`make clean` will delete inside `library/`, which is user content and is not
versioned: nothing there is recoverable. The deletion is driven by the layout
function, never by a glob written at the call site, and the test that proves it
spares `sources/` comes before the change, not after.

Nothing new is needed for git: `library/` is already ignored whole.

---

## Acceptance Criteria

- [ ] After a full build, review and preview, `out/` holds `pdf/` and `epub/` and nothing else
- [ ] `make review` and `make preview` write inside the document and find their own output on the next run
- [ ] `make clean` on a tree holding `sources/`, `document/` and `.work/` removes only `.work/`, proven by a test
- [ ] `make clean DOC=topic/slug` removes one document's `.work/` and leaves the others
- [ ] `make test` passes

---

## Notes
