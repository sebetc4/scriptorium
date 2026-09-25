# A document

A document is a directory under `library/`, and it holds five things at most.
This page says what each one is, who writes it, and what happens to it — so
that any file in a document has an answer to *where does this go* that nobody
has to invent twice.

`docs/architecture.md` §11 argues for this shape. This page assumes it.

```
library/<topic…>/<slug>/
  document/     index.md, cover.md, theme.css, assets/
  sources/      what you gave it
  study/        what the tools learned from your sources
  generators/   code that draws an asset
  .work/        everything a command can make again
```

The directories above it are topics, at whatever depth: `library/finance/2026/`
holds `report-q3/`, and nothing anywhere declares that. A directory becomes a
document the moment it holds a `document/index.md`.

---

## The five, at a glance

| | Who writes it | Read by the build | Yours to edit | `make clean` |
|---|---|---|---|---|
| `document/` | the agent, with you | **yes, and only this** | yes — it is the deliverable | never |
| `sources/` | **you** — a tool may add to it, never change what is in it | no | yes, it is yours | never |
| `study/` | the agent | no | yes, but you rarely need to | never |
| `generators/` | the agent | no | yes | never |
| `.work/` | commands | no | pointless — it is remade | **removed** |

Two of them are refused to the agent's own hand: an edit to `sources/` or
`.work/` is stopped by `.claude/hooks/protect-paths.sh`, with the reason. The
scripts still write there through `make`, which is the difference between a tool
*acquiring* on your behalf and an agent *editing* what is yours.

A document has only the directories it needs. `make new` creates `document/`;
the others appear when something has to go in them.

---

## `document/` — what a reader ends up with

```
document/
  index.md      the document: front matter, then Markdown
  cover.md      optional, the cover's own Markdown
  theme.css     optional, this document's departure from the art direction
  assets/       the images and SVGs index.md references
```

**The build reads this and nothing else.** That is the one rule the machine
checks for you: a file on the wrong side of it breaks a build, which is visible
on the next run, while every other misplacement is silent.

The cut is about what a file is *for*, not who made it. A schematic drawn by
hand over an afternoon sits in `assets/` beside a photograph a script pulled out
of a PDF, because `index.md` references both and the build embeds both.

`assets/` lives inside `document/` so that an image link of the form
`assets/x.svg` keeps working wherever the document goes.

---

## `sources/` — what you gave it

**This directory is yours.** You fill it with whatever you judge relevant to the
task, and no tool changes what is in it.

A tool may *add* to it on your behalf — `make import` copies the PDF you pointed
at, `make fetch` saves the page as it arrived, a `sourcing` session saves the
photographs and threads it collected. That is acquisition, and the result is
material you could have put there yourself. What a tool *computes* from it is a
different act and goes to `study/`.

You can empty it, refill it, rename things in it. The one consequence is that
`make rederive` needs what it was given: with the source gone, `study/` holds
the only copy of the extraction.

---

## `study/` — what the tools learned

```
study/
  extracted.md  the raw extraction of an import or a capture, never edited
  meta.json     provenance: where it came from, when, its digest
  NOTES.md      an investigation's journal
  discussion.md a discussion's journal: what you said, what was decided, what is established
  translate/    a translation in progress, or one already applied
```

Never read by the build, never removed by `make clean`. Two things in it are
worth knowing:

**`extracted.md` is a reference, not a draft.** A translation checks against it
that nothing was invented. `make rederive` rebuilds it from `sources/` — the
same input gives the same output — but only while the source is still there,
and only while the script that reads it has not changed. It has: two documents
imported before this repository was translated re-derive with a different
placeholder caption. That is why the file is kept rather than recomputed.

**`meta.json` is never re-derived.** An import date, a fetch timestamp, an HTTP
status, whether a certificate verified: facts about a moment, which nothing
recomputes.

**`discussion.md` is the only memory of a conversation.** The `discussion`
skill writes it while you talk a document through, and a later session resumes
from it rather than from the conversation, which is gone. It may exist before
`document/` does: a discussion usually starts before `make new`.

**`translate/` is durable, and that is deliberate.** An engine's answers are the
translation; re-running gives *a* translation, not the one that was under way.
It is **spent** once `apply` has written the document, and nothing deletes it
then — `apply` says so and leaves it to you.

---

## `generators/` — code that draws

A script that produces something in `document/assets/` lives here, beside the
document and never inside it: the build reads what it produced, not the code
that produced it. It survives `make clean`, because deleting it loses the
ability to redraw.

---

## `.work/` — everything a command can make again

```
.work/
  review/<variant>/   page sheets and checks, from make review
  preview/            EPUB contact sheets, from make preview
  pages/              each page of an imported PDF as an image
```

Hidden because it is disposable, inside the document because that is what it is
about. `make clean` removes it without asking. Nothing here is worth editing:
change what produces it.

---

## The life of a document

What each command reads, what it writes, and what is left.

### `make new DOC=topic/slug [PRESET=report] [TITLE="…"]`

Creates `document/index.md` from the preset's seed, and `document/assets/`.
Nothing else: an empty directory made in advance teaches nothing and invites the
wrong file.

### `make import SRC=x.pdf DOC=topic/slug TO=en`

| Writes | Where |
|---|---|
| the PDF you pointed at, copied | `sources/` |
| the extracted text, as `index.md` to edit | `document/` |
| the images found in the PDF | `document/assets/` |
| the extraction, intact | `study/extracted.md` |
| provenance, digest, page counts | `study/meta.json` |
| every source page as an image | `.work/pages/` |

The document arrives untranslated, with a comment block at the top of
`index.md` listing what is left to do.

### `make fetch URL=https://… DOC=topic/slug`

| Writes | Where |
|---|---|
| the page exactly as received | `sources/page.html.gz` |
| the extracted content, to prune | `document/index.md` |
| the images, recompressed | `document/assets/` |
| the extraction, intact | `study/extracted.md` |
| URL, status, TLS, date, digest | `study/meta.json` |

### `make rederive DOC=topic/slug`

Re-runs the extraction from `sources/` alone and rewrites `study/extracted.md`
and `.work/pages/`. Not `meta.json`, not `index.md`, not `assets/` — the
provenance nothing recomputes and the work done since. It says nothing when the
document was neither imported nor captured, and says so plainly when it was
imported but its source is gone.

### `make build [DOC=topic/slug]`

Reads `document/` and the art direction. Writes `out/pdf/<topic>/<slug>/`, one
PDF per variant the front matter's `theme:` asks for.

### `make review DOC=topic/slug [VARIANT=] [ZOOM="3 7"]`

Reads the built PDF. Writes the checks and the page sheets to
`.work/review/<variant>/`. A PDF older than anything in `document/` is refused:
build first.

### `make epub [DOC=topic/slug]` · `make preview` · `make preview-style`

`epub` writes `out/epub/<topic>/<slug>/`. `preview` writes the contact sheets to
`.work/preview/`, and `preview-style` the style proof.

### `translate.py prepare | run | apply DOC=topic/slug`

`prepare` reads `document/index.md` and `study/meta.json` and writes the job to
`study/translate/`. `run` fills in the answers. `apply` checks every chunk and,
if none fails, rewrites `document/index.md` in the target language.

### `make clean [DOC=topic/slug]`

Removes `out/` and every document's `.work/`, and nothing else. With `DOC=`,
that one document's `.work/`, and `out/` is left alone.

---

## Where things are refused

`.claude/hooks/protect-paths.sh` stops an edit before it happens and says why.
Inside a document it refuses two paths:

- **`sources/`** — it is yours. Derived material belongs in `study/`, the
  document in `document/index.md`.
- **`.work/`** — a command remakes it. Change what produces it.

It also refuses the pieces of an investigation — `raw/`, `datasheets/`,
`images/` in a document whose `study/NOTES.md` exists — which are kept as they
were received.

Outside a document it refuses `brand/tokens.css` and `brand/icons/`, which are
generated, and the `diagram-design` plugin, which is replaced on update.

---

## One document does not fit

`electronique/repair/electribe-2/sources` keeps an investigation's
`datasheets/`, `images/`, `raw/` and `threads/` at its root rather than in
`sources/`: it is a `sourcing` session's own material that became a document, so
its root *is* the investigation. `tests/test_anatomy.py` names it as an
exception rather than widening the rule for everyone, and the day it is reshaped
the test will say whether anything still needs it.

Two things the anatomy still does not place, for the same reason — nobody has
needed to decide yet:

- **`glossary.yaml`**, a translation's term list. Read by `translate`, never by
  the build, written by you. It sits at the document's root.
- an investigation's **`threads/`**, transcriptions derived from the raw
  captures, kept with them in `sources/` because they were collected together.
