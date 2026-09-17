# Phase 6: The `sourcing` Skill

---

## Status

**Current Status:** 🟢 Done (100% — 17/17)
**Started:** 2026-09-13
**Completed:** 2026-09-16
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

Turn a real investigation into a skill. This roadmap's `sources/sourcing/` holds
the inventory
of an actual enquiry — reconstructing the power-up circuit of a Korg Electribe
2 from a handful of links, every one of which on the main forum was dead — and
thirteen scripts exactly as they ran. This phase generalises the method and the
tools that earned their place, and throws away the rest.

---

## Overview

### Why This Phase Matters

The material is unusually good: nothing in it is theoretical, every entry was
used at least once and most between three and ten times, and the failure modes
are recorded at the point where they happened rather than summarised
afterwards. That kind of inventory decays fast — it lives in an untracked
directory and its author already knows it will not be rewritten.

The method is the larger half of the value. The tools save minutes; the
discipline of a journal written *during* collection, of keeping the piece
separate from its transcription, of going up one rung to the primary source,
is what decided the outcome.

### What It Enables

Investigations stop starting from zero. The map of what is blocked and what is
open alone saves dozens of wasted requests: knowing up front that Reddit is
closed on every endpoint and that `polynominal.com` serves service manuals
directly is worth more than any single script.

### Out of Scope

- Capturing one page into a document. That is `fetch`, Phase 5, and this skill
  calls it rather than reimplementing it.
- Site-specific extraction regexes and document-type mirror chains. The
  inventory is explicit that these change too fast to be worth freezing.
- The editorial work. `archive_imgs.py` carries a hand-written 29-entry plan;
  only the recompression-and-manifest mechanism is tooling.

---

## Tasks

### The method
- [x] Write `SKILL.md` in English: what an investigation is, and the moment it stops being a `fetch` — *and the refusal amended: see Notes, "Where an investigation lives"*
- [x] Write the three-status journal — established, hypothesis, still to find — and the rule that it is written during collection, not after
- [x] Write the three levels that are never mixed: the piece received intact, the verbatim transcription with its provenance header, the analysis that cites both
- [x] Write the four method rules: go up to the primary source, cross-check visual testimony, follow the lead the source abandoned, look elsewhere rather than force a closed door
- [x] Write the map of closed doors and open doors, dated, and state that it is maintained while the extraction regexes are not

### The tools that paid for themselves
- [x] `contact-sheet` — a folder of images or a PDF's pages, thumbnails carrying their filename; built on the shared brick, not a third copy
- [x] `html2text` — the stripping order that decides between readable text and an unreadable slab, with the Discourse `.json` route tried first
- [x] `crop` — fractional coordinates, never pixels, and LANCZOS on enlargement
- [x] `wayback` — CDX queries, batch availability, automatic preference for the print view, size checking across a batch — *plus three fixes found live, see Notes*
- [x] `fetch-checked` — probe, MIME verification, mirror chain, stopping at the first real hit — *the mirror chain stays in the skill, not `core/net.py`: one caller*

### The tools that unblocked a specific wall
- [x] `pdf-find` — the pages carrying a term, and the report of pages with no text layer
- [x] `pdf-render` — high-resolution render then fractional crop, the two-step procedure for reading a schematic
- [x] `imgur-album` — the full list through the API, with the thumbnail suffix removed
- [x] `archive-images` — capped recompression and a manifest carrying the originals' SHA-256
- [x] `forum-index` — title to topic id, rebuilt from archived listings

### Closing
- [x] Tests for every tool, each one covering the loud failure on an empty result
- [x] Check that every lesson in `sources/sourcing/` has a home in the skill, and mark the archive as superseded

---

## Technical Details

### Files to Modify

```
.claude/skills/sourcing/SKILL.md                 written in full
.claude/skills/sourcing/references/access-map.md  to be created
.claude/skills/sourcing/scripts/                  ten tools
.claude/skills/sourcing/tests/                    one suite per tool
sources/sourcing/                                 marked superseded, kept as archive
core/                                              the shared image and PDF bricks
```

### Dependencies

Phase 5 — `fetch-checked` and `fetch` share the probing and MIME rules, and the
shared half belongs to the core. Phase 2's shared bricks: `contact-sheet`,
`crop` and `pdf-render` are the same code the PDF review loop and `make preview`
already run.

### Constraints

Two invariants the inventory insists on, to hold in every tool:

- **Absolute paths.** The working directory is reset between calls; a `cd`
  followed by a background task writes elsewhere, in silence.
- **Fail loudly on an empty result.** A script that writes `0 messages
  transcribed` without raising produces an empty file believed full. It
  happened, and the pattern fallback in `04-transcrire-forum.sh` exists because
  of it.

The Imgur `client_id` is the one from the public web client. It may stop
working, so the tool needs a clear message rather than a crash.

---

## Acceptance Criteria

- [x] A skill named `sourcing` holds the method, the tools and their tests
- [x] Its `description` triggers on a multi-source investigation and not on capturing a single page
- [x] The ten tools run, each with tests including the empty-result case
- [x] `contact-sheet`, `crop` and `pdf-render` call the shared bricks — the repository holds one implementation of each, not two — *`make preview` turned out not to be a grid, see Notes*
- [x] Every tool uses absolute paths and raises on an empty result
- [x] The access map is present, dated, and marked as maintained
- [x] The method section covers the journal, the three levels and the four rules
- [x] Nothing in `sources/sourcing/` that was worth keeping is lost, and the archive is marked superseded
- [x] `make test` is green

---

## Notes

### Three things the investigation could not have known in advance

Each of these is worth more than the script that exploits it:

- **phpBB message permalinks are almost never archived; topic pages almost
  always are.** The eight starting links were all `p=` and had zero captures.
  The workaround — rebuild the forum index from archived listings to get the
  `t=` — is what `forum-index` generalises.
- **`&view=print` on phpBB.** A twelve-message thread: 16 KB of clean text
  against 91 KB of full page, the whole thread on one page, no navigation, no
  signatures. The counterpart is that the print view loses attachment image
  links, so a picture-heavy thread needs both variants.
- **Imgur's `h` suffix.** Forum pages only ever cite thumbnails.
  `https://i.imgur.com/<id>h.jpg` is 40 KB and unusable;
  `https://i.imgur.com/<id>.jpg` is 3 MB and readable.

### Why the contact sheet comes first

Used four times, decisive each time: fifteen repair photos, fifteen teardown
photos, nine schematic pages. One plate, one look, two images kept. The
inventory ranks it the best benefit-to-effort ratio of the whole toolkit, and
notes that the repository already owns the brick twice — in `make preview` and
in the PDF review loop. Exposing it for an arbitrary folder or an arbitrary PDF
is a few lines on top of code that already exists.

The filename written on each thumbnail is not optional: without it you see the
interesting image without knowing which one it is.

### Sizing

Seventeen tasks makes this the roadmap's largest phase. If the file grows past
700 lines while being worked, split it into `phase-6a` (method and the five
tools that paid for themselves) and `phase-6b` (the five situational tools and
the tests) rather than letting it grow.

### What was built

Ten tools in `.claude/skills/sourcing/scripts/`, 1,297 lines with their shared
helper, and **110 tests**: 93 in the skill, and 17 in `tests/` for the core
bricks added under them. The suite went 158 → 268. The tools are named with
underscores (`contact_sheet.py`, `fetch_checked.py`…) rather than the hyphens
this file uses, so the tests can import them. None of those names collides with
an installed module or with another skill's scripts, which was checked first.

- **In the core:** `imaging.crop()` (fractions, LANCZOS, and an empty region
  raises), `imaging.contact_sheet()` (a labelled grid), `pdfpage.render_page()`
  (one page, not the whole manual at `scale=6`) and `pdfpage.text()` (an empty
  string for a page with no text layer).
- **`_sourcing.py`**, the skill's helper, holds the two invariants once:
  `absolute()`, `run()` (a `ToolError` becomes a message and exit 1), `region()`
  (a region in pixels is refused as such) and `same_size()` (three or more
  identical sizes in a batch).
- **`crop.py --compare`** absorbed `09-comparer.sh`: the inventory's §8 puts the
  composite under `crop`, and it needs the same region and a common width.
- **`imgur_album.py --scan`** absorbed §3.4, the images with their context,
  because the investigation only ever did it for Imgur links.
- **`wayback.py` is also a library for `forum_index.py`,** which imports its
  `cdx()`, `raw_url()` and `piece_name()` as a sibling script.

### Where an investigation lives — the architecture was wrong

`docs/architecture.md` §5 said `sourcing` refuses "to write anything under
`library/`". The investigation this skill comes from did exactly that: its
journal, pieces and transcriptions are in
`library/electronique/repair/electribe-2/sources/`, beside the document they
feed. The same `sources/` is where `fetch` and `make import` put their source
material. **The rule now says what was actually meant:** an investigation never
writes a document, meaning an `index.md`, but its material may live in the
`sources/` of the document it feeds. §5 is corrected, with a mark saying so.

### The contact sheet had one owner, not two

The roadmap and the architecture both said the contact-sheet brick was held
twice, "in `make preview` and in the PDF review loop". Neither is a grid:
`make preview` renders objects through a six-inch window, and the review loop
renders pages one by one. The grid is new with this phase, and `sourcing` is its
only caller. It went to the core anyway, as the architecture's table of
borderline cases had already decided, and the acceptance criterion holds: one
implementation. The table now says so.

### Tested against servers, then against the real ones

The networked tools run against the root conftest's local server. That server
gained computed routes (`web.handle(prefix, fn)`), since a CDX index or an API
answers according to the query. It also gained a 20 ms shutdown poll: the
default 0.5 s was paid at every test's teardown, and the skill's suite dropped
from 17 s to 3.3 s. Every tool's tests include its empty result. The tests that
first went red on a stub rather than on the specific behaviour were checked by
mutation: html2text's three ordering rules, the print-view preference, `f=48`
matched exactly, the chain stopping at its first hit, and the eight-character
thumbnail rule. Each mutation turned its test red.

**The live runs found three defects in `wayback.py` that the local tests could
not have**, each now covered by a test:

1. **The CDX index answered 503** on the second URL of a batch, and `check`
   aborted the whole batch. It now retries (2, 5 and 10 s) on 429 and 5xx.
2. **One URL the index keeps refusing no longer sinks the others.** It is
   reported as unchecked, which is not the same as "no capture", and the run
   exits 1.
3. **The archived page opened with the Wayback toolbar.** "2 captures, 15 Nov
   2025…" was the first line of every transcription. `get` and `forum_index`
   now fetch the `<timestamp>id_/` form: the bytes the site served, which is
   also the truer piece.

Also verified live, 2026-09-13: the Imgur API still accepts the public
`client_id` and lists the `zEsqp` album; the Syntaur Discourse thread reads
through its `.json`; `p=699929` still has no capture while `t=105619` and
`t=94641` do; Reddit is still 403. These went into the access map, dated.
`forum_index.py` was **not** run live: the real `f=48` listing is some hundreds
of captures, and the tool's value does not need re-proving at that cost.

### Every lesson of `sources/sourcing/`, and its home

| Inventory | Home |
|---|---|
| §1.1 falling back when WebFetch gives up | `SKILL.md`, *How they chain*; `core/net.py` |
| §1.2 probe first | `fetch_checked.py --probe` |
| §1.3 MIME before processing | `core/net.sniff`; `fetch_checked.py`, `pdf_render.py`, `pdf_find.py`, `imgur_album.py` |
| §1.4 mirror chain | `fetch_checked.py` |
| §1.5 absolute paths, batches of 6–8 | `_sourcing.absolute`; `wayback.WORKERS`, `forum_index.WORKERS` |
| §2.1 CDX | `wayback.py list`, `wayback.cdx` |
| §2.2 batch availability | `wayback.py check` |
| §2.3 `p=` → `t=` | `forum_index.py`; `SKILL.md` |
| §2.4 print view, and both views for pictures | `wayback.py get [--both]` |
| §2.5 prefer CDX to `available`; identical sizes | access map; `_sourcing.same_size` in `wayback.py`, `imgur_album.py`, `forum_index.py` |
| §3.1 the stripping order | `html2text.strip` |
| §3.2 Discourse `.json` | `html2text.py` |
| §3.3 pattern fallback, reporting which served, loud on zero | `forum_index.PATTERNS`; site-specific post regexes deliberately not frozen, per §8 |
| §3.4 images with their context | `imgur_album.py --scan` |
| §4.1 contact sheet, labels, ~2000 px | `contact_sheet.py`; `core/imaging.contact_sheet` |
| §4.2 fractional crop, LANCZOS | `crop.py`; `core/imaging.crop` |
| §4.3 side-by-side composite | `crop.py --compare` |
| §4.4 Imgur API, `client_id`, `h` suffix | `imgur_album.py` |
| §4.5 manifest, SHA-256 of the original, 2600 px / q88 | `archive_images.py` |
| §5.1 locate a term | `pdf_find.py` |
| §5.2 pages with no text layer | `pdf_find.py`; `core/pdfpage.text` |
| §5.3 a PDF's pages as a sheet | `contact_sheet.py file.pdf` |
| §5.4 `scale=6` and a crop | `pdf_render.py` |
| §5.5 do not trust extracted tables | `SKILL.md`, *Two traps in PDFs*; `pdf_find.py` docstring |
| §6 the access map and its principle | `references/access-map.md`, dated and maintained |
| §7.1 journal, three statuses | `SKILL.md`, *The method* |
| §7.2 three levels, provenance header | `SKILL.md`; `html2text.py -o --url --archive --conditions` |
| §7.3–7.5 primary source, visual testimony, abandoned lead | `SKILL.md`, *Four rules* (with §6's principle as the fourth) |
| §8 the two invariants; what not to script | `_sourcing.py`; `SKILL.md`, *What this skill refuses* |
| scripts `README.md` — usage counts, order | `SKILL.md`, the *Used* column and *How they chain* |
| `archive_imgs.py` `PLAN` | `archive_images.py --plan`, as the editorial half, in JSON |

Both archive files carry a "superseded" notice in French, in their own
language, and are otherwise untouched.
