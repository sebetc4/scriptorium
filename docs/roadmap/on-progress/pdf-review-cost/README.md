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
Phase 0  The Targeted Pass                    🟢 ████████████████████ 100%  (4/4)
Phase 1  What A Check Can See Without An Eye  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                            █████████░░░░░░░░░░░  44%  (4/9)
```

**Current Phase:** Phase 0 — The Targeted Pass
**Blocked By:** —
**Next Milestone:** Phase 1 — What A Check Can See

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
| 0 | [The Targeted Pass](phase-0-targeted-pass.md) | 4 | 🟢 Done |
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

**Roadmap Status:** 🟡 In Progress
**Location:** `docs/roadmap/on-progress/pdf-review-cost/`
**Version:** 1.1.0
**Created:** 2026-09-18
**Last Updated:** 2026-09-20

---

## Changelog

### 1.1.0 (2026-09-20)

Phase 0 closed, 4/4. A verification pass costs **21,619 tokens against 32,666**
for a full one on a fifteen-page document — −33 % of the tokens, −46 % of the
tool calls, −57 % of the wall time — and writes six page images instead of four
sheets and six zooms. `review.py` runs the text-layer checks in both shapes, so
a fix that reflowed a page the pass was not given is still caught.

Four delegated attempts changed nothing before that. The agent's file asserted
its shape in four places, and — the part no rewording would have reached — kept
every judging criterion inside the full pass's own steps, so the other pass had
nowhere to learn what a defect is. Separating the criteria from the shape fixed
it in one edit. The `pdf-verifier` restructuring raised mid-phase is withdrawn.

### 1.0.0 (2026-09-18)

Carried from the review of session `4c7bb3d0`, written during phase 4 of the
`session-review` roadmap — the first review written with the real tooling, and
the one that measured what four delegated passes actually cost. Two phases,
nine tasks.
