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
  manifest.yaml what each of the above is, kept by the catalogue
```

The directories above it are topics, at whatever depth: `library/finance/2026/`
holds `report-q3/`, and nothing anywhere declares that. A directory becomes a
document the moment it holds a `document/index.md`. Every directory also
describes itself in a `manifest.yaml`: see [The catalogue](#the-catalogue--manifestyaml).

One document lives outside the library: the style guide, `brand/style-guide/`,
which the repository owns and your library does not have to carry. It has the
same shape, and its outputs go under `out/<kind>/brand/style-guide/`.

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

The cut is about what a file is *for*, not who made it. A figure drawn by
hand over an afternoon sits in `assets/` beside a photograph a script pulled out
of a PDF, because `index.md` references both and the build embeds both.

`assets/` lives inside `document/` so that an image link of the form
`assets/x.svg` keeps working wherever the document goes.

---

## `sources/` — what you gave it

**This directory is yours.** You fill it with whatever you judge relevant to the
task, and no tool changes what is in it.

A tool may *add* to it on your behalf — `make import` copies the PDF you pointed
at, `make fetch` saves the page as it arrived. That is acquisition, and the
result is material you could have put there yourself. What a tool *computes*
from it is a different act and goes to `study/`. So does what an investigation
*finds* on its own — pages, threads, documents: you did not give it.

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
  raw/, threads/, documents/, images/
                the pieces the investigation found, kept as received
  discussion/   a discussion's journal: index.md, topics/, sessions/
  translate/    a translation in progress, or one already applied
```

Never read by the build, never removed by `make clean`. Five things in it are
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

**An investigation's pieces are its findings, not your sources.** What a
`sourcing` session collected — pages as received, their transcriptions,
documents, images — sits beside its `NOTES.md`, which cites each piece by
id. It is kept as received: the guard refuses an edit in `raw/`,
`documents/` and `images/` there.

**`discussion/` is the only memory of a conversation.** The `discussion`
skill writes it while you talk a document through, and a later session resumes
from it rather than from the conversation, which is gone. It may exist before
`document/` does: a discussion usually starts before `make new`. It has three
layers: `index.md`, what you said about the whole document, the decisions, the
open questions, the outline, and a map of the topics — the only file a resume
reads; `topics/`, one file per subject, as it stands now; `sessions/`, what
each session covered and what it replaced, never rewritten. Nothing is lost
when a point is superseded: it moves to its session, with a link both ways.
What the discussion read — your notes, a photo, a document elsewhere in the
library — is cited by id where it served, and `links` on the entry lists what
it relies on outside it.

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

## The catalogue — `manifest.yaml`

Every directory of `library/` except the root holds a `manifest.yaml` that
says what it is, so that finding something never means opening everything.
`core/catalogue.py` keeps them.

**Two kinds of directory, read from what they hold.** A **topic** holds only
directories: `home`, `home/appliances`. An **entry** holds one of the
five roles, or a file: a document, a directory of sources waiting to be
studied, or a directory holding a single PDF. A directory with no visible file
anywhere under it is neither, and has no manifest.

```yaml
# Written by the catalogue, core/catalogue.py: change it through
# `sync` and `describe`, never by hand.
id: lave-linge-a8f2c3d9
name: Lave-linge K-450
description: "Le lave-linge de la maison : sa notice et les photos de sa panne."
items:
- path: sources/notice.pdf
  id: notice-k7m3p2x9
  name: Notice du lave-linge K-450
  description: "La notice du fabricant : installation, programmes, messages d'erreur."
  kind: pdf
  sha256: 9f2c…
- path: sources/panne
  kind: directory
  files: 12
  sha256: 41ab…
```

- **A topic's manifest never lists its children**: the file system knows
  them. Its description says what belongs in the topic, not what is in it,
  so it stays true when an entry arrives.
- **An entry's items describe its files**: by default one per direct child of
  each role, and one per file or other directory at its root; `.work/` is
  never listed. An item that names one file inside a covered directory takes
  that file out of it: a file is covered by the item with the longest path
  leading to it.
- **The anatomy's standard files are named by the tool**: `document/index.md`,
  `cover.md`, `theme.css`, `assets/`, `study/extracted.md`, `meta.json`,
  `NOTES.md`, `discussion/`, `translate/`, `glossary.yaml`.
- **A digest for your files only** — anything outside `document/`, `study/`
  and `generators/`. A source never changes, so a new digest means something:
  a rename to follow, or a description to review. The agent's files change
  every session, and a digest would say nothing there.
- **Names and descriptions are in the library's language**, so that a search
  finds everything with the same words; the keys are English. The library
  says which in `.catalogue.yaml` at its root — `language: fr` — and the tool
  names the standard files in it; English when it says nothing.

### Ids, and how the agent cites

An id is 8 characters the tool draws, when a node is first named, from an
alphabet without `0`, `o`, `1`, `l` or `i`: `k7m3p2x9`. It is unique in the
library — the tool checks each new one against all the others, retired ones
included — it never changes and is never reused, so a session written today
still points at the same thing after any rename. It says nothing of what it
names: the name and the description do, and a wrong one is corrected with
`describe`. A node not named yet has no id, and cannot be cited.

Ids were first written with a prefix the agent chose, `notice-k7m3p2x9`: a
prefix could say something false, and could never be corrected. Such an id is
read by its last 8 characters — a citation of it still leads to the same
place, and a session is never rewritten for it — and the next `sync` stores the
manifests' ids short.

The agent cites by a Markdown link whose target is an id, in its own files —
`[Notice du lave-linge K-450](id:k7m3p2x9)`: the text for the reader, the id for
the tool. Everything a manifest describes is cited that way, an entry's own
sources included. **No id goes into `document/`**: those references serve the
agent, not the reader.

### `sync` and `describe`

```bash
.venv/bin/python -m core.catalogue sync [<path or id> …]
.venv/bin/python -m core.catalogue describe <path or id> --name "…" --description "…"
```

**`sync`** brings the manifests in step with the disk, for the whole library
or for what it is given (with the topics above it). It creates the missing
manifests, adds an item for each file no item covers, follows a source you
renamed or moved by its digest, keeps its id, name and description, and
reports a named source gone or changed since it was described. It never
touches a name or a description, and a second run changes nothing. It reads
your sources only to compute their digests.

**`describe`** names and describes a topic, an entry or an item, reached by
its path or its id. The first naming gives the name and the description, and
the tool draws the id; after that, either one alone. A path inside an entry that no item
names becomes an item of its own. Describing a source records its digest as it
is now: the description was written against that content.

A manifest is written through these two commands only: the guard refuses an
edit by hand. The three commands that create an entry — `make new`, `make
import`, `make fetch` — run `sync` on it as their last step, and print what is
left to name there and in the topics above it.

### Reading the map: `find`, `ls`, `links`, `path`, `peek`

Five read-only commands answer a question from the manifests, in a few lines
whatever the size of the library. The agent calls them as
`.venv/bin/catalogue <command>`; you call the first four through `make`.

| Command | `make` | Answers |
|---|---|---|
| `find <words> [--in <topic or entry>] [--text]` | `make find Q="…" [IN=…] [TEXT=1]` | every node and item whose name or description holds every word, case and accents folded — `ete` finds « été ». One line each: kind, id, name, where. With `--text`, the lines of the text items (Markdown, extractions, journals, notes) that hold them, each under its item's name. |
| `ls [<path or id>] [-l \| -ll]` | `make ls [AT=…] [L=1\|2]` | a topic's topics and entries, with their counts; an entry's items; an item, with a directory's files — each with its date, and the id of the item it has of its own, if any: a file that arrived in a described directory has none. `-l` adds the descriptions, `-ll` the kind, size and date. Markers say what is `to describe`, `new` (on the disk, no item covers it), `to review` (a described source changed) or `gone`. |
| `links <path or id>` | `make links AT=…` | what an entry or an item cites and what cites it, from the `id:` citations alone, grouped by entry, each with the file and line that cites. |
| `path <id>` | `make path ID=…` | where an id is, from the repository's root — or, for a retired id, that it was removed, or the item it was merged into. |
| `peek <path or id> [--pages 2-5]` | — | a first look at a file, cheap enough to take before any image: a PDF's page count and the text layer of its first pages, an image's size and the date and camera it records, a text's first lines, a directory's files. |

**An answer is 20 lines at most.** Past that, its last line says how many more
there are and how to narrow the question; `--limit N` raises the bound, `0`
removes it. Nothing is read in advance: each command reads the manifests when
it runs, so the size of an answer depends on the question, never on the
library.

### Cleaning up, renaming, moving: `unused`, `remove`, `merge`, `rename`, `move`

Five commands change what the library holds, and the agent runs them only on
your word, by the `catalogue` skill's rules: it proposes, you confirm, the
command does exactly that. They have no `make` target.

| Command | Does | Refuses |
|---|---|---|
| `unused <entry>` | lists the sources of an entry that no citation points at and no tool derives from — a capture's page, an import's PDF — each with its reason. Writes nothing. | a topic, an item |
| `remove <item>… [--used]` | deletes the files of the items named and their lines in the manifest, together | anything not named exactly as an item; an item of `document/`; a directory holding an item not named as well; without `--used`, an item still cited or derived from. One refusal, and nothing is deleted. |
| `merge <item>…` | folds items back into the named item above them — the inverse of describing a file inside a directory — and leaves the files where they are | an item with no named item above it; a file already gone |
| `rename <item> <new-name>` | renames one of your files and its item together, in its own directory, keeping its extension; the manifest keeps the original name under `original:` | a directory; the agent's own files; a file a tool derives from, which `make rederive` finds by name |
| `move <item> <new-path>` | moves one item's file or directory to another path of its entry, across roles too — an investigation's pieces out of `sources/` into `study/` — keeping its id, name and description; the items inside a directory go with it, and a directory left empty is removed | anything not named exactly as an item; a destination that exists, is hidden or leaves the entry; a file a tool derives from |

**An id is never erased.** A removed item's id, and a merged one's, stays in
the entry's manifest under `retired:`, with the item's name, its path, the
date and, for a merge, the id it went into. A journal's session is never
rewritten: what it cited keeps leading somewhere, `path` says where it went,
and the id is never drawn again.

Every command also takes `--library DIR`, before the command, to work on a
copy rather than on `library/` — for a trial.

---

## The life of a document

What each command reads, what it writes, and what is left.

### `make new DOC=topic/slug [PRESET=report] [TITLE="…"]`

Creates `document/index.md` from the preset's seed, and `document/assets/`.
Nothing else: an empty directory made in advance teaches nothing and invites the
wrong file. Then the entry's `manifest.yaml`, and those of the topics above it
that had none.

### `make import SRC=x.pdf DOC=topic/slug TO=en`

| Writes | Where |
|---|---|
| the PDF you pointed at, copied | `sources/` |
| the extracted text, as `index.md` to edit | `document/` |
| the images found in the PDF | `document/assets/` |
| the extraction, intact | `study/extracted.md` |
| provenance, digest, page counts | `study/meta.json` |
| every source page as an image | `.work/pages/` |
| the entry on the map | `manifest.yaml`, and the topics' above it |

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
| the entry on the map | `manifest.yaml`, and the topics' above it |

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

### `make check-library`

Reads every document of `library/`, every discussion's journal, and every
manifest, and **writes nothing** — no `.work/`, no `out/`, no EPUB, no
manifest. It prints one line per defect, naming the document, the entry or the
topic:

| Kind | What it found |
|---|---|
| `anatomy` | something at a document's root that is none of the five |
| `derived` | `extracted.md`, `meta.json` or `pages/` in your `sources/` |
| `generator` | a `.py` outside `generators/` |
| `layout` | an `out/`, or a `source/` in the singular, anywhere in the tree |
| `load` | a front matter the build cannot read — an unknown preset or theme |
| `convert`, `xhtml` | a body that does not convert, or that the EPUB could not package |
| `journal` | a discussion's journal still in one file, or a link from its `index.md` or a topic to a file that does not exist |
| `manifest` | a directory without a manifest or with an unreadable one, a topic or entry without a name or a description, a topic's manifest listing items, two items for one path, an item whose path is gone |
| `id` | an id that is not one, or an id held twice — a copied directory, whose copy has to be told which ids it keeps |
| `citation` | an `id:` link that leads to no manifest, or one inside `document/` |

It ends with the count, and fails when it found anything. A last line counts
what remains to do without failing on it: the files no item covers, the items
not described yet, the sources changed since they were described. It is not
part of `make test`, which never reads your library.

---

## Where things are refused

`.claude/hooks/protect-paths.sh` stops an edit before it happens and says why.
Inside a document it refuses two paths:

- **`sources/`** — it is yours. Derived material belongs in `study/`, the
  document in `document/index.md`.
- **`.work/`** — a command remakes it. Change what produces it.

Anywhere in the library it refuses **`manifest.yaml`**: the catalogue keeps
its paths, kinds and digests true to the disk, and `sync` and `describe` are
how it changes.

It also refuses the pieces of an investigation — `raw/`, `documents/`,
`images/` beside its `NOTES.md`, in `study/` — which are kept as they were
received.

Outside a document it refuses `brand/tokens.css` and `brand/icons/`, which are
generated, and the `diagram-design` plugin, which is replaced on update.

---

## What the anatomy does not place yet

Two things, because nobody has needed to decide:

- **`glossary.yaml`**, a translation's term list. Read by `translate`, never by
  the build, written by you. It sits at the document's root.
- an investigation's **`threads/`**, transcriptions derived from the raw
  captures, kept with them in `sources/` because they were collected together.
