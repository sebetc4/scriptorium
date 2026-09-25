# Phase 0: A Suite Independent of the Library

---

## Status

**Current Status:** 🟢 Done (100% — 9/9)
**Started:** 2026-09-25
**Completed:** 2026-09-25
**Blocked By:** —

---

## While Working

Keep `phase-0-library-free-suite-report.md` current as the work happens —
after each significant step, and before every commit, pause, or end of
session.

---

## Objective

Make `make test` depend on the repository alone. It must pass or fail on the
code, never on what the user keeps in `library/`, and never write an EPUB as
a side effect. The checks that are really about the user's library move to a
separate, read-only command.

---

## Overview

### Why This Phase Matters
On 2026-09-24 `make test` failed with 18 failures and 5 errors, none caused by
code. The user had renamed `library/electronique/` to `electronics/`, and
`electribe-2/sources/` has subdirectories. One document, `maialen/euskara`,
converts to malformed XHTML. Because `library/` is user content and changes
at any time, the suite breaks whenever the user reorganises it. Every
roadmap's closure runs `make test`, so it also blocks every phase in the
repository. And every run writes a real EPUB into `out/epub/` for each
`report` document, which nobody asked for.

The tests that read `library/` fall into three families, from a reading of
every such file:

| Family | Files | What they really test | Fix |
|---|---|---|---|
| **A. Code, run on a real document used as an example** | `epub/tests/test_build.py`, `test_checks.py`, `test_sheets.py`, `test_css.py`, `test_tokens.py`, `test_cover.py`; `pdf/tests/test_pdf_layout.py` (the build); `pdf/tests/test_review.py` (targeted passes) | EPUB building, the checks, the cover, the stylesheets. They used `electronique/components/led`, `controlers/esp32` and `exemples/guide-de-style` because those happened to be there | fictional fixture documents, frozen under `tests/fixtures/` |
| **B. The user's library itself** | `tests/test_anatomy.py`, `tests/test_layout.py`, "the whole library builds", "the whole library produces well-formed XHTML" | the state of the user's content | a separate read-only command, `make check-library`, that never blocks `make test` |
| **C. A path in the code** | `fetch.LIBRARY == repo / "library"`, the PDF scripts pointing at `library/` | a constant | nothing: no dependency on content |

### What It Enables
Every roadmap can close again. The user's library is checked on request, with
findings that name the document and the defect, instead of failing a code
test.

### Out of Scope
Fixing the user's documents themselves (`maialen/euskara`, the layout of
`electribe-2/sources/`). `make check-library` reports those defects; the user
decides what to do with them.

---

## Tasks

### The fixtures
- [x] Write fictional fixture documents under `tests/fixtures/library/`: one `report` carrying what the family-A tests exercise (a table the EPUB transposes, a diagram, a cover with an eyebrow and a subtitle), and a copy of `exemples/guide-de-style` as the style proof's input
- [x] Give the root `conftest.py` a fixture that copies the fixture library into `tmp_path`, so no test writes under `tests/fixtures/` or `out/`
- [x] Move the family-A tests of `epub` onto the fixture documents, building into `tmp_path`
- [x] Move the family-A tests of `pdf` (`test_pdf_layout.py`, the targeted passes of `test_review.py`) onto the fixture documents

### The library check
- [x] Write `make check-library`: anatomy, layout and well-formed XHTML for every document of `library/`, converted in memory, with no EPUB and no PDF written, and one line per defect naming the document
- [x] Remove the family-B tests from `make test`, keeping their logic in the command's own tested module
- [x] Add `make check-library` to the `Makefile` help, `CLAUDE.md`'s commands and `docs/document.md`

### Proof
- [x] Show that `make test` passes with `library/` moved aside, and writes nothing under `out/`
- [x] Run `make check-library` on the real library and hand its report to the user

---

## Technical Details

### Files to Modify
```
tests/fixtures/library/                  new, the fictional documents
conftest.py                              the fixture-library fixture
.claude/skills/epub/tests/               family A
.claude/skills/pdf/tests/                family A
tests/test_anatomy.py, tests/test_layout.py   family B, moved
the check-library module and its tests   new — its place decided by docs/architecture.md §2
Makefile, CLAUDE.md, docs/document.md
```

### Dependencies
None.

### Constraints
- A fixture document is written so that the test it serves can pass. That
  makes such a test weaker than one run on real content, and the user said
  so. Two things compensate: every fixture carries the defects a check must
  catch, not only the clean case, and `make check-library` keeps real content
  under check, on demand.
- `library/` is never modified by this phase.

---

## Acceptance Criteria

- [x] `make test` passes with `library/` absent or renamed
- [x] `make test` writes nothing under `out/` or `library/`
- [x] `make check-library` reports the known defects of the real library — the `euskara` XHTML, the `electribe-2/sources/` subdirectories — and writes no file
- [x] No test under `tests/` or `.claude/skills/*/tests/` names a path inside the user's `library/`
