---
name: pdf
description: Write, build and review a paginated PDF document of this library from Markdown, with the repository's shared art direction — presets, front matter, cover, icons, diagrams — and rebuild an external PDF as such a document. Use when asked to write, create, update or rebuild a document here, to create a new document under library/, to change the art direction, to add a diagram or an icon to a document, to import a PDF into the library, or to merge, split or extract pages from a built PDF. Not for the EPUB output (the `epub` skill), for a PDF read as evidence in an investigation (`sourcing`), for translating a document (`translate`), or for capturing a web page (`fetch`).
---

# PDF documents of the library

The chain: `index.md` (Markdown and front matter) → HTML → **WeasyPrint** →
`out/pdf/<topic>/<slug>/<slug>.pdf`. No browser is involved. The formatting
comes **entirely** from the repository's CSS cascade: the Markdown content never
carries a graphic decision.

The scripts live in this skill's `scripts/` and are reached through `make` from
the repository root: `build.py`, `new.py`, `ingest.py`, `review.py`.

## Who does what

| Need | Skill |
|---|---|
| Write, build or review a document here | **this one** |
| Rebuild an external PDF as a document here | **this one**, *Importing an external PDF* |
| Merge, split, extract text or images from a built PDF | **this one**, `references/manipulation.md` |
| A diagram, schematic or chart to insert | `diagram-design` |
| The EPUB of a document, and its review | `epub` |
| Translate a document already in the library | `translate` |
| Capture one web page as a document | `fetch` |
| Read a PDF as evidence — find a term, read a schematic | `sourcing` |

The boundary with `sourcing`, since both open PDFs: **does the operation end in
an `index.md` under `library/`? Then it is this skill.** If the PDF stays a
source and the output is knowledge, it is `sourcing`, and nothing is written
under `library/`.

`diagram-design` is a plugin installed outside the repository and replaced on
every update: **never modify it**. The art direction reaches it through its
profile mechanism (see *The art direction*).

## What this skill refuses

- **Reflowable output.** An EPUB is the `epub` skill, even for a `report`.
- **Reviewing an EPUB page by page.** It has no pages; its review rule is the
  `epub` skill's.
- **Translating.** An import leaves an untranslated `index.md`; the translation
  is the `translate` skill.
- **Drawing a PDF by hand** with a canvas API. A PDF is made by `make build` from
  a document, never drawn.
- **Forms, encryption, OCR.** No document here is a form or a scan.

## What to ask, and in what order

Two decisions belong to the user. Never presume them, and do not ask them again
on every rebuild: they live in the front matter.

**On an import — the language first, before the import itself:**

> *"Which language should it be translated into?"*

It drives the import itself (`TO=`), the document's hyphenation (`lang:`) and
the whole translation. `make import` refuses to run without it rather than
guess.

**Then, for every document, before the first build:**

> *"Document theme: light, dark, or both?"*

`theme: light | dark | both` in the front matter. `both` produces two PDFs:
`<slug>.pdf` (light, the reference output) and `<slug>-dark.pdf`.

The order matters: on an import, ask for the language **before** the theme. The
language commits the extraction; the theme only the rendering.

**And one general rule: invent nothing that is displayed.** A footer, an
eyebrow, a provenance note, a collection name: anything the reader will see
that neither the source document nor the user supplied is asked for. By default
there is **no** footer — the footer carries the page numbers only. `footer:` is
filled in only when the user wanted it.

## Creating a document

```bash
make new DOC=<topic>/<slug> PRESET=<preset> TITLE="Title"
```

`<topic>` is a free directory under `library/`, at whatever depth
(`finance/2026/report-q3`). Intermediate directories are created as needed;
there is no register to update. A directory becomes a document as soon as it
holds a `document/index.md` — a document is five directories and the build
reads one of them (`docs/architecture.md` §11).

The seeds are in this skill's `assets/templates/`, one `index.md` per preset:
creating a document is this skill's job alone, and nothing reads a seed after.

Presets: `report` (default — cover, table of contents, H1 = chapter), `onepager`
(one to four pages, dense, two columns), `letter`, `slides` (landscape deck).

## Writing the content

Front matter, at the top of `index.md`:

```yaml
---
title: Report Q3               # required in practice
subtitle: One line of context
eyebrow: Report                # above the title — only if supplied
author: First Last
date: 2026-09-04
preset: report
footer: My library             # running footer — only if the user wanted one
toc: true                      # default: true except onepager/letter
cover: true                    # same
lang: en
theme: light                   # light | dark | both — ask, see above
meta: {Client: Acme, Version: "1.0"}   # the cover's footer columns
page: {size: A4, margin: 24mm 20mm}    # one-off overrides
css: [extra.css]               # additional stylesheets, relative to the document
translated_from: en            # written by the translate skill — never by hand
---
```

In the body:

- `##` structures the document and feeds the table of contents; `#` opens a page.
- The table of contents appears only from two entries on: below that it
  informs nothing, and the page it takes is lost.
- Tables, footnotes, definition lists: Markdown `extra` syntax.
- Admonition: `!!! <type> "Title"`, then a block indented by four spaces. Three
  registers, by increasing severity: `important` / `success` (green,
  editorial) — `warning` / `caution` / `attention` (orange, vigilance) —
  `danger` / `error` (red, material or bodily risk). Any other type is neutral.
  Each gets its icon automatically (see *Icons*).
- An image alone in its paragraph becomes a captioned figure:
  `![alt](assets/x.svg "Figure 1 — Caption"){: .diagram }`
- Breaks and cohesion: the classes `.break-before` and `.keep`, via `{: .keep }`.
- An HTML block containing Markdown: add `markdown="1"` on the tag.
- Icon: `:lucide-name:` — see *Icons*.

A `report` also produces an EPUB, which reflows. Wide tables, dense diagrams and
colour-only meaning behave differently there: before writing one, read the
`epub` skill, *The e-ink rules*.

### The cover — to be validated

The title block sits at the top of the page, the metadata at the bottom. Between
the two, a free zone: if the document holds a `cover.md`, its Markdown is
rendered there. That is where what must appear on the cover without belonging
to the body goes — scope, a warning, an executive summary, a version box, an
illustration.

**The cover is the page read most and proofread least: its content is proposed,
never decided.** Before building, submit what is meant to go on it — the text
of `cover.md` *and* the `meta:` columns — in a form the user can accept, refuse
or amend line by line. Announcing what has been written is not enough.

Two traps, both seen:

- **Provenance almost never interests the reader.** "Translated from English",
  "after the source document": that is process information. It lives in the
  `source:` front matter and in `sources/meta.json`, where it stays traceable.
  Put it on the cover only if the user asks — which happens, for a contractual
  or regulatory piece.
- **The `meta:` columns are a cover footer, not a datasheet.** Three or four at
  most, and only what identifies the document for its reader.

```markdown
<!-- library/<topic>/<slug>/document/cover.md -->
## What this document covers

- :target.accent: The scope
- :calendar: The period observed
```

This file follows the body's rules: icons, diagrams and the art direction's
roles work there. Its register is deliberately quieter, so as not to compete
with the title.

## Build, then review

```bash
make build DOC=<topic>/<slug>     # or `make build` for everything
make watch DOC=<topic>/<slug>     # rebuild on every change
make check DOC=<topic>/<slug>     # also keeps the HTML, to debug the CSS
```

**A PDF is never delivered without having been looked at.** Looking is paid in
images — some 1,600 tokens a page, carried by every later turn — so the look is
prepared first:

```bash
make review DOC=<topic>/<slug>              # every built variant
make review DOC=<topic>/<slug> ZOOM="1 7"   # these pages alone, full resolution
```

It writes under `library/<topic>/<slug>/.work/review/<variant>/` — beside the
document, and removed by `make clean` — and prints:

- **the checks**, read from the PDF's text layer at no image cost. Textual:
  a table-of-contents number that is not its target's page (`toc`), a glyph set
  in a font outside the art direction (`font`), a straight apostrophe
  (`apostrophe`), an address cut by hyphenation (`url-hyphen`), two letters
  carried over by a hyphenation (`short-hyphen`), text under 5 pt (`tiny-text`),
  an icon name left as text (`icon`), a missing running header or page number.
  Layout: a blank or near-blank page, text past the text block (`overflow`), a
  heading left at the foot of a page (`orphan-heading`), a justified line
  stretched far wider than the page's (`loose-line`). A check **points at a
  page**; the layout ones are confirmed by looking.
- **the sheets**, `sheet-NN.png`: the pages four to an image, labelled, sized
  just under the budget past which an image is scaled down anyway.

Chosen and accepted, so not reported: a justified line stretched because the
next one opens with inline code, which never breaks (`white-space: nowrap`).

Then the look itself, in this order: every sheet; then, alone and at full
resolution, the cover — the page read most — and every page a check named or a
sheet made doubtful. On them: no stray blank page, no heading orphaned at the
bottom of a page, no table cut in the wrong place, no overflowing image, correct
headers and page numbers, acceptable hyphenation for the document's language.
`make review` refuses a PDF older than its sources: build first.

With `theme: both`, two PDFs come out and **both are reviewed**: the dark
variant has its own contrast pitfalls.

**Delegate the look to the `pdf-reviewer` agent** (`.claude/agents/`) rather
than reading the images here: it runs `make review`, reads every sheet, zooms on
the cover and at most five doubtful pages, and returns only the defects — the
checks as printed, and what it saw. It reviews and does not diagnose: finding
causes and fixing stay here. Run it once per variant — both at once with
`theme: both` — and say when the document is an import; then build and review
again.

## The art direction

`brand/tokens.yaml` is **the only** source of brand values. It has two levels:
`palette` holds the raw brand ramps, `colors` maps the semantic roles onto them
**by reference** — `primary.600`, `neutral.light.100`, or
`alpha(primary.600, 0.10)` for a tint. Never copy a hex value into `colors`: the
reference is what prevents drift. After a change:

```bash
make brand
```

which regenerates `brand/tokens.css` (read by the PDFs) **and** the profile
`~/.diagram-design/profiles/scriptorium.md`, selected by the `.diagram-design`
marker at the root (read by `diagram-design`). Both share the same semantic
roles — `paper`, `ink`, `muted`, `soft`, `rule`, `accent`, `link` — so a
diagram fits in without retouching.

The rules, held in every document:

- **Three colours, three uses that do not mix.** `accent` (green) is
  **editorial**: it underlines what matters, once or twice a page. `alert`
  (orange) and `danger` (red) are **signalling**: they state a risk, never an
  emphasis. They are exempt from the once-or-twice budget — a real danger is
  flagged as often as it occurs — but an alert placed on what is not risky
  devalues every other one.
- `alert` when the mistake costs time or skews a result; `danger` when it
  destroys equipment or injures. When in doubt, `alert`.
- Never a hard-coded hexadecimal value in a stylesheet or a document: always
  `var(--<role>)`.
- Headings in `--font-head`, body in `--font-body`, technical text in
  `--font-mono`. A fourth family does not come in.
- `alert` and `danger` are **not** propagated to `diagram-design`, whose model
  holds a single accent hue. A diagram that must state a risk states it by its
  shape and labels, not by a colour it does not know.

### Departing from the theme for one document

The cascade, from the most general to the most specific — each level redefines
only its departure:

```
brand/tokens.css → theme/base.css → theme/code.css → theme/page.css
  → theme/<preset>.css → front matter `page:` → <doc>/document/theme.css → front matter `css:`
```

A one-off format need goes through the front matter. A graphic need specific to
the document goes through a `theme.css` **beside its `index.md`**:

```css
/* library/finance/report-q3/document/theme.css */
:root { --accent: var(--link); }
.cover h1 { font-size: 48pt; }
```

Change `theme/*.css` or `brand/tokens.yaml` only when the change must apply to
the **whole** library — and say so explicitly to the user.

## Inserting a diagram

1. Invoke `diagram-design`; it reads the art direction through the marker.
2. Save the rendering **as SVG** in `library/<topic>/<slug>/document/assets/`.
3. **Replace the SVG's hex values with roles**: `fill="var(--paper-2)"`,
   `stroke="var(--accent)"`, `font-family="var(--font-sans)"`.
4. Reference it as a captioned figure (see *Writing the content*), class
   `.diagram`.

The build inlines the SVG into the page and resolves its `var(--role)` against
the document's cascade — so a diagram follows the art direction **and** a
document's local override, without being regenerated. The build does the
substitution because WeasyPrint does not resolve `var()` inside an SVG, and a
role left unresolved would fall to black.

Internal identifiers (arrow markers, gradients) are prefixed at inlining, so
several diagrams can coexist in one document.

WeasyPrint renders SVG as vectors. Avoid PNG except for photographs.

## Icons

The **Lucide** set ships in `brand/icons/` (2057 SVGs, the version pinned in
`brand/icons/VERSION`). Nothing to install, nothing to download while writing.

```markdown
Status :circle-check.accent: compliant

- :arrow-right: First step
- :triangle-alert.muted: Point of vigilance
```

- `:name:` takes the `ink` role; suffix it with `.accent`, `.alert`, `.danger`,
  `.muted` or `.soft`. No other colour choice exists: the art direction stays
  closed. `.alert` and `.danger` follow the admonitions' rule — they state a
  risk, not an emphasis.
- A list entry opening on an icon has its bullet replaced.
- Admonitions get the icon **and the colour** of their type automatically
  (`important` → `circle-alert` in green, `warning` → `triangle-alert` in
  orange, `danger` → `octagon-alert` in red, `note` → `info`, neutral). Writing
  one yourself in the title turns the automatism off for that admonition.
- An unknown name does not fail: the source text is restored as it was and the
  build reports it. Valid names are those of `brand/icons/*.svg` — search with
  `ls brand/icons | grep <word>`, never guess.
- Never edit a file in `brand/icons/`: `make icons` regenerates it.
  `make icons V=1.41.0` changes version.

As for diagrams, the stroke colour and width are applied at build time
(`--icon-stroke`, `--icon-size` in `brand/tokens.yaml`): WeasyPrint follows
neither `currentColor` nor `var()` inside an SVG.

## Importing an external PDF

The import produces an ordinary document of the library — not a special format.
`make build` then applies the art direction to it, as to any other document.

This is reading a PDF **to rebuild it**. Reading one to know what it says — a
term across a manual, a page with no text layer, a schematic to crop — ends in
knowledge rather than a document, and is the `sourcing` skill.

**Ask for the target language first** (see *What to ask*). Then:

```bash
make import SRC=report.pdf DOC=watch/wto-report TO=fr
```

`TO` is mandatory — and named so because `LANG` is a standard environment
variable, which make would inherit (`fr_FR.UTF-8`).

It writes:

| Path | Content |
|---|---|
| `document/index.md` | front matter + extracted text, **to translate in place** |
| `document/assets/` | the extracted raster images, at their original resolution |
| `sources/extracted.md` | the raw extraction — an immutable reference, never edit it |
| `sources/meta.json` | provenance: path, SHA-256 digest, pages, metadata |
| `sources/pages/*.png` | each source page as an image (not versioned) |

### The procedure

0. **Ask for the target language**, before the import. Then, once the document
   exists, **ask for the theme** and write it into the front matter.
1. **Look at the source pages** in `sources/pages/` before writing anything. The
   extraction renders the text faithfully, not the layout: what is lost — tables
   without rules, columns, boxes, visual hierarchies — is only restored by
   seeing the page.
2. **Restore the structure**, before any translation:
   - delete the imported table of contents — the preset generates one;
   - delete the scattered cover blocks (`DATE`, `VERSION`, isolated values) and
     carry them into the `meta:` front matter;
   - rebuild as a Markdown table what arrived as scattered lines;
   - rejoin the paragraphs the extraction cut at a page break;
   - replace the imported headings with the repository's `##`/`###` hierarchy;
   - empty the front matter of what the import could not infer — a wrong title,
     a useless eyebrow.
3. **Translate** `index.md` in place — the `translate` skill. It comes after the
   structure on purpose: a translation engine keeps the structure it is given
   and never repairs it.
4. **Redraw the vector figures.** A vector drawing is not extracted: the import
   names the pages concerned. Redo them with `diagram-design` (see *Inserting a
   diagram*), never as a screenshot.
5. **Build and review** (see *Build, then review*), comparing each page with the
   matching source PNG: nothing omitted, nothing duplicated, the order kept.

### What the import does not do

- It does not translate. Translation happens on the Markdown, where the meaning
  is reachable and the formatting already normalised.
- It detects only tables **with rules**. A borderless table arrives as lines of
  text: step 2 rebuilds it, from the page's PNG.
- It does not recover the source document's fonts. On purpose: the rebuilt
  document carries the repository's art direction, not the original's.

### Options

Passed through `IMPORT_FLAGS=`: `--pages 3-18` limits the imported range,
`--preset` chooses the register, `--force` overwrites an existing destination,
`--no-page-images` skips rendering the pages of a very long document.

## Known pitfalls

- An empty element placed before `.cover` creates a blank page: the cover is a
  named page, and any content preceding it takes a page of its own.
- `display: none` also removes `string-set`: do not use it to hide a metadata
  carrier.
- CSS grid is not supported by WeasyPrint. Use flex, `columns`, or a table.
- `target-counter()` resolves to 0 inside a `display: flex` container: every
  table-of-contents entry would read page 0. Lay such a line out as a table.
- `body` keeps the user agent's 8px margin unless it is reset: the text then
  sits inside the page margins while the running headers sit on them.
- A named page (`@page cover`) inherits from `@page`: do not redeclare margin or
  size there, or a preset that changes the geometry would be ignored.
- Code highlighting goes through `theme/code.css`, which uses only `ink`, `soft`
  and `accent`. Do not bring back a coloured Pygments theme.
- A font missing from the machine is replaced silently. Check with
  `fc-list : family | grep -i "<name>"` before writing it into `tokens.yaml`.
- `attr_list` cannot target a `<ul>`, only its `<li>`: do not try to put a class
  on a list from the Markdown.
- A `:word:` in running text — or in an imported source — can look like an icon.
  The rendering is safe — unknown name, text restored, the build reports it —
  but avoid the phrasing when it may confuse. Code blocks and spans are intact
  by construction.
