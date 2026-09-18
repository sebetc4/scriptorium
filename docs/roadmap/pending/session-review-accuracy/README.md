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
Phase 0  What Belongs To The Task   🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                  ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — What Belongs To The Task

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
| 0 | [What Belongs To The Task](phase-0-attribution.md) | 5 | 🔴 Not Started |

---

## Dependencies

`metrics.py` and its suite, from the `session-review` roadmap, phase 1.

---

## Related Documentation

- `.claude/skills/session-review/SKILL.md` — the budget the exclusion protects.
- `docs/roadmap/completed/session-review/` — where the instrument was built, to be created when that roadmap closes.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/session-review-accuracy/`
**Version:** 1.0.0
**Created:** 2026-09-18
**Last Updated:** 2026-09-18

---

## Changelog

### 1.0.0 (2026-09-18)

Carried from four reviews of session `53a9d27e`, written during phase 4 of the
`session-review` roadmap. One phase, five tasks: separate running the review
tooling from working on it, so that a slice is measured whole.
