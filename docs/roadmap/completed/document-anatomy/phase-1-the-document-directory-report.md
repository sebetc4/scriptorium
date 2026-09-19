# Phase 1 Report: The Document, In Its Own Directory

**Phase:** [phase-1-the-document-directory.md](phase-1-the-document-directory.md)
**Start Commit:** 302a0bf

---

## Work Log

### 2026-09-19

Phase opened. Phase 0's file and report were read in full: 6/6 tasks, 4/4
acceptance criteria, no restructuring pending.

**The inventory came before anything else, and it corrected the roadmap.** There
are **eight** documents, not twelve. The figure in the README came from counting
directories *named* `sources` at every depth — there are fifteen of those — and
not documents. Two of the eight are unusual and both were found by listing
rather than assumed:

- `electronique/repair/electribe-2/sources` is a document whose slug is
  literally `sources`: an investigation's material promoted to a document. It
  holds `NOTES.md`, `datasheets/`, `images/`, `raw/`, `threads/` and no
  `assets/`.
- `electronique/components/led` carries a `theme.css`, a per-document stylesheet
  that §11 did not place. The cut settles it without hesitation — both
  `build.py` and `epub.py` read it, so it is build-read and it moved into
  `document/` with the rest.

A backup of the whole library, 120 MB, was taken before any move.

**The before state was built and fingerprinted first.** `make build` turned out
not to be byte-reproducible: two builds of the same source give different bytes,
with no date in the metadata — WeasyPrint's document identifier. So the
comparison is on content: page count, page size, text digest and image count per
page. 15 PDFs, 292 pages.

**Then the code.** `DOCUMENT = "document"` and `doc_dir(d)` in `core/doc.py`, and
every path inside a document goes through the helper rather than being built at
the call site. Discovery matches `document/index.md` and returns its
grandparent, which also fixes something the old code could not express: an
`index.md` a user keeps in their own material is no longer a document, so
discovery cannot wander into `sources/`. That is now a test.

**The migration, and the two silent failures it exposed.** The dry run listed
eight documents, every move, and everything that stays — no surprises. After the
move, everything still built, and the fingerprint disagreed on seven PDFs.

The first failure: `build.py` inlines an SVG by resolving its `src` against the
document directory, and guards containment the same way. Both still pointed at
the root, so no SVG was inlined any more. The figures still *rendered* —
WeasyPrint resolved them through the base URL, which had been fixed — so the
build succeeded, the image count per page was unchanged, and the only trace was
that the text inside every schematic had left the PDF's text layer. Inlining is
what substitutes the art direction's roles into an SVG, so the dark variants
would have carried unresolved colours. Nothing in the suite covers this.

The second: `epub.py` names each image after its stem plus a digest of its path
*relative to the document root*. That path gained a `document/` segment, so every
image in every archive was renamed, and every XHTML file and manifest that
referenced them changed with it. The content was identical throughout — the
digests of the images themselves never moved — but the churn was gratuitous. The
name now derives from the path inside `document/`, which is what it always
meant: where a file sits *within* a document, not where the document sits.

After both fixes, three comparisons: 15 PDFs and 292 pages content-identical, 8
EPUBs and 180 archive entries identical entry by entry, and 221 library files
byte-identical between the backup and the migrated tree — nothing rewritten,
nothing lost.

**`make list` was a third dependency, outside Python.** It ran `find library
-name index.md -printf '%h\n'`, which after the migration printed every path
with a trailing `/document`. It now matches `*/document/index.md` and strips the
segment.

`make new`, `make build`, `make review` and `make preview` were each run end to
end. `make test`: 493 passed, up from 485 — eight new tests, and twenty-two
fixtures moved to the new shape across four suites.

---

## Decisions

- **`doc_dir(d)` is the only place that knows where the build looks.** Every
  call site that had `d / "cover.md"` or `d / "assets"` now goes through it.
  Phase 2 adds `work_dir()` beside it on the same argument.

- **The staleness check walks `document/` and excludes nothing.** It used to
  walk the whole document and skip `sources/` by name. The cut removes the
  special case — and it was about to become wrong anyway: once `.work/` sits
  inside the document, a review writing its own sheets there would make every
  PDF look stale forever.

- **An EPUB's image names derive from the path inside `document/`.** A document
  that moves must not rename every image in its archive. This is a correction of
  intent, not of the migration: the digest was always meant to disambiguate two
  assets within one document.

- **Discovery requires `document/index.md`, not any `index.md`.** It is what
  keeps `sources/` — the user's directory, which they fill as they see fit —
  from being walked into. Phase 4's guard inherits a discovery that already
  refuses to look there.

---

## Files Changed

**Added**

- `docs/roadmap/on-progress/document-anatomy/phase-1-the-document-directory-report.md`

**Modified**

- `core/doc.py`
- `Makefile`
- `CLAUDE.md`
- `.claude/skills/pdf/scripts/build.py`
- `.claude/skills/pdf/scripts/new.py`
- `.claude/skills/pdf/scripts/ingest.py`
- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/pdf/tests/test_review.py`
- `.claude/skills/epub/scripts/epub.py`
- `.claude/skills/epub/tests/test_raster.py`
- `.claude/skills/fetch/scripts/fetch.py`
- `.claude/skills/fetch/SKILL.md`
- `.claude/skills/fetch/tests/test_capture.py`
- `.claude/skills/translate/scripts/translate.py`
- `.claude/skills/translate/SKILL.md`
- `.claude/skills/translate/tests/test_translate.py`
- `tests/test_doc.py`
- `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/on-progress/document-anatomy/phase-1-the-document-directory.md`
- `docs/roadmap/on-progress/document-anatomy/phase-3-sources-study-generators.md`
- `docs/roadmap/on-progress/document-anatomy/phase-4-the-guard.md`

The last two are the document count corrected from twelve to eight, in the tasks
that repeat it. `library/` is user content, outside git, and appears in neither
list: eight documents moved, and the moves are recorded above.

---

## Problems And Deviations

- **The roadmap said twelve documents; there are eight.** Corrected in the
  README's body and in the tasks of phases 1, 3 and 4 that repeated it. No
  changelog entry carried the figure, so none was rewritten; the wrong count
  also stands in the commit message that created the roadmap, `2db2c9b`, which
  is history and stays as it is. The 1.3.0 entry explains the correction.

- **`theme.css` and `glossary.yaml` are files §11 does not place.** `theme.css`
  is settled by the cut — the build reads it, so it went into `document/`.
  `glossary.yaml` is not read by the build and is not produced by it;
  `translate.py` reads it at the document's root and still does. `translate`'s
  `SKILL.md` said it lives "beside its `index.md`", which stopped being true the
  moment the entry moved, and now says the root and names the gap. No document
  currently has one, so nothing was migrated. Phase 3 touches `translate` and is
  where it should be settled.

- **Two silent failures reached a successful build**, both described in the Work
  Log. Neither was caught by 485 passing tests; both were caught by comparing
  the outputs. That is the argument for the comparison being a task rather than
  a formality.

- **The PDFs could not be compared byte for byte**, because `make build` is not
  byte-reproducible at all. The criterion's second branch — "or the difference
  is explained" — is what was used, and the comparison is on content.

All seven tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

- `phase-3-sources-study-generators.md` and `phase-4-the-guard.md`: the document
  count corrected from twelve to eight in the tasks that name it. No task was
  added, removed or moved.

Phase 3 inherits one open question rather than a change: where `glossary.yaml`
belongs. It is recorded above and in `translate`'s `SKILL.md`, not in the phase
file, because the phase already owns `translate` and the answer belongs in its
notes.

---

## Assessment

The phase did what it set out to and the interesting part is what the outputs
said rather than what the tests did. Four hundred and eighty-five tests passed
on a tree where no SVG was being inlined any more — where every schematic in the
library would have shipped with unresolved colours in its dark variant. The
failure was invisible in every way a test currently looks: the build succeeded,
the pages were the right size, the figures were on them, and the image count per
page never moved. It showed up as a changed text digest on seven PDFs, because
an inlined SVG puts its labels in the text layer and a linked one does not.

That is worth carrying beyond this roadmap. The repository's test suite covers
scripts; it does not cover *the document as built*, and the one check that would
have caught this — compare the output against the output before the change —
exists only as a task inside a migration phase.

What Phase 2 needs to know first: `doc_dir()` is in `core/doc.py` and `work_dir()`
belongs beside it, built the same way, so that `make clean` deletes by asking
the layout rather than by matching a glob at the call site. The staleness check
in `review.py` already walks `document/` only, which is what makes it safe for
`.work/` to live inside the document — that was changed in this phase for
exactly that reason. And the comparison harness that found both failures is
throwaway code in the session's scratchpad; Phase 2 moves large outputs and will
want it again, so rebuilding it is the first task, not an afterthought.
