# scriptorium

A library of documents written in Markdown and built to paginated PDF and
reflowable EPUB, with one shared art direction that each document can override.
Around the build sit the jobs that bring a document into the library: importing
an external PDF, capturing a web page, translating, and investigating a question
across sources.

```bash
make setup
make new DOC=finance/report-q3 TITLE="Report Q3"
make build DOC=finance/report-q3
# -> out/pdf/finance/report-q3/report-q3.pdf
```

## How it works

`index.md` → HTML → **WeasyPrint** → PDF. No browser, no LaTeX: the only
dependencies are Python and the Pango/Cairo system libraries.

A document is any directory under `library/` holding a `document/index.md`.
The directories above it are topics, at any depth, and nothing has to be
declared anywhere. Beside `document/` a document may hold four more directories,
each with one job — `sources/` is yours, `study/` is what the tools learned,
`generators/` is code that draws, `.work/` is anything a command can remake.
[`docs/document.md`](docs/document.md) is the manual.

The repository is organised around six Claude Code skills, one per job. Each
carries its own rules, scripts and tests under `.claude/skills/<name>/`; what two
or more of them share lives in the `core/` package. A seventh,
`session-review`, stands outside that chain: it produces no document and
measures a finished task instead.

| Skill | Job |
|---|---|
| `pdf` | Write, build and review a paginated document; import an external PDF |
| `epub` | The reflowable output and its review |
| `fetch` | Capture one web page as a document |
| `sourcing` | Investigate a question across sources — produces knowledge, not a document |
| `discussion` | Talk a subject through with the user before its document exists, keeping a journal any session resumes from |
| `translate` | Translate a document already in the library, in place |
| `session-review` | Measure a finished task and write the review to `reviews/` — outside the production chain |

`docs/architecture.md` explains why each directory exists and where each skill
stops.

## The art direction

`brand/tokens.yaml` is the single source. It separates the brand palette (raw
ramps) from the mapping onto semantic roles, which refers to it by path —
`primary.600`, `alpha(neutral.light.1200, 0.12)` — rather than copying hex
values. `make brand` propagates it to two consumers:

- `brand/tokens.css`, at the head of the cascade applied to the PDFs;
- `~/.diagram-design/profiles/scriptorium.md`, the profile read by the
  `diagram-design` plugin (selected by the `.diagram-design` marker).

Both share the same semantic roles, so a diagram fits into a document without
retouching. `diagram-design` is installed as a plugin outside the repository and
never modified: its profile is tuned, not the plugin.

Three colours carry meaning: `accent` (green) is editorial and underlines;
`alert` (orange) and `danger` (red) are signals and state a risk.

Diagrams are written with the same roles (`fill="var(--accent)"`): the build
inlines them into the page and resolves their variables, so a diagram follows
the art direction and a document's local override without being regenerated.

The **Lucide** icon set ships in `brand/icons/` (pinned version) and is written
`:circle-check:` or `:circle-check.accent:` in the Markdown. `make icons`
reinstalls it or changes its version.

A `brand/logo.svg` appears at the top of the covers; brand fonts are declared in
`type.faces` and placed in `brand/fonts/`.

## Overriding the theme

From the most general to the most specific:

```
brand/tokens.css → theme/base.css → theme/code.css → theme/page.css
  → theme/<preset>.css → front matter `page:` → <doc>/theme.css → front matter `css:`
```

A document writes only its difference: a `theme.css` in its directory is enough
to give it its own accent or cover, without touching anything else.

Presets: `report` (cover, table of contents, one chapter per H1), `onepager`,
`letter`, `slides`.

## Light, dark, or both

`theme: light | dark | both` in the front matter. `both` produces `<slug>.pdf`
and `<slug>-dark.pdf` in one pass, from the same source.

A `cover.md` in the document's directory fills the free area of the cover,
between the title block and the metadata.

## Reading on an e-reader

```bash
make epub DOC=electronique/components/led
# -> out/epub/electronique/components/led/led.epub
```

The PDF is a fixed artefact; the EPUB reflows, and the reader chooses the text
size, the font and the background. Both outputs start from the same source and
have no reason to look alike.

Three visible consequences:

- **body text has no imposed colour or font** — it takes the e-reader's
  settings;
- **signalling colours are taken at equalised luminance**: an e-ink screen
  renders them as grey, and at brand values the orange would fade while the red
  stayed stark. The meaning is carried by the icon; the hue only supports it;
- **tables wider than five columns become blocks**, one per row. The PDF keeps
  its full-width matrix.

Diagrams are rasterised by the SVG engine that produces the PDFs, so both outputs
show the same image. `make epub` checks every archive it writes.

## Reviewing an EPUB

```bash
make preview DOC=electronique/components/led   # what does not reflow
make preview-style                             # the whole style guide
```

An EPUB has no pages, so there is no screen to review: the e-reader repaginates
to its own. The review covers the only objects that do not reflow — diagrams,
transposed tables, code blocks — gathered on a sheet at the true scale of a
six-inch screen.

## Importing an external PDF

```bash
make import SRC=report.pdf DOC=watch/wto-report TO=en
```

`TO` is the target language, required — the tool never presumes it. The
extraction yields the text, the images recompressed according to their nature,
and each page as a PNG. It produces an ordinary document: its structure is
restored first, then the `translate` skill translates `index.md` in place, and
`make build` applies the art direction. `study/extracted.md` keeps the
extraction intact as a reference.

## Capturing a web page

```bash
make fetch URL=https://example.org/article DOC=watch/article TO=en
```

The content is extracted without the navigation, the images are downloaded and
recompressed, and the received page is kept gzipped — a web page changes or
disappears. The capture fails loudly on an HTTP error, a PDF, or a page with no
text. `RENDER=1` goes through a headless browser for client-rendered pages
(Playwright, not installed by default); the tool detects the case and says so.

## Translating

The `translate` skill translates a document in place into the language its
front matter states, chunk by chunk, with code, icon names and front-matter keys
protected and a per-document glossary. Today the agent is the engine; the
contract for a local model is in `docs/local-translation.md`.

## Tests

```bash
make test
```

Each skill runs its own suite, collected with the core's into one run. The
suite never reads `library/`: its tests run on fictional documents under
`tests/fixtures/library/`, copied to a temporary directory, so it passes on a
fresh clone and writes nothing under `out/`.

```bash
make check-library
```

checks your own library instead, and writes nothing: a document root holding
anything but the five roles, derived material in `sources/`, a front matter
that does not load, a body the EPUB could not package. One line per defect,
naming the document.

## Example

`library/exemples/guide-de-style/` documents the art direction and serves as the
rendering test.
