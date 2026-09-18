# Roadmap: The Closure Contract

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
Phase 0  What A Closure Must Not Rediscover  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/4)
TOTAL                                           ░░░░░░░░░░░░░░░░░░░░   0%  (0/4)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — What A Closure Must Not Rediscover

---

## Why This Roadmap Exists

Four phases closed in this repository on 2026-09-18, each audited before being
reported. Three of the four audits returned `FAIL`, and all three failures were
the same section of the same kind: `## Files Changed` disagreeing with what
`git diff` reports from the phase's start commit.

The cause was found only on the third: a phase is opened during the previous
phase's closure, before that closure is committed. `HEAD` at that instant is one
phase behind, so a diff from it sweeps in work that belongs to the phase before.

Nothing was wrong with the ritual and nothing was wrong with the auditor. The
fact simply lived nowhere a person opening a phase would read it. It now lives
in one phase report, which is worse than nowhere — it looks recorded.

This is carried from four reviews, where `aggregate.py` ranked it second on
recurrence across the corpus.

---

## Deliberately Out Of Scope

- The `roadmap` skill. It is installed outside this repository and replaced on
  update, like `diagram-design`. This repository fixes what this repository
  owns: its contract.
- Automating the check. A rule that fits in two lines of `CLAUDE.md` does not
  need a script first.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [What A Closure Must Not Rediscover](phase-0-closure-discipline.md) | 4 | 🔴 Not Started |

---

## Dependencies

None. `CLAUDE.md` already carries the contract; this adds two lines to it.

---

## Related Documentation

- `CLAUDE.md`, `## Roadmaps` — the contract being extended.
- `.claude/agents/roadmap-auditor.md` — what caught this four times.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/roadmap-contract/`
**Version:** 1.0.0
**Created:** 2026-09-18
**Last Updated:** 2026-09-18

---

## Changelog

### 1.0.0 (2026-09-18)

Carried from four reviews of session `53a9d27e`, written during phase 4 of the
`session-review` roadmap. One phase, four tasks: write the start-commit rule and
the Files Changed discipline into this repository's roadmap contract.
