# Phase 2: A Trigger Audit of Every Skill

---

## Status

**Current Status:** 🟢 Done (100% — 5/5)
**Started:** 2026-09-25
**Completed:** 2026-09-25
**Blocked By:** —

---

## Before Starting This Phase

Read `phase-1-trigger-review.md` and `phase-1-trigger-review-report.md` in
full before touching anything here: the decisions already taken, the problems
and deviations recorded, and the changes made to this phase.

---

## While Working

Keep `phase-2-trigger-audit-report.md` current as the work happens — after
each significant step, and before every commit, pause, or end of session.

---

## Objective

Bring the description of every skill in `.claude/skills/` up to the
§5 trigger check. Each must carry a discriminating phrase that no other
carries, and name what must not trigger it. Each gets a test that holds it
there.

---

## Overview

### Why This Phase Matters
The user asked to use this roadmap to improve every skill, not only
`discussion`. The trigger check in `docs/architecture.md` §5 was written for
five skills; seven exist now. Only `discussion` has a test that holds its
discriminating phrase. The six others have none.

### What It Enables
A skill added later inherits the same test, and a description edit that
creates an overlap fails at once.

### Out of Scope
The body of each skill. Only the descriptions and their tests change here,
unless a finding from a Phase 1 review points at a body.

---

## Tasks

- [x] Read every skill's description against §5's trigger table, and list the overlaps and the missing "must not trigger" clauses
- [x] Rewrite the descriptions that fail, keeping the repository's style: what the skill does, when to use it, what is not its job
- [x] Write one repository-level test that every description carries a phrase no other description carries, and names at least one neighbour it must not be confused with
- [x] Update §5's trigger table to the seven skills, `session-review` included
- [x] Fold in the `trigger` findings the reviews since Phase 1 have produced, and the loads `metrics.py --transcript <t> --owed` reads from every transcript of the project, reviewed or not

---

## Technical Details

### Files to Modify
```
.claude/skills/*/SKILL.md          the description lines
tests/test_documentation.py        or a new repository-level test
docs/architecture.md               §5
```

### Dependencies
Phase 1, so that the reviews produce `trigger` findings to fold in.

### Constraints
The `discussion` skill's own description test stays; the repository-level
test generalises it and does not replace it.

---

## Acceptance Criteria

- [x] The repository-level test passes for all seven skills
- [x] §5's trigger table lists all seven skills
- [x] `make test` passes
