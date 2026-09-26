---
name: sourcing
description: Investigate a question across several sources that are not known in advance — live pages, archived pages, forums, PDFs, photographs — keeping a journal, the pieces received intact, and their verbatim transcriptions. Use when an answer has to be established and cross-checked rather than transcribed. It produces knowledge, never a document under library/; capturing one known page is the `fetch` skill, and rebuilding a PDF as a document is the `pdf` skill.
---

# Sourcing an investigation

**It produces knowledge, not a document.** An investigation establishes an
answer that no single source holds: what a document nobody published would
have said, what a dead forum said about it, whether three photos by three
people agree. The output is a journal, the pieces as
they were received, and their transcriptions. A document may be written from
them afterwards, with the `pdf` skill.

Everything here comes from a real investigation, started from a handful of
links whose main forum was dead. It produced dozens of images, a dozen
transcribed threads and several PDFs. Nothing below is theoretical: each tool
was used at least once, most between three and ten times.

## When it stops being a `fetch`

`fetch` captures **one URL, known up front, whose content becomes the
document**. An investigation starts the moment either condition breaks:

- **the sources are not known in advance** — the first link leads to a dead
  forum, the forum to an archive, the archive to a manual nobody linked;
- **there are several, and they must be checked against each other** — a forum
  claim against a primary source, a photo against another photo.

A request that starts from one URL can still be an investigation: "find out,
from this thread and whatever it leads to, what really happened" is.
The answer is not on that page; it has to be established. When the work turns
out to be capturing one page after all, hand it to `fetch`.

## What this skill refuses

- **Writing a document.** No `index.md` is ever written by an investigation.
  When it feeds a document of the library, it lives in that entry's `study/`
  — its journal and the pieces it found (*In the library*, below) — and the
  document itself is written separately, with `pdf`.
- **Putting what it found in `sources/`.** `sources/` keeps what the user gave
  or pointed at. A page, a thread, a document the investigation found is the
  agent's finding, and goes beside its journal.
- **Presenting a second-hand rendering as a primary source.** A search engine's
  excerpt of a dead page is a lead, never a piece to cite.
- **Presenting a hypothesis as established.** That is what the journal is for.
- **Freezing a site's extraction regexes or a document type's mirror list.**
  They change too fast. The access map is maintained; those are not.

## The method

The tools save minutes. The method decided the outcome.

### The journal, three statuses, written during collection

One file, `NOTES.md`, from the first hour, with three separate sections:

- **Established** — each point with its verbatim quotation and its source;
- **Hypothesis** — whose, on what basis, with the reservations;
- **Still to find** — as checkboxes.

It is written **during** the collection, not after. Three times a later source
moved a point from one section to another. Without the journal the nuance is
lost, and the final document asserts what was only a supposition.

A checked box says **what was found**, including "read through, nothing
usable". Two threads were opened twice for want of that line.

### Three levels, never mixed

| Level | Where | What it is |
|---|---|---|
| The piece | `raw/*.html.gz`, `documents/`, `images/` | what was received, intact — the proof. Never edited. |
| The transcription | `threads/*.md` | verbatim text, with a provenance header |
| The analysis | `NOTES.md` | cites both levels above — by id, in the library |

Every transcription carries a **provenance header**: original URL, archive URL,
retrieval date, and **the conditions of the collection** — "the forum answered
HTTP 500 on every page; the Wayback Machine was the only way in".
`html2text.py -o … --url … --archive … --conditions …` writes it.

### Four rules

1. **Go up one rung, to the primary source.** A forum names a thing, a figure,
   a date; the primary source — the maker's documentation, the original
   record, the text itself — confirms it, and gives what the forum left out:
   the detail that lets the claim be checked. A forum gives a lead; a primary
   source gives a fact.
2. **Cross-check visual testimony.** Three photos of the same thing, by three
   people, years apart: when they converge, what they show holds beyond one
   case — and a label or an inscription read on them can settle what the
   written sources disagree on. **A photo is a piece of evidence like any
   other**, and often more reliable than a remembered account.
3. **Follow the lead the source abandoned.** A source mentions in passing a
   document it has seen, then drops it. That aside can be the best seam of an
   investigation: it led to official documents holding what no other source
   had. What a source mentions without exploiting is worth a detour.
4. **Look elsewhere rather than force a closed door.** The document that would
   answer is not public; a close relative of it often is — another model of
   the same family, an earlier edition, a neighbouring case — and holds the
   same answer. That detour produced the investigation's best result.

### Where things are

An investigation folder, wherever it lives:

```
NOTES.md            the journal
raw/                pieces: pages as received, gzipped
threads/            transcriptions, each with its provenance header
documents/          PDFs and other documents received
images/             archived images + manifest.json
```

**Absolute paths, always.** The working directory is reset between two tool
calls: a `cd` followed by a background task writes elsewhere, silently. It cost
a whole batch. Every tool here resolves its paths at once and prints them
resolved.

### In the library

An investigation that feeds a document of the library has that entry's
`study/` for its folder: `study/NOTES.md`, and beside it `study/raw/`,
`study/threads/`, `study/documents/`, `study/images/`. **What it found is the
agent's, not the user's**: `sources/` keeps what the user gave or pointed at —
their notes, their photos, the PDF they imported, the page they had captured.
The guard refuses an edit in `raw/`, `documents/` and `images/` beside a
`NOTES.md`: the pieces are kept as received.

There, the library's map applies:

- **Before collecting, look in the library.** `.venv/bin/catalogue find <the
  subject's words>`: a piece the library already holds is a piece already
  received. Read what the search points at, and cite it.
- **Its pieces become items.** After each batch of collection, `sync` the
  entry: each new directory of `study/` is an item. A piece the journal cites
  alone — the document a claim rests on, the page that settled a point, the
  image a detail was read from — gets an item of its own, named and
  described by the `catalogue` skill from what the journal says of it; a batch
  cited only as a whole stays in its directory's item.
- **`NOTES.md` cites them by id**, never by path — the path may stay as the
  link's text: [`raw/forum-page.html.gz`](id:k7m3p2x9). A
  rename or a move no longer breaks the journal, and `links <piece>` says
  which lines of the analysis rest on it.

An investigation whose pieces sit in `sources/` predates this layout. On the
user's word, each directory goes to `study/` with
`.venv/bin/catalogue move <item> study/<dir>`, which keeps its id, its name
and its description.

## Before any request: the access map

`references/access-map.md` records, dated, which doors were closed and which
were open — Reddit closed on every endpoint, a search engine's HTML answering
with a challenge, the Wayback Machine reached through its CDX index. **Read it
before probing**: it saves dozens of wasted requests. **Update it** when an
investigation meets a wall or a door it does not list. It is the one piece of
site knowledge worth maintaining.

## The tools

In `scripts/`, run directly — no `make` target, since their subject is a URL, a
file or a PDF outside the library:

```bash
.venv/bin/python .claude/skills/sourcing/scripts/<tool>.py --help
```

All of them fail out loud: a tool that finds nothing exits 1 with the reason,
and writes nothing it could be believed to have written. Identical sizes across
a downloaded batch (three error pages) fail the batch.

### The ones that paid for themselves

| Tool | Does | Used |
|---|---|---|
| `contact_sheet.py <folder\|pdf> -o sheet.png [--pages 3-12]` | one look at a folder of images or a PDF's pages; every thumbnail carries its filename or page number | 4×, decisive each time |
| `html2text.py <file\|url> [-o t.md --url --archive --conditions]` | readable text, stripping in the order that avoids a slab; a Discourse thread goes through its `.json` first | ~10× |
| `crop.py <image> --region x0,y0,x1,y1 [--width N] [--compare other]` | a region in fractions, enlarged with LANCZOS; `--compare` puts the same region of two photos side by side | ~8× |
| `wayback.py list\|check\|get` | the CDX index: captures of a pattern, availability of a batch, the latest capture — phpBB print view preferred, without the archive toolbar | ~15× |
| `fetch_checked.py URL… -o file [--expect MIME]` · `--probe URL…` | a mirror chain stopping at the first URL that really serves the type; the probe line for each | continuously |

### The ones that unblocked a specific wall

| Tool | Does | Used |
|---|---|---|
| `pdf_find.py TERM pdf…` | the pages carrying a term, ignoring case and spacing, **and the pages with no text layer**, which a text search cannot see | 4× |
| `pdf_render.py pdf PAGE [--scale 6] [--region …]` | one page at high resolution, cropped | 6× |
| `imgur_album.py ALBUM [--download dir]` · `--scan page.html` | an album in full through the API; a page's Imgur images as originals, with the text before each | 2×, without which 15 images were lost |
| `archive_images.py folder\|--plan plan.json --dest images/` | capped recompression and a manifest with each original's SHA-256 | 2× |
| `forum_index.py "site/viewforum.php?f=48" [--grep …]` | title → topic id, rebuilt from the archived listings of a dead forum | 1×, and it unblocked everything |

### How they chain

- **Start with a probe.** `fetch_checked.py --probe` on every starting URL: in
  three seconds a whole forum answered 500, and the work moved to the archives.
- **When the agent's own web tool gives up, these do not.** WebFetch stops on an
  expired certificate, a filtered user agent, or a domain it will not fetch.
  All three were met on the first links. The tools here send a browser's user
  agent and fall back on an unverified connection, saying so: without that
  fallback, the investigation stopped at its first link.
- **A dead site → the archive.** `wayback.py check` on the batch first, then
  `get`. phpBB **message permalinks (`p=`) are almost never archived; topic
  pages (`t=`) almost always are.** When all you have is `p=`, run
  `forum_index.py` on the sub-forum's listing, find the title, take its `t=`.
- **A thread → a transcription.** `wayback.py get` keeps the print view — the
  whole thread on one page, 16 kB against 91 — then `html2text.py -o` with the
  header. The print view loses attachment links: for a thread whose value is in
  its pictures, `get --both`, then `imgur_album.py --scan` on the full view.
  **Imgur's `h` suffix** marks a 40 kB thumbnail; the tools strip it to reach
  the 3 MB original.
- **A pile of images → the two that matter.** `contact_sheet.py`, then
  `crop.py` to read the detail, `crop.py --compare` when two sources
  disagree, and `archive_images.py` for what is kept — provenance recorded at
  collection time, never afterwards.
- **A manual → a fact.** `pdf_find.py` to find the page, reading its report of
  pages with no text layer; `contact_sheet.py manual.pdf` to spot a figure by
  its title block; `pdf_render.py --scale 6 --region …` to read it.

### Two traps in PDFs

- **A page with no text layer is not an empty page.** A drawing, a scan, a
  figure yields zero characters. A text search concludes "not in this PDF"
  exactly where the answer is: `pdf_find.py` names those pages on every run.
- **Do not trust extracted tables.** A table of values comes out with its
  subscripts torn from their symbols and its numbers split across cells, as
  `CV utoff Value X(off) Y=–10, Z=0 –1 –5 1. –V 2.`; rendered, the same line
  reads without effort. Text extraction *locates* a page; the image is what
  is read.

## Shared with the rest of the repository

The bricks under these tools are the core's, not this skill's:
`core/net.py` (probe, MIME read from the bytes, browser user agent, TLS
fallback — shared with `fetch`), `core/imaging.py` (`crop`, `contact_sheet`),
`core/pdfpage.py` (`render_page`, `text`). The repository holds one
implementation of each.
