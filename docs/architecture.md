# Target Architecture

Written by Phase 0 of the [repo-overhaul roadmap](roadmap/completed/repo-overhaul/README.md),
before a single file moves. Its job is to make the eight phases that follow
mechanical: every one of them is a move, and a move is only cheap when the
destination is already decided.

Three questions, answered without ambiguity: what each root directory is for,
what earns a place in the shared core rather than in a skill, and where each
skill stops.

This document was written ahead of the tree it describes. Since Phase 8 it
describes the repository **as it is**; where a later phase revised an early
decision, the revision is recorded in place, in italics, rather than rewriting
the reasoning it replaced.

---

## 1. The target tree

Every root directory that exists today survives. One is renamed — `lib/`
becomes an importable package, because the skills that will hold the scripts
cannot reach it any other way (§6).

*Phase 8 revised this: `templates/` left the root for
`.claude/skills/pdf/assets/templates/`. Phase 0 kept it beside `theme/` on the
argument that a `report` feeds both outputs — but that holds for the preset,
which `theme/` carries, not for the seed. A seed is read once, by `new.py`, when
a document is created, and creating a document is `pdf`'s alone (§2). One
consumer, one skill.*

```
pyproject.toml          the package; installed editable by `make setup`
Makefile                the human facade — seventeen targets (§8)
requirements.txt        runtime dependencies
CLAUDE.md               repo map, commands, and the rules no skill owns
README.md               what the repository is, for a reader arriving cold
.diagram-design         marker selecting this repo's diagram-design profile
conftest.py             the fixtures every suite shares, the core's and the skills'

core/                   the shared core (§3)
brand/                  the single source of the art direction (§4)
theme/                  the CSS cascade, indivisible (§4)
library/                user content; a document's five directories are §11
tests/                  the core's suite and the repository-level suite (§7)
out/                    build artefacts, ignored by git
docs/                   this document, the roadmaps, the design notes
.claude/skills/         pdf · epub · fetch · sourcing · discussion · translate · session-review (§5)
.claude/agents/         pdf-reviewer
.claude/hooks/          guards and automations, declared in .claude/settings.json
```

Reason, directory by directory:

| Root | Why it exists |
|---|---|
| `core/` | What two or more skills need, or what something outside every skill needs. An installable package rather than a loose directory, so a skill's script and a hand-run tool resolve the same import. |
| `brand/` | The art direction's only source. `tokens.yaml` feeds the PDF cascade, the EPUB colour mapping and the `diagram-design` profile: three consumers, none of them a single skill. |
| `theme/` | The CSS cascade. Indivisible: `core/doc.py` derives the preset registry from this directory's listing. |
| `library/` | User content, at whatever depth and in whatever language its author chose. Nothing in *this* roadmap touched it; the `document-anatomy` roadmap declared what a document is made of, in §11, and moved the library into that shape. |
| `tests/` | The core's suite, plus the tests whose subject is the repository itself — its layout, its documentation, its `make` targets. Each skill's own suite lives inside the skill. |
| `out/` | Build artefacts, reconstructible by `make build` and `make epub`. Gitignored. |
| `docs/` | Prose about the repository: this document, the roadmaps under `docs/roadmap/`, and the design notes a roadmap hands over (`docs/local-translation.md`, Phase 7). |
| `.claude/skills/` | Seven skills, one per context. Each carries its own scripts, tests and assets. |
| `.claude/agents/` | Subagents a skill delegates to. `pdf-reviewer` holds the look at a built PDF — `make review`'s checks, sheets and zooms — so no page image enters the main conversation. |
| `.claude/hooks/` | What a skill states as a rule but memory would enforce badly: generated and immutable files, the venv's Python, `make brand` after `tokens.yaml`, a skill's suite after its scripts change. Declared in `.claude/settings.json`. |

Nothing is slated for removal. Two directories are generated and must not be
edited by hand: `brand/icons/` (`make icons`) and `brand/tokens.css`
(`make brand`). Two more are transient and gitignored: `.venv/`, `out/`.
Everything else that appears at the root is tool residue, gitignored and never
justified as a directory: `__pycache__/`, `.pytest_cache/`,
`scriptorium.egg-info/` (written by the editable install), `.superpowers/`.

*Phase 8: `lib/` is gone. Renamed to `core/` in Phase 2, it survived only as an
untracked `__pycache__/` and was deleted.*

No scratch or staging directory exists at the root. Raw material travels with
the roadmap that consumes it, under that roadmap's `sources/` — which is how it
reaches `completed/` alongside the phases that distilled it, without a root
directory ever having to be justified or emptied.

---

## 2. The rule that decides between the core and a skill

> **A thing is core if two or more skills need it, or if something outside every
> skill needs it. A thing belongs to a skill if it is the intent rather than the
> brick.**

The first clause is the test; the second is what stops the test from swallowing
everything. Rendering a PDF page to an image is a brick — three skills do it.
*Reading a PDF in order to rebuild it as a document* is an intent, and it
belongs to exactly one skill.

Applied to a case not yet encountered, the rule asks two questions in order:
who needs this, and is this the thing being asked for or the thing it is made
of?

### The borderline cases, resolved by name

Principles do not settle arguments; names do. These were the arguable ones.

| Case | Verdict | Why |
|---|---|---|
| Rendering a PDF page with `pypdfium2` | **core** — `core/pdfpage.py` | The PDF review loop, `ingest`, the EPUB contact sheet and two `sourcing` tools all do it. The repository currently owns it twice. |
| Building a contact sheet | **core** — `core/imaging.py` | Same brick, two owners today (`make preview` and the PDF review loop), and `sourcing` was about to become a third. *Phase 6: the grid of labelled thumbnails is `imaging.contact_sheet()`. `make preview` turned out not to be a grid — it renders through a six-inch window — so `sourcing` is the grid's one caller so far, and the core holds it by this table's decision.* |
| Fractional cropping | **core** — `core/imaging.py` | Written for `sourcing`, but it is the same operation the review loop needs to read a detail. |
| Probing a URL, verifying its MIME type | **core** — `core/net.py` | `fetch` and `sourcing`'s `fetch-checked` share it. The half that differs is what each does with the result. |
| Writing an extracted image | **core** — `core/imaging.py` | Already shared by PDF import and web capture. |
| Markdown extensions (`figures`, `icons`) | **core** — `core/mdext.py` | Consumed by `core/doc.py`, which is upstream of both output backbones. |
| Rasterising an SVG | **`epub`** | Only the reflowable backbone does it. The paginated one inlines SVG instead, so there is no second caller — one skill, not the core. |
| `brand/sync.py`, `brand/icons.py` | **root**, not a skill | Reached by `make brand` and `make icons`, and by `diagram-design` through the profile. Used outside every skill, so the second clause of the rule applies. |
| Creating a document from a template | **`pdf`** | An intent, not a brick. `epub` consumes the result but never creates one. |
| Checking that a converted body is well-formed XHTML | **core** — `core/doc.py` | *suite-and-review, phase 0.* The EPUB build refuses a chapter it could not package, and `make check-library` reports the same document before anyone builds it. Two callers, one of them outside every skill. |
| The style guide | **root** — `brand/style-guide/` | *suite-and-review, at the user's request.* The art direction's own document, beside `brand/tokens.yaml`, rather than an `exemples/` topic in a library the user organises. `core.doc.STYLE_GUIDE` names it; `doc.relative()` places it from the repository root, so its outputs go under `out/<kind>/brand/style-guide/`. |
| Checking the user's library | **core** — `core/library.py` | *suite-and-review, phase 0.* Reached by `make check-library`, outside every skill, and it checks what both backbones read. |
| The catalogue: manifests, ids, `sync`, `describe` | **core** — `core/catalogue.py` | *library-catalogue, phase 0.* `make` and several skills read the map, and `make check-library` checks it. Keeping it — naming, describing, cleaning up — is an intent, and goes to a skill. |

### The shared core

```
core/
  __init__.py
  doc.py        document discovery, front matter, Markdown → HTML, token map
  mdext.py      this repository's Markdown extensions (figures, icons)
  imaging.py    store() · crop() · contact_sheet()
  pdfpage.py    render every page or one · each page's text layer, empty when there is none
  net.py        probe · MIME verification · browser UA · relaxed TLS
  catalogue.py  the manifests · ids · sync · describe · the `id:` citations
  library.py    make check-library
```

The package is named `core` because that is the phrase this document already
uses for it, and the rule in §2 is written in those words: the code should read
like the rule that placed it. The usual objection to a generic top-level name
applies to a published library, not to an application with a repository-local
venv and an editable install — and the name was checked free of any collision
before being taken.

Two module names were avoided deliberately. Not `raster.py`: rasterisation
already means SVG-to-PNG in the EPUB backbone, and a module of that name would
read as its home. Not `http.py`: it shadows a standard-library module, which
works until it does not.

`net.py` exists as of Phase 5, and `sourcing` will be its second caller.
`fetch.py` already retrieves through it — the probe, the MIME type sniffed from the
bytes, the browser user agent, the relaxed-TLS fallback. The mirror chain is
**not** in it, and Phase 6 decided it stays out: its only caller is `sourcing`'s
`fetch_checked.py`, so by the rule above it belongs to that skill.

`pdfpage.py` exists as of Phase 2. It was the brick held **three** times in
code, not twice — `rasterize_svg`, `render_cover` and `render_screens` each
opened a PDF and computed their own scale factor from `get_width()` — plus a
fourth time in prose, in the PDF review loop. `pypdfium2` is now imported in
exactly one module.

**The package is filled before it is emptied.** Phase 2 renames `lib/` to
`core/` whole, so every module is importable as `core.<name>` from the first
commit and no skill ever needs a transitional path. Phases 3 to 7 then move
each module out into its skill, and `core/` is reduced to the list above only
when Phase 7 closes. Until then the name is deliberately a misnomer: a package
called `core` holding `build.py` is uncomfortable to read, which is the point —
it keeps the unfinished move visible where a neutral name would hide it.

---

## 3. Where each `lib/` module goes

Ten modules, ten named destinations.

| Today | Destination | Note |
|---|---|---|
| `lib/doc.py` | `core/doc.py` | Upstream of both backbones. Unchanged in substance. |
| `lib/mdext.py` | `core/mdext.py` | |
| `lib/imaging.py` | `core/imaging.py` | Gains `crop()` and `contact_sheet()`. |
| `lib/build.py` | `.claude/skills/pdf/scripts/build.py` | |
| `lib/new.py` | `.claude/skills/pdf/scripts/new.py` | |
| `lib/ingest.py` | `.claude/skills/pdf/scripts/ingest.py` | Import whose destination is a document. |
| `lib/epub.py` | `.claude/skills/epub/scripts/epub.py` | Keeps the SVG rasterisation. |
| `lib/check.py` | `.claude/skills/epub/scripts/check.py` | Must keep running on every `make epub`. |
| `lib/preview.py` | `.claude/skills/epub/scripts/preview.py` | Contact sheet and style proof. |
| `lib/fetch.py` | `.claude/skills/fetch/scripts/fetch.py` | Its probing half is extracted to `core/net.py` first. |

`brand/sync.py` and `brand/icons.py` stay where they are.

---

## 4. `theme/` and `brand/` — the document's look

One rule covers both:

> **The document's look stays at the root — `theme/` and `brand/`. The skills
> own the machinery that transforms it.**

A `report` document produces both a PDF and an EPUB from one source, so its
preset cannot belong to only one output. Two further mechanics settle `theme/`
and `brand/`:

- **`theme/` is indivisible because the core reads its listing.**
  `core/doc.py` derives the preset registry by globbing the directory and
  subtracting the four sheets that are not presets — `base`, `page`, `code`,
  `epub`. The core therefore already knows `epub.css` by name. Moving that sheet
  into the `epub` skill would have a core function globbing into a skill to
  learn what a preset is.

  This settles the question Phase 4 leaves open: **`theme/epub.css` stays in
  `theme/`.** It is a self-contained sheet, not a concatenation of the
  paginated ones — "flattening" in the EPUB backbone means resolving `var()`
  and dropping `@page`, not merging the PDF cascade.

- **`brand/` has three consumers, none of them a skill.** `tokens.yaml` feeds
  `tokens.css` (read by `theme/*.css`), the `[data-theme="epub"]` block (read by
  the EPUB flattening) and the `diagram-design` profile (read by a plugin
  outside the repository). A directory serving a plugin cannot live inside a
  skill.

The cost is stated rather than hidden: the skills are **less
self-contained than "each skill carries its own assets" suggests**. They carry
their scripts, their tests and the assets specific to their transformation.
They do not carry the document.

---

## 5. The seven skills, and where each one stops

### What each is for

| Skill | Its one context |
|---|---|
| `pdf` | Writing, building and reviewing a paginated document of this library — and rebuilding an external PDF as one. |
| `epub` | The reflowable output of a document of this library, and its review. |
| `fetch` | One web page, known by its URL, captured as a document of this library. |
| `sourcing` | A question established across several sources not known in advance. Produces knowledge, not a document. |
| `discussion` | A subject talked through with the user before its document exists, and resumed from its journal. Produces a journal and an outline, not a document. |
| `translate` | A document already in this library, translated in place. |
| `session-review` | A finished task, measured, and written to `reviews/`. Outside the production chain: it makes no document and changes no skill. |

### The boundaries that needed a rule

**`pdf` / `sourcing` — sorted by destination, not by format.** The same PDF file
is the subject of both skills, so the format cannot discriminate.

> **Does the operation end in a document under `library/`? → `pdf`.
> Does the PDF stay a source, the output being knowledge? → `sourcing`.**

Read to be rebuilt — text extracted, images carried over, pages rendered as a
proofreading aid, then translated and given the repository's art direction —
that is `pdf`. Read to be known — locate a term across a manual, detect the
pages with no text layer, render a page at high resolution and crop it to read
a silkscreen — that is `sourcing`.

The shared machinery is the same in both cases, which is exactly why it belongs
to the core (§2) rather than to either skill. Each skill owns its intent;
neither owns the brick.

*The escape hatch, recorded as available and not taken:* if in practice a
request keeps landing between the two, a sixth `import` skill is split out. The
signal to watch for is a request whose answer begins "it depends what you want
to do with it" more than once or twice.

**`fetch` / `sourcing` — sorted by how many sources, and whether they were
known.**

> **One URL, known in advance, whose content *becomes* the document → `fetch`.
> Several sources, unknown at the outset, cross-checked against each other,
> where the output is a journal and its pieces → `sourcing`.**

**`discussion` / `sourcing` — sorted by where the knowledge comes from.** Both
keep a journal in `study/`, both produce knowledge rather than a document, and
both separate what is established from what is only claimed.

> **The user's word and an agent's account, worked out in conversation →
> `discussion`. Sources outside the conversation, found and cross-checked →
> `sourcing`.**

A discussion never establishes a claim itself: when the document will state a
number, a date or a point two accounts disagree on, the claim is handed to
`sourcing`, and its result comes back to the discussion's journal as
established. *Added by the discussion-and-illustration roadmap, phase 0.*

And what each refuses, which is the part a reader actually needs:

| Skill | Refuses to |
|---|---|
| `fetch` | follow a link — one URL, one document; translate; reproduce the site's layout; assemble several pages |
| `sourcing` | write a document — an `index.md` — anywhere; present a search-engine excerpt as a primary source. *Its pieces may live in the `sources/` of the document the investigation feeds, as the Electribe 2 investigation's did (corrected by Phase 6).* |
| `discussion` | write `index.md`; establish a fact itself; infer what the user said from a pasted answer; keep a transcript; edit `sources/` |
| `pdf` | produce reflowable output; review an EPUB page by page; translate |
| `epub` | write or build the paginated document; be reviewed screen by screen |
| `translate` | import or capture; edit `study/extracted.md`, which is immutable |

### The trigger check

A skill that fires on a neighbour's job is worse than no skill. Each
description must carry one discriminating phrase that no other carries:

| Skill | What triggers it | What must *not* trigger it |
|---|---|---|
| `pdf` | write / build / review / fix a document; a preset; the art direction; import a PDF **into the library** | an EPUB; a PDF read as evidence; a subject still being talked through |
| `epub` | EPUB; e-reader; e-ink; reflow; contact sheet; style proof | authoring; page-by-page review |
| `fetch` | a URL to turn **into a document** | several sources; an investigation; a PDF, even behind a URL |
| `sourcing` | investigate; establish; cross-check; archived page; read a schematic | capturing one page; producing a document |
| `discussion` | talk a subject through **before its document exists**; resume that discussion; passages pasted out of other agents' conversations | an exchange about the repository itself; establishing a fact; writing `index.md` |
| `translate` | translate an `index.md`; a document in the wrong language | importing; capturing |
| `session-review` | a task **once it is finished**, when a review is asked for | a task in progress; reviewing a built PDF or code |

The overlap to watch, because it is real rather than theoretical: `fetch` and
`sourcing` both start from a URL. The discriminator is *how many* and *known in
advance*, and both descriptions must say so explicitly rather than leave it to
the reader.

`discussion` has an overlap of a different kind: every session is a
conversation. Its description names what makes one of them its job — a
document of the library at the end — and names the exchange about the
repository itself as not its job.

The table is the design; the session reviews are the measurement. *Since
suite-and-review, phase 1*, `session-review` makes every review account for
each skill its task loaded — read from the `Skill` calls of the transcript —
and ask whether a job ran without the skill that covers it. Either failure
is a `trigger` finding against the description at fault.

`tests/test_triggers.py` holds the table: each description's discriminating
phrase, absent from every other description, and the neighbours it must
name. A skill added without a row fails it. Its first rows came from the
overlaps met in real sessions (*suite-and-review, phase 2*):
- `discussion`'s opening request, "talk about my solder joints to make a
  document of them", also reads as `pdf`'s "create a document";
- a repair that `make check-library` reported was done without `pdf`, whose
  description had no verb for fixing;
- a PDF behind a URL loads `fetch`, which then refuses it.

A phrase counts only where it is said positively. "Sources not known in
advance" is `sourcing`'s job and `fetch`'s negative clause, so it
discriminates nothing.

---

## 6. Inside a skill

### Layout

```
.claude/skills/<name>/
  SKILL.md          frontmatter (name, description) + the prose
  scripts/          the executables, one concern per file
  tests/            the suite, plus a three-line conftest.py
  references/       prose loaded on demand, not on every invocation
  assets/           what this skill's transformation needs and no one else does
```

`SKILL.md` is what makes the directory a skill; nothing the layout adds may
interfere with that discovery. `references/` holds what would bloat `SKILL.md`
if inlined — the upstream PDF manipulation recipes (Phase 3), the access map
(Phase 6). `assets/` is for a skill's *own* material — the document seeds in
`pdf/assets/templates/`, for one. The document's look is at the root (§4), so
several skills will have no `assets/` at all.

### Imports

`pyproject.toml` makes `core` an installable package; `make setup` runs
`pip install -e .`. A skill's script then reaches the core the same way from
anywhere:

```python
from core import doc
from core.imaging import contact_sheet
```

This is the option Phase 2 asks Phase 0 to settle, chosen over the two
alternatives for one reason: **it is the only one that also works when a script
is run directly.** A `PYTHONPATH` set in the `Makefile` works until someone
invokes a tool by hand, which the ten `sourcing` tools are designed to invite.
A `.pth` file in the venv works but is invisible, and leaves the core occupying
top-level names as generic as `doc` and `check`.

The cost, stated: **`make setup` becomes mandatory on a fresh clone.** Running
a script before it has been run now fails with an `ImportError` rather than
working by accident.

### How pytest finds a skill's suite

pytest puts the *test* file's directory on `sys.path`, not the directory of the
code under test. So a skill's tests cannot `import build` on their own. Each
skill's `tests/` therefore carries a three-line `conftest.py` inserting
`../scripts` — local, explicit, and one per skill:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
```

Keeping that `conftest.py` local — rather than one root conftest inserting all
five `scripts/` directories — is what stops two skills' flat module names from
colliding.

**A second conftest, at the repository root, carries the fixtures every suite
shares.** pytest loads the conftest of every directory from the rootdir down to
a test file, so `conftest.py` at the root serves the repository's own suite
*and* each skill's. The `repo` fixture lives there; `tests/conftest.py` no
longer exists. The division is: the root conftest holds what is shared, a
skill's conftest holds only the path to its own `scripts/`.

`make test` is `pytest -q` with no argument. The two roots are declared once, in
`pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests", ".claude/skills"]
```

One invocation, one reported result. `.claude` begins with a dot and pytest's
default `norecursedirs` would skip it, but naming it as a testpath makes it an
explicit root, and nothing below it is hidden.

**No test reads `library/`.** It is user content, reorganised at any time: a
suite that read it failed on a rename rather than on a defect, and wrote a real
EPUB into `out/` for every document on each run. The root conftest provides
`fixture_library`, a copy of the fictional documents under
`tests/fixtures/library/` in a temporary directory, with `doc.LIBRARY` and
`doc.OUT` pointed at it — `on_fixtures()` does the same for a fixture wider than
one test. Code that must follow the redirection reads `doc.LIBRARY` at call
time, through `doc.relative()`, and prints paths through `doc.shown()`, which
does not assume a path lies under the repository. The user's library is checked
by `make check-library` instead, which writes nothing. *suite-and-review,
phase 0.*

Build artefacts must not appear inside a skill directory. The `.gitignore`
patterns are path-independent on purpose, so they keep matching under
`.claude/skills/<name>/`: `__pycache__/`, `.pytest_cache/` and `*.egg-info/` —
the last two added by Phase 2, the editable install and the per-skill suite
being what creates them.

---

## 7. Where each test file goes

Sixteen files. Five stay at the root, eleven move into `epub`. The imbalance is
faithful rather than accidental: the EPUB work is the most recent and by far the
best covered.

| Today | Destination | Subject |
|---|---|---|
| `tests/conftest.py` | `conftest.py`, at the root (§6) | the `repo` fixture, shared with every skill's suite |
| `tests/test_harnais.py` | `tests/test_harness.py` | the repository has its key directories |
| `tests/test_disposition.py` | `tests/test_layout.py` | sources under `library/`, outputs under `out/` |
| `tests/test_documentation.py` | `tests/test_documentation.py` | the documentation follows the code |
| `tests/test_doc.py` | `tests/test_doc.py` | the core's extraction, at constant behaviour |
| `tests/test_chapitres.py` | `epub/tests/test_chapters.py` | one XHTML file per H1 |
| `tests/test_paquet.py` | `epub/tests/test_package.py` | the EPUB 3 archive and its identifier |
| `tests/test_xhtml.py` | `epub/tests/test_xhtml.py` | the embedded XHTML is well-formed XML |
| `tests/test_tableaux.py` | `epub/tests/test_tables.py` | transposition past five columns |
| `tests/test_raster.py` | `epub/tests/test_raster.py` | diagrams become PNGs |
| `tests/test_couverture.py` | `epub/tests/test_cover.py` | the cover still reads as a 300px thumbnail |
| `tests/test_epub_css.py` | `epub/tests/test_css.py` | no `var()` survives |
| `tests/test_controles.py` | `epub/tests/test_checks.py` | the mechanical checks, `epubcheck` included |
| `tests/test_build_epub.py` | `epub/tests/test_build.py` | full assembly, on the real documents |
| `tests/test_planches.py` | `epub/tests/test_sheets.py` | the review covers what does not reflow |
| `tests/test_jetons.py` | `epub/tests/test_tokens.py` | the EPUB colour mapping at equalised luminance |

*suite-and-review, phase 0: `tests/test_layout.py` is gone, its checks moved to
`make check-library`; `tests/test_anatomy.py` keeps only the guard; every test
that opened a real document — `test_build.py` "on the real documents" among
them — now opens the fixture library (§6).*

`test_jetons.py` is the one arguable placement. It reads `brand/tokens.css`,
which is root material, but what it asserts is the **EPUB** mapping — equalised
luminance, tinted backgrounds removed. The subject decides, not the file it
opens.

### Two gaps this document records and does not close

- **`lib/fetch.py` and `lib/ingest.py` have no tests at all** — 939 lines
  between them, and only `test_disposition.py` imports them, to check that they
  point at `library/`. Phase 5's task "move the fetch suite" has nothing to
  move; it writes one.
- **`pdf` starts with an empty suite.** Nothing tests `build.py` or `new.py`
  beyond the paths `test_layout.py` checks. Phase 3 moves `ingest.py` into a
  skill whose `tests/` directory is empty on arrival.

Neither is a defect this phase may fix — Phase 0 produces a document and
nothing else — but a phase that believes it is moving a suite will otherwise
discover this at the worst moment.

---

## 8. What remains of `make`

`make` is the harness, and the harness belongs to no skill. It stays at the
root, it keeps all sixteen targets, and the rule that decides whether a
seventeenth ever appears is:

> **A `make` target exists when the operation's subject is the library, or a
> document in it. A tool whose subject is an arbitrary file or URL is run
> directly.**

| Target | After the roadmap |
|---|---|
| `setup` `brand` `icons` `test` `list` `clean` `help` | unchanged — the harness itself |

*The `document-anatomy` roadmap, phase 2, revised `clean`: it takes an
optional `DOC=`, and it now deletes inside `library/` — every document's
`.work/`, and nothing else. What it may remove is decided by `core/doc.py`,
never by a pattern written in the `Makefile` (§11).*
| `new` `build` `watch` `check` `import` `review` | facades over `pdf` |
| `epub` `preview` `preview-style` | facades over `epub` |
| `fetch` | facade over `fetch` |

A facade is one line: the same invocation the user already knows, pointing at a
script that has moved. Target names do not change — they are muscle memory, and
a rename would be the one part of this roadmap a user feels.

Two consequences:

- **The ten `sourcing` tools get no target**, and neither does the `translate`
  engine. Their subject is a file, a URL or a PDF that has nothing to do with
  `library/`, and their arguments — `--region 0.05,0.15,0.62,0.85`, `--scale 6`
  — are exactly what `make` relays badly. They are run directly, which is why
  the import mechanism had to work for direct runs (§6).
- **`make epub` stays separate from `make build`.** A document is rebuilt dozens
  of times while being written, and rasterising twelve diagrams on every pass is
  a gratuitous slowdown. The reason is a comment in the `Makefile` today and
  must survive the move.

*After the roadmap, the rule let in a seventeenth: `review`. Its subject is a
document of the library — the PDF `make build` made of it — so it is a target,
not a tool run directly.*

`make help` must keep listing every target that exists — a test already enforces
it, and that test stays at the root because its subject is the repository.

---

## 9. Glossary

Phase 1 translates the code, the harness and the tests. Three modules each
coining their own word for the same thing is the failure this table exists to
prevent, so it is normative: where a term appears here, Phase 1 uses this
word and no synonym.

**Spelling convention: British.** *behaviour*, *colour*, *rasterise*,
*normalise*, *organise*. It is what the roadmap already uses, and a repository
that mixes the two reads as two authors.

### The document and its structure

| French | English | Note |
|---|---|---|
| bibliothèque | library | |
| dépôt | repository | |
| thème (folder under `library/`) | **topic** | `library/<topic>/<slug>`. Frees `theme` for the other sense. |
| thème (front matter `light`/`dark`/`both`) | **theme** | stays `theme:` — it is a front-matter key |
| document | document | a directory holding a `document/index.md` (§11) |
| preset | preset | unchanged, it is already the front-matter key |
| registre (of a document, of an admonition) | register | |
| squelette, gabarit | template | what `.claude/skills/pdf/assets/templates/` holds |
| front-matter | front matter | two words in prose |
| couverture | cover | |
| surtitre | eyebrow | already the front-matter key |
| sommaire | table of contents | `toc` in the front matter |
| chapitre | chapter | |
| encart | admonition | the pymdownx term |
| légende | caption | |
| étiquette | label | |
| en-tête | header | a table's header row; a provenance header |
| sous-entrée | sub-entry | |
| rangée | row | |
| tableau | table | |
| seuil (de transposition) | threshold | `table-threshold` |
| niveau (de découpe) | level | |
| matière d'origine | source material | what `sources/` holds: what the user gave the document (§11) |
| ce qui a été appris | study | what a tool derived from the sources and keeps: `study/` (§11) |
| atelier | workspace | a translation under way, in `study/translate/` |
| jetable | disposable | remade by a command, in `.work/`, removed by `make clean` (§11) |
| provenance | provenance | |
| empreinte | digest | SHA-256 |
| manifeste | manifest | `manifest.yaml`, in every directory of the library but its root (§11) |
| entrée | entry | a directory holding one of the five roles, or a file (§11) |
| élément | item | what an entry's manifest says about one of its files or directories |
| identifiant | id | a prefix and 8 drawn characters, permanent: `manuel-k7m3p2x9` |
| citation | citation | a Markdown link whose target is an id: `[…](id:…)` |
| horodatage | timestamp | |
| clé | key | |

### The two outputs

| French | English | Note |
|---|---|---|
| paginé | paginated | the PDF output |
| reflué, refluée | reflowable | the EPUB output |
| ne reflue pas, non reflable | does not reflow, non-reflowing | the review's subject |
| dorsale | backbone | one per output |
| mise en page | page layout | |
| disposition (of the repository) | layout | distinct from *page layout* above |
| découpe, découpage | split, splitting | at H1, for chapters |
| aplatissement | flattening | resolving `var()`, dropping `@page` |
| rastérisation | rasterisation | SVG → PNG |
| paquet | package | the EPUB 3 package, the OPF |
| liseuse | e-reader | |
| écran (of an e-reader) | screen | |
| six pouces | six-inch | the reference screen |
| e-ink | e-ink | |
| veuve, orphelin | widow, orphan | |
| césure | hyphenation | |
| police | font | *typeface* for the family |
| sortie(s) | output(s) | |

### Review

| French | English | Note |
|---|---|---|
| relecture | review | |
| **planche de contact** | **contact sheet** | the photographic term, and the Phase 6 tool name |
| **planche de style** | **style proof** | a printer's proof. *style sheet* is unusable beside CSS |
| vignette | thumbnail | |
| recadrage | crop | fractional coordinates, never pixels |
| cadrage | framing | |
| guide de style | style guide | the document the style proof renders |
| contrôle, contrôles | check, checks | mechanical, run on every build |
| balayage | sweep | |
| signaler | report | what a check does |
| lever (une erreur) | raise | |
| repli | fallback | |

*The roadmap's own prose says "contact plate" and "style plate" in places. This
glossary supersedes it: Phase 0 is where the term is settled, and the Phase 6
tool is already named `contact-sheet`.*

### Art direction

| French | English | Note |
|---|---|---|
| direction artistique, DA | art direction | |
| marque | brand | |
| jeton | token | |
| table des jetons | token map | the function is already `token_map` |
| rôle | role | `accent`, `alert`, `danger`, `ink`, `muted`, `soft` |
| rampe (of the palette) | ramp | the raw brand ramps in `palette` |
| teinte | tint | `alpha(primary.600, 0.10)` |
| filet | rule | the line; matches the `--rule` token |
| puce | bullet | |
| gouttière | gutter | |
| feuille (de style) | stylesheet | one word |
| cascade | cascade | |
| densité | density | |
| réglage | setting | |
| icône | icon | Lucide, in `brand/icons/` |

### Sourcing

| French | English | Note |
|---|---|---|
| enquête | investigation | |
| pièce | piece | what was received, intact — the evidence |
| journal | journal | the three-status log: established, hypothesis, to find |
| sonder, sonde | probe | status, size, content type, effective URL |
| dépouiller | strip | HTML → text |
| élaguer | prune | what the extraction left behind |
| miroir | mirror | a mirror chain |
| mur, porte | wall, door | the access map's two columns |
| fiche (technique) | datasheet | |

### The harness

| French | English | Note |
|---|---|---|
| harnais | harness | `make`, `brand/sync.py`, the venv |
| cible | target | a `make` target |
| aide | help | `make help` |
| surveillance | watch | `make watch` |

---

## 10. What this document does not decide

- **`library/`.** User content. Nothing here translates it, moves it, or imposes
  a convention on it. *Superseded by §11: the `document-anatomy` roadmap imposes
  a convention on the directories a tool writes inside a document, and on
  nothing the user puts there.*
- **The art direction itself.** `brand/tokens.yaml` and the cascade are moved
  and documented, not redesigned.
- **`diagram-design`.** A plugin installed outside the repository, reached
  through the `.diagram-design` marker and the profile written by
  `brand/sync.py`. Never modified, before or after this roadmap. Phase 2 must
  not break the marker when the layout moves.
- **Any new capability.** Every phase ends with the same outputs it started
  with. The two test gaps in §7 are recorded, not filled.
- **The local translation engines.** Phase 7 builds the seam and records the
  candidates; a roadmap of its own implements them.
- **The number of skills.** Five, settled at the roadmap's opening. This
  document draws their borders and records the escape hatch to a sixth (§5); it
  does not reopen the count.

---

## 11. The inside of a document

*Added by the `document-anatomy` roadmap, phase 0. It supersedes the first
bullet of §10: `library/` remains user content, and this section imposes a
convention on the directories a tool writes inside it, not on what the user puts
there or on how the topic tree above is arranged.*

*It sits last rather than beside §1's tree because this document's prose refers
to its sections by number, and inserting one would have renumbered the rest in
silence. Phase 5 kept it here for the same reason and pointed §1 at it instead.
The reference manual, written for a reader rather than for this argument, is*
[`docs/document.md`](document.md).

Until now a document's anatomy was never declared. `core/doc.py` knows one fact
— `index.md` is the entry — and the rest was habit: `assets/` because the first
document had images, `sources/` because the first import needed somewhere to put
a PDF. Four skills write into a document directory and none of them agreed with
the others about what belongs where.

The cost was never tidiness. It was that nobody could say whether a given file
may be deleted, regenerated or edited, and so nothing ever was.

### The cut that decides the rest

**The build reads `document/` and nothing else.**

It is the only boundary the machine checks for you: a file on the wrong side of
it breaks a build, which is visible on the next run. Every other misplacement is
silent, and a silent convention is the one that decays.

Note what the cut is not. It is not authorship: a schematic drawn by hand over
an afternoon lives in `document/assets/` beside a photograph extracted from a
PDF by a script, because the document references both and the build embeds both.
It is not cost either: an expensive file and a cheap one sit together if they
are read together. **What a file is for decides where it lives; who made it does
not.**

### The five roles

```
library/<topic…>/<slug>/
  document/     index.md, cover.md, assets/
  sources/      what was received
  study/        extracted text, provenance, the investigation and discussion journals
  generators/   the code that draws an asset
  .work/        review sheets, EPUB proofs, page renders
  manifest.yaml what each of the above is (see *The manifest*, below)
```

| | Written by | Read by the build | `make clean` |
|---|---|---|---|
| `document/` | the agent, with the user | **yes, and only this** | never |
| `sources/` | the user — a tool may acquire into it, never derive | no | never |
| `study/` | the agent | no | never |
| `generators/` | the agent | no | never |
| `.work/` | the tools | no | **removed** |

A document has only the directories it needs. `make new` creates `document/`;
the rest appear when something has to go in them. An empty directory created in
advance teaches nothing and invites the wrong file — `out/translate/` existed
for three days, empty, because a skill made it before it had anything to write.

**`document/`** holds what a reader ends up with: `index.md`, `cover.md` and the
`assets/` they reference. `assets/` sits inside rather than beside it so that
every relative link a document already writes keeps working unchanged.

**`sources/` belongs to the user.** It is the only directory they write into,
and they fill it with whatever they judge relevant to the task. **No tool ever
modifies what is in it.** That half of the rule is enforced; the other half —
that the user leaves the rest alone — is advice, not a fence. It is their
repository.

**`study/`** is what the agent learned from the sources and must keep: the text
extracted from an imported PDF, the provenance of a capture, the journal an
investigation wrote. The build never reads it, and `make clean` never touches
it.

**`generators/`** is code that produces something in `document/assets/`. It is
kept apart from `study/` so that neither directory has an exception to its own
rule: one holds prose and data, the other holds programs.

**`.work/`** is everything a command can make again: review sheets, EPUB
contact sheets, page renders. It is hidden because it is disposable, inside the
document because that is what it is about, and removed by `make clean` without a
thought.

### Acquire, derive

A tool may **acquire** into `sources/` and may never **derive** into it.

Copying an imported PDF or saving a captured page fills the user's directory on
their behalf: the result is received material like any other, and the user could
have put it there themselves. Computing `extracted.md` from that PDF is a
different act — it produces something the user never had — and it goes to
`study/`.

The line does not exist in the code today. `ingest.py` and `fetch.py` each do
both, into the same directory, which is why `sources/` became a place where a
user cannot tell what they put there from what a script left behind.

### Durable, disposable

A file is **disposable** when a command can make it again *and* nothing is lost
by making it later. Both halves matter, and the second is the one that catches
the interesting cases.

| | Where | Why |
|---|---|---|
| `extracted.md` | `study/` | Regenerable from `sources/`, but its worth is that it does not change: a translation reads it to check that nothing was invented. Durable by choice. |
| `meta.json` | `study/` | A URL, a date, a digest. Nothing recomputes when a page was fetched. Durable by necessity. |
| `NOTES.md` | `study/` | An investigation's journal. Written, neither received nor derived, and no command makes it again. |
| `discussion/` | `study/` | A discussion's journal: an index, its topics, the sessions' archive. Written, neither received nor derived — and the conversation it records is gone once the session ends, so it is the only copy of what the user said. |
| `figures.py` | `generators/` | Code. Deleting it loses the ability to redraw what it drew. |
| a hand-drawn SVG | `document/assets/` | Expensive, durable, agent-made — and the document references it, so the cut sends it with the document. |
| a translation workspace | `study/` | A command re-runs a translation, but not the same one: an engine's answers are the work itself, and for the `agent` engine they are an agent's writing. Both halves of the rule fail. It is **spent** once `apply` has written the document, and nothing removes it automatically. |
| review sheets, page renders | `.work/` | A command makes them again, and nothing is lost by making them later. |

A translation workspace is the case that shows why the second half of the rule
carries the weight. It *looks* like working state — a job in progress, named
after a command — and `make clean` would have taken a half-translated hundred-page
document with it. What a command can produce again is *a* translation, not *the*
translation that was under way.

The ambiguous case is `extracted.md`, and it is ambiguous in a way worth naming:
it is regenerable, so it *could* live in `.work/`, but only if regeneration is
deterministic. If it is not — a library version moves, an extraction changes —
then the reference a translation checked against is gone, and the file was never
disposable. It is placed in `study/` on that argument, and the roadmap's phase 3
verifies the premise rather than assuming it.

### The manifest

*Added by the `library-catalogue` roadmap, phase 0.*

The five roles say where a file goes; they do not say what it is. Knowing that
meant opening it, and a file named `Sans titre.jpg` or `20260924_123413.jpg`
says nothing. So every directory of the library describes itself in a
`manifest.yaml`, beside what it describes: a directory the user renames or
moves takes its manifest along, and nothing has to be reconciled. A database
was considered and rejected — it sits beside the directories rather than in
them, and would keep the one costly part, the descriptions, in a file git does
not track. It comes back only as an index rebuilt from the manifests, if a
search grows slow.

**Two kinds of node, read from the directory.** A *topic* holds only
directories, and its manifest never lists them: its description says what
belongs there, so it stays true when an entry arrives. An *entry* holds one of
the five roles, or a file, and its manifest sits at its root, never below:
a subdirectory of `sources/` is an item of that manifest, and nothing is
written into `sources/`. An entry need not be a document — most of the
user's directories are sources waiting to be studied, and they are entries
all the same.

**The agent writes the name, the description and an id's prefix; the tool
writes the rest** — paths, kinds, file counts, and a digest for what is the
user's. The digest is what lets `sync` follow a source the user renamed, so
the user renames as they like and no file is renamed for the agent's sake.

**What the agent cites, it cites by id**, never by path: a path breaks at the
next rename, silently when it sits between backticks. The id is permanent and
never reused, because a discussion's sessions are never rewritten and must not
end up pointing at something else. No id goes into `document/`: references
between documents serve the agent, not the reader.

`docs/document.md` is the manual for all of it.
