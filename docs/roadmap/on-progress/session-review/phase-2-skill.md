# Phase 2: The Skill

---

## Status

**Current Status:** 🟡 In Progress (0% — 0/7)
**Started:** 2026-09-18
**Completed:**
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

Write the rules a session follows when it reviews its own work — rules built on
the assumption that it would rather not.

---

## Overview

### Why This Phase Matters
A session grading itself gives itself a good mark. The skill therefore never
asks what went wrong; it sets obligations that the measurements trigger. A
measure above one and a half times its median owes an explanation. A non-zero
waste counter owes a finding. Every correction the user made owes one or a
reason why it was unavoidable.

### What It Enables
Reviews exist. The corpus begins.

### Out of Scope
Changing any production skill. A finding names a target and proposes a fix; it
does not apply one.

---

## Tasks

### The skill
- [ ] Write `SKILL.md`, in English, with a description that states in the negative what it never does — it is not part of doing the work, it measures the work once the work is done
- [ ] Write in the six obligations: explain the three largest costs, explain every measure past one and a half times its median, a finding or a justification for each non-zero waste and friction counter, a finding or a reason for each user correction, no finding without a target and a fix, and no section for what went well
- [ ] Write in its own budget: two commands, at most two file reads, no rebuild and no subagent, prose under six hundred words, findings of three lines each — and the whole under eight thousand tokens, which the next review will check
- [ ] State what the eight thousand cover: everything the review puts in the context, the tooling's own output included — `metrics.py`'s block, the medians beside it, `--timeline` when it is asked for — so that a budget cannot be met by moving cost from the prose into a command

### The loop
- [ ] Close the loop: at the end of a review, list the `severity: high` findings, ask which are carried to `docs/roadmap/pending/`, and write their `carried:`

### The repository
- [ ] Add the row to `CLAUDE.md`'s *Which skill* table, marked as outside the production chain, and the mention `README.md` needs
- [ ] Write the suite: a review produced against a fixture transcript satisfies `corpus.py`, and the obligations fire on the thresholds they claim to

---

## Technical Details

### Files to Modify
```
.claude/skills/session-review/SKILL.md      new — about 150 lines
CLAUDE.md                                   one row in the skill table
README.md                                   the skill named
.claude/skills/session-review/tests/        the obligations
```

### Dependencies
Phase 1's `metrics.py`, and Phase 0's format and vocabulary.

### Constraints
`tests/test_documentation.py::test_claude_md_and_readme_point_at_every_skill`
requires every skill under `.claude/skills/` to be named, in backticks, in both
`CLAUDE.md` and `README.md`. Adding the directory without both mentions breaks
`make test`.

The description is the only thing that stops this skill loading during ordinary
work. `sourcing` is the model: it says what it produces and, plainly, what it
is not for.

---

## Acceptance Criteria

- [ ] A session asked to write a PDF does not load this skill; a session asked to review a finished task does
- [ ] The skill states a rule for the degraded case: a review belongs at the end of its task, not at the end of a long session, because compaction takes the part no script can rebuild
- [ ] A review written under the skill costs under eight thousand tokens, tooling output included, measured by the next one
- [ ] `make test` passes, documentation test included
- [ ] The six obligations are each testable, and tested
- [ ] `--timeline` is named as optional, and the budget is met without it

---

## Notes
