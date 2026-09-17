# Phase 4: The `epub` Skill

---

## Status

**Current Status:** 🟢 Done (100% — 11/11)
**Started:** 2026-09-13
**Completed:** 2026-09-13
**Blocked By:** —

---

## Before Starting This Phase

> Read the previous phase in full before touching anything here: its notes,
> its unchecked tasks, and its unmet acceptance criteria. Skip this section
> only for the roadmap's first phase, which has no predecessor.

**Read First:**
1. The previous phase's `## Notes` section — what it found, decided, and
   left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Give the reflowable output its own skill. The EPUB chain is four modules, a
stylesheet that is not a preset, nine test files and a review discipline that
is the opposite of the PDF one — and all of it currently lives as a section
inside a skill about PDFs.

---

## Overview

### Why This Phase Matters

The EPUB output does not merely differ from the PDF in format; it inverts the
rules. A PDF is reviewed page by page because its pagination is fixed. An EPUB
has no pages — the reader repaginates by screen size and text size — so
reviewing "screen 23 of 47" would certify a pagination no device reproduces.
What is reviewed instead is what does not reflow: diagrams, transposed tables,
code blocks.

Two rules of the same repository that say opposite things about proofreading
should not be two paragraphs of one document. The e-ink constraints compound
it: no `var()` may survive, colour never carries meaning alone, signalling
colours are taken at equalised luminance.

### What It Enables

`pdf` stops carrying a domain it does not own. The EPUB rules — currently
spread across `claude.md`, `README.md` and `pdf-doc` — land in one place, where
a change to the reflowable output has exactly one document to update.

### Out of Scope

- Writing the document. The source of an EPUB is the same `index.md` as the
  PDF; authoring is `pdf`.
- The art direction itself. `epub` consumes the roles and states how they are
  flattened for a reader, it does not define them.

---

## Tasks

### The skill's prose
- [x] Write `SKILL.md` in English: one source, two outputs that have no reason to resemble each other
- [x] Write the review rule: an EPUB is not reviewed screen by screen, only what does not reflow is reviewed
- [x] Write the e-ink rules: no surviving `var()`, colour never alone, signalling roles at equalised luminance through `colors.epub`
- [x] Document the transposition of tables past five columns and the per-document `epub: {table-threshold:}` override

### The code
- [x] Move `core/epub.py` and its tests into the skill
- [x] Move `core/check.py` and its tests, `epubcheck` integration included
- [x] Move `core/preview.py` and its tests — contact plate and style plate — *already moved by Phase 2 as its proof of the mechanism; this phase only repointed its import of `epub`*
- [x] Place `theme/epub.css` per the Phase 0 decision: a skill asset, or a stylesheet that stays in `theme/` while being flattened at build — *stays in `theme/` (`docs/architecture.md` §4)*
- [x] ~~Keep the SVG rasterisation brick shared with `pdf` rather than copying it~~ Keep the page-render brick under the rasterisation shared — *amended, see Notes: `pdf` never rasterises*

### Closing
- [x] Turn `make epub`, `make preview` and `make preview-style` into facades over the skill's entry point — *one line each, target names unchanged*
- [x] Verification: build the style guide EPUB, run both review plates, `make test` green

---

## Technical Details

### Files to Modify

```
.claude/skills/epub/SKILL.md   written in full
core/epub.py                    697 lines, moved
core/check.py                   201 lines, moved
core/preview.py                 164 lines, moved
theme/epub.css                 placed per Phase 0
tests/                         the nine EPUB suites, moved
Makefile                       epub, preview, preview-style
```

### Dependencies

Phase 3. `pdf` must already own the authoring chain before `epub` can point at
it for "how a document is written".

### Constraints

- `make epub` stays a separate target from `make build`. A document is rebuilt
  dozens of times while being written, and rasterising twelve diagrams on each
  pass is a gratuitous slowdown — the reason is already recorded as a comment
  in the `Makefile` and should survive the move.
- `core/check.py` runs on every `make epub`. Moving it must not make it optional.
- Only `report` presets produce an EPUB. The skill states the limitation rather
  than papering over it.

---

## Acceptance Criteria

- [x] A skill named `epub` holds the reflowable chain, its scripts and its tests
- [x] Its `description` triggers on EPUB, e-reader and reflowable-output requests, and not on PDF authoring
- [x] Every EPUB rule currently in `claude.md`, `README.md` or `pdf-doc` is in the skill
- [x] `make epub`, `make preview` and `make preview-style` work unchanged from the repository root
- [x] The checks still run on every `make epub`
- [x] No `var()` survives in the style guide's EPUB, verified by the checks
- [x] `make test` is green, the nine EPUB suites included — *ten moved, eleven with `test_sheets.py`; see Notes*
- [x] The style guide EPUB has been reviewed through its plates

---

## Notes

### Why the EPUB rules are worth their own document

Five constraints, none of them deducible from knowing EPUB in general, all of
them learned here:

1. Readers under RMSDK do not resolve `var()` — the colour falls back to
   `inherit` without raising anything. Flattening is done by the build and
   verified by the checks; the sources keep their roles.
2. An e-ink screen renders colour as grey, so `accent`, `alert` and `danger`
   are taken at equalised luminance. At brand values, orange would vanish where
   red stayed strong.
3. Meaning is carried by the admonition's glyph, which follows the reader's
   text colour. The hue lives on the rule, where losing it costs only style.
4. A table past five columns is transposed into blocks. The source is not split
   — the PDF keeps its full matrix from the same source.
5. A dense diagram is unreadable at six inches, vector or bitmap alike. If the
   contact plate shows it, the diagram is what gets redrawn, not the output.

### What was actually moved

Two modules and ten test files: `epub.py` and `check.py`, plus
`test_build`, `test_chapters`, `test_checks`, `test_cover`, `test_css`,
`test_package`, `test_raster`, `test_tables`, `test_tokens` and `test_xhtml`.
The phase's count of "nine suites" was written before Phase 1 renamed and split
the files. With `test_sheets.py`, which Phase 2 moved, the skill holds eleven.
`preview.py` was already here, since it was Phase 2's proof. `core/` is now
`doc`, `mdext`, `imaging`, `pdfpage`, plus `fetch` until Phase 5, and `tests/`
holds only the four suites whose subject is the repository or the core.

- **`epub.py` imports `check.py`, not the reverse**, so the two moved in one
  commit. The imports became `import check` and `import epub`: sibling scripts
  resolved from the script's own directory when run directly, and through the
  skill's conftest under pytest. No installed module claims either name, which
  was checked before choosing them.
- **Test count: 126 before, 126 after**, 104 of them now in the skill. Every
  moved test file was diffed against its original: only the import lines
  changed, plus one comment naming the conftest that now lives at the root.
  One near miss is worth recording. The script that regrouped the imports put
  `import epub` after a module constant in four files. The suite stayed green,
  because the import still ran, so it was the reading of the diff that caught
  it, not the tests.
- **The outputs are byte-reproducible, so the verification is on bytes.** All
  seven EPUBs in the library and the style guide's three review sheets were
  hashed before the move. Two consecutive builds gave identical hashes, and so
  did the build after the move: 18 files, 0 differences. That includes a change
  to comments in `theme/epub.css` and `brand/tokens.css`, which flattening
  strips before they can reach the archive.

### The rasterisation task was based on a false premise

"Keep the SVG rasterisation brick shared with `pdf` rather than copying it"
assumed `pdf` rasterises. It does not: the paginated backbone inlines SVG, and
`docs/architecture.md` §2 already ruled that rasterising belongs to `epub`
alone. What *is* shared is the brick underneath, `core/pdfpage.py`, and it
stayed in the core. The task is amended rather than ticked as written.

### Where the rules came from, and one that was missing

The skill gathers what `claude.md` (five rules), `README.md` (two sections) and
the carried-over section in the stub said, and the stub's placeholder is gone.
It also states three things that were only in the code: **`theme:` does not
apply to the EPUB**, which always uses `colors.epub`; **a document's local
`theme.css` follows it into the EPUB**, flattened; and **`check.py`'s numbers**
(a contrast floor of 6.5:1, and at most 8 grey levels between the three
signalling roles). Every factual claim was checked against the scripts before
it was committed.

`claude.md` and `README.md` keep their EPUB paragraphs, in French. Phase 8
rewrites both, and `tests/test_documentation.py` still pins one of them
(`ne reflue pas`).

### Found during the review

- **The contact sheet can strand an object's label.** On `components/led`, the
  label "object 3 / 4" sits at the bottom of the first screen, while its figure
  opens the second. The sheet is a review aid, the EPUB itself is unaffected,
  and keeping each label with its object is a behaviour change, not a move. It
  is recorded here for whoever next touches `preview.py`.
- **The style guide EPUB contains `var(` three times, inside `<code>`.** That is
  the guide explaining roles in prose, not an unresolved variable. The check
  inspects the stylesheets, which is where RMSDK would fail, so it is right not
  to flag them. Worth knowing before anyone "tightens" it into a grep over the
  whole archive.
- **`epubcheck` is not installed on this machine**, so EPUB 3 conformance was
  not verified in this phase, and `make epub` says so. The mechanical checks
  passed on all seven books.
