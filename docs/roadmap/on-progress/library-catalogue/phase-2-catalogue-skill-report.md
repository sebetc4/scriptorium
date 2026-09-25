# Phase 2 Report: The Catalogue Skill

**Phase:** [phase-2-catalogue-skill.md](phase-2-catalogue-skill.md)
**Start Commit:** 969e5fa

---

## Work Log

### 2026-09-25

Resumed from the phase file and Phase 1's report, which set nothing pending.
Read what the phase builds on: the `discussion` skill (the closest model, a
skill of prose with no script) and its suite, `tests/test_triggers.py`, §5 of
`docs/architecture.md`, the `pdf-reviewer` agent, and how an import and a
capture record their source — an import's `meta.json` carries the PDF's
`sha256` and `make rederive` takes the first PDF of `sources/`; a capture's
carries `sha256_html` and `rederive` reads `sources/page.html.gz` by name.

Reading §8 of `docs/architecture.md` for the targets turned up a Phase 1
omission: the rule there admits `find`, `ls`, `links` and `path` (their
subject is the library), but neither §8 nor §1's count of targets was updated
when they were added. Repaired in this phase.

Designed the commands before writing them, and two questions changed the
plan. First, `remove` erasing an id would leave any citation of it leading
nowhere — and a session is never rewritten, so `make check-library` would stay
red for good; the same happens when the user deletes a cited file by hand.
Hence the retired ids (see Decisions). Second, the skill must teach splitting
and merging items; splitting is `describe` on a file inside a directory item,
but nothing could undo it without deleting the file. Hence `merge`. And the
describing agent needs a cheap first look at a file before any image enters
its context: hence `peek`.

Wrote `unused`, `remove`, `merge` and `rename` in `core/catalogue.py`, `peek`
in `core/navigate.py`, the retired ids through both and through the check,
and a `--library` option on the entry point for trials on a copy. Tests: 87 in
`tests/test_catalogue.py`, 40 in `tests/test_navigate.py`, one more in
`tests/test_library.py`. Two failures on the first run: a vanished item could
not be named by its path, since resolving a path required it on the disk;
`resolve` now also accepts the path of an item whose file is gone.

Re-reading `resolve` then showed a real hole: a target such as
`lab/tc-22/../../../outside.txt` resolved to an entry with the path
`../../../outside.txt`, because `library / "../x"` still lists the library
among its parents. Checked on a scratch copy — it did — at the moment `remove`
and `rename` could act on what it returned. Every path from the command line
now goes through one function, `under`, which refuses a `..`; a test runs
`rename`, `remove`, `describe` and `sync` against it. A test of `peek` had been
written with `or True`, which hid that a damaged PDF crashed it; `peek` now
reports the file as unreadable, and the test asserts it. `make test`: 738
passed.

Wrote the skill: `SKILL.md`, and the rules for names, descriptions and
prefixes in `references/describing.md`, a file the describing agent reads too.
One of its examples described a pasted conversation about choosing a
capacitor — too close to the real entry the trial was about to run on, which
could have led the agent to copy the example rather than look; replaced by an
unrelated one before the trial. The skill's suite checked, at first, a set of
commands captured by patching `argparse`; `core/catalogue.py` now builds its
command line in `parser()`, and the suite reads `commands()` from it — every
command the skill's table lists exists, and every command that exists is
listed. Registered the skill in `CLAUDE.md`, `README.md` (whose count of
skills was already one behind) and the three tables of §5, with a boundary
rule; `tests/test_triggers.py` has its row. Wrote the agent,
`.claude/agents/catalogue-describer.md`, and documented the new commands in
`docs/document.md`. `make test`: 751 passed.

The trials. The harness loads agent types when a session starts, so
`catalogue-describer` was not callable in this one; both trials ran a general
agent told to read the agent's file and follow it exactly — one read more, and
wider tools than `Read, Bash`, which it did not use.

- **On the fixture library**, in a copy in the scratchpad, `--library` on
  every command: `sample/component` without its manifest, plus three sources
  written for the trial — a two-page PDF with a text layer, an SVG named
  `Sans titre.svg`, a note. **54,518 tokens, 13 tool calls, 188 s.** It
  described the three and the entry, read the PDF through `peek` alone, and
  caught a real inconsistency — the drawing shows two leads, the datasheet
  three pins — which it wrote as a doubt and turned into a question rather
  than a guess. One rename proposal, for `Sans titre.svg`.
- **On the user's library**, announced first: `electronics/components/capacitor`,
  which the user had just opened in the editor. Between the first look at
  the library and the trial, the user had reorganised the entry (its images
  moved into `sources/images/`, its conversation became
  `sources/capacitor-1.md`); `sync` took the disk as it was, and wrote three
  manifests — the entry's, and the header-only manifests of the two topics
  above it. **64,968 tokens, 12 tool calls, 209 s, two images read.** It
  described both items and the entry, copied the labels exactly (« 1 µF »,
  « 10000uF63V »), and returned two questions — the images' origin and
  licence, the text's author — and two rename proposals, none applied.

`make check-library` on the user's library: 31 defects, down from 32 — the
entry is clean, and its two topics are now reported as unnamed rather than
without a manifest.

---

## Decisions

- **A removed or merged id is retired, never erased.** An entry's manifest
  keeps a `retired` list — the id, the item's name and path, the date, and for
  a merge the id it went `into`. A citation of a retired id is not a defect;
  `path` says it was removed, or follows it into the item it was merged into;
  `links` shows it; `describe` refuses it; and `ids()` still counts it, so it is
  never drawn again. Without it, removing a cited item, or the user deleting a
  cited file by hand, would leave a session citing nothing, forever.
- **`remove` refuses an item still in use unless `--used` is given**: cited
  (directly, or through an id merged into it), derived from by a tool, or
  holding such an item. It also refuses an item of `document/`, a directory
  holding an item not named as well, and any target that is not exactly an
  item. It checks every target before touching anything: one refusal and
  nothing is deleted.
- **What a tool derives from** is a capture's `sources/page.html.gz`, and an
  import's PDF, found both by the digest its provenance records and as
  `make rederive` finds it, the first PDF of `sources/`.
- **`rename` renames one source file**, keeping its extension, in its own
  directory; a file inside a directory item gets its own item, unnamed, with
  its original name. The very first name is the one kept, and renaming back to
  it clears it. A rename is not a change of content: the directory items
  above it stay current if they were. It refuses a file a tool derives from,
  since `rederive` would no longer find it.
- **`merge` folds an item back into the named item above it**, leaving the
  file where it is: the inverse of describing a file inside a directory. It
  refuses when no named item lies above, or when the file is gone (`remove`
  retires those).
- **`unused` lists the sources of one entry** that nothing cites and no tool
  derives from, each with its reason: never named, cited by nothing (and, when
  the entry has a document, that the document may rest on it — documents
  written before ids cite nothing), or gone from the disk.
- **`peek` is the first look**: a PDF's page count and the text layer of its
  first pages (`--pages` for others), an image's size with the date and camera
  its EXIF records, a text's first lines, a directory's files — bounded like
  every answer.
- **No `..` in a path given on the command line**: `under()` refuses it, for
  every command.
- **`--library DIR`** runs the entry point on another library than the
  repository's: the describing agent's trial on a copy of the fixture library
  needs it.
- **The rules for describing live in one file**,
  `.claude/skills/catalogue/references/describing.md`, which the skill and the
  agent both read: a name given in the conversation and one given by the agent
  follow the same rules.
- **The agent describes, and only describes.** It never renames, removes,
  merges, syncs or edits a file; what it cannot settle comes back as a
  question, and a file whose name says nothing as a rename proposal. Its
  budget: three images per directory item and twelve in all, PDFs through
  `peek`, a page as an image only when its text layer is empty.
- **The skill hands an entry to the agent from four images or a long PDF
  upward**; one or two items are described in the conversation.
- **The commands that keep the map get no `make` target**: they are run by
  the agent under the skill's rules, and a target would invite running them
  without. Recorded in §8 of `docs/architecture.md`.
- **The skill's command line is built by `parser()`**, and `commands()` lists
  its commands, so that the suite checks the skill's table against the code
  rather than against a copy.

---

## Files Changed

**Added**

- `.claude/agents/catalogue-describer.md`
- `.claude/skills/catalogue/SKILL.md`
- `.claude/skills/catalogue/references/describing.md`
- `.claude/skills/catalogue/tests/test_catalogue_skill.py`
- `docs/roadmap/on-progress/library-catalogue/phase-2-catalogue-skill-report.md`
- `assets/icon.png` — untracked before this roadmap opened, and not its work:
  left out of its commit

**Modified**

- `CLAUDE.md`
- `README.md`
- `core/catalogue.py`
- `core/library.py`
- `core/navigate.py`
- `docs/architecture.md`
- `docs/document.md`
- `docs/roadmap/on-progress/library-catalogue/README.md`
- `docs/roadmap/on-progress/library-catalogue/phase-2-catalogue-skill.md`
- `docs/roadmap/on-progress/library-catalogue/phase-3-library-mapped.md`
- `docs/roadmap/on-progress/library-catalogue/phase-4-skills-use-the-map.md`
- `tests/test_catalogue.py`
- `tests/test_library.py`
- `tests/test_navigate.py`
- `tests/test_triggers.py`

Outside git, since `library/` is ignored, the trial on the user's library
wrote three manifests: `library/electronics/manifest.yaml`,
`library/electronics/components/manifest.yaml` and
`library/electronics/components/capacitor/manifest.yaml`.

---

## Problems And Deviations

- **Five commands, not three.** `merge` and `peek` join `unused`, `remove` and
  `rename`: the skill cannot teach merging without the first, and the
  describing agent would read every PDF as images without the second.
- **The `retired` key**, not planned, joins `original` in the manifest's
  format.
- **Phase 1 left §8 and §1 of `docs/architecture.md` behind** on the `make`
  targets it added. Repaired here.
- **The agent type could not be called by its name in this session**: the
  harness reads `.claude/agents/` when a session starts. Both trials ran a
  general agent following the agent's file, which costs one read more than the
  real agent will. From a new session, `catalogue-describer` is callable.
- **The real trial wrote three manifests, not one**: `sync` on an entry
  creates the missing manifests of the topics above it, by Phase 0's design.
  Both are the header alone, and were announced with the entry's.
- **A cost higher than hoped**: 55,000 to 65,000 tokens for an entry of two or
  three items, most of it fixed per call — the agent's rules, and a context
  resent at each of a dozen tool calls. Mapping the user's fourteen waiting
  entries one call each would cost close to a million tokens. Recorded in
  Phase 3, with the remedy: several small entries per call.

---

## Changes To Later Phases

- `phase-3-library-mapped.md`: added two constraints — the describing agent's
  measured cost and the advice to give it several small entries per call, and
  its being callable by name only from a new session; and that
  `electronics/components/capacitor` is already described, with two rename
  proposals waiting for the user.
- `phase-4-skills-use-the-map.md`: reworded the task on `pdf` and `fetch` —
  `pdf`'s description claims every repair `make check-library` reports, and
  must now name `catalogue` for a `manifest`, `id` or `citation` defect, with
  `tests/test_triggers.py`'s neighbours to match. Changing another skill's
  description is Phase 4's, not this phase's.

---

## Assessment

The phase delivered the skill, its commands and its agent, and proved the agent
twice, once on a real entry. What the tool cannot do — say what a file is, in
the words someone will search for — now has written rules, and the trials
showed the rules working where they matter most: a doubt written as a doubt,
labels copied exactly, a question instead of a guess.

It also found two things the plan did not foresee. An id cannot simply be
erased, because the sessions that cite it are never rewritten: retired ids
answer that. And a hole in how paths were resolved, found at the moment the
commands became able to delete and rename — closed, and tested.

What Phase 3 needs first: the describing agent's cost. At 55,000 to 65,000
tokens for a small entry, mostly fixed, the fourteen waiting entries should go
to it several per call, from a new session where `catalogue-describer` is
callable by name. The user's time is the other dependency: one review of the
named tree, and the rename proposals — two of which, for the capacitor's
images, are already waiting.
