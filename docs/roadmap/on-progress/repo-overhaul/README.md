# Roadmap: Repo Overhaul

```
Phase 0  Target Architecture        🟢 ████████████████████ 100%  (9/9)
Phase 1  English Pass               🟢 ████████████████████ 100%  (12/12)
Phase 2  Skill Layout               🟢 ████████████████████ 100%  (10/10)
Phase 3  PDF Skill                  🟢 ████████████████████ 100%  (13/13)
Phase 4  EPUB Skill                 🟢 ████████████████████ 100%  (11/11)
Phase 5  Fetch Skill                🟢 ████████████████████ 100%  (11/11)
Phase 6  Sourcing Skill             🟢 ████████████████████ 100%  (17/17)
Phase 7  Translate Skill            🟢 ████████████████████ 100%  (12/12)
Phase 8  Repo Clarification         🟢 ████████████████████ 100%  (11/11)
TOTAL                                  ████████████████████ 100%  (106/106)
```

**Current Phase:** — (all phases done)
**Blocked By:** —
**Next Milestone:** Roadmap closure — move to `completed/`

---

## Why This Roadmap Exists

The repository was built to turn Markdown into PDFs. It now also produces
EPUBs, imports external PDFs, captures web pages, translates documents, and has
just been used to run a full multi-source investigation. Six jobs.

Its structure did not follow. Everything executable sits in a flat `lib/`
because `lib/` was there when each capability landed; everything testable sits
in a flat `tests/` under French names; and the whole thing is described by two
skills — `pdf`, vendored from upstream and generic, and `pdf-doc`, whose
description has to spend four lines telling the reader when *not* to use it.

Two consequences, both felt:

- **The prose no longer fits the skills.** `pdf-doc` carries PDF authoring, the
  art direction, the EPUB output with its inverted review rule, PDF import and
  web capture. A skill that describes five jobs describes none of them well,
  and the rules of each keep leaking into `claude.md` and `README.md`, where
  they drift.
- **The repository is written in French, which is a choice that now costs.**
  Identifiers, comments, test names, CLI messages, documentation. `library/` is
  user content and stays in whatever language its author chose; everything else
  moves to English.

This roadmap does both at once, because doing either alone means touching every
file twice. It ends with a repository where each root directory has a stated
reason to exist, each skill covers one context and carries its own scripts,
tests and assets, and `CLAUDE.md` describes what is actually there.

---

## Decisions Taken At Opening

**Five skills, one per context.** `pdf`, `epub`, `translate`, `fetch`,
`sourcing`. `lib/` keeps only what two or more skills share, or what is used
outside every skill.

**Importing a PDF is sorted by destination, not by format.** The same file can
be read to be rebuilt as a document — that is `pdf`, and it ends in an
`index.md` under `library/` — or read as a piece of evidence, to find a term,
detect a page with no text layer, render and crop a schematic — that is
`sourcing`, and it produces no document. The shared machinery, rendering and
cropping and contact sheets, belongs to the core precisely because both use it.
If the boundary leaks in practice, a sixth `import` skill is split out; that is
recorded as available, not taken.

**The `pdf` skill is forked and becomes ours.** `pdf-doc` is absorbed into it.
From the vendored upstream content, what has actually served here — merge,
split, extract, render to images — is kept as a reference file; form filling,
encryption and OCR go, along with their scripts. The rule *never modify the
provided skills* is then restated for `diagram-design` alone, which really is
replaced on every update.

**English first, then move.** One pure translation pass over the code, the
harness and the tests, with the suite green at the end; then pure movement into
the skills. Two diffs, each reviewable on its own, and `git log --follow` keeps
resolving. The documents that are rewritten rather than translated —
`README.md`, `claude.md`, `pdf-doc` — are skipped by the translation pass and
written directly in English in their own phase.

**Local translation is prepared, not built.** Phase 7 defines the engine
contract and wires the engine that exists today. The local models get their own
roadmap.

**The raw material lives with the roadmap that consumes it.** The investigation
inventory and the translation notes moved out of a root `pending/` directory and
into `sources/` here. Their lifecycle is the roadmap's: needed until Phase 7
closes, then archive — and they reach `completed/` alongside the phases that
distilled them, without a root directory ever having to be justified or emptied.
Phases 6 and 7 mark that archive superseded rather than delete it.

---

## Deliberately Out Of Scope

- **`library/`.** User content, at whatever depth and in whatever language its
  author chose. Nothing here translates it, moves it, or imposes a convention
  on it.
- **Implementing local translation.** No model downloaded, no inference code,
  no GPU dependency added to `requirements.txt`. Phase 7 builds the seam and
  opens the roadmap that fills it.
- **`diagram-design`.** Installed as a plugin outside the repository, reached
  through the `.diagram-design` marker and the profile written by
  `brand/sync.py`. Never modified, before or after this roadmap.
- **New capability of any kind.** This is a restructuring. Every phase ends
  with the same outputs it started with — the style guide builds identically in
  both formats — and anything that would need a new test to be trusted is a
  different roadmap.
- **The art direction itself.** `brand/tokens.yaml` and the theme cascade are
  moved and documented, not redesigned.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [Target Architecture](phase-0-target-architecture.md) | 9 | 🟢 Done |
| 1 | [English Pass](phase-1-english-pass.md) | 12 | 🟢 Done |
| 2 | [Skill Layout and Shared Core](phase-2-skill-layout.md) | 10 | 🟢 Done |
| 3 | [The `pdf` Skill](phase-3-pdf-skill.md) | 13 | 🟢 Done |
| 4 | [The `epub` Skill](phase-4-epub-skill.md) | 11 | 🟢 Done |
| 5 | [The `fetch` Skill](phase-5-fetch-skill.md) | 11 | 🟢 Done |
| 6 | [The `sourcing` Skill](phase-6-sourcing-skill.md) | 17 | 🟢 Done |
| 7 | [The `translate` Skill](phase-7-translate-skill.md) | 12 | 🟢 Done |
| 8 | [Repo Clarification and Documentation Rewrite](phase-8-repo-clarification.md) | 11 | 🟢 Done |

The order is not arbitrary. Phase 0 decides the destinations so the moves are
cheap; Phase 1 translates so the moves are pure; Phase 2 builds the container
and proves it on one module so four phases do not each discover the same
plumbing. Phases 3 to 7 each fill one slot, `fetch` before `sourcing` because
the second builds on the first. Phase 8 writes down what exists.

---

## Dependencies

- **`diagram-design`**, installed as a plugin outside the repository. The
  profile it reads is written by `brand/sync.py` and selected by the
  `.diagram-design` marker at the root. Neither the plugin nor that mechanism
  changes here, but Phase 2 must not break the marker when the layout moves.
- **Documents under `library/` kept out of the repository.** Part of the test
  suite reads them. On a fresh clone those tests fail for want of files, not
  for want of an assertion, so `make test` there exercises only a subset.
  Verification passes run on the working clone.
- **`epubcheck`**, used by the EPUB checks on every `make epub`.
- **Playwright**, optional, for capturing client-rendered pages. Not installed
  by default, and the `RENDER=1` path must keep saying so.

---

## Related Documentation

The raw material this roadmap distils travels with it, under `sources/` in this
folder. The three paths below are relative to the roadmap's own directory.

- `sources/sourcing/outillage-sourcing.md` — the inventory of a real
  investigation, and the source material for Phase 6.
- `sources/sourcing/scripts-sourcing/` — thirteen scripts exactly as they ran,
  uncleaned on purpose.
- `sources/translation/index.md` — the local-translation notes, and the source
  material for Phase 7.

Elsewhere in the repository:

- [`docs/architecture.md`](../../../architecture.md) — the target architecture,
  written by Phase 0.
- `.claude/skills/pdf/SKILL.md` — the authoring convention, into which Phase 3
  absorbed the former `pdf-doc` skill.

---

## Metadata

**Roadmap Status:** 🟡 In Progress
**Location:** `docs/roadmap/on-progress/repo-overhaul/`
**Version:** 1.9.0
**Created:** 2026-09-12
**Last Updated:** 2026-09-17

---

## Changelog

### 1.9.0 (2026-09-17)

Phase 8 closed, eleven tasks, all eleven acceptance criteria met — three with a
qualification recorded in the phase file. Every phase is now done; the roadmap
itself is not yet closed.

Every root directory is justified. `lib/`, a leftover `__pycache__/`, was
deleted. **`templates/` moved into `.claude/skills/pdf/assets/templates/`,
revising Phase 0**: its argument held for the preset, not for the seed, which
only `new.py` reads. `conftest.py` joined the tree in `docs/architecture.md`,
and `.gitignore` now ignores `.claude/settings.local.json` itself.

`claude.md` became `CLAUDE.md`, rewritten in English at half its length: a
table routing each intent to its skill, the repo map, the commands, and only
the three rules no skill owns. `README.md` was rewritten in English around the
five skills. The documentation test now reads the skills and core modules from
disk and fails when a document leaves one out.

**The project was renamed `scriptorium`** — package, `diagram-design` profile,
titles. The EPUB identifier namespace keeps the old name on purpose, so no book
changes identity on an e-reader.

**Phase 1 had missed French in `requirements.txt` and `brand/tokens.yaml`**;
both translated, the YAML's data verified identical. One stale path fixed in
the architecture (§7, `conftest.py`), and `fetch` and `sourcing` now name the
neighbouring skill they exclude.

The closing pass — `make setup`, `test` (349), `build`, `epub`,
`preview-style` — passed on the working clone, and the style guide was reviewed
page by page in both PDF themes and both EPUB style sheets.


### 1.8.0 (2026-09-16)

Phase 7 closed, twelve tasks, all ten acceptance criteria met. One task carries
a qualification recorded in the phase file: the two-engine cross-check is built
and tested with a stand-in engine, never run with two real ones, since the
second does not exist yet.

The `translate` skill holds the contract and the agent engine. Five scripts —
`zones.py`, `chunking.py`, `engines.py`, `qc.py`, `translate.py` — and 79 tests;
the suite went 268 → 348. The agent engine runs *through* the `Engine`
interface: its answers go through request and answer files, and are validated,
stored and checked exactly as a model's would be.

**A real run on a throwaway copy of a document found two defects** the
synthetic tests had missed: a heading stranded at the end of a chunk, cut from
its section, and a re-`prepare` that kept answers whose chunk text had changed.
Both fixed and tested.

**The import procedure had its order backwards.** The `pdf` skill translated
and restored the structure in one pass; the structure is now restored first, so
an engine is never handed material it will mangle. `fetch` now records the
page's `source_language` in `sources/meta.json`, as the import already did, so
the language is stated once.

`docs/local-translation.md` records the two target engines, their figures
marked unverified. `docs/roadmap/pending/local-translation/` opens with three
phases and 18 tasks; its opening questions were answered from this phase's
decisions rather than asked, and its changelog says so. `sources/translation/`
is marked superseded, every point mapped to its home.

Phase 8 opened.


### 1.7.0 (2026-09-16)

Phase 6 closed, seventeen tasks, all nine acceptance criteria met.

The `sourcing` skill turns the Electribe 2 investigation into a method and ten
tools. `SKILL.md` carries the three-status journal, the three levels never
mixed, and the four rules. `references/access-map.md` is the dated map of
closed and open doors, marked as maintained. The ten tools in `scripts/` share
one helper holding the two invariants: absolute paths, and a loud failure on an
empty result or on a batch of identical sizes. Under them, `core/imaging.py`
gained `crop()` and `contact_sheet()`, and `core/pdfpage.py` gained
`render_page()` and `text()`. The suite went 158 → 268, all offline, against
the root conftest's local server, which gained computed routes and a shutdown
twenty-five times faster.

**Live runs found three defects local tests could not.** The CDX index answered
503 mid-batch and sank it, and a single refused URL did too; `get` saved pages
with the archive's toolbar at their head. All three are fixed and tested.

**Two premises were corrected rather than obeyed.** `docs/architecture.md` said
`sourcing` writes nothing under `library/`, but the investigation it comes from
lives in a document's `sources/`: the rule now forbids writing a document, not
a directory. And the contact-sheet brick was said to exist twice; neither
supposed owner is a grid, so the grid is new, and it sits in the core as the
architecture's table had decided. The mirror chain stays in the skill, reversing
the 1.6.0 expectation, because it has one caller.

`sources/sourcing/` is marked superseded, in French, and every one of its
lessons is mapped to its new home in the phase notes.

Phase 7 opened.


### 1.6.0 (2026-09-13)

Phase 5 closed, eleven tasks, all eight acceptance criteria met.

The `fetch` skill holds web capture, and the capture now fails out loud.
`fetch.py` moved into `.claude/skills/fetch/scripts/`. A new `core/net.py`
carries what `sourcing` will share with it: the probe line, the MIME type read
from the bytes, a browser user agent, and a fallback to an unverified connection
when a certificate fails, which is reported rather than hidden. Before writing
any file, the capture now refuses an HTTP error, a real PDF (pointing to
`make import`), a `.pdf` URL answering HTML, any non-page, and an extraction
with no text.

**A suite written rather than moved.** `fetch.py` had no tests. This phase wrote
32, test-first, against a real local HTTP and HTTPS server added to the root
conftest, where Phase 6 can reuse it. They found two defects beyond the task
list: `page.html.gz` was a UTF-8 re-encoding rather than the received bytes, and
the sniff missed HTML behind a byte-order mark or a comment. The suite went
126 → 158.

**Verified on the live web as well:** a Wikipedia article captured, built and
reviewed; `expired.badssl.com` captured and flagged; an arXiv PDF, a 404 and a
403 refused. The review met the `lang:`-blind quotation marks Phase 1 recorded,
on real content.

Left to Phase 6 on purpose: the batch-size check and the mirror chain, both of
which need a batch to act on.

Phase 6 opened.


### 1.5.0 (2026-09-13)

Phase 4 closed, eleven tasks, all eight acceptance criteria met. One task was
amended rather than ticked as written.

The `epub` skill holds the reflowable chain. `epub.py` and `check.py` moved into
`.claude/skills/epub/scripts/` beside `preview.py`, and ten test files moved
into its `tests/`, so the skill carries 104 of the suite's 126 tests.
`theme/epub.css` stays in `theme/`, per Phase 0. `core/` is down to `doc`,
`mdext`, `imaging` and `pdfpage`, plus `fetch` until Phase 5. The skill's prose
gathers the EPUB rules from `claude.md`, `README.md` and the stub, and adds
three that lived only in the code: `theme:` does not apply to the EPUB, a
document's `theme.css` follows it in, and the checks' actual thresholds.

**Verified on bytes, not pixels.** The EPUB and its review sheets turned out to
be byte-reproducible across builds, so all eighteen output files were hashed
before the move and compared after: no difference.

**One task rested on a false premise.** "Keep the SVG rasterisation brick shared
with `pdf`" assumed `pdf` rasterises. It inlines SVG instead. The shared brick
is `core/pdfpage.py`, underneath the rasterisation, and it stayed in the core.

Found and recorded, not fixed: the contact sheet can strand an object's label at
the bottom of one screen with its figure on the next. And `epubcheck` is not
installed here, so EPUB 3 conformance went unverified in this phase, which
`make epub` states.

Phase 5 opened.


### 1.4.0 (2026-09-13)

Phase 3 closed, thirteen tasks, all eight acceptance criteria met — two of them
with a qualification recorded in the phase file rather than a silent reading.

One `pdf` skill, in English, now covers writing, building, reviewing and
importing a document. `pdf-doc` is gone. `build.py`, `new.py` and `ingest.py`
live in `.claude/skills/pdf/scripts/` and take `ROOT` from `core.doc`, because
`parent.parent` would have pointed inside the skill once they moved. The `make`
targets kept their names. The "never modify the provided skills" rule now names
`diagram-design` alone. The style guide's ten pages are pixel-identical to the
pre-phase baseline, and the suite went 124 → 126.

**The upstream licence decided the "absorb" task.** It forbids derivative works,
so no upstream prose could be adapted. `references/manipulation.md` is written
from scratch, every recipe run before commit, and every upstream file —
`LICENSE.txt` included — is removed. Nothing is kept, so nothing needs
attribution.

**`pdf-doc` held three other skills' prose** — the EPUB section, the web
capture and the translation steps. They were carried into the `epub`, `fetch`
and `translate` stubs rather than lost before Phases 4, 5 and 7 exist to
receive them.

Found and left alone: the style guide under `library/` is stale — it still
names `pdfs/`, holds a hex value in its override example and shows a footer the
invent-nothing rule would not produce. Out of scope; flagged for its author.

Phase 4 opened.


### 1.3.0 (2026-09-13)

Phase 2 closed, ten tasks. Seven of the eight acceptance criteria met; the
eighth is deferred by an amendment the phase makes visible rather than silently
reinterpreting.

**The roadmap contradicted itself and the user settled it.** Phase 2 asked both
to move *one* module as proof and to *reduce `lib/` to the shared core*, while
Phases 3 to 7 each said "move `lib/<module>`". The resolution: `lib/` is renamed
to `core/` **whole**, so every module is importable as `core.<name>` from the
first commit and no skill ever needs a transitional path; Phases 3 to 7 then
take theirs out, and the reduction completes when Phase 7 closes. Supersedes
the name `doclib` recorded under 1.2.0 — the package is `core`, because that is
the phrase `docs/architecture.md` already uses for it, and because a package
named `core` holding `build.py` is uncomfortable to read, which keeps the
unfinished move visible.

The mechanism needed **two** conftests, not the one the phase anticipated. A
skill's tests cannot import their own scripts (pytest puts the *test* file's
directory on `sys.path`), and they could not see the `repo` fixture either,
which lived under `tests/`. So: a local conftest per skill for its `scripts/`
path, and a second at the repository root for the fixtures every suite shares.
`testpaths` in `pyproject.toml` makes `make test` a bare `pytest -q` reporting
one result — 124 tests, 117 from the repository and 7 from the `epub` skill.

The render brick was held **three** times in code, not twice: `rasterize_svg`,
`render_cover` and `render_screens` each computed their own scale factor from
`get_width()`. All three now call `core/pdfpage.py`, and `pypdfium2` is imported
in exactly one module.

And a near miss worth the record: rewriting a file with
`io.open(p, "w").write(io.open(p).read()…)` empties it, and the suite fell from
124 to 123 **without a failure** — a deleted test does not fail. Caught by
diffing collected-test counts, not by a red run.

Phase 3 opened.


### 1.2.0 (2026-09-13)

Phase 1 closed, twelve tasks, all six acceptance criteria met. The code, the
harness and the tests are in English; `library/`, `README.md` and `claude.md`
are untouched, as the phase scoped them.

Verified against a detached worktree at the phase-0 closure commit, with the
working tree's uncommitted `icon-item` fix transplanted onto it so the diff
isolates this phase: the style guide's two PDFs are pixel-identical and its
EPUB is byte-identical. `make test` green at every one of the twelve commits.

Four findings recorded in the phase notes, three of which change later phases.
**PDFs are not byte-reproducible** — a timestamp inside the embedded font
subset — so the phase's own "byte-comparable" objective was wrong and the
verification is on rendered pixels; comparing bytes would have reported a
difference on every task. **An accent-based grep is not a French detector**:
`theme/code.css` held two French lines with no accented character, and a lexical
sweep over the function words was needed to close the criterion honestly.
**Three comments named the wrong file** — `lib/build.py` for `ADMONITION_ROLE`,
the `li.icon-item` marking and the icon colour substitution, all three of which
live in `lib/doc.py`; they were corrected rather than translated, since writing
a known falsehood in English is worse than leaving it in French.

And one capability the phase repeatedly ran into without building: **neither
output localises on `lang:`**. A document gets a French `Sommaire`, French
quotation marks from `smarty`, and now an English letter template whatever its
language. Nine strings across `build.py`, `epub.py`, `doc.py` and
`templates/letter/` are held hostage to it. It belongs to a roadmap of its own,
and the notes say so in the three places it surfaced.

Phase 2 opened.


### 1.1.0 (2026-09-12)

Phase 0 closed, nine tasks, all seven acceptance criteria met.
`docs/architecture.md` created: the target tree with a stated reason per root
directory, the core/skill rule with nine borderline cases resolved by name, the
three boundaries stated as questions applicable to a case not yet encountered,
the inside of a skill, the fate of `make`, and the glossary.

Four decisions the later phases were waiting on. The import mechanism is an
installable package — `lib/` becomes `doclib`, `pip install -e .` in
`make setup` — chosen because it is the only option that also works when a
script is run by hand, which the ten `sourcing` tools are designed to invite.
`templates/`, `theme/` and `brand/` all stay at the root under one rule: the
document's substance stays at the root, the skills own the transformation —
which settles Phase 4's open question, `theme/epub.css` stays in `theme/`. The
glossary fixes `library/<topic>/<slug>` so `theme:` keeps the light/dark sense
alone, and settles "planche" as **contact sheet** and **style proof**,
superseding the "plate" this roadmap's own prose uses in places. `make` keeps
all sixteen targets and gains none.

Three findings recorded in the phase notes rather than acted on. `theme/` is
indivisible for a mechanical reason, not the one assumed at opening:
`doc.PRESETS` derives the preset registry from the directory's listing, so the
core already knows `epub.css` by name — and `theme/epub.css` is a self-contained
sheet, not a concatenation of the paginated ones. `fetch.py` and `ingest.py`
have no tests at all, 939 lines between them, so Phase 5 writes a suite rather
than moving one and `pdf` starts with an empty `tests/`. And `.pytest_cache/` is
absent from `.gitignore`, which goes unnoticed only while it appears at the root
alone.

Phase 1 opened. The roadmap moved from `pending/` to `on-progress/`.


### 1.0.1 (2026-09-12)

The raw material moved from the root `pending/` directory into `sources/` inside
this roadmap: `sources/sourcing/` (the investigation inventory and its thirteen
scripts) and `sources/translation/` (the local-translation notes). It had never
been committed and existed only in one working tree, while two of the nine
phases depend on it.

Three consequences in the phase files, no task added or removed and therefore no
total to recompute: Phases 6 and 7 now check that every lesson has found a home
and mark the archive superseded, rather than retiring a directory; Phase 8 now
checks that no scratch directory survives at the root, which the move already
settles.

### 1.0.0 (2026-09-12)

Roadmap created, nine phases, 106 tasks. The work splits into a design phase
that writes the target architecture, a translation pass that puts the code and
the harness into English, a phase that builds and proves the skill layout, five
phases that each fill one skill — `pdf`, `epub`, `fetch`, `sourcing`,
`translate` — and a closing phase that justifies every root directory and
rewrites `CLAUDE.md` and `README.md` against what was built.

Four decisions taken at opening: five skills rather than six, with the PDF
import sorted by destination rather than by format; the `pdf` skill forked from
upstream and merged with `pdf-doc`; English before movement, in two separate
passes; and local translation prepared through an engine seam but implemented
in a roadmap of its own.

The repository contract was written into `claude.md` at the same time — roots
under `docs/roadmap/`, roadmaps in English, `make test` as the check, git as
the versioning.
