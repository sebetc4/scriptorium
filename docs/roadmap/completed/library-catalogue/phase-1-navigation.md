# Phase 1: Navigating the Library

---

## Status

**Current Status:** 🟢 Done (100% — 8/8)
**Started:** 2026-09-25
**Completed:** 2026-09-25
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-0-manifest.md` and `phase-0-manifest-report.md` in full before
touching anything here: the decisions already taken, the problems and
deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-1-navigation-report.md` current as the work happens — after each
significant step, and before every commit, pause, or end of session.

---

## Objective

Answer "what does the library hold about this?" and "what is in this
directory?" in a few lines, whatever the size of the library. Four read-only
commands: `find`, `ls`, `links` and `path`.

---

## Overview

### Why This Phase Matters
The user's concern, stated when the design was agreed: the library grows,
and a map read whole at the opening of a session would make every context
grow with it, while a discussion rarely needs the whole library. So nothing
is loaded by default. A question costs the lines of its answer: a few for a
search, a few for a directory, a few for the neighbours of the entry being
worked on.

### What It Enables
The agent finds the material an answer depends on without listing the file
system. It moves through the library three ways: down the tree from the
root, straight to a result, or sideways to the neighbours of an entry.

### Out of Scope
Any command that writes. Ranking results beyond a stable order. A search
index or a database: `find` reads the manifests each time.

---

## Tasks

### The commands
- [x] Write `find`: the words of the query matched against names and descriptions, case and accents folded, across the library or under an id with `--in`, one line per result (kind, id, name, where)
- [x] Add `--text` to `find`: search the content of the items the manifest knows to be text (Markdown, extractions, journals, notes), each hit reported by its item's name and its line
- [x] Write `ls`: a topic lists its topics and entries with their counts, an entry its items; `-l` adds the descriptions, `-ll` the kind, size and date; markers show what is to describe, new, or to review
- [x] Write `links`: what an entry or an item cites and what cites it, computed from the `id:` citations of the agent's files, grouped by entry, each with the file that cites it
- [x] Write `path`: an id resolved to its path
- [x] Bound every output to 20 lines by default, closing with how many more there are and how to narrow the query

### Access
- [x] Give the commands one entry point for the agent and `make` targets for the user, documented in `docs/document.md` and `CLAUDE.md`

### Proof
- [x] Measure each command on the fixture library and on a generated library of 500 entries: for the same query, the output has the same length

---

## Technical Details

### Files to Modify
```
core/catalogue.py                        the four commands, or a module beside it
tests/test_catalogue.py                  the commands, and the 500-entry measurement
Makefile                                 the targets for the user
docs/document.md, CLAUDE.md              the commands
```

### Dependencies
Phase 0: the manifests and the `id:` citation scanner.

### Constraints
- Every command is read-only.
- The generated 500-entry library lives in the test's temporary directory,
  never under `tests/fixtures/`.

---

## Acceptance Criteria

- [x] `make test` passes
- [x] For the same query, each command's output is no longer on the 500-entry library than on the fixture library
- [x] `find etain` finds a description that writes « étain »
- [x] `links` on an entry lists what it cites and what cites it, from `id:` citations alone
