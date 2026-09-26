# Phase 3 Report: The Library Mapped

**Phase:** [phase-3-library-mapped.md](phase-3-library-mapped.md)
**Start Commit:** 234245e

---

## Work Log

### 2026-09-25

Resumed from the phase file and Phase 2's report. Baseline: `make
check-library` on the user's library reported 31 defects — 29 directories
without a manifest, and the two topics above the capacitor, unnamed since
Phase 2's trial.

`sync` over the whole library wrote 29 manifests and named the standard files
of the documents (`document/index.md`, `cover.md`, `theme.css`, `assets`,
`study/extracted.md`, `meta.json`) itself. Left: 31 topics and entries to name
— the 31 defects, now all "no name and no description" — and 50 items to
describe, which the check counts as to-do, not as defects. No file was
unexpected: two waiting entries hold their PDF at their root rather than in
`sources/` (`learning/smd-256-led`, `learning/transistor-tester`), and
`notebook` holds `discussion.md` at its root; `sync` took them as they are.

Described the items of the nine entries that have a `document/`, from what was
already studied: the document's front matter and headings, `study/meta.json`,
and each source's first lines through `peek`. The `electribe-2` investigation
needed no image at all: its journal, `study/NOTES.md` §7, inventories every
source directory and the origin of its 46 images. The same held for
`notebook`, whose discussion journal says what its photo shows and what the
`tc-22` tips pages are. Two standard names from `sync` were rewritten because
they were wrong for their entry: `electribe-2`'s `document/index.md` holds
the user's starting notes, with no front matter, not a document's text; its
`study/NOTES.md` is a sourcing journal, now named for its subject.

Two document entries, `round-led-d4017` and `maialen/euskara`, hold four
images each that neither document uses, so nothing studied says what they
show. Both went to `catalogue-describer` in one call — the first call by the
agent's name. **46,032 tokens, 21 tool calls, 162 s, for two entries**, 8
images and 2 PDF pages looked at: less than one entry cost in Phase 2's
trials, the fixed part shared. It named `round-led-d4017`'s entry again
(*Anneau DEL à dégradé progressif CD4017*), and returned three questions and
four rename proposals; one of these was in English (`component-list.jpg`),
against the rule that proposals are French.

The thirteen waiting entries were named from a first look, their items
described where that look settled them: every text, and every PDF through
`peek`'s text layer. The two screenshots of `HKT002` were read in the
conversation, since the entry had nothing else to name it by. Four
descriptions first went beyond what `peek` had shown — "montage", "composants"
at the end of a notice's contents; a TC22 manual's chapters guessed — and
were rewritten after reading further: the `musical-pectrum` kit has a
microphone, and `transistor-tester` is sold as a transistor tester but
measures capacitance, inductance and frequency. Then the nine topics, each
described by what belongs in it.

`make check-library`: **no defect**, 6 items left to describe — the five
images of `components/transistor` and the image directory of
`lab/tools/support`. Task 4 names the transistor's `Sans titre.jpg` and
`licensed-image_*` as rename candidates, and a name cannot be proposed for an
image nobody looked at: both entries went to the agent in a second call.

`ls -l` from the root lists one level — the two topics — not the tree the
phase meant to show; the tree for the user's review was printed from the
manifests instead.

The second agent call, on `components/transistor` and `lab/tools/support`:
**43,222 tokens, 15 tool calls, 77 s**, 8 images. It kept to its budget of
three images per directory and left two of the support's five photos unopened,
without a rename proposal; those two were looked at in the conversation —
more shop photos of the same support — and the directory's description
completed. `make check-library`: no defect, **0 items to describe**.

Then the task on `make new`, `make import` and `make fetch`. One function in
the core, `mapped()` in `core/catalogue.py`, syncs the entry and returns what
is left to name — the entry, the topics above it, the items — and each of the
three scripts prints it as its last step. Tests: three in
`tests/test_catalogue.py`, one per command in the `pdf` and `fetch` suites.
`new.py` reads `brand/tokens.yaml` under its `ROOT`, so its test copies it
into the temporary root. `docs/document.md` says what the three commands now
write. `make test`: 757 passed.

Shown to the user, once: the named tree — 9 topics, 23 entries, every name and
description — with nine questions gathered from the conversation and the two
agent calls, and 19 rename proposals (the capacitor's two from Phase 2
included; the agent's `component-list.jpg` put into French). Waiting for the
corrections and the accepted renames.

### 2026-09-26

The user's answers. The tree stands as named: `maialen` confirmed, `HKT002`
and `musical-pectrum` left for when their documents are written (the latter's
notice is a bad translation). Applied: `transistor`'s Gemini link and its
canvas image (`Sans titre.jpg`), unusable, removed through `remove` — their ids
retired; the TO-220 parts are transistors; the three WhatsApp captures are
Maialen's notes, the euskara document's source; the ikastola logo is kept for
later documents. The entry and item descriptions were rewritten to match.

All the image renames accepted, 18 of them (the 19th, `Sans titre.jpg`, was
removed instead), each through `rename`. Nine of the files were inside a
directory item (`capacitor`'s and `support`'s images, the round-led's paper
sheet, the notebook's photo): `rename` gives such a file its own unnamed item,
so each was described on its own from its directory's description, and the
directory's description rewritten to point at them. The notebook's discussion
journal cited its photo by its old path: its `index.md` and the topic
`anneau-round-led-d4017.md` now give the new one; the session of 2026-09-24,
a record, was left as written. `make check-library`: no defect, 0 items to
describe.

Open: "D4017" occurs nowhere but in the directory name `round-led-d4017`, and
the user wants it corrected to CD4017 — renaming the directory is asked to
the user before it is done, since the notebook's journal cites that path. And
the user asked for a naming convention for sources pasted from conversations
with web AIs, told apart from the internal discussions: a convention and the
ten renames it implies were proposed.

The user accepted the convention, with file names in English like the rest of
the repository's tree, and asked for the images at the root of `sources/` to
go into `sources/images/`. Ten images moved by hand in three entries
(`transistor`, `HKT002`, `euskara`); `sync` followed each by its digest, ids
and descriptions kept. Then 28 renames through `rename`: the 18 images again,
into English, and the ten pasted AI conversations as `ai-<subject>-<angle>.md`
— the manifest still keeps each file's very first name. Three directory
descriptions and the notebook journal's current files cited the French names,
and were updated. The catalogue skill's rename rule said French: it now says
English, for the file name only; the describing agent's report format says so
too, since the agent never read that rule — its proposals had mixed both
languages.

The "D4017" the round-led agent asked about was not only in the directory
name, as told to the user the day before: the document's front matter printed
`Référence: D4017` on the cover. The search that missed it filtered out every
line whose path held `round-led-d4017`. The reference is corrected to CD4017
in `document/index.md`; the PDF shows it at its next build. The directory's
own rename, put to the user on the wrong premise, is asked again before it is
done. `make test`: 757 passed. `make check-library`: no defect, 0 to describe.

The user extended the convention to the two sources that looked alike —
`diy-tools`' guide and `cable-tester`'s five studies — and asked for the two
PDFs lying at their entry's root to go into `sources/`, since the entries are
not started. The PDFs moved, `sync` followed them; six more renames, the five
studies described each on their own inside `documents/` (one prefix, over
24 characters, refused and shortened).

The proof: `make check-library` on the user's library — **9 documents
checked, no defect; 0 files no item covers, 0 items to describe, 0 sources
changed since described**. Handed to the user. `make test`: 757 passed.

---

## Decisions

- **The three commands map their entry in their scripts, not in the
  Makefile.** An agent runs `ingest.py` or `fetch.py` directly as often as
  through `make`; a sync in the Makefile would be skipped then. The Makefile
  is unchanged. `rederive` does not sync: it creates nothing.
- **`mapped()` never fails the command that created the entry.** The entry
  exists by then; a manifest it could not write is printed as a warning, and
  `make check-library` reports it.
- **The items of the waiting entries were described too**, although the
  phase put them out of scope: the look needed to name each entry had already
  settled its texts and PDFs, and task 4's rename candidates are images of a
  waiting entry, which cannot be renamed without being looked at. The whole
  library ends with 0 items to describe.
- **A standard name from `sync` is rewritten when it is wrong for its
  entry**: `electribe-2`'s `document/index.md` is the user's starting notes,
  not a document's text.
- **Source file names are English; names and descriptions stay French.**
  The user's rule: the repository's tree is English. Recorded in the catalogue
  skill and in the describing agent.
- **Conversations pasted from web AIs are named `ai-<subject>-<angle>.md`**,
  told apart from the internal discussions (`study/discussion/`,
  `discussion.md`); the AI, when known, goes in the description. The user's
  convention, kept out of the repository's rules at their request.
- **Images at the root of `sources/` go into `sources/images/`.**
- **A file renamed inside a directory item is described on its own.** `rename`
  gives it its own unnamed item; described from its directory's description,
  it keeps its original name in the manifest, which a merge would lose.
- **The describing agent takes several entries per call**, as Phase 2
  advised: two calls, four entries, 16 images, 89,254 tokens in all.

---

## Files Changed

**Added**

- `.claude/skills/pdf/tests/test_mapped.py`
- `docs/roadmap/on-progress/library-catalogue/phase-3-library-mapped-report.md`
- `assets/icon.png` — untracked before this roadmap opened, and not its work:
  left out of its commit

**Modified**

- `.claude/agents/catalogue-describer.md`
- `.claude/skills/catalogue/SKILL.md`
- `.claude/skills/fetch/scripts/fetch.py`
- `.claude/skills/fetch/tests/test_capture.py`
- `.claude/skills/pdf/scripts/ingest.py`
- `.claude/skills/pdf/scripts/new.py`
- `core/catalogue.py`
- `docs/document.md`
- `docs/roadmap/on-progress/library-catalogue/README.md`
- `docs/roadmap/on-progress/library-catalogue/phase-3-library-mapped.md`
- `docs/roadmap/on-progress/library-catalogue/phase-4-skills-use-the-map.md`
- `tests/test_catalogue.py`

Outside git, since `library/` is ignored: 29 manifests created and every
manifest of the library written through `sync`, `describe`, `remove` and
`rename`; two sources removed from `components/transistor`; 12 files moved
into `sources/images/` or `sources/`; 34 source files renamed; the round-led
document's `Référence` corrected in `document/index.md`; and the notebook's
journal repointed at its renamed photo in `study/discussion/index.md` and
`study/discussion/topics/anneau-round-led-d4017.md`.

---

## Problems And Deviations

- **The items of the waiting entries were described**, against the phase's
  Out of Scope: the look that named each entry had settled them, and the
  rename candidates were images of waiting entries. The library closes at 0
  items to describe.
- **The Makefile was not modified**, although the phase listed it: the sync
  lives in the three scripts, which an agent also runs without `make`.
- **`ls -l` from the root shows one level**, not the tree the phase meant to
  show the user; the tree was printed from the manifests by a one-off script.
  No command prints the named tree; left open, since the review happens once.
- **A wrong claim reached the user**: that "D4017" occurred only in the
  round-led directory's name, when the document's front matter printed it on
  the cover. A search had filtered out every line whose path held
  `round-led-d4017`. Found before any directory was moved; the reference is
  corrected in `document/index.md`, and the PDF, not rebuilt, shows it at its
  next build, as the user decided. The directory keeps its name.
- **The describing agent proposed names in two languages**: its report
  format said nothing of the language. Fixed in the agent's file, with the
  rule the user then set — file names in English.
- **`rename` inside a directory item splits it.** Each renamed file gets its
  own item; in `capacitor`, `support` and `cable-tester/sources/documents`
  every file was renamed, and the directory's item now covers nothing of its
  own — kept, its description pointing at its files. Left open: harmless,
  and a `merge` would lose the original names.
- **Work beyond the plan, on the user's word**: two sources removed, ten
  images and two PDFs moved into `sources/images/` and `sources/`, 34
  renames in all, and the user's convention for conversations pasted from
  web AIs.
- **The agent's budget left two photos unopened** (three per directory);
  looked at in the conversation, since both had to be renamed.
- Seen and left: `electribe-2`'s `document/index.md` has no front matter, and
  `make check-library` accepts it — the document is not written yet;
  `.claude/skills/pdf/scripts/new.py` loads `brand/tokens.yaml` and never
  uses it.

---

## Changes To Later Phases

- `phase-4-skills-use-the-map.md`: two constraints added — the notebook's
  journal still cites one renamed photo by its old path in a session, and the
  manifest's `original:` is how the migration finds its id; and
  `electribe-2`'s pieces are directory items while its journal cites single
  files inside them, which the `sourcing` task has to decide on.
- `phase-4-skills-use-the-map.md`: `**Blocked By:**` set to the baseline
  session of discussion-and-illustration Phase 0, which its Dependencies
  already required before `discussion` changes, and which is not held yet
  (that phase stands at 13/14).

---

## Assessment

The user's library is mapped: 9 topics and 23 entries named and described,
every item described, `make check-library` without a defect, and the three
commands that create an entry now leave it on the map. The tree was reviewed
once, and the review turned into more than corrections: two unusable
sources removed, 34 files renamed, images and PDFs put where the anatomy
expects them, and two conventions from the user — source file names in
English, and `ai-<subject>-<angle>.md` for conversations pasted from web AIs.

Most of the describing needed no image. The documents' study — front
matter, provenance, and above all the journals of `electribe-2` and the
notebook — said what their sources were; `peek` settled every text and PDF.
The describing agent took 16 images in two calls of two entries, 89,254
tokens: half Phase 2's cost per entry, the fixed part shared.

What Phase 4 needs first: the map is complete and current, so its skills can
rely on `find` and `links` from the first session. The journals still cite
by path — the notebook's among them, one of its session paths already stale
after this phase's renames — and the manifest's `original:` is the bridge
the migration to ids will use.
