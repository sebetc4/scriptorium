# Roadmap: Session Review Accuracy

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
Phase 0  What Belongs To The Task   🟢 ████████████████████ 100%  (5/5)
TOTAL                                  ████████████████████ 100%  (5/5)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** —

---

## Why This Roadmap Exists

`metrics.py` discards every turn whose tool input mentions the review tooling,
so that a review does not bill a task for the cost of reviewing it. The rule is
a substring match, and it cannot tell **running** the instrument from
**working on** it.

The consequence was measured, not suspected. The session that built this
instrument — four phases of the `session-review` roadmap — was measured at 106
API calls of 147 and 43 Bash calls of 125. A third of the work vanished, and
the direction is never random: the discarded turns are always work, so the
measure is always flattering.

This roadmap fixes the rule. It is carried from four reviews that each recorded
it, ranked first by `aggregate.py` on recurrence and severity.

---

## Deliberately Out Of Scope

- Rewriting the reviews already in the corpus. Their blocks record what the
  instrument said at the time, which is the honest thing for them to record.
- Any other measure. The exclusion is one function.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [What Belongs To The Task](phase-0-attribution.md) | 5 | 🟢 Done |

---

## Dependencies

`metrics.py` and its suite, from the `session-review` roadmap, phase 1.

---

## Related Documentation

- `.claude/skills/session-review/SKILL.md` — the budget the exclusion protects.
- `docs/roadmap/completed/session-review/` — where the instrument was built, to be created when that roadmap closes.

---

## Metadata

**Roadmap Status:** 🟢 Done
**Location:** `docs/roadmap/completed/session-review-accuracy/`
**Version:** 2.0.0
**Created:** 2026-09-18
**Last Updated:** 2026-09-20

---

## Changelog

### 2.0.0 (2026-09-20)

Roadmap closed, 5/5, and moved to
`docs/roadmap/completed/session-review-accuracy/` — straight from `pending/`,
since a roadmap of one phase never passes through `on-progress/`. `summary.md`
records where it started, where it landed, what was learned that outlives it,
and the two things it leaves open.

The instrument no longer under-measures work done on itself. What stays open is
named rather than buried: a turn that runs the tooling is excluded even when
running it was the work, and the five reviews already in the corpus keep the
figures the old rule produced.

No restructuring was left pending.

### 1.1.0 (2026-09-20)

Phase 0 closed, 5/5. The exclusion now asks what a tool call *does* rather than
what it names: a command that executes one of the three scripts, the skill being
invoked, or a write into `reviews/`. Reading, editing, testing or grepping those
same files is the task.

A second defect surfaced while measuring and is fixed with it: the exclusion was
applied record by record, and the transcript writes one record per content
block, so a message whose call sat in one record and whose thinking sat in
another had its call dropped and its turn counted. A turn is excluded now, not a
line of the file.

On the four slices of session `53a9d27e`: 106 API calls and 43 Bash calls
before, **132 and 110** after, against a raw 141 and 119 with no exclusion at
all. Two thirds of that session's commands had been discarded.

One acceptance criterion is left unticked. Its figures — 147 and 125 — were
taken over the whole file on 2026-09-19, and the four slices cover 09:16 to
10:09 while the session ran to 17:49. Both halves of the gap are measured in the
phase report.

### 1.0.0 (2026-09-18)

Carried from four reviews of session `53a9d27e`, written during phase 4 of the
`session-review` roadmap. One phase, five tasks: separate running the review
tooling from working on it, so that a slice is measured whole.
