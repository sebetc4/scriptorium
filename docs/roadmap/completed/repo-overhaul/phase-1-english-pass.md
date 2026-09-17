# Phase 1: English Pass

---

## Status

**Current Status:** 🟢 Done (100% — 12/12)
**Started:** 2026-09-12
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

The glossary written in Phase 0 is normative here. Translate to it, not around
it.

---

## Objective

Turn the code, the harness and the tests into English, in place. Not one file
changes directory, not one function changes behaviour. At the end of this
phase `make test` is green, the built PDFs and EPUBs are byte-comparable, and
nothing in the repository outside `library/` and the documentation is still in
French.

---

## Overview

### Why This Phase Matters

Translating and moving in the same commit produces a diff where a rename and a
rewrite are indistinguishable, and `git log --follow` loses the file. Splitting
them costs one extra pass over each file and buys a reviewable history: this
phase's diff is pure text, the next one's is pure movement.

It also front-loads the only part of the work that is mechanical. Once the code
is in English, the restructuring phases can be judged on structure alone.

### What It Enables

Phase 2 onwards move English files. Every skill written from Phase 3 on quotes
English identifiers and English messages, so the prose and the code agree
without a translation step in the middle.

### Out of Scope

- `library/` — user content. Whatever language its author wrote it in, it stays.
- `README.md`, `claude.md`, `.claude/skills/pdf-doc/SKILL.md` — these are
  **rewritten**, not translated. `pdf-doc` is absorbed in Phase 3 and written
  directly in English; the two root documents are rewritten in Phase 8 against
  the final architecture. Translating them now would be work thrown away twice.
- Target names in the `Makefile` (`build`, `epub`, `new`, `import`, `fetch`…)
  are already English and are muscle memory. They do not change here, and the
  ones that do change, change in their own skill's phase.
- Any behaviour change. If a translated message reads badly because the
  behaviour is odd, note it — do not fix it here.

---

## Tasks

### The shared modules
- [x] `lib/doc.py` and `lib/mdext.py` — comments, docstrings, and every string the user can see
- [x] `lib/build.py` and `lib/new.py`
- [x] `lib/epub.py` — the largest file, 71 comment lines, worth its own pass
- [x] `lib/check.py` and `lib/preview.py`
- [x] `lib/ingest.py`
- [x] `lib/fetch.py` and `lib/imaging.py`

### The harness
- [x] `brand/sync.py` and `brand/icons.py`
- [x] `Makefile` — the `help` text and the comments; target names stay as they are
- [x] `theme/*.css` comments and the four `templates/*/index.md`

### The suite
- [x] Rename the fifteen test files to English, one `git mv` per file so the history follows
- [x] Translate the test function names and docstrings; leave `test_documentation.py` asserting on the French documents, which are still French until Phase 8
- [x] Full verification pass: `make test`, then build and diff the style guide in PDF and EPUB against its pre-phase output

---

## Technical Details

### Files to Modify

```
lib/*.py                 10 modules, ~2900 lines
brand/sync.py
brand/icons.py
Makefile
theme/*.css
templates/*/index.md
tests/*.py               15 files, renamed and translated
```

### Dependencies

The Phase 0 glossary. Without it, three modules will each coin their own word
for the same thing.

### Constraints

- `make test` stays green at every commit, not only at the end of the phase.
- Part of the suite reads documents from `library/` that are deliberately kept
  out of the repository. On a fresh clone those tests fail for want of files,
  not for want of an assertion. Run the verification on the working clone,
  where they do run.
- `tests/test_documentation.py` asserts on French strings in `claude.md`
  (`"ne reflue pas"`) and on the `lib/` module map. Those assertions stay
  French and stay pointed at `lib/` until Phase 8 rewrites both sides at once.
- User-facing CLI messages are in scope. `make new` telling the user
  `« document créé »` is exactly the kind of French this phase removes.

---

## Acceptance Criteria

- [x] No French remains in `lib/`, `brand/`, `theme/`, `templates/`, `tests/` or the `Makefile` — comment, docstring, identifier or printed string
- [x] The fifteen test files carry English names and English test function names
- [x] `make test` is green
- [x] The style guide builds to PDF and EPUB with no visible difference from before the phase
- [x] `git log --follow` resolves on every renamed test file
- [x] Every term used is the term the Phase 0 glossary chose

---

## Notes

### The verification method, settled on the first task

Phase 1's objective says the built PDFs and EPUBs are "byte-comparable" after
the pass. **For PDFs that is not true, and it was not true before this phase
either.** Two builds of the same unchanged source produce different bytes —
69078 and 69074 on the style guide. The difference sits inside an embedded font
subset's FlateDecode stream, whose uncompressed length is identical: an
OpenType `head` table carries a timestamp, so the subset differs run to run.

The EPUB *is* byte-reproducible, and a test already asserts it
(`test_larchive_est_reproductible`).

So the verification for every task in this phase is:

- **EPUB** — compare the archive's SHA-256 before and after. It must be equal.
- **PDF** — render every page with `pypdfium2` and compare the pixel buffers,
  not the file. On `doc.py` and `mdext.py` this gave identical pixels across all
  ten pages of the style guide, light and dark.

Comparing PDF bytes would report a difference on every single task and teach
the reader to ignore the check.

### Task 1 — `doc.py` and `mdext.py`

32 blocks in `doc.py`, 4 in `mdext.py`, each replaced against a verified unique
occurrence so the code itself could not be touched. No test asserts on any
message these modules emit, which is what made the CLI strings safe to
translate.

One behaviour oddity noted and **not** fixed, per this phase's out-of-scope
rule: `MD_CONFIG["smarty"]` hard-codes French quotation marks (`« »`) for every
document, whatever its `lang:`. An English document therefore gets French
quotes. It is a behaviour change, so it belongs to `pdf`'s phase or a roadmap of
its own, not here.

---

### Task 2 — `build.py` and `new.py`, and the five strings that must stay French

`build.py` and `epub.py` between them hold **five hard-coded French strings that
are rendered into the document**, not printed to a terminal:

| Location | String | Rendered as |
|---|---|---|
| `build.py:63` | `Auteur` | a cover footer label |
| `build.py:65` | `Date` | a cover footer label |
| `build.py:160` | `Sommaire` | the PDF table-of-contents heading |
| `epub.py:493` | `Sommaire` | the navigation document's `<title>` |
| `epub.py:496` | `Sommaire` | the navigation document's `<h1>` |

**They are not translated, and this phase must not translate them.** They are
the document's own content, and the document's language is `lang:` in its front
matter — not the language the codebase is written in. Translating them would
change every built PDF and EPUB, which this phase's own constraint forbids and
its acceptance criterion ("no visible difference") would catch.

This puts two of the phase's own statements in tension: "no French remains in
`lib/` — comment, docstring, identifier or **printed string**" against "any
behaviour change […] note it, do not fix it here". The second wins, because the
first was written about the language of the code and these five strings are
output localisation.

What they actually reveal is a missing capability: **the paginated and
reflowable outputs have no localisation keyed on `lang:`.** A document with
`lang: en` gets a French `Sommaire` today, exactly as it gets French quotation
marks (task 1's note). That is one feature, not two, and it belongs to a roadmap
of its own — recorded here so Phase 8 does not read the leftover French as an
oversight.

`new.py`'s `{{AUTHOR}}` placeholder *was* translated — `Prénom Nom` → `First
Last` — because it seeds a new document from `templates/`, which task 9 of this
same phase translates. Leaving it French would seed English templates with a
French author line.

The `slugify` diacritic-folding table in `new.py` stays as it is: those accented
characters are data, not prose.

---

### Task 3 — `epub.py`, and the tests that pin the messages

48 prose blocks, then 36 French local identifiers renamed — `chapitres`,
`bornes`, `entetes`, `cellules`, `niveau`, `echecs` and the rest. The
acceptance criterion names identifiers explicitly, and this is the file that
had them; `doc.py` and `build.py` had none.

**Three tests broke, and the lesson generalises to every remaining task.** The
suite pins user-facing strings:

| Test | Pinned |
|---|---|
| `test_couverture.py::test_le_titre_domine_la_composition` | `--titre: 132px` |
| `test_controles.py::test_epubcheck_avec_messages…` | `epubcheck : …` (French spacing before the colon) |
| `test_controles.py::test_epubcheck_absent…` | `epubcheck absent` |

The first two were invisible to a search for the usual assertion shapes
(`pytest.raises`, `match=`), because they are plain `in` and `.count()` on
captured output. **From here on, a module's translation and the assertions that
pin its messages land in the same commit** — the phase requires the suite green
at every commit, not only at the end.

A search that would have found them: `grep -n 'assert.*"[^"]*[a-z] : ' tests/`
catches the French space-before-colon, which is the tell.

### Two renames worth recording

- `--titre` → `--title-size`, a CSS custom property inside the cover template
  string. Renaming a property inside a generated stylesheet is only safe when
  every occurrence moves together, so it was done before the word-boundary
  renames rather than by them.
- `Ko` → `kB` in the size report. It is a unit shown to the user, not document
  content, so it belongs to this pass.

The EPUB came out **byte-identical**, which also proves the cover PNG is
pixel-identical, since it lives inside the archive.

---

### Task 4 — `check.py` and `preview.py`, and where the glossary bites

47 prose blocks and 15 identifier renames. The grep recorded in task 3's note
found the one assertion that pinned a message —
`test_controles.py` on `"hors manifeste"` — before the translation rather than
after it, which is the whole point of writing it down.

Two decisions the glossary forced, both of which change something other than a
comment:

- **The contact sheet's files are now `contact-NN.png`, not `planche-NN.png`.**
  The prefix is a filename written to disk. Nothing pins it — not a test, not
  the `Makefile`, not `claude.md` — and the artefacts live under `out/preview/`,
  which is gitignored and regenerated by `make preview`. Renaming it is what the
  glossary decides; leaving it would have left the repository's most-used review
  artefact carrying the word the glossary retired.
- **The label rendered onto the sheet is `object N / M`, not `objet N / M`.**
  This is text rendered into an image, so it deserved the distinction: a contact
  sheet is *tool chrome*, not document content. The document's own text — figure
  captions, diagram labels — stays French on the same image, which is the
  correct outcome and was verified by looking at the sheet rather than assuming
  it.

That line is where the rule from task 2 becomes usable: **a string is document
content if it would be wrong in a language other than the document's; it is tool
output if it would be wrong in a language other than the repository's.**
`Sommaire` on a PDF is the first. `object 3 / 4` on a review sheet is the second.

---

### Task 5 — `ingest.py`, and two strings written *into* a document

41 blocks. No test touches this module, so the only verification available was a
real import, run end to end on a built PDF: 5 pages, 59 blocks, the heading
levels detected, the vector pages reported.

Two strings the tool writes into the `index.md` it produces, both translated,
and the reasoning is the task-4 rule applied to a harder case:

- **The `<!-- IMPORTED, NOT TRANSLATED … -->` note block.** It addresses whoever
  translates the document, in the repository's voice, and it is deleted during
  translation. Tool output.
- **`"Figure — to be captioned"`,** the caption placeholder on every imported
  image. Same status as `new.py`'s `{{AUTHOR}}` placeholder in task 2: a
  placeholder the operator replaces. If it survives to the built PDF, that is a
  defect either way — its language does not change that.

The contrast with `Sommaire` holds: `Sommaire` is generated on **every** build
and is meant to stay; these two are generated **once** and are meant to go.

---

### Task 6 — `fetch.py` and `imaging.py`

37 blocks. Like `ingest.py`, neither module has a test, so the verification was
the CLI itself: `--help`, and the scheme refusal on an `ftp://` URL.

One thing worth knowing before Phase 5 reads this file: **two values written
into `sources/meta.json` changed language** — `"mode"` is now `browser` /
`static` rather than `navigateur` / `statique`, and `"extraction"` is `precise` /
`wide` rather than `précis` / `large`. Nothing reads them back — checked across
`lib/`, `tests/` and the `Makefile` — so this breaks nothing, but the documents
captured before today keep the French values in their provenance file. They are
a record of what happened at capture time, so they are not rewritten.

The `slugify` diacritic-folding table stays, here as in `new.py` and
`ingest.py`. Three copies of the same fourteen-pair table, which Phase 2 should
notice: it is exactly the kind of thing the shared core exists for. Recorded,
not acted on — this phase does not move code.

---

### Task 7 — `brand/sync.py` and `brand/icons.py`, and a generated file

32 blocks. The wrinkle here is that `sync.py` does not only *have* comments, it
**writes** them: the header of `brand/tokens.css`, the `[data-theme="dark"]`
banner, the EPUB block's explanation. `tokens.css` is generated *and* versioned,
so translating the generator without running `make brand` would have left the
repository holding a French file no one could explain. The regeneration is in
the same commit; its diff is seven comment lines, nothing else.

The same applies outside the repository: the `notes:` line of the
`~/.diagram-design/profiles/pdf-creator.md` header is now English. The marker
file `.diagram-design` came out byte-identical, which is what Phase 2 needs to
stay true when the layout moves.

One string deliberately left French: `t["name"]` prints as
`art direction “Ma bibliothèque”`. It is the brand's own name, read from
`brand/tokens.yaml` — user data, like `library/`. The sentence around it is
English; the name is not the repository's to translate.

---

### Task 8 — the `Makefile`

Nine blocks. Target names are untouched, as the phase requires. The help text
is where the glossary becomes visible to the user: `DOC=theme/slug` is now
`DOC=topic/slug` on all seven targets that take it, `planche de contact` is
`contact sheet` and `planche de style` is `style proof`.

`test_documentation.py` parses this file — it splits on `help:`, takes
everything up to the first blank line, and requires `make <target>` to appear
there for every target except `help` and `check`. A translation that reflowed
the help block, or that put a real blank line inside it, would have broken that
test rather than a build. It still passes; the blank line in the help is an
`@echo ""` recipe line, not an empty source line.

---

### Task 9 — `theme/*.css` and the four templates, and three lies

65 comment blocks across eight stylesheets, plus the four templates. Three
things came out of it that a pure translation would have carried forward.

**An accent-based search is not a French detector.** `theme/code.css` held two
French lines with no accented character in them — *"Trois registres seulement :
ink (le code), soft (le commentaire)"* — and the `grep -P '[àâäéèê…]'` used on
every task before this one walked straight past them. A lexical sweep over the
function words (`le`, `la`, `des`, `qui`, `pour`, `dans`, `sans`, `deux`,
`chaque`…) was then run over **everything already translated**; it returned only
false positives — `sans-serif`, the PIL modes `LA`/`PA`, the English `plus`.
Both checks are needed, and the lexical one is the one that actually proves the
criterion.

**Three comments named the wrong file.** `theme/base.css` twice and
`lib/mdext.py` once pointed at `lib/build.py` for `ADMONITION_ROLE`, for the
`li.icon-item` marking and for the icon colour substitution. All three live in
`lib/doc.py` — presumably since `doc.py` was extracted as the shared upstream
half and the comments did not follow. They are corrected rather than translated:
writing a known falsehood in English is worse than leaving it in French, and a
stale cross-reference is not a behaviour change. Phase 2 would have hit all
three while splitting the core.

**The templates raise the localisation gap in its sharpest form.** Translating
them means a new document is seeded in English — and for `templates/letter/`
that is not placeholder text but French correspondence convention: *Madame,
Monsieur* / *Objet :* / *Cordialement* became *Dear Sir or Madam* / *Subject:* /
*Yours sincerely*. A user writing a French letter now has to undo that on every
`make new`. The task asks for it and it is done, but it is the same missing
capability as `Sommaire` (task 2) and the hard-coded French quotation marks
(task 1), and it is now the most visible of the three. **Whichever phase builds
output localisation should treat `templates/` as part of it.**

Verified by building all four presets from their translated templates, and by
comparing the style guide against the task-4 fingerprint: identical.

---

### Task 10 — the renames

Eleven `git mv`, not fifteen: `test_doc.py`, `test_documentation.py`,
`test_raster.py` and `test_xhtml.py` were already English and were left alone.
The task counts fifteen files; four of them needed nothing.

The names are the ones `docs/architecture.md` §7 assigns them, so Phases 2 and 4
move the files without renaming them again. Two read as generic while the suite
is still flat — `test_build.py` is the **EPUB** assembly suite, not the PDF
backbone's, and `test_checks.py` is the EPUB mechanical checks. Each says so in
its first line, and both land in `.claude/skills/epub/tests/` where the name is
exact. Renaming them twice to avoid three phases of ambiguity would have cost
`git log --follow` for no gain.

---

### Task 11 — the suite's contents, and the four French strings that stay

124 test names, every docstring and comment, and the French local variables
(`noms`, `corps`, `cible`, `sortie`, `valeurs`, `nuances`, `touches`…). Sample
data was translated too where it was arbitrary: `<h1>Un</h1>` became
`<h1>One</h1>`, `sans-image.epub` became `no-image.epub`, `fantome.xhtml`
became `ghost.xhtml`.

**Four French strings remain in `tests/`, all deliberately.**

| Location | String | Why it stays |
|---|---|---|
| `test_documentation.py:12` | `"ne reflue pas"` | asserts on `claude.md`, which stays French until Phase 8 — the phase says so explicitly |
| `test_package.py:7` | `"Les LED"` | the real title of `library/electronique/components/led` |
| `test_cover.py:9,21` | `"Les LED"`, its subtitle | the same document, mirrored as a fixture |

The last three are **user content quoted in a test**, not the repository's own
prose. `library/` is out of this roadmap's scope, and a fixture that stopped
naming the document it models would be worse, not better. Checked against the
document's front matter rather than assumed: it really does read
`title: Les LED` / `eyebrow: Fiche technique`.

Phase 8 removes the first one when it rewrites `CLAUDE.md`. The other three
stay for as long as that document does.

---

### Task 12 — the closing verification

The comparison the phase asks for, done properly: a detached worktree at
`1c100fc` — the phase-0 closure, the last commit before this phase — with the
working tree's uncommitted `icon-item` fix transplanted onto it, so the diff
isolates Phase 1 and nothing else.

| Artefact | Pre-phase | Post-phase |
|---|---|---|
| `guide-de-style.pdf` | 5p `c8bf9c643889` | 5p `c8bf9c643889` |
| `guide-de-style-dark.pdf` | 5p `8c0a4159862a` | 5p `8c0a4159862a` |
| `guide-de-style.epub` | `c028cf67c3e7` | `c028cf67c3e7` |

PDF compared on rendered pixels, EPUB on bytes, per the method settled on task
1. Then the whole harness: `make test` (124), `make build` over the library,
`make epub`, `make preview-style`, `make list`. And `git log --follow` resolves
past the rename on all eleven renamed files, three to seven commits deep.

---

### Where the French actually is

Measured at opening: the function names in `lib/` are already almost entirely
English (`build_cover`, `split_chapters`, `non_reflowing`, `rasterize_svg`).
The French is concentrated in four places — comments (~250 lines across the ten
modules), the `Makefile` help text, the test file and function names, and the
CLI messages. That makes the phase large but shallow.

Three test files carry French that is structural rather than cosmetic:
`test_jetons.py` (tokens), `test_planches.py` (plates), `test_paquet.py`
(package). Their names have to agree with the glossary, since the skills
written later will quote them.
