# Phase 2: The Catalogue Skill

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/8)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-1-navigation.md` and `phase-1-navigation-report.md` in full
before touching anything here: the decisions already taken, the problems and
deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-2-catalogue-skill-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Write the `catalogue` skill, which keeps the map: how to name and describe,
when to turn to the user, how to clean up and rename on the user's word.
Add the three commands its procedures need, and an agent for the heavy
description work.

---

## Overview

### Why This Phase Matters
The tool does everything mechanical. What is left is judgement: a name that
says what a file is, a description with the words someone would search for,
the moment to ask the user rather than guess. Without written rules, each
session would describe differently, and a search depends on the words being
consistent.

### What It Enables
Phase 3 describes the user's library by these rules. The describing agent
keeps PDF pages and images out of the main conversation while it reads them.

### Out of Scope
Describing the user's library (Phase 3). Changes to the other skills
(Phase 4). Running the description on local models.

---

## Tasks

### The commands the procedures need
- [ ] Write `unused`: the sources of an entry that no `id:` citation of the library points at, each with its reason; a source a tool derived something from (an import, a capture) counts as used
- [ ] Write `remove`: delete the files of the items it is given and their lines in the manifest, together; no default, each item named
- [ ] Write `rename`: rename a source file and update its item in one step, keeping the original file name in the manifest

### The skill
- [ ] Write `.claude/skills/catalogue/SKILL.md`: when it fires; naming and describing (the words someone would search for, where to look inside the file); splitting and merging items; when to turn to the user (a new source whose nature is unclear, a vanished source, something hard to identify, a name to find); cleaning up and renaming only on the user's word; what it refuses (changing a source's content, writing an id by hand, an id in `document/`)
- [ ] Write the skill's suite: the commands it names exist, and it states its refusals
- [ ] Give the description a phrase no other skill carries, and register the skill in `CLAUDE.md`, `README.md` and every table of `docs/architecture.md` §5, with `tests/test_triggers.py` passing

### The describing agent
- [ ] Write `.claude/agents/catalogue-describer.md`: given an entry, it reads the items left to describe, writes their names and descriptions through `describe`, and returns only a summary and the questions for the user
- [ ] Run it on one fixture entry and on one of the user's waiting entries, and record its cost in tokens

---

## Technical Details

### Files to Modify
```
core/catalogue.py                        unused, remove, rename
tests/test_catalogue.py                  the three commands
.claude/skills/catalogue/                new: SKILL.md, tests/
.claude/agents/catalogue-describer.md    new
CLAUDE.md, README.md                     the skill
docs/architecture.md                     §5
```

### Dependencies
Phase 1: `find` and `ls`, which the skill's rules rely on.

### Constraints
- `remove` and `rename` act only on the items named on their command line.
  The skill runs them only after the user has confirmed the list or accepted
  the proposal.
- The describing agent's trial on a real entry writes that entry's manifest:
  the one write into `library/` before Phase 3, and it is announced to the
  user first.
- The skill and the describing agent reach every command through the one
  entry point Phase 1 gave them, `.venv/bin/catalogue`; `unused`, `remove`
  and `rename` join it as subcommands.
- The manifest's format refuses an unknown key (Phase 0): `rename` adds the
  key that keeps the original file name to `ITEM_KEYS` in `core/catalogue.py`.

---

## Acceptance Criteria

- [ ] `make test` passes, `tests/test_triggers.py` included
- [ ] No command deletes or renames a file that was not named on its command line
- [ ] The describing agent's cost on a real entry is recorded in the report
