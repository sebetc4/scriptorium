# Phase 0: The Discussion Skill

---

## Status

**Current Status:** 🟢 Done (100% — 14/14)
**Started:** 2026-09-24
**Completed:** 2026-09-26
**Blocked By:** —

---

## While Working

Keep `phase-0-discussion-skill-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Write the `discussion` skill: its `SKILL.md`, its journal template, its
boundaries with `sourcing` and `pdf`. Then register it everywhere the
repository names its skills.

---

## Overview

### Why This Phase Matters
Several documents already come from conversations held elsewhere. The
`sources/` of `led`, `instruments-diy`, `esp32` and `transistor` hold passages
the user copied out of them. Those passages are the other agent's answers,
without the questions that prompted them. The repository receives the result
without what the user said, without what was decided, and without knowing which
claims were checked. No discussion has been held in this repository yet. The mechanics of
a discussion need no tooling. What a skill adds is rules: where the journal
lives, what it records, what status each claim carries, and when to hand over.

### What It Enables
A discussion that can be resumed from one file, in any session, at the cost
of reading that file rather than replaying a transcript. It also gives a
pasted excerpt a way into a document without its claims gaining authority on
the way.

### Out of Scope
Any script. Writing `index.md`, which stays with `pdf`. Establishing a fact
from external sources, which stays with `sourcing`. Storing raw session
transcripts.

---

## Tasks

### The skill
- [x] Write `.claude/skills/discussion/SKILL.md`: when it fires (a discussion meant to become a document of the library, resuming one, an excerpt pasted from a conversation with another agent), what it refuses (writing `index.md`, establishing a fact from external sources, saving a raw transcript), and its handoffs to `sourcing` and `pdf`
- [x] Write the journal template in the skill's `assets/`: the goal, what the user said, the decisions, the claims with their status, the open questions, the outline, a dated session log
- [x] Write the resume procedure: a new session reads the journal alone, never the old transcript, and opens by stating where the discussion stands
- [x] Write the procedure for a pasted excerpt: the paste stays intact in `sources/`, its claims enter the journal as an agent's account, the chatter and the agent's offers are dropped, several pastes merge into one journal, and — because a paste carries the answers without the questions — what the user said is asked for, never inferred from the answers

### Boundaries and documentation
- [x] Write the description with a discriminating phrase no other skill carries, and check that it does not fire on an ordinary exchange about the repository
- [x] Add the skill to `CLAUDE.md`, `README.md` and `docs/architecture.md` §5: what it is for, what it refuses, its trigger row, and its boundary with `sourcing`
- [x] Add the journal to `docs/document.md` and to the durable table of `docs/architecture.md` §11

### Tests
- [x] Add the skill's suite: the template carries every section the skill names, and the skill states its three statuses and its two handoffs

### The first real case
- [x] Hold the user's discussion here with the draft, over at least one fresh-session resume, and fold what it shows into the skill

### The archive
- [x] Rewrite the skill and the template for a multi-file journal: `study/discussion/index.md` (the entry, the only file a resume reads, with a map of topics), `topics/<subject>.md` (the current state of a subject), `sessions/<date>.md` (the append-only archive of what each session covered, decided and replaced)
- [x] Write the rules that keep the files from drifting: one fact lives in one place, a superseded point moves to its session's archive with a link both ways, and a topic is loaded only when the discussion returns to it
- [x] Test that every link of an `index.md` and of a topic file resolves, on a fixture journal
- [x] Migrate the notebook's journal (`electronics/notebook/study/discussion.md`) to the new layout, after asking the user
- [x] Validate on a next session of the notebook and a fresh-session resume: the resume reads `index.md` alone, and a point from an earlier session is found through the links

---

## Technical Details

### Files to Modify
```
.claude/skills/discussion/SKILL.md           new
.claude/skills/discussion/assets/journal.md  new, the template
.claude/skills/discussion/tests/             new, the skill's suite
CLAUDE.md                                    Which skill
README.md                                    the skills list
docs/architecture.md                         §5 and §11
docs/document.md                             study/
```

### Dependencies
None.

The archive also touches `core/library.py`, `tests/test_library.py` and a
fixture journal under `tests/fixtures/library/sample/component/study/`: the
link check runs in `make check-library` (see the report's Decisions).

### Constraints
- The journal lives in `study/`. It is written by the agent and neither
  received nor derived, so it is durable, like the `NOTES.md` of `sourcing`.
- The three statuses are *said by the user*, *an agent's account, unverified*
  (this agent's, or that of the agent a paste came from) and *established*. The last one always points at the `sourcing` journal that
  established it. They are worded to read like the three sections of the
  `sourcing` journal.
- No instruction writes into `sources/`: `.claude/hooks/protect-paths.sh`
  refuses it anyway.
- The skill ships no script. One is added only if Phase 1 shows a step to be
  mechanical and repeated.

---

## Acceptance Criteria

- [x] `make test` passes, including `test_claude_md_and_readme_point_at_every_skill`
- [x] The skill names where the journal lives, and none of its instructions writes into `sources/`
- [x] The two descriptions alone are enough to tell whether a request is `discussion` or `sourcing`
- [x] In the user's real discussion, the skill fires unasked both when the discussion opens and when it resumes in a fresh session
- [x] At that resume, the size of the journal read and of the transcript it replaces are both recorded in the report, and the journal is a small fraction of the transcript
