# Phase 0 Report: The Manifest

**Phase:** [phase-0-manifest.md](phase-0-manifest.md)
**Start Commit:** 845b31a

---

## Work Log

### 2026-09-25

Opened the phase and read the code it builds on: `core/library.py` and its
suite, the guard `.claude/hooks/protect-paths.sh` and its probe in
`tests/test_anatomy.py`, the shared `fixture_library` in `conftest.py`, and the
shape of the user's library (read, never written). Two shapes there were not in
the roadmap's examples: `components/capacitor` holds an `images/` directory
beside `sources/`, outside every role, and `notebook` holds a `discussion.md`
at its root. Both had to be covered by the default items.

Wrote `core/catalogue.py` in one pass: the format and its validation, the two
kinds of node, the default items and the longest-path rule, digests, ids,
`sync`, `describe`, the `id:` citation scanner, and a command line
(`-m core.catalogue sync | describe`). A first draft of `resolve` came out
tangled and was rewritten around two small helpers, `_inside` and `node_of`.
On re-reading, three things changed before any test ran: a path is tried
before an id (a directory could be named like one); the rename-follow computed
a directory's digest once per file inside it, and now computes each candidate
once; and a vanished item that was never named is dropped rather than reported
forever, since nothing can cite it.

Wrote `tests/test_catalogue.py` (59 tests, then 60): all passed on the first
run. Then extended `core/library.py` with the defects and the counts, which
turned 22 of the 24 existing `test_library.py` tests red. That was expected:
their libraries had no manifests. The helper `make_doc` now leaves its library
catalogued (synced, every node named), and each test adds its one defect to
that.

Gave the fixture library its manifests through the tool itself, not by hand,
and added a citation to the fixture journal (`topics/brochage.md` cites the
style guide by id), so that the clean library exercises the citation check.
The first manifests showed French text quoted with doubled apostrophes
(`d''étude`); the dumper now prefers double quotes.

Two tests still failed: an empty `out/` or `source/` directory under a topic
was reported twice, once by the layout check and once as a directory without a
manifest. Decided that a directory with no visible file at any depth is not a
node (see Decisions), which also makes an empty directory in the user's
library cost nothing.

Added the guard's refusal and its test, `catalogue` to `CLAUDE.md`'s map of the
core (a test pins it), and the documentation: a section on the catalogue in
`docs/document.md`, with the three new kinds of defect and the to-do line; and
in `docs/architecture.md` the row in §2, the core's listing, five glossary
terms, the manifest in §11's tree, and a subsection *The manifest* at the end
of §11.

Dry run on a copy of the user's library, in the session's scratchpad: `sync`
wrote 32 manifests in 0.07 s, leaving 32 nodes to name and 51 items to
describe; a second run wrote nothing; the check then reported 32 defects, all
a node without a name and a description, and no uncovered file. `make test`:
667 passed.

---

## Decisions

- **A directory outside the roles at an entry's root is an item of its own.**
  The default items are one per direct child of each role, and one per other
  child of the root — a file or a directory. `components/capacitor/images/` is
  the case that needed it: without it, its photographs would be covered by no
  item.
- **A directory with no visible file at any depth is not a node.** It has
  nothing to describe, and would otherwise be reported as a directory without
  a manifest. Hidden files (`.gitkeep`) and `.work/` are never seen, at any
  depth.
- **`kind` is the nature of the content**, from the extension: `directory`,
  `pdf`, `image`, `text`, `video`, `audio`, or `file`. Whether an item is a
  source is read from its path — anything outside `document/`, `study/` and
  `generators/` — and never stored. Phase 1's `find --text` reads `text`.
- **A directory's digest is the digest of its files' relative paths and
  digests.** Renaming the directory keeps it, so `sync` follows it; adding a
  file inside changes it, so a described directory of sources is reported as
  changed.
- **A digest is recorded against a description.** `sync` refreshes the digest
  of an item not described yet, and never that of a described one: "changed
  since described" is the difference between the two. `describe` records the
  digest of the content it described.
- **`sync` follows a move in the same entry first, then anywhere in its scope
  when exactly one candidate of the same kind matches.** An ambiguous match is
  not followed. Syncing the whole library therefore follows a source moved
  from one entry to another; syncing one entry does not see the others.
- **The standard files get ids**, with fixed prefixes (`document`,
  `extraction`, `discussion`…), so that every named node can be cited.
  `document/assets` joins the task's list of standard files: every document
  has one, and naming it by hand would be busywork.
- **A prefix is lowercase ASCII words joined by hyphens, at most 24
  characters.**
- **A duplicate id is reported once per id**, against its first holder, naming
  every place that holds it. A copied entry therefore reports its own id and
  each of its items' ids.
- **Citations are read from every Markdown file of the library outside
  `sources/` and hidden directories**, sessions included, and located against
  the entry that holds the file.
- **The command line is `-m core.catalogue`, run with the venv's
  interpreter, for now.** Phase 1 gives the commands one entry point and
  `make` targets.

---

## Files Changed

**Added**

- `core/catalogue.py`
- `tests/test_catalogue.py`
- `tests/fixtures/library/exemples/manifest.yaml`
- `tests/fixtures/library/exemples/guide-de-style/manifest.yaml`
- `tests/fixtures/library/sample/manifest.yaml`
- `tests/fixtures/library/sample/component/manifest.yaml`
- `docs/roadmap/on-progress/library-catalogue/phase-0-manifest-report.md`
- `assets/icon.png` — untracked before this phase opened, and not its work:
  left out of its commit

**Modified**

- `.claude/hooks/protect-paths.sh`
- `CLAUDE.md`
- `core/library.py`
- `docs/architecture.md`
- `docs/document.md`
- `tests/test_anatomy.py`
- `tests/test_library.py`
- `tests/fixtures/library/sample/component/study/discussion/topics/brochage.md`
- `docs/roadmap/pending/discussion-and-illustration/README.md` — a link
  repaired after this roadmap's folder moved
- `docs/roadmap/pending/discussion-and-illustration/phase-0-discussion-skill-report.md`
  — the same link repair
- `docs/roadmap/pending/discussion-and-illustration/phase-1-discussion-pilot.md`
  — the same link repair

**Renamed**

- `docs/roadmap/pending/library-catalogue/README.md` → `docs/roadmap/on-progress/library-catalogue/README.md`
- `docs/roadmap/pending/library-catalogue/phase-0-manifest.md` → `docs/roadmap/on-progress/library-catalogue/phase-0-manifest.md`
- `docs/roadmap/pending/library-catalogue/phase-1-navigation.md` → `docs/roadmap/on-progress/library-catalogue/phase-1-navigation.md`
- `docs/roadmap/pending/library-catalogue/phase-2-catalogue-skill.md` → `docs/roadmap/on-progress/library-catalogue/phase-2-catalogue-skill.md`
- `docs/roadmap/pending/library-catalogue/phase-3-library-mapped.md` → `docs/roadmap/on-progress/library-catalogue/phase-3-library-mapped.md`
- `docs/roadmap/pending/library-catalogue/phase-4-skills-use-the-map.md` → `docs/roadmap/on-progress/library-catalogue/phase-4-skills-use-the-map.md`

---

## Problems And Deviations

- **`make check-library` on the user's library now fails**, with 32 defects,
  each a directory without a manifest; it was clean before this phase. This is
  the check doing its job on a library not mapped yet. Phase 3's first task,
  `sync` on the user's library, clears these, and naming every node clears the
  rest. Left open until then, and recorded as a constraint in Phase 3.
- **"One fixture per defect" is one test per defect, each building its own
  library**, the pattern `tests/test_library.py` already followed, rather than
  one defective directory under `tests/fixtures/library/`. The fixture library
  itself stays clean, which is what every other suite reading it needs.
- **A topic that receives a stray file becomes an entry**, by the rule that
  reads the kind from the directory, and its subdirectories become its items.
  Not seen in the user's library (the dry run found 32 nodes, each of the
  expected kind); recorded so that Phase 3 recognises it if it appears.

---

## Changes To Later Phases

- `phase-2-catalogue-skill.md`: added a constraint — the manifest's format
  refuses an unknown key, so `rename` adds the key that keeps the original file
  name to `ITEM_KEYS` in `core/catalogue.py`.
- `phase-3-library-mapped.md`: added a constraint — until its first task runs,
  `make check-library` fails on the user's library, reporting each directory
  as without a manifest.

---

## Assessment

The phase delivered what it set out to: a manifest format, the tool that keeps
it true to the disk, and a check that holds the library to it, all proved on
the fixture library, with the user's library left untouched. The design settled
at the roadmap's opening held without a change. What this phase added is the
detail the roadmap left open: directories outside the roles, empty
directories, what a digest is compared against, how far a move is followed.

What Phase 1 needs first: every command reads the map through
`core/catalogue.py` — `nodes()`, `read()`, `ids()`, `covering()`,
`citations()` — and `core/library.py`'s `todo()` already computes the three
markers `ls` will show (uncovered, to describe, changed). An item is text when
its `kind` is `text`. The command line is still `-m core.catalogue`, and
giving it one entry point is Phase 1's.
