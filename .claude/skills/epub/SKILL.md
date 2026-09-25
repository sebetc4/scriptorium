---
name: epub
description: Build and review the reflowable EPUB output of a document in this library, for reading on an e-reader. Use when asked for an EPUB, for e-ink or e-reader output, to run the contact sheet or the style proof, or when a table, a diagram or a colour has to survive reflow. Not for writing or building the paginated PDF — that is the `pdf` skill.
---

# EPUB output

**One source, two outputs that have no reason to resemble each other.** The PDF
is a fixed artefact. The EPUB reflows, and the reader chooses the text size,
the font and the background. Both are built from the same `index.md`. This skill
turns that source into an EPUB and reviews the result. It does not write the
source: that is the `pdf` skill.

The chain: `index.md` → `core/doc.py` (front matter, Markdown → HTML, shared
with the PDF) → this skill's `epub.py` (transpose, rasterise, split, flatten,
package) → `out/epub/<topic>/<slug>/<slug>.epub` → `check.py`, on every build.

The scripts live in this skill's `scripts/` and are reached through `make` from
the repository root: `epub.py`, `check.py`, `preview.py`. The stylesheet,
`theme/epub.css`, stays in `theme/` with the rest of the cascade. It is not a
preset: `core/doc.py` reads that directory's listing to learn what the presets
are, and excludes it by name.

## Who does what

| Need | Skill |
|---|---|
| Build an EPUB, run its checks, review it | **this one** |
| Write or change the document it comes from | `pdf` |
| Build or review the PDF | `pdf` |
| A diagram to insert | `diagram-design`, through `pdf` |

## What this skill refuses

- **Writing or building the paginated document.** The source is authored with
  `pdf`, and `make build` is not this skill's.
- **Being reviewed screen by screen.** See *Reviewing*.
- **Presets other than `report`.** For `slides`, `letter` and `onepager` the
  page layout *is* the point, and reflowing it would destroy it. `make epub`
  names them as skipped instead of producing a broken book.
- **Splitting a source to suit the EPUB.** The PDF keeps its full matrix from the
  same source. Adjustments go in the front matter's `epub:` key, never into the
  body.

## Building

```bash
make epub DOC=<topic>/<slug>      # -> out/epub/<topic>/<slug>/<slug>.epub
make epub                         # every `report` in the library
rsync -a out/epub/ /media/<e-reader>/documents/
```

`make epub` is a separate target from `make build`, on purpose. A document is
rebuilt dozens of times while being written, and rasterising every diagram on
each pass would slow it down for nothing. Build the EPUB when the document is
ready to read, not on every edit.

The `theme:` front-matter key does not apply here. The EPUB always uses its own
`colors.epub` mapping, because an e-reader cannot be asked which background its
reader chose (see *The e-ink rules*).

### What the build does to a document

- **Chapters**: one XHTML file per heading of the split level, usually `#`. The
  same level feeds the book's native table of contents, so the two always agree.
- **Diagrams**: every SVG is rasterised to PNG, 1600 px wide, through the same
  WeasyPrint SVG engine that renders the PDF, so both outputs show the same
  image. Its `var(--role)` are resolved first. Rasterising is this skill's own
  step, because the PDF inlines its SVG instead. The page-rendering brick
  underneath it is shared, in `core/pdfpage.py`.
- **Cover**: composed as an image in which the title dominates, since at a
  300 px thumbnail only the title stays readable.
- **Identifier**: derived from the document's path, so a rebuild does not look
  like a new book to the e-reader. The archive is byte-reproducible.

### Wide tables

A table of **more than five columns** is transposed into blocks, one per row.
Each block is titled by the row's first cell, and the other cells follow as
label/value pairs. Nothing is lost, and the result reflows at any text size. The
PDF keeps the full-width matrix: the transposition exists only in the EPUB, and
`index.md` is untouched.

A wide table that would transpose badly — a matrix whose reading is by column —
raises the threshold for its own document:

```yaml
epub:
  table-threshold: 12
```

## The e-ink rules

Four constraints, none of them deducible from knowing EPUB in general, all of
them learned here. They are enforced by the build and the checks, and they bind
what gets written into `theme/epub.css` and `brand/tokens.yaml`.

1. **No `var()` survives in an EPUB.** Readers running RMSDK do not resolve
   them, and the colour falls back to `inherit` without any error. The sources
   keep their roles, and the build *flattens* the stylesheet: every `var()` is
   resolved, and the variable declarations, `@page` and comments are dropped.
   `check.py` fails the build if a `var(` remains. A document's own `theme.css`
   follows it into the EPUB, flattened the same way, because it carries content
   typography as well as page layout. Whatever it says about the page simply
   has nothing to act on.
2. **Colour never carries a meaning alone.** An admonition's level is carried
   by its icon's glyph, which follows the reader's text colour. The tint lives
   on the rule, where losing it costs only style. Headings are never tinted: a
   fixed tint becomes unreadable on a dark background the reader chose.
3. **The signalling roles are taken at equalised luminance.** An e-ink screen
   renders colour as grey, and at brand values the orange would fade while the
   red stayed firm. `colors.epub` in `brand/tokens.yaml` maps `accent`, `alert`
   and `danger` to shades of equal grey strength, and tinted backgrounds become
   `transparent`. After editing it, run `make brand`. `check.py` verifies both
   sides: each meaningful role contrasts at least 6.5:1 with the paper, and the
   three signalling roles stay within 8 grey levels of each other.
4. **The body has neither colour, background nor embedded font.** It takes the
   reader's settings. `theme/epub.css` is written for the e-reader rather than
   derived from the paginated sheets, whose `@page` rules, millimetres and cover
   layout do not survive reflow.

For the author, this comes down to three things to know before writing:

- a table past five columns will be transposed, so there is no need to split it;
- a dense diagram will be **unreadable at six inches**, whether vector or
  bitmap. If the contact sheet shows it, redraw the diagram, not the output;
- the admonition's icon must be enough on its own to say what it is.

## The checks

`check.py` runs on **every** `make epub` and is not optional. A document with an
anomaly is reported `✗` with the list, and the command fails. It needs no eye
because each check is an assertion:

- `mimetype` is the archive's first entry, stored uncompressed;
- `META-INF/container.xml` and `OEBPS/content.opf` are present;
- no stylesheet holds an unresolved `var(`;
- every XHTML file is well-formed XML;
- the manifest and the archive match in both directions;
- every chapter is in the spine and in the table of contents;
- every spine entry exists in the manifest;
- every `<img src>` points at a manifest entry;
- the `colors.epub` contrast floor and the equal grey strengths (rule 3).

**`epubcheck`**, the reference conformance tool, runs too when it is installed.
It needs Java, so it stays optional. When it is missing, `make epub` prints that
EPUB 3 conformance was *not verified*: an absence is never reported as a
success.

## Reviewing

**An EPUB is not reviewed screen by screen. What does not reflow is.**

An EPUB has no pages. The e-reader repaginates according to its screen and the
text size the reader chose, so reviewing "screen 23 of 47" would certify a
pagination no device will ever reproduce. This is the opposite of the PDF rule,
and it is not an exception to it: the PDF is reviewed page by page *because*
its pagination is fixed.

What does stay verifiable is exactly what does not reflow, and that set is
bounded: **diagrams, transposed tables, code blocks.**

```bash
make preview DOC=<topic>/<slug>   # the contact sheet
make preview-style                # the style proof
```

- **The contact sheet** gathers a document's non-reflowing objects, numbered,
  at the real scale of a six-inch e-ink screen (1072 × 1448 px, 300 dpi), in
  one or two images: `library/<topic>/<slug>/.work/preview/contact-NN.png`. Review it for
  **every** document that has an EPUB. Read each image: is every diagram legible
  at that size, does every transposed table read as blocks, is any code line
  cut off? A document with nothing that does not reflow produces no sheet, and
  says so.
- **The style proof** renders the whole style guide — `brand/style-guide/`, the
  one document the repository owns, outside the library — through the same
  six-inch window: `brand/style-guide/.work/preview/style-NN.png`. Review it **only when
  `theme/epub.css` or `colors.epub` changes**, not for each document. It is what
  a change to the reflowable look is judged on.

Render the sheets, then actually look at the images, as with the PDF. A sheet
that has not been looked at has not been reviewed.

## Known pitfalls

- **A review image can come out blank without raising anything.** WeasyPrint
  resolves a relative `src` against the working directory unless it is given a
  `base_url`, and does not report an image it cannot find. `preview.py` passes
  one, and a test guards it. Keep that in mind before changing how the sheets
  are rendered.
- **`dark` and `epub` are both theme values inside `core/doc.py`**, but only
  `epub` is used here. Setting `theme: dark` on a document changes its PDF, not
  its EPUB.
- **A chapter-level mismatch lists every chapter as its own sub-entry.** The
  split level is computed once and handed to both the splitter and the table of
  contents. Do not compute it twice.
