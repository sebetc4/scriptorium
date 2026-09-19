# Summary — The Anatomy Of A Document

---

## Where We Started

`out/` held five directories and three of them were not documents: 25 MB of
review sheets, the EPUB contact sheets, and a translation workspace — working
artefacts of one document, kept in a parallel tree joined to it by nothing but a
path convention.

The inside of a document had never been declared at all. `core/doc.py` knew one
fact — `index.md` is the entry — and the rest was habit: `assets/` because the
first document had images, `sources/` because the first import needed somewhere
to put a PDF. Four skills wrote into a document directory and none agreed with
the others about what belongs where. `sources/` held, undifferentiated, what the
user had provided, what a script had derived from it, and the code that drew its
figures.

Neither cost a reader anything. Both cost every future document and every future
skill, because nobody could say where a new kind of file belonged, and so it
landed wherever the last one did.

---

## Where We Landed

A document is five directories, and the build reads one of them:

```
library/<topic…>/<slug>/
  document/     index.md, cover.md, theme.css, assets/
  sources/      what the user gave it
  study/        what the tools learned from those sources
  generators/   code that draws an asset
  .work/        everything a command can make again
```

`out/` holds `pdf/` and `epub/`. `make clean` takes `out/` and every `.work/`,
and `make clean DOC=` takes one document's. A hook refuses an edit to `sources/`
or `.work/`, a test fails when a document holds anything the anatomy does not
place, and a second test fails when the five constants in `core/doc.py` and the
three documents describing them stop agreeing.

`docs/document.md` is the manual; `docs/architecture.md` §11 is the argument.

Eight documents migrated. 15 PDFs and 8 EPUBs, compared against the
fingerprints taken before anything moved: identical. 510 tests, up from 485.

---

## What Each Phase Delivered

**Phase 0 — the anatomy.** Two documents and no behaviour change: §11 states the
five roles, the cut that decides the rest, and the acquire / derive line. Its
result was a definition, not a description — the cut had to be stated as
*consumption*, because "the agent's files" and "the user's files" reads as
authorship and authorship places a hand-drawn schematic wrongly.

**Phase 1 — `document/`.** The only phase that touched the core. Discovery
returns the root that holds `document/`, so the slug, the title and the output
path stay right. Two silent failures reached a successful build and neither was
caught by 485 passing tests: no SVG was inlined any more, so every schematic
would have shipped with unresolved colours in dark; and every image in every
EPUB was renamed. Both found by comparing the outputs.

**Phase 2 — `.work/`.** The review sheets and EPUB proofs moved into the
document; `out/` became an export folder. The care went into `make clean`, the
first command here that deletes inside user content: `work_dirs()` asks the
document roots rather than globbing for `.work`, because a glob would have
deleted somebody's notes the first time they named a folder that way.

**Phase 3 — received, learned, making.** The premise was tested before anything
moved and held: the same input gives the same extraction. It also showed that
`ingest.py` had never kept the source, so re-derivation had never been
guaranteed — `meta.json` recorded a path under `pdfs/`, a directory renamed a
roadmap earlier. The import copies the source now, and `make rederive` rebuilds
`study/extracted.md` from `sources/` alone.

**Phase 4 — the guard.** `protect-paths.sh` already refused `sources/`, so the
task looked like changing a message. Its second check had been dead for three
days: moving `NOTES.md` to `study/` turned off the protection of every
investigation's pieces, in silence, under 499 passing tests.

**Phase 5 — the documentation.** `docs/document.md`, written for someone who has
never seen the repository. Three statements were known to have become false;
five had, and two links had been dead since the previous roadmap closed.

---

## What We Learned

**Classify by role, not by content type.** The rule that decided everything is
"does the build read it" — the one boundary a wrong answer makes visible, since
a file on the wrong side breaks a build on the next run. Every other
misplacement is silent. A taxonomy by content type would have blurred within
months: a transcription is neither source nor derived, a hand-drawn SVG is both
expensive and generated.

**Disposable has two halves, and the second carries the weight.** A file is
disposable when a command can make it again *and nothing is lost by making it
later*. The first half alone would have sent `extracted.md` to `.work/`, and a
translation workspace with it — which the user caught before it happened:
translate half a hundred-page document, run `make clean`, lose everything.
Re-running produces *a* translation, not the one that was under way.

**Four silent breakages, one shape.** An SVG path resolved against the wrong
root; an EPUB image named after a path that gained a segment; a guard looking
for a journal beside a directory it no longer sits beside; two links pointing at
a roadmap that moved. Every time the code kept running and said nothing, and
every time a test suite passed over it. What they share is a rule expressed as a
filename pattern and a file that moved. The anatomy does not prevent that — it
makes the patterns fewer and gives them one place to live.

**Compare the outputs, not just the tests.** 485 tests passed on a tree where no
SVG was being inlined. The failure was invisible in every way a test currently
looks: the build succeeded, the pages were the right size, the figures were on
them, the image count never moved. It showed as a changed text digest, because
an inlined SVG puts its labels in the text layer and a linked one does not.

**A field written once and never read back is not provenance, it is a comment.**
`meta.json` recorded where a PDF came from for two years, and the path stopped
existing when the repository reorganised. Nothing noticed, because nothing ever
read it.

**Name an exception rather than widening a rule.** One document keeps an
investigation's material at its root. It is one entry in a test, with its
reason, and the day the document is reshaped the test says whether anything
still needs it. Widening `ROLES` would have let every document hold those names
for ever.

---

## What We Are Leaving Open

- **`glossary.yaml`** — a translation's term list, read by `translate`, never by
  the build, written by the user. It sits at the document's root because the
  anatomy has no settled place for it and no document has one today.
- **An investigation's `threads/`** — transcriptions, derived in the strict
  sense, kept in `sources/` with the captures they were collected beside.
- **`electronique/repair/electribe-2/sources`** — an investigation's own
  material promoted to a document, so its root *is* the investigation. Named as
  the anatomy's one exception. Reshaping it means rearranging user content, and
  nobody asked for that.
- **The retirement of a spent translation workspace** — decided and stated,
  implemented by nobody: `apply` says the workspace is spent and leaves it. A
  tool that deletes a translation is what this roadmap moved the workspace out
  of `.work/` to prevent.
- **`docs/architecture.md` §8's table** still calls `clean` "unchanged" with a
  revision note beside it. Rewriting the table is a bigger edit than this
  roadmap's subject.
