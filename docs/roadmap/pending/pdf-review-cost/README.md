# Roadmap: The Cost Of Looking At A PDF

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
Phase 0  The Targeted Pass                    🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/4)
Phase 1  What A Check Can See Without An Eye  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                            ░░░░░░░░░░░░░░░░░░░░   0%  (0/9)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — The Targeted Pass

---

## Why This Roadmap Exists

Reviewing one PDF document cost more than writing it. On session `4c7bb3d0`,
measured after the fact by `metrics.py`, four delegated passes read 91,911 fresh
tokens against 154,333 for everything the main context did, and eleven images
carried 625,600 tokens of context between them.

Two findings, both carried from `reviews/2026-09-17-4c7bb3d0-round-led-d4017.md`
on the working machine, account for most of it:

- A verification pass re-reads the whole document. The second round cost 46,636
  fresh tokens to confirm fixes on six pages of fifteen.
- Nothing checks a figure before it is looked at. Text at 4.6 pt, three label
  collisions and a missing `≈` glyph were each found by an eye, three steps
  later, after eleven images had entered the conversation.

The first is a matter of what the reviewer is allowed to be asked. The second is
arithmetic that no one is doing.

---

## Deliberately Out Of Scope

- Making the reviewer judge more. It sees; the conversation diagnoses. Both
  phases keep that line.
- Reducing the number of review rounds. Two rounds found real defects both
  times; what is expensive is their shape, not their existence.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [The Targeted Pass](phase-0-targeted-pass.md) | 4 | 🔴 Not Started |
| 1 | [What A Check Can See](phase-1-svg-preflight.md) | 5 | 🔴 Not Started |

---

## Dependencies

`.claude/agents/pdf-reviewer.md` and `.claude/skills/pdf/scripts/review.py`,
both of which already exist and are already under budget.

---

## Related Documentation

- `.claude/agents/pdf-reviewer.md` — the budget idiom neither phase may loosen.
- `.claude/skills/pdf/SKILL.md` — where a targeted pass is asked for.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/pdf-review-cost/`
**Version:** 1.0.0
**Created:** 2026-09-18
**Last Updated:** 2026-09-18

---

## Changelog

### 1.0.0 (2026-09-18)

Carried from the review of session `4c7bb3d0`, written during phase 4 of the
`session-review` roadmap — the first review written with the real tooling, and
the one that measured what four delegated passes actually cost. Two phases,
nine tasks.
