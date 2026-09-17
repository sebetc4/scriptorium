# Phase 3: The `pdf` Skill

---

## Status

**Current Status:** 🟢 Done (100% — 13/13)
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

One `pdf` skill, ours, covering the whole PDF domain of this repository:
writing a document, building it, reviewing it, and importing an external PDF to
rebuild it as a document. `pdf-doc` disappears into it. The vendored upstream
content is kept only where it has actually served, as a reference file.

---

## Overview

### Why This Phase Matters

Today a request about a PDF has to choose between two skills whose names do not
say which. `pdf` is the upstream general-purpose toolkit; `pdf-doc` is the
repository's own authoring chain, and its description spends four lines telling
the reader when *not* to use it. That is a boundary the user has to hold, and
they should not have to.

This phase also lifts a rule that has been true and is about to stop being
true. `claude.md` says **never modify the provided skills** — written when the
only provided skills were upstream ones replaced on every update. Forking the
PDF skill into a project skill makes it ours; the rule then applies to
`diagram-design` alone, and saying so precisely is part of the deliverable.

### What It Enables

The repository's flagship capability gets a single, complete entry point. Every
later skill can refer to `pdf` for "what a document of this library is" instead
of restating it.

### Out of Scope

- The EPUB output. A `report` document produces both, but the EPUB chain is
  Phase 4 and the two skills reference each other rather than duplicate.
- Reading a PDF as evidence — locating a term, rendering a schematic to read
  it. That is `sourcing`, Phase 6, per the boundary set in Phase 0.
- Translating an imported document. `import` produces an untranslated
  `index.md`; the translation is `translate`, Phase 7.

---

## Tasks

### The skill's prose
- [x] Write `SKILL.md` in English: the chain from `index.md` to PDF, the four presets, the front-matter, and what the skill refuses
- [x] Carry over the cover section from `pdf-doc` — the content is proposed and validated line by line, never decided
- [x] Carry over the art-direction section: the three colours and their three uses, the cascade, the icons, the diagrams
- [x] Carry over the review loop: a PDF is not delivered until it has been rendered to images and looked at page by page
- [x] Write the external-PDF import section, and state the boundary with `sourcing` in the skill's own words
- [x] ~~Absorb the upstream parts that have actually served here~~ Cover merge, split, extract and render to images in `references/manipulation.md` — *written from scratch, see Notes: the upstream licence forbids derivative works*
- [x] Drop the upstream parts that never served here: form filling, encryption, OCR, and the scripts that go with them

### The code
- [x] Move `core/build.py` and its tests into the skill
- [x] Move `core/new.py`, and `templates/` if Phase 0 assigned it here — *it did not: `templates/` stays at the root (`docs/architecture.md` §4)*
- [x] Move `core/ingest.py` and its tests into the skill
- [x] Leave the page-render brick in the shared core — `epub` and `sourcing` both use it

### Retiring `pdf-doc`
- [x] Delete `.claude/skills/pdf-doc/` and redirect every reference to it in the repository
- [x] Rewrite the "never modify the provided skills" rule so it names `diagram-design` and only `diagram-design`, and settle what happens to the upstream `LICENSE.txt` for the content kept

---

## Technical Details

### Files to Modify

```
.claude/skills/pdf/SKILL.md                   rewritten
.claude/skills/pdf/references/manipulation.md  to be created
.claude/skills/pdf/scripts/                   pruned to what is used
.claude/skills/pdf/forms.md                   removed
.claude/skills/pdf/reference.md               absorbed, then removed
.claude/skills/pdf-doc/                       removed
core/build.py, core/new.py, core/ingest.py       moved into the skill
tests/                                        the matching suites, moved
Makefile                                      new, build, watch, check, import
claude.md                                     the provided-skills rule
```

### Dependencies

Phase 2's layout. This is the first skill to use it for real, on three modules
rather than the one that proved it.

### Constraints

- `make build` must keep working from the repository root, with the same
  invocation. Users and tests both depend on it.
- `.claude/skills/pdf/LICENSE.txt` covers the upstream content. Whatever is
  kept from it keeps its attribution; whatever is dropped takes its licence
  obligations with it.
- The art-direction rules are also stated in `claude.md` and `README.md`. Those
  two are rewritten in Phase 8 — until then the skill is the authority and the
  duplication is tolerated, not resolved here.

---

## Acceptance Criteria

- [x] One skill named `pdf` covers the domain; `pdf-doc` no longer exists
- [x] Its `description` triggers on writing, building, importing and reviewing a PDF, and on nothing belonging to `epub`, `translate` or `sourcing`
- [x] Every rule `pdf-doc` carried is either in the new skill or explicitly dropped with a reason
- [x] No reference to `pdf-doc` survives anywhere in the repository — *outside the roadmap's own files, which are a log and keep their history*
- [x] The kept upstream content is attributed; the dropped content is gone with its scripts — *nothing upstream is kept, so there is nothing to attribute; `LICENSE.txt` went with the rest*
- [x] `make new`, `make build`, `make watch`, `make check` and `make import` work unchanged from the repository root
- [x] `make test` is green
- [x] The style guide builds to PDF and has been reviewed page by page

---

## Notes

### What "absorb the useful in reference" means concretely

The upstream skill covers merge, split, rotate, watermark, form filling,
encryption, image extraction and OCR. Of those, the repository has used
rendering pages to images (the review loop, `pypdfium2`) and text extraction
(`ingest.py`). Merge, split and extraction are plausible next needs for a
library of documents. Form filling, encryption and OCR are not — no document
here has ever been a form, and nothing here is scanned.

The test for keeping a section: can a document of this library ever be its
subject? If not, it goes.

### The rule being lifted

`claude.md` currently reads:

> **Ne jamais modifier les skills fournies** : `.claude/skills/pdf/`, et
> `diagram-design`, installée en plugin hors du dépôt.

After this phase, `.claude/skills/pdf/` is a project skill and is modified
freely. `diagram-design` remains a plugin installed outside the repository,
replaced on every update, and reached through the `.diagram-design` marker and
the profile written by `brand/sync.py` — for it the rule is unchanged and the
reason is worth restating rather than assuming.

### The upstream licence decided the "absorb" task

`.claude/skills/pdf/LICENSE.txt` is not a permissive licence. It forbids
reproducing the materials and creating derivative works from them. "Absorb the
useful parts as a reference file" could therefore not mean adapting upstream
prose. `references/manipulation.md` is **written from scratch**: our own words,
our own examples, restricted to the three libraries `requirements.txt` already
pins (`pypdf`, `pymupdf`, `core.pdfpage`). No system tool is involved: neither
`qpdf` nor `pdftk` is installed, and poppler is not a repository dependency.

Every upstream file went: `forms.md`, `reference.md`, the eight form scripts
(`convert_pdf_to_images.py` included, since `core.pdfpage` does that job), and
`LICENSE.txt` with them. Nothing upstream is kept, so there is nothing to
attribute. If an upstream passage is ever wanted back, the licence question
comes back with it.

Every recipe in `manipulation.md` was run against a real PDF before being
committed. The images recipe was run on a document that actually has images
(`round-led-d4017`, 42): the style guide has none, so running it there would
have proven nothing.

What was dropped, and why, by the test in the note above: **form filling,
encryption, OCR** (no document here is a form or a scan); **rotation and
watermarking** (a watermark would be CSS in a document, not a patch on an
output); **drawing a PDF with `reportlab`** (a PDF here is made by `make build`,
never drawn); **the JavaScript libraries** (no JavaScript in the chain).

### `pdf-doc` carried three other skills' prose

`pdf-doc` held the EPUB section, the web capture (§9) and the translation steps
of the import. Deleting it in this phase would have lost all three before their
own phases (4, 5, 7) exist to receive them. Each was **carried into the
matching stub**, in English and unchanged in substance, under a line saying so:
`epub/SKILL.md`, `fetch/SKILL.md`, `translate/SKILL.md`. Those phases rewrite
the sections. They do not need to hunt for them in git history.

This is also what makes the criterion "every rule `pdf-doc` carried is in the
new skill or dropped with a reason" true. The rules are in the new skill *or in
the neighbour that owns them*, and none was dropped. Only the §-numbers went:
cross-references now name the section (*The cover*, *Build, then review*),
because numbers drift when a section is added.

One example was corrected rather than carried: the local-override example
`:root { --accent: #1f7a5a; }` was a hex value in a document's stylesheet, which
the rule two sections above it forbids. It now reads `var(--link)`.

### The mechanics of the move

- **`ROOT` comes from `core.doc`.** All three scripts computed it as
  `Path(__file__).parent.parent`, which is the skill directory once they have
  moved. `build.py`, `new.py` and `ingest.py` now import `ROOT` and `LIBRARY`
  from the core. A new test pins `module.ROOT == repo` for all three: a wrong
  root does not always fail loudly, since `new.py` would happily create
  `library/` inside the skill.
- **The path tests split.** `tests/test_layout.py` imported `build`, `new` and
  `ingest` from `core`. Their assertions moved to
  `.claude/skills/pdf/tests/test_pdf_layout.py`, and `fetch` stays at the root
  until Phase 5. The name is `test_pdf_layout.py`, not `test_layout.py`: with no
  `__init__.py`, pytest refuses two test modules with the same basename.
- **Counted, as Phase 2 advised:** 124 → 125 → 126. One test removed and two
  added at the first move, one added at the second.
- **Verified end to end,** not just by the suite: `make new` and `make import`
  ran into a throwaway `library/tmp-phase3/` (deleted afterwards), `make watch`
  started, `make check` built. The style guide's ten pages, light and dark, are
  **pixel-identical** to the pre-phase baseline and were reviewed image by
  image.

### Left for later, deliberately

- **The style guide's own content is stale** — `library/`, out of scope. It
  still says documents live under `pdfs/`, and its `theme.css` example carries
  the same hex value corrected above. It also shows a `Ma bibliothèque` footer,
  which the invent-nothing rule would not have produced. Worth a pass by its
  author; not this roadmap's to make.
- **`claude.md` and `README.md`** were only redirected, in French: the module
  map's three rows, the skill pointer, and the rule. Phase 8 rewrites both. The
  duplicated art-direction rules remain tolerated, as this phase's constraints
  said.
- **`docs/architecture.md` §7** still says "`pdf` starts with an empty suite".
  That was true when it was written. The suite now holds the path tests and
  nothing that exercises a build, so the gap it records is still real.
