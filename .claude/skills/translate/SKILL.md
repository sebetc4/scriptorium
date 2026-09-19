---
name: translate
description: Translate a document that is already in this library, in place, into the language its front matter states. Use when asked to translate an index.md, or after an import or a capture has left a document in the wrong language. Not for importing a PDF or capturing a page in the first place — those are the `pdf` and `fetch` skills.
---

# Translating a document

**In place, into the language the front matter states.** A document of this
library arrives untranslated — `make import` and `make fetch` extract, they do
not translate — and this skill turns its `index.md` into the target language
without touching what must not move: code, icons, links, markup, numbers, the
front matter's keys.

Translation happens **on the Markdown**, never on a PDF: that is where the
meaning is reachable and the formatting already normalised. `study/extracted.md`
is the immutable record of the extraction and is never edited.

## Where it sits

```
make import / make fetch  →  restore the structure  →  translate  →  make build, review
        (pdf / fetch)              (pdf, step 2)        (this skill)       (pdf)
```

**The structure is restored before translation, by the agent** — the imported
table of contents removed, scattered cover blocks moved into `meta:`, lines
that were a table made a table again, paragraphs cut at a page break rejoined,
headings set to the repository's hierarchy. That is the `pdf` skill's import
procedure, step 2. An engine keeps the structure it is handed and is never
asked to repair one: a local model given a mangled table returns a mangled
table, translated.

## What this skill refuses

- **Importing or capturing.** It starts from a document already in `library/`.
- **Editing `sources/`.** `extracted.md`, `meta.json` and the received page are
  the provenance; a translation leaves them as they are.
- **Asking for the language again.** See *The language, stated once*.
- **Fixing what the protected zones hold.** An unknown `:word:` stays as it is:
  the build reports it, and a translation that "corrected" it would hide the
  report.

## The language, stated once

| What | Where it is stated | Who reads it |
|---|---|---|
| The target language | `TO=` on `make import` or `make fetch`, written as `lang:` in the front matter | this skill, the hyphenation, the EPUB |
| The source language | recorded by the import and the capture as `source_language` in `study/meta.json` | this skill |

So `translate.py` asks nothing. The target is `lang:` — and a document with no
explicit `lang:` is refused rather than given the build's default. The source
is `study/meta.json`, or `--from`, or, for a document with neither, detected
and printed.

**A capture without `TO=` keeps the page's language**, and its `lang:` says so.
If the user then wants it translated, that is the one question: set `lang:` to
the target language, and the translation follows. `prepare` refuses a document
whose source and target languages are the same, and says which line to change.

**After translation, `translated_from:` is added to the front matter**, next to
`lang:`. The build ignores it; `prepare` reads it, and refuses to translate a
document a second time without `--force`.

## The procedure

The tool is run directly — no `make` target, per `docs/architecture.md` §8:

```bash
T=".venv/bin/python .claude/skills/translate/scripts/translate.py"
$T prepare <topic>/<slug>          # protect, chunk, write the job
$T run     <topic>/<slug>          # one request at a time, for the agent engine
$T apply   <topic>/<slug>          # check every chunk, then write index.md
make build DOC=<topic>/<slug>      # and review it — the pdf skill
```

1. **Look at the source pages first**, after an import: `.work/pages/` shows
   what the extraction lost — borderless tables, columns, boxes. Restore the
   structure (above) before anything else.
2. **Write the glossary if the document has terms to hold** (see *Terminology*).
3. **`prepare`** writes the job into `study/translate/` — durable, because an
   engine's answers are the work itself and `make clean` must not take a
   translation under way: the
   protected zones, the chunks, the languages, a copy of the untranslated
   `index.md` as `original.md`.
4. **`run`, answer, `run` again.** With the `agent` engine, each `run` stops at
   the first chunk without an answer and prints two paths: the request to read,
   and the answer file to write. Read the request, write **only the
   translation** to the answer file, run again. `run` validates every answer as
   it goes: a placeholder lost, doubled or invented stops it and names the file
   to fix.
5. **`apply`** checks every chunk (see *Quality control*). An error writes
   nothing; fix the answer named, run `apply` again. With no error, `index.md`
   is rewritten and the warnings are printed for the review.
6. **Build and review**, the `pdf` skill's way: rendered, page by page, and for
   an import, each page against the source PNG. A translation that passed every
   check can still be wrong in meaning — the checks see numbers and structure,
   not sense.

On a long document, **build between slices** rather than at the end: `apply`
needs every chunk, but reading the requests and answers in order is itself the
slice-by-slice review.

`prepare` can be run again at any time. Answers to chunks whose text did not
change are kept; the others are discarded, and `run` asks for them again. After
an edit to `index.md`, `apply` refuses until `prepare` has been rerun — it
never writes a translation over text it did not translate.

The workspace is durable, under `study/translate/`: `make clean` never touches
it, so a translation under way survives one. It is **spent** once `apply` has
written the document — the answers are the translation and the translation is
now in `index.md` — and `apply` says so. Nothing removes it automatically:
deleting a translation is exactly what moving it out of `.work/` prevented.

## What an engine is given, and what it keeps

### Protected zones

Before any engine sees the text, `zones.py` replaces what must not be
translated by a placeholder, `⟦n⟧`, and puts it back afterwards:

- fenced code blocks and code spans;
- icon names, `:name:` and `:name.role:` — known or not;
- the admonition marker and its type, `!!! warning` — its quoted title is
  translated;
- link and image targets, `](assets/x.svg` — the caption after it is translated;
- attribute lists, `{: .keep }`;
- raw HTML tags and comments — the text between tags is translated;
- autolinks and bare URLs;
- footnote labels, `[^1]`;
- a table's separator row.

**In the front matter**, keys are never offered. Only the strings a reader sees
are translated — `title`, `subtitle`, `eyebrow`, `footer` — and written back
into their own line, so the other keys, the comments and the layout are
untouched. `meta:` is not translated: its columns are the cover's footer and are
proposed to the user, like the rest of the cover (the `pdf` skill).

### Chunks carry their context

A sentence sent alone loses what "it" refers to and which term the previous
paragraph settled. `chunking.py` cuts the body at block boundaries — never
inside a paragraph, a list, a table, a code block or an admonition — into
chunks of up to 6,000 characters (`--budget`), preferably starting at a heading,
and **never ending on one**: a heading travels with its section. Each request
carries:

- the chunk, with its placeholders;
- **the context before it**: the whole blocks just before, up to 1,200
  characters — to read, not to translate;
- **the engine's own previous translation**, for consistency of terms and tone;
- the headings it sits under;
- the glossary entries that occur in it.

A block larger than the budget stays whole, in a chunk of its own.

### Terminology

A document's glossary lives at **the document's root**, beside `document/`,
as `glossary.yaml`. It is neither read by the build nor produced by it, so it
does not belong inside `document/`; the anatomy has no settled place for it yet
(`docs/architecture.md` §11):

```yaml
terms:                      # source term → the translation to use
  running light: chenillard
  forward voltage: tension directe
keep:                       # never translated, matched case-sensitively
  - CD4017
  - Electribe
```

It is document substance, versioned with the document. Each request receives
the entries that occur in its chunk, and `apply` checks them.

## Quality control

`apply` checks every chunk against its source, both still carrying their
placeholders. **Errors block** — nothing is written:

- a number lost or changed (`2.1` and `2,1`, `1 000` and `1000` are the same);
- a chunk returned unchanged;
- a glossary term not translated as given, or a `keep` term missing;
- a heading, a list item or a table row lost, or a row's cells changed;
- a placeholder that stood alone on its line and no longer does.

**A warning** — a length far from the source's — is printed for the review.
`--force` writes despite errors, and is for after each one has been read and
judged a false alarm: a number spelled out on purpose, a unit converted at the
user's request.

**The two-engine cross-check** runs two engines over the same job and names the
chunks where they disagree on numbers, structure or length — where a reviewer
reads first:

```bash
$T run <topic>/<slug> --engine local
$T cross-check <topic>/<slug> --engines agent local
```

It needs a second engine, which does not exist yet (below).

## The engines

`engines.py` holds the contract: a `Request` in, the translated text out, and
the six things an engine may not assume — that it sees the document, that the
text is plain prose, that the structure is its to change, that numbers and
references are text, that the glossary is advice, that the context is to be
translated. Every engine goes through the same runner and the same checks.

| Engine | State |
|---|---|
| `agent` | **The one that works.** The agent running this skill translates each chunk; its side of the interface is the request file it reads and the answer file it writes. |
| `local` | **A seam.** It raises and points to `docs/local-translation.md`, which records the target models, and to the roadmap that will implement it, `docs/roadmap/pending/local-translation/`. |

The agent engine has what no local model will: a whole document's worth of
understanding. The contract is written against it anyway, so that the local
engine is a substitution, not a rewrite — and so that its answers already go
through the checks a model's will need.
