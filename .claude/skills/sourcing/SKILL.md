---
name: sourcing
description: Investigate a question across several sources that are not known in advance — live pages, archived pages, forums, PDFs, photographs — keeping a journal, the pieces received intact, and their verbatim transcriptions. Use when an answer has to be established and cross-checked rather than transcribed. It produces knowledge, never a document under library/; capturing one known page is the `fetch` skill, and rebuilding a PDF as a document is the `pdf` skill.
---

# Sourcing an investigation

**It produces knowledge, not a document.** An investigation establishes an
answer that no single source holds: which part cuts the power on a machine
whose schematic was never published, what a dead forum said about it, whether
three photos by three people agree. The output is a journal, the pieces as
they were received, and their transcriptions. A document may be written from
them afterwards, with the `pdf` skill.

Everything here comes from one real investigation — reconstructing the power-up
circuit of a Korg Electribe 2 from a handful of links, every one of which on the
main forum was dead. It produced 46 images, 11 transcribed threads and 8
manufacturer PDFs. Nothing below is theoretical: each tool was used at least
once, most between three and ten times.

## When it stops being a `fetch`

`fetch` captures **one URL, known up front, whose content becomes the
document**. An investigation starts the moment either condition breaks:

- **the sources are not known in advance** — the first link leads to a dead
  forum, the forum to an archive, the archive to a manual nobody linked;
- **there are several, and they must be checked against each other** — a forum
  claim against a datasheet, a photo against another photo.

A request that starts from one URL can still be an investigation: "find out,
from this thread and whatever it leads to, how the power circuit works" is.
The answer is not on that page; it has to be established. When the work turns
out to be capturing one page after all, hand it to `fetch`.

## What this skill refuses

- **Writing a document.** No `index.md` is ever written by an investigation. Its
  material may live in the `sources/` of the document it feeds — as the
  Electribe investigation did, in `library/electronique/repair/electribe-2/sources/`
  — but the document itself is written separately, with `pdf`.
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
| The piece | `raw/*.html.gz`, `datasheets/`, `images/` | what was received, intact — the proof. Never edited. |
| The transcription | `threads/*.md` | verbatim text, with a provenance header |
| The analysis | `NOTES.md` | cites both levels above |

Every transcription carries a **provenance header**: original URL, archive URL,
retrieval date, and **the conditions of the collection** — "the forum answered
HTTP 500 on every page; the Wayback Machine was the only way in".
`html2text.py -o … --url … --archive … --conditions …` writes it.

### Four rules

1. **Go up one rung, to the primary source.** The forum said "MOSFET CPH6302".
   The Sanyo datasheet confirmed P-channel, gave the pinout and the package
   marking `JB` — the only practical way to find the part on the board — and
   let the dimensioning be checked by calculation. A forum gives a lead; a
   manufacturer's datasheet gives a fact.
2. **Cross-check visual testimony.** Three photos of the same board area, by
   three people, on two models, three years apart. They converged, so the
   layout is stable across models and the diagnosis transposes — and the
   silkscreen settled three contradictory designations in the written sources.
   **A photo is a piece of evidence like any other**, and often more reliable
   than a forum memory.
3. **Follow the lead the source abandoned.** The main thread's author mentions in
   passing having seen "something similar in the microKORG service manual",
   then drops it. That was the best seam of the investigation: four official
   manuals, the Korg part code, the designator, the pinout, and the jack
   mechanism drawn by the manufacturer. What a source mentions without
   exploiting is worth a detour.
4. **Look elsewhere rather than force a closed door.** The Electribe 2 power
   schematic is not public. Those of three other Korg machines of the same
   family are, and they hold the part, its designator and its pinout. That
   detour produced the investigation's best result.

### Where things are

An investigation folder, wherever it lives:

```
NOTES.md            the journal
raw/                pieces: pages as received, gzipped
threads/            transcriptions, each with its provenance header
datasheets/         manufacturer PDFs
images/             archived images + manifest.json
```

**Absolute paths, always.** The working directory is reset between two tool
calls: a `cd` followed by a background task writes elsewhere, silently. It cost
a whole batch. Every tool here resolves its paths at once and prints them
resolved.

## Before any request: the access map

`references/access-map.md` records, dated, which doors were closed and which
were open — Reddit closed on every endpoint, datasheet aggregators 403, and
`polynominal.com` serving synth service manuals directly. **Read it before
probing**: it saves dozens of wasted requests. **Update it** when an
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
  `crop.py` to read the silkscreen, `crop.py --compare` when two sources
  disagree, and `archive_images.py` for what is kept — provenance recorded at
  collection time, never afterwards.
- **A manual → a fact.** `pdf_find.py` to find the page, reading its report of
  pages with no text layer; `contact_sheet.py manual.pdf` to spot a schematic by
  its title block; `pdf_render.py --scale 6 --region …` to read it.

### Two traps in PDFs

- **A page with no text layer is not an empty page.** The Korg service manuals'
  schematics yielded zero characters. A text search concludes "not in this PDF"
  exactly where the answer is: `pdf_find.py` names those pages on every run.
- **Do not trust extracted tables.** The CPH6302 characteristics table came out
  as `CV utoff Voltage GS(off) VDS=–10V, I D=0 –1mA –5 1. –V 2.` Rendered, the
  same line reads without effort. Text extraction *locates* a page; the image is
  what is read.

## Shared with the rest of the repository

The bricks under these tools are the core's, not this skill's:
`core/net.py` (probe, MIME read from the bytes, browser user agent, TLS
fallback — shared with `fetch`), `core/imaging.py` (`crop`, `contact_sheet`),
`core/pdfpage.py` (`render_page`, `text`). The repository holds one
implementation of each.
