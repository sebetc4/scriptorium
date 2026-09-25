# Phase 1 Report: Skill Triggers in the Session Review

**Phase:** [phase-1-trigger-review.md](phase-1-trigger-review.md)
**Start Commit:** 00a356a

---

## Work Log

### 2026-09-25

Opened the phase from `00a356a`, the commit that closed Phase 0, after
reading Phase 0's file and report. No restructuring was pending.

Before starting the phase's own tasks, the user asked for three changes
outside its scope. They are recorded here because they fall inside its diff.

**The two findings of `make check-library`, fixed.**
- `maialen/euskara`: its raw HTML held 31 `<img … alt="">` never closed as
  XML requires, and one stray `</div>` (117 opening tags, 118 closing). Both
  were fixed in `document/index.md`. The rebuilt PDF is pixel-identical to the
  previous one on all 7 pages, at 72 and 100 dpi.
- `electronics/repair/electribe-2`: the anatomy migration had taken the
  investigation folder, `electribe-2/sources/`, for the document's root,
  because it held an `index.md`. The root moved up one level:
  - `document/` and `study/` moved to `electribe-2/`;
  - the investigation's pieces (`datasheets/`, `images/`, `raw/`, `threads/`)
    stayed in `sources/`;
  - an empty `assets/` and the old `.work/` were removed.

  Every file was kept apart from the 6 of `.work/`, checked against a listing
  taken before the move. The rebuilt PDF has the same 18 pages, and its text
  differs only in its title, from "Sources" to "Electribe 2". The stale
  outputs under `out/…/electribe-2/sources/` were removed.
- `make check-library` now reads: 9 documents checked, no defect.

**A glossary is tolerated at a document's root.** Reading the `translate`
skill showed that it keeps `glossary.yaml` beside `document/`, as
`docs/document.md` says. `make check-library` would have reported every
translated document, so `TOLERATED` in `core/library.py` admits it, and a test
holds it.

**The style guide left the user's library.** The user did not want an
`exemples/` topic in a library they are organising.
- The guide is now `brand/style-guide/`, the one document the repository owns,
  named once as `core.doc.STYLE_GUIDE`.
- `doc.relative()` places a repository document from the root, so
  `make build DOC=brand/style-guide` writes to `out/pdf/brand/style-guide/`.
- A targeted `make clean` removes any document's `.work/`, and a full one
  removes the guide's too.
- `.work/` is ignored.
- `make preview-style` reads the guide there.
- Four stale statements in the guide were corrected: two `pdfs/` paths, the
  place of a document's `theme.css`, and a hexadecimal value in an example
  that contradicted the rule the guide documents.
- Its review reports the same three findings as the old copy did, on the
  same five pages.
- `library/exemples/` was removed once a diff showed that nothing but those
  four corrections separated it from the new copy. The frozen fixture copy
  under `tests/fixtures/` is unchanged.

`make test`: 550 passed.

---

## Decisions

- **electribe-2 was reshaped, not re-read.** Its `document/index.md` is a
  pasted ChatGPT conversation, and its journal speaks of a final document
  that was never written. Moving the conversation to `sources/` would have
  left no document to build. The root moved up one level and nothing else
  changed. Whether the conversation becomes a source and a real document is
  written, with the `discussion` skill, is the user's decision.
- **The style guide lives in `brand/`**, beside the art direction it shows,
  rather than under `docs/`, which holds prose about the repository.
- **The guide's three review findings were left as they were**: a straight
  apostrophe in the subtitle, an arrow set in a fallback font, a loose line.
  They predate the move. The frozen fixture copy relies on one of them: the
  targeted-pass test needs a finding past page 1. Fixing them in the living
  guide is the user's call.

---

## Files Changed

---

## Problems And Deviations

---

## Changes To Later Phases

---

## Assessment
