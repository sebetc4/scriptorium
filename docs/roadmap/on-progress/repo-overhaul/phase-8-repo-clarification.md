# Phase 8: Repo Clarification and Documentation Rewrite

---

## Status

**Current Status:** 🟢 Done (100% — 11/11)
**Started:** 2026-09-16
**Completed:** 2026-09-17
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

Read Phase 0's `docs/architecture.md` alongside them: this phase's job is to
make the repository match it, and to write down the result.

---

## Objective

Close the roadmap. Every root directory earns its place or leaves. `claude.md`
becomes `CLAUDE.md` and is rewritten in English against the architecture that
now exists. `README.md` follows. The documentation test stops asserting on a
layout that is gone.

---

## Overview

### Why This Phase Matters

Eight phases of restructuring leave two documents describing a repository that
no longer exists. `claude.md` maps ten modules in `core/`, names two skills, and
carries EPUB and art-direction rules that now live in the skills that own them.
Documentation that lies is worse than none: it is trusted.

This is also the phase where the "default location" problem is settled. The
brief for this roadmap named it directly — every directory at the root should
have a reason to be there, not be where something landed.

### What It Enables

A reader who clones the repository can find out what it does and where things
are without reading the code. The next roadmap starts from documentation that
matches reality.

### Out of Scope

New capability of any kind. This phase writes down what the previous eight
built and removes what they left behind. Anything that would need a new test to
be trusted does not belong here.

---

## Tasks

### The tree
- [x] List every root directory and justify it against `docs/architecture.md`; move or delete what has no reason
- [x] Check `.gitignore` covers the artefacts the new layout produces, inside the skills included
- [x] Confirm no scratch or staging directory survives at the root — raw material lives with the roadmap that consumes it

### The documents
- [x] Rename `claude.md` to `CLAUDE.md` with `git mv`, so the history follows
- [x] Rewrite `CLAUDE.md` in English from scratch: repo map, skill map, commands, and only the rules that have no skill to live in
- [x] Keep the `## Roadmaps` contract in the rewritten `CLAUDE.md`
- [x] Rewrite `README.md` in English against the final architecture

### Coherence
- [x] Update `tests/test_documentation.py` to the new documents and the new layout
- [x] Check that every path quoted in a skill or a document actually exists
- [x] Check that no skill description overlaps another's, now that all five are written
- [x] Closing pass: `make setup`, `make test`, `make build`, `make epub`, `make preview-style`, and a page-by-page review of the style guide in both outputs

---

## Technical Details

### Files to Modify

```
claude.md -> CLAUDE.md    renamed, then rewritten
README.md                 rewritten
tests/test_documentation.py
.gitignore
docs/architecture.md      brought up to what was actually built
```

### Dependencies

Every earlier phase. This one describes their result and cannot precede it.

### Constraints

- `tests/test_documentation.py` currently asserts on French strings
  (`"ne reflue pas"`) and on the `core/` module map. Both sides change here, in
  the same commit, or the suite goes red between them.
- The art-direction rules, the EPUB rules and the two questions to ask in order
  now live in the skills that own them. `CLAUDE.md` points at them; it does not
  restate them. A rule written twice drifts.
- `make list` and the `make help` text must match the targets that survive. A
  test already enforces that every target appears in the help.

---

## Acceptance Criteria

- [x] Every root directory is in `docs/architecture.md` with a stated reason
- [x] No scratch or staging directory exists at the root
- [x] `CLAUDE.md` exists, is in English, and describes the repository as it now is
- [x] The `## Roadmaps` contract is in `CLAUDE.md`
- [x] `README.md` is in English and matches the final architecture
- [x] No French remains anywhere outside `library/` — *outside the roadmaps' archives and test fixtures, see Notes*
- [x] No rule is stated in two places — *between `CLAUDE.md` and the skills; `README.md` explains some of them to a human reader, see Notes*
- [x] Every path quoted in a document or a skill resolves
- [x] `tests/test_documentation.py` asserts on the current layout and is green
- [x] `make setup`, `make test`, `make build`, `make epub` and `make preview-style` all pass on a clean run — *on the working clone, not a fresh one; `epubcheck` still absent*
- [x] The style guide has been reviewed in PDF and through the EPUB plates

---

## Notes

### What the current `CLAUDE.md` carries that must find a home

Its rules section holds eleven rules. After eight phases, most belong to a
skill:

| Rule | Destination |
|---|---|
| Never modify the provided skills | `CLAUDE.md`, restated for `diagram-design` alone (Phase 3) |
| No hard-coded hex outside the palette | `pdf` — art direction |
| `accent` editorial, `alert` and `danger` signalling | `pdf` — art direction |
| A document never edits `theme/` for itself | `pdf` — the cascade |
| Two questions to ask, in order | `pdf` — language, then theme |
| Invent nothing that gets displayed | `pdf` — the cover |
| The cover is proposed and validated | `pdf` |
| A PDF is not delivered unreviewed | `pdf` — the review loop |
| An EPUB is not reviewed screen by screen | `epub` |
| No `var()` survives in an EPUB | `epub` |
| Colour never carries meaning alone in an EPUB | `epub` |
| An icon is chosen from `brand/icons/`, never guessed | `pdf` |

What stays in `CLAUDE.md` is what no skill owns: the repo map, the commands,
the venv rule, the note that part of the suite depends on documents kept out of
the repository, and the roadmap contract.

### The lowercase filename

`claude.md` is lowercase today. The conventional spelling is `CLAUDE.md`, and
on a case-insensitive filesystem a plain rename can be a no-op — use `git mv`
through an intermediate name if the rename does not take.

### What the phase found

**Two root directories had no reason to be there.** `lib/` survived Phase 2's
rename as an untracked `__pycache__/`, and was deleted. `templates/` was the
real case: Phase 0 kept it at the root on the argument that a `report` feeds
both outputs, but that holds for the preset — which `theme/` carries — not for
the seed. A seed is read once, by `new.py`, at creation, and creation is `pdf`'s
alone. It moved to `.claude/skills/pdf/assets/templates/`, and
`docs/architecture.md` records the revision in place.

**The project was renamed `scriptorium`.** "pdf-creator" described one output
of five jobs. The package, the `diagram-design` profile slug and the titles
changed. **The EPUB identifier namespace did not**: `epub.py`'s `UID_NS` still
hashes the old URL, with a comment saying why — changing it would give every
EPUB a new identifier, and an e-reader would take each for a different book.
The old profile `~/.diagram-design/profiles/pdf-creator.md` and the working
directory's name are outside the repository and left to the user.

**`CLAUDE.md` went from 110 lines to 60.** Eleven of its twelve rules already
lived in the `pdf` and `epub` skills — checked by grep, not assumed — so it now
routes by intent to a skill and keeps only the three rules no skill owns. The
documentation test no longer asserts on French strings: it reads the skills and
the core modules from disk and requires `CLAUDE.md` (and `README.md`, for the
skills) to name each one, so a skill added later and not documented fails the
suite. It also refuses `lib/` and a root `templates/` in the three main
documents.

**French survived Phase 1 in two files it did not scan.** `requirements.txt`'s
comments and all of `brand/tokens.yaml`'s. Both were translated; for the YAML,
the parsed data was compared before and after (identical) and `make brand`
regenerated nothing. What remains is deliberate: French test fixtures for the
translation and capture suites, the French → English glossary in
`docs/architecture.md`, the slug transliteration tables, the brand's display
name "Ma bibliothèque" (user-facing, not translated unasked), and the two
superseded archives under `sources/`.

**The path check found one stale destination.** `docs/architecture.md` §7 sent
`tests/conftest.py` to `tests/conftest.py`; Phase 2 had moved it to the root.
Every other unresolved hit was a path relative to a document (`sources/`,
`assets/`), a model identifier, or a "Today" column of a historical move table.

**The skill descriptions did not overlap, but two pointed one way only.** `fetch`
refused to translate without naming `translate`; `sourcing` did not name `pdf`
for rebuilding a PDF. Both now name their neighbour.

**Rules explained twice, on purpose.** `README.md` explains the meaning of
`accent`, `alert` and `danger`, and why an EPUB is reviewed through sheets, to a
reader arriving cold. It explains; the skills prescribe. Accepted as the one
tolerated duplication, and the place to look if the two drift.

**The closing pass ran on the working clone.** `make setup` (which also
reinstalled the package under its new name), `make test` (349), `make build`
(the whole library), `make epub` and `make preview-style` all passed. The style
guide was reviewed page by page in light and dark PDF and through both EPUB
style sheets: no layout defect. Its content is still stale — `pdfs/`, a hex in
its override example — as Phase 3 already recorded; it is `library/` content and
left to its author. The review included the user's uncommitted change to
`theme/base.css`, which renders cleanly.
