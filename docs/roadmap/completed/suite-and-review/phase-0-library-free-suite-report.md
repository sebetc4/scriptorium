# Phase 0 Report: A Suite Independent of the Library

**Phase:** [phase-0-library-free-suite.md](phase-0-library-free-suite.md)
**Start Commit:** daf585f

---

## Work Log

### 2026-09-25

Opened the phase from `daf585f`, the commit that added this roadmap.

Read every test that touches `library/` and the code they call. Three facts
shaped the approach:
- `core/doc.py` keeps `LIBRARY` and `OUT` as module attributes, and
  `find_docs`, `out_dir` and the EPUB build read them at call time. A test can
  therefore point them at a copy of fixture documents.
- The scripts print paths with `relative_to(ROOT)`, which fails for a document
  outside the repository, and `review.py` computed a document's path from
  `ROOT / "library"` rather than from `LIBRARY`.
- The guard hook, `protect-paths.sh`, decides from the shape of a path under
  `$CLAUDE_PROJECT_DIR/library/` and needs no real document.

Changes to the core:
- `doc.relative()` and `doc.shown()` added; `out_dir` goes through
  `relative()`;
- the messages of `epub.py`, `preview.py`, `build.py` and `review.py` go
  through `shown()`;
- `check_xhtml` and `resolve_entities` moved from the `epub` skill into the
  core.

Fixtures:
- Wrote the fixture library: a copy of `exemples/guide-de-style`, and
  `sample/component`, a fictional `report` with three chapters, four
  role-based diagrams, a seven-column table, a code block, admonitions, icons
  and a footnote.
- `git check-ignore` showed that the unanchored `library/` rule in
  `.gitignore` would have ignored `tests/fixtures/library/` too. The rule is
  now anchored at the root, as `/library/`.
- Added `fixture_tree`, `on_fixtures` and `fixture_library` to the root
  conftest.

Moving the tests onto the fixtures, file by file:
- EPUB `test_build` (10 passed), `test_checks` (14),
  `test_sheets`/`test_css`/`test_tokens`/`test_cover` (29), and `test_xhtml`
  together with `test_tables` (19);
- PDF `test_pdf_layout` and the targeted passes of `test_review` (56 in the
  skill's suite, 4 s);
- the core's `test_doc`, plus two tests for the new helpers.

A grep for `find_docs([])` found three more tests that read the whole user
library and had never failed: `test_tables`, `test_chapters` and
`test_raster`. They were moved too.

Wrote `tests/test_library.py` first. It has fifteen cases: each builds a
library carrying the one defect a check must catch, and two run on the
fixture library, which must come out clean and unchanged. Then wrote
`core/library.py` until they passed.
- `tests/test_anatomy.py` keeps only the guard, probed under a temporary
  project root.
- `tests/test_layout.py` was removed.

Updated the documentation:
- `Makefile`: the target and its help line;
- `CLAUDE.md`: the core map, the commands, and the rule that said part of the
  suite reads the user's library;
- `README.md`;
- `docs/document.md`: the command, and the electribe-2 paragraph;
- `docs/architecture.md`: §2 borderline table, §6 and §7.

Results:
- `make test`: 546 passed, and nothing under `out/` or any document's
  `.work/` changed during the run.
- `make check-library` on the real library: 10 documents checked, 5 defects.
  - the four investigation directories at the root of
    `electronics/repair/electribe-2/sources`;
  - the malformed XHTML of `maialen/euskara`.

  No file was written.

Committed as `a59bf1b`. For the proof, checked that commit out into a git
worktree: `library/` is ignored, so the worktree has none. With `PYTHONPATH`
pointed at the worktree so that its own `core` is imported:
- 546 tests passed;
- no `out/` and no `library/` were created;
- `python -m core.library` answered "nothing to check" and exited 0.

The worktree was then removed.

The `discussion-and-illustration` roadmap's Phase 0 was blocked on
`make test`. That condition is now met. Its blocker was repointed at this
roadmap's Phase 1, which the user asked to settle before the archive work.

---

## Decisions

- **The suite reads a copy of the fixture library, made once per session.**
  `fixture_tree` copies `tests/fixtures/library/` into a temporary directory
  with an `out/` beside it. Nothing a test builds lands in the repository, and
  the expensive builds run once. The copy is shared across tests. That is
  safe because every build is deterministic, and `test_rebuilding_gives_the_same_file`
  checks exactly that.
- **Code that must follow the redirection reads `doc.LIBRARY` at call time.**
  `doc.relative()` does that, and messages print through `doc.shown()`, which
  does not assume a path lies inside the repository. Modules that import
  `LIBRARY` by value (`build`, `new`, `ingest`, `fetch`) were left alone:
  their tests only pin the constant, and none of them runs on a fixture.
- **`check_xhtml` is core** (§2): the EPUB build and the library check both
  call it.
- **`make check-library` is `core/library.py`, run as `python -m core.library`.**
  It is reached by `make`, outside every skill. It exits 1 when it finds a
  defect, like a linter, and it is never part of `make test`.
- **It converts every document, whatever its preset,** as the whole-library
  test it replaces did. A malformed body is a defect before it is an EPUB
  failure.
- **It carries no exception list.** The old anatomy test named
  `electronique/repair/electribe-2/sources` as a recorded exception. The check
  reports it on every run instead: the rule is stated once, and reshaping
  that document is the user's decision (`docs/document.md`, *One document does
  not fit*).
- **Fixture tests assert exact counts derived from the fixture's content**
  rather than the old lower bounds:
  - 8 objects that do not reflow: 4 diagrams, 3 row blocks and 1 code block;
  - 5 diagrams;
  - 2 EPUBs;
  - `touched == ["component"]` for the transposition.

  A fixture is written to make its test pass, as the user pointed out. An
  exact count at least fails when the fixture or the code drifts.

---

## Files Changed

**Added**
- `assets/icon.png` — untracked and not ignored, dated 2026-09-21: already there when this session began, before the roadmap existed. Not this phase's work, and not committed by it
- `core/library.py`
- `docs/roadmap/on-progress/suite-and-review/phase-0-library-free-suite-report.md`
- `tests/fixtures/library/exemples/guide-de-style/document/assets/.gitkeep`
- `tests/fixtures/library/exemples/guide-de-style/document/assets/chaine.svg`
- `tests/fixtures/library/exemples/guide-de-style/document/cover.md`
- `tests/fixtures/library/exemples/guide-de-style/document/index.md`
- `tests/fixtures/library/sample/component/document/assets/brochage.svg`
- `tests/fixtures/library/sample/component/document/assets/coupe.svg`
- `tests/fixtures/library/sample/component/document/assets/courbe.svg`
- `tests/fixtures/library/sample/component/document/assets/montage.svg`
- `tests/fixtures/library/sample/component/document/cover.md`
- `tests/fixtures/library/sample/component/document/index.md`
- `tests/test_library.py`

**Modified**
- `.claude/skills/epub/scripts/epub.py`
- `.claude/skills/epub/scripts/preview.py`
- `.claude/skills/epub/tests/test_build.py`
- `.claude/skills/epub/tests/test_chapters.py`
- `.claude/skills/epub/tests/test_checks.py`
- `.claude/skills/epub/tests/test_cover.py`
- `.claude/skills/epub/tests/test_css.py`
- `.claude/skills/epub/tests/test_raster.py`
- `.claude/skills/epub/tests/test_sheets.py`
- `.claude/skills/epub/tests/test_tables.py`
- `.claude/skills/epub/tests/test_tokens.py`
- `.claude/skills/epub/tests/test_xhtml.py`
- `.claude/skills/pdf/scripts/build.py`
- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/tests/test_pdf_layout.py`
- `.claude/skills/pdf/tests/test_review.py`
- `.gitignore`
- `CLAUDE.md`
- `Makefile`
- `README.md`
- `conftest.py`
- `core/doc.py`
- `docs/architecture.md`
- `docs/document.md`
- `docs/roadmap/pending/discussion-and-illustration/README.md` — its blocker repointed at this roadmap's Phase 1 now that `make test` is green
- `docs/roadmap/pending/discussion-and-illustration/phase-0-discussion-skill.md` — same
- `tests/test_anatomy.py`
- `tests/test_doc.py`

**Deleted**
- `tests/test_layout.py`

**Renamed**
- `docs/roadmap/pending/suite-and-review/README.md → docs/roadmap/on-progress/suite-and-review/README.md`
- `docs/roadmap/pending/suite-and-review/phase-0-library-free-suite.md → docs/roadmap/on-progress/suite-and-review/phase-0-library-free-suite.md`
- `docs/roadmap/pending/suite-and-review/phase-1-trigger-review.md → docs/roadmap/on-progress/suite-and-review/phase-1-trigger-review.md`
- `docs/roadmap/pending/suite-and-review/phase-2-trigger-audit.md → docs/roadmap/on-progress/suite-and-review/phase-2-trigger-audit.md`

---

## Problems And Deviations

- **Three tests read the user's library without ever failing.**
  `test_tables`, `test_chapters` and `test_raster` iterated
  `doc.find_docs([])` over the whole library. The phase's own family table,
  drawn from the failures, missed them; a grep found them. They moved with the
  rest.
- **`.gitignore` would have hidden the fixture library.** The unanchored
  `library/` rule matched `tests/fixtures/library/`. It was anchored at the
  root; the user's library is still ignored, checked with `git check-ignore`.
- **One check was dropped rather than moved.** `test_layout.py` also asserted
  that no `pdfs/` directory exists at the root, a guard left over from an old
  migration. It checks the repository, not the library, and guards against
  nothing that can recur, so it did not go to `make check-library`.
- **The electribe-2 exception is gone, and `make check-library` reports the
  document every time** (four lines). This is deliberate, see Decisions, but
  it means the command is never clean until the user decides about that
  document.
- **`make preview-style` still reads `library/exemples/guide-de-style`.**
  That is production code, not a test, and it is out of this phase's scope.
  The style proof depends on a document in the user's library, and a copy of
  that document now lives in the fixtures. Left open.
- **Stale `__pycache__` compiled when the repository was still called
  `pdf-creator`** showed the old path in tracebacks. It was removed. The
  directories are ignored, so nothing else is affected.

---

## Changes To Later Phases

No change to this roadmap's later phases.

---

## Assessment

Delivered: `make test` depends on the repository alone.
- It passes on a checkout with no `library/` (546 tests).
- It writes nothing under `out/` or `library/`.
- It reads two fictional documents that are versioned in
  `tests/fixtures/library/`.

The user's library is checked on request by `make check-library`. It is
read-only and prints one line per defect: today five, all of them known.

The phase found more coupling than the failures showed. Three tests read the
whole library and simply had never failed. Four scripts printed paths in a
way that breaks outside the repository. And an unanchored ignore rule would
have hidden the fixtures.

What Phase 1 needs first:
- `make test` is green again, so the phases of every roadmap can close.
- Phase 1 works inside `session-review`, whose suite has its own transcript
  fixtures and never touched `library/`.
- The two transcripts it must run the new obligation on are the notebook's,
  in `~/.claude/projects/-code-claude-scriptorium/`:
  - the opening session `3e933365`, continued with `--resume` as `03bbff2b`;
  - the fresh-session resume `a9d72882`.
