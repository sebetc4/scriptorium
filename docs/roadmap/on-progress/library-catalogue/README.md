# Roadmap: The Library Catalogue

---

## Status Indicators

- 🔴 Not Started
- 🟡 In Progress
- 🟢 Done
- ⏸️ Blocked
- ⚠️ Needs Review

---

## Overall Progress

```
Phase 0  The Manifest               🟢 ████████████████████ 100%  (12/12)
Phase 1  Navigating the Library     🟢 ████████████████████ 100%  (8/8)
Phase 2  The Catalogue Skill        🟢 ████████████████████ 100%  (8/8)
Phase 3  The Library Mapped         🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 4  The Skills Use the Map     🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
TOTAL                                  ██████████████░░░░░░  68%  (28/41)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 3 — The Library Mapped

---

## Why This Roadmap Exists

The notebook's discussion (`electronics/notebook`) reached beyond its own
directory. To talk about the user's soldering station, it opened the
station's manual and the pages of its tips in `lab/tools/tc-22`. It also
read the board holder's page in `lab/tools/support`, a draft in
`lab/workshop`, and the kit's document in `learning/round-led-d4017`. It
found them by listing the file system, and wrote them down by hand, by path,
in the journal's **Material** section. That section is the problem this
roadmap solves, and it has three parts.

**Finding.** Nothing says what a directory holds without opening it. The
library has 23 directories of material under 9 topics. Only 9 of the 23 have
a `document/`, and `make list` knows only those. The other 14 are waiting to
be studied, and no tool sees them. The library grows, and searching it by
listing files grows with it.

**Identifying.** Many file names come from a copy and paste or a camera:
`Sans titre.jpg`, `licensed-image_002_aEns.jpg`, `20260924_123413.jpg`.
Knowing what such a file is means opening it.

**Referring.** A path breaks at the next rename, silently when it is written
between backticks rather than as a link. The user renamed three times in a
few weeks: `electronique` → `electronics`, `labo` → `lab`,
`learning/pratice` → `notebook`. The first turned `make test` red with 18
failures, which the suite-and-review roadmap had to fix.

The answer applies a principle the discussion journal and the skills already
follow: a short description decides what gets opened. Each directory of the
library describes itself in a manifest. What an agent cites, it cites by a
permanent id. And a few commands answer a question in a few lines, however
large the library grows. The user expects the largest gain in the
discussions: the discussion agent gets a map of the library.

---

## Decisions Taken At Opening

Settled with the user on 2026-09-25, in the conversation that designed this
roadmap.

**Files, not a database.** There is one `manifest.yaml` in every directory
of `library/` except the root.
- It lives in the directory it describes. A directory the user renames or
  moves keeps its id, and nothing has to be reconciled.
- It is text: readable in the editor, and saved with the rest of the library.

SQLite was considered as the source of truth and rejected, for two reasons.
It sits beside the directories rather than in them, so a rename made in a
file manager leaves it guessing. And it would keep the descriptions, the
only part that is costly to redo, in one binary file that git does not track
(`library/` is ignored). A database comes back only if the need is felt
explicitly: a search grown slow, or a question the manifests cannot answer.
It would then be an index rebuilt from the manifests, never their
replacement.

**Two kinds of node, read from the directory and never declared.**
- A **topic** holds only directories: `electronics`, `electronics/lab`.
- An **entry** holds one of the five roles, or a file: `lab/tools/tc-22`,
  `notebook`, or `learning/smd-256-led`, which holds a single PDF.

Inside an entry, **items** describe its files.

**A topic's manifest never lists its children.** The file system knows them,
and `ls` computes them. Its description says what belongs in the topic, not
what is in it. That way it stays true when an entry arrives, and it tells the
agent where the next one goes.

**One manifest per entry, at its root.** A subdirectory of `sources/` is an
item of that manifest, never a manifest of its own, and nothing is written
into `sources/`.

**The agent writes the name, the description and an id's prefix; the tool
writes everything else.** Everything else means the paths, the kinds, the
file counts and the digests. A manifest is written only through the tool,
and the hook that guards `sources/` refuses a direct edit.

**An id is a short prefix followed by 8 random characters**, as in
`manuel-a8f2c3d9`.
- The agent proposes the prefix when it names the node. The tool draws the
  suffix from an alphabet without `0`, `o`, `1`, `l` or `i`, and checks that
  the id is unique across the library.
- A node not yet named has no id, and cannot be cited.
- An id never changes and is never reused. An archive session is never
  rewritten, so it must not end up pointing at something else.
- A UUID gives the same guarantees, but costs 36 unreadable characters and
  about twenty tokens per citation.
- One duplicate escapes the suffix: a copied directory. The check reports it,
  and the user says which copy keeps its ids.

**Items cover an entry once, by the longest path.**
- By default there is one item per direct child of each role, and one per
  file at the root. `.work/` is never listed.
- An item that names one file inside a covered directory takes that file out
  of it.
- The anatomy's standard files (`index.md`, `extracted.md`, `meta.json`, a
  journal…) are named and described by the tool.

**Digests for sources only.** A source never changes, so a different digest
means something: a rename to follow, or a description to review. The agent's
files change at every session, and a digest would say nothing there.

**A citation is a Markdown link whose target is an id**, written in the
agent's files: the text « Manuel de la TC22 », for the reader, pointing at
`id:manuel-a8f2c3d9`, for the tool.
- Everything a manifest describes is cited that way, the entry's own sources
  included.
- Relative links are kept for the inside of one of the agent's files, such
  as a journal's index and its topics.
- No id goes into `document/`. References between documents serve the agent,
  not the reader.

**Neighbours are computed from citations, never stored.** "The notebook cites
the station's manual" gives, the other way round, "the manual is cited by the
notebook".

**The size of an answer depends on the question, never on the library.**
Nothing is loaded when a session opens. `find`, `ls`, `links` and `path`
print at most twenty lines, then say how many more there are.

**Sources stay read-only in content.** The manifest's name is what makes a
file identifiable, so no file needs renaming for the agent's sake.
- For a flagrantly generic name, such as `Sans titre.jpg`, the agent may
  propose a new file name: it helps the user when they search outside the
  manifest.
- The agent renames only once the user accepts, and through the tool, which
  keeps the original name.
- The user renames and moves files as they like: `sync` follows a source by
  its digest.

**Cleaning up is done only when the user asks.** The agent proposes the
sources that no citation points at, each with its reason. Nothing is deleted
before the user confirms the list. A source a tool derived something from
counts as used.

**`sync` runs from the tools, not from a session hook**: at the end of
`make new`, `make fetch` and `make import`, and when work on an entry
starts. A session about the code has no business writing into `library/`.

**The code goes to the core; keeping the map is a skill.** `make` and
several skills need the commands, which is the first clause of
`docs/architecture.md` §2. The `catalogue` skill carries the intent: naming,
describing, cleaning up, turning to the user. Reading the map is a brick.
Each skill that needs it carries the one rule that concerns it, without
loading `catalogue`.

**A subagent only for the heavy description work.** It reads the PDFs and
images of an entry, describes them through the tool, and returns a summary.
The pages stay out of the main conversation, as with `pdf-reviewer`.
Navigating needs no subagent: a search costs a few lines, while a subagent
starts from nothing.

**The discussion searches when the answer depends on the library, not by
default.** An explanation the agent can give from its own knowledge is given
that way, and recorded as an agent's account. The library is searched in
three cases:
- the subject is the user's own: their equipment, their kit, their project;
- the document will state a claim as established;
- the discussion needs to know how a document of the library explains
  something.

Only what the search points at is read, and only the part needed. The
context stays light when nothing requires more.

**The journal's Material section goes.** The manifest describes the files,
and the topics cite them: one fact, one place. At a resume, `sync` and `ls`
on the entry show what is new.

**Names and descriptions are in French**, the language of the library, so
that a search finds everything with the same words. The keys are in English,
like the rest of the repository.

---

## Deliberately Out Of Scope

- A database or a full-text index. The Decisions say what would reopen it.
- References inside the documents themselves, in their PDF or EPUB.
- Reorganising the library: moving or renaming anything beyond the renames
  the user accepts.
- Describing every item of the 14 waiting entries. Each gets its entry-level
  name and description; its items are described as it is studied.
- Structured fields for querying, such as the components a project uses or
  the tools the user owns. The manifest serves finding and identifying.
- Running the description on local models, which waits for the local-model
  work.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [The Manifest](phase-0-manifest.md) | 12 | 🟢 Done |
| 1 | [Navigating the Library](phase-1-navigation.md) | 8 | 🟢 Done |
| 2 | [The Catalogue Skill](phase-2-catalogue-skill.md) | 8 | 🟢 Done |
| 3 | [The Library Mapped](phase-3-library-mapped.md) | 6 | 🔴 Not Started |
| 4 | [The Skills Use the Map](phase-4-skills-use-the-map.md) | 7 | 🔴 Not Started |

---

## Dependencies

- The user's time: in Phase 3, one review of the named tree and of the rename
  proposals; in Phase 4, a real discussion session.
- The baseline for Phase 4. The discussion-and-illustration roadmap's Phase
  0 closes on a real notebook session, held with the three-layer journal. It
  has to happen before Phase 4 changes the `discussion` skill, and Phase 4
  measures against it.
- In the other direction, that roadmap's Phase 1, the transistor pilot,
  waits for this one. Its material is spread across `components/transistor`,
  `learning/m328` and `learning/transistor-tester`.

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md): §2, core or skill; §5,
  the skills and the trigger check; §11, the inside of a document.
- [`docs/document.md`](../../../document.md): what each command puts where.
- [discussion-and-illustration, phase 0 report](../../pending/discussion-and-illustration/phase-0-discussion-skill-report.md):
  the three-layer journal, and the migration that showed the Material
  section at work.
- The notebook's journal, `library/electronics/notebook/study/discussion/index.md`:
  the **Material** section this roadmap replaces.

---

## Metadata

**Roadmap Status:** 🟡 In Progress
**Location:** `docs/roadmap/on-progress/library-catalogue/`
**Version:** 1.3.0
**Created:** 2026-09-25
**Last Updated:** 2026-09-25

---

## Changelog

### 1.3.0 (2026-09-25)

Phase 2 closed, 8 of 8 tasks. Delivered the `catalogue` skill, with its rules
for naming and describing in a reference its agent shares; the commands
`unused`, `remove`, `merge`, `rename` and `peek`; retired ids, so that a
removed or merged item's citations keep leading somewhere; and the
`catalogue-describer` agent, tried on a copy of the fixture library (54,518
tokens) and on the user's `electronics/components/capacitor` (64,968 tokens),
whose manifests are the only ones written into `library/` so far. Found and
closed a hole: a path with `..` resolved outside the library just as commands
became able to delete and rename. Two constraints were added to Phase 3 and a
task reworded in Phase 4.

### 1.2.0 (2026-09-25)

Phase 1 closed, 8 of 8 tasks. Delivered `core/navigate.py` with `find`
(and `--text`), `ls`, `links` and `path`, every answer bounded to 20 lines; one
entry point for the agent, the console script `catalogue`; and the `make`
targets `find`, `ls`, `links`, `path`. Measured on the fixture library plus
500 entries: every answer has the same length on both. The measurement found
two costs, the pure-Python YAML loader and an `ls` that computed lines it did
not show, both fixed: 70 to 180 ms per command on 500 entries. A constraint
was added to Phase 2.

### 1.1.0 (2026-09-25)

Phase 0 closed, 12 of 12 tasks. Delivered `core/catalogue.py` (the manifest,
ids, `sync`, `describe`, the `id:` citations), the catalogue's defects and
to-do counts in `make check-library`, the guard's refusal of a manifest edited
by hand, manifests for the fixture library, and the documentation. Found: a
directory outside the roles at an entry's root, and an empty directory, which
the Decisions did not place; the phase report records how each was settled.
`make check-library` fails on the user's library until Phase 3 syncs it. A
constraint was added to Phases 2 and 3. The roadmap moved from `pending/` to
`on-progress/`.

### 1.0.0 (2026-09-25)

Roadmap created with five phases and 41 tasks. First the manifest and its
checks, then the navigation commands, then the `catalogue` skill with its
describing agent. After that, the user's library is mapped, and last the
skills are made to use the map, proved in a real discussion session.
