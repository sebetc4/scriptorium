# Roadmap: Session Review

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
Phase 0  The Format                 🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
Phase 1  The Measurement            🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 2  The Skill                  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 3  The Ledger                 🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 4  The Corpus In Use          🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                  ░░░░░░░░░░░░░░░░░░░░   0%  (0/30)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — The Format

---

## Why This Roadmap Exists

Five skills carry this repository's work, and nothing measures them. When a
document costs twice what it should, when a check cries wolf for the third
time, when an instruction in a `SKILL.md` sends the agent somewhere it should
not go — the session that lived it is the only witness, and it closes.

One such witness statement exists: a session review written by hand on
2026-09-17. It is the origin of this roadmap, and it is also its best argument,
because half of it is wrong. It estimates four `pdf-reviewer` passes at
"≈ 109,500 tokens". The transcript of that session records **196,578 fresh
tokens and 727,020 cache reads**. The agent counted correctly everything it
could see pass — tool calls, duration, images — and invented the rest.

This roadmap builds the thing that does not invent. A script reads the
transcript and writes what is countable. A skill frames what only the session
knows: why it deviated, what it worked around, what it never thought to ask.
The two are kept apart on purpose, because they have different kinds of truth.

---

## What Was Measured Before Opening

Each of these was verified against real transcripts of this project, and each
one is load-bearing. A phase that finds one of them false should stop and say
so rather than work around it.

| Fact | Why it matters |
|---|---|
| `CLAUDE_CODE_SESSION_ID` is in the environment | The script finds its own transcript. No guessing by modification time, no collision between parallel conversations. |
| The transcript flushes live, about two seconds behind | A review written at the end of a task measures the whole task. |
| `attributionSkill` is a plain string on each assistant record | Turns and output can be attributed per skill, which is what makes a per-skill baseline possible. |
| Subagents live in `<session>/subagents/agent-<id>.jsonl` with a `.meta.json` carrying `agentType` | Delegated cost is exact, per agent and per run — the largest item in a review session and the one most often guessed. |
| Images are countable exactly | The hand-written review said eleven; the transcript says eleven. |
| `SessionStart` fires in this repository | Confirmed by the superpowers hook. `SessionEnd` could not be confirmed on this corpus, which is why the ledger sweeps at start (Phase 3). |
| Identical repeated Bash commands: zero on the session tested | A waste counter worth keeping, but not the one that will reveal anything here. Recorded so that Phase 1 does not oversell it. |

---

## Decisions Taken At Opening

**One task, one review.** Not one session. A conversation that builds two
documents produces two reviews, bounded by a cursor: a review starts where the
previous review of the same session stopped. Nothing is inferred from the shape
of the conversation — no heuristic on which user message opens a new task — and
the trigger is always explicit.

**The script owns `measured:`, the session owns the rest.** What a transcript
records is never written by hand; what a transcript cannot record is never
computed. A review that blurs the two is worth less than either half.

**`reviews/` is not versioned.** The corpus stays on the working machine,
because a review names the documents it reviewed. The consequence is
structural, not incidental: a finding reaches this repository only by becoming
a line in `docs/roadmap/pending/`. The `carried:` field exists for that.

**Medians are a dependency, not a report.** The skill's strongest defence
against self-flattery is comparing each measure to the median of previous
reviews of the same skill. That makes `corpus.py` part of the foundation
(Phase 0) and only the reports deferrable (Phase 4).

**The ledger sweeps at session start.** A hook on `SessionEnd` misses exactly
the sessions worth knowing about — the ones that crashed or were killed.

**Reviews are written in English**, like the rest of this repository.

**The suite runs on synthetic transcripts.** Unlike parts of the existing
suite, this one passes on a fresh clone: it never reads a real conversation.

---

## Deliberately Out Of Scope

- Reviewing code, or reviewing a built PDF. Those are `/code-review` and the
  `pdf-reviewer` agent, and this skill points at them rather than competing.
- Changing any production skill's behaviour. A review proposes; the roadmap
  disposes. A phase here that edits `pdf/SKILL.md` has left its lane.
- Any judgement written without a session. The hook records numbers and never
  prose, and nothing in this roadmap infers a cause from a measurement.
- Money. The scripts report tokens. Converting them to a price depends on
  tiers and cache rates this repository has no business tracking.
- Dashboards, HTML, artifacts. Text on stdout, in the idiom of `make list`.
- Sessions of other projects. The scripts read this project's transcript
  directory and nothing else.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [The Format](phase-0-format.md) | 5 | 🔴 Not Started |
| 1 | [The Measurement](phase-1-measurement.md) | 7 | 🔴 Not Started |
| 2 | [The Skill](phase-2-skill.md) | 7 | 🔴 Not Started |
| 3 | [The Ledger](phase-3-ledger.md) | 6 | 🔴 Not Started |
| 4 | [The Corpus In Use](phase-4-corpus.md) | 5 | 🔴 Not Started |

---

## Dependencies

- The transcript layout of Claude Code, as verified above. It is not a public
  contract: a version that moves it breaks Phase 1, and the suite is what will
  say so.
- `.venv/bin/python` and the repository's existing hook wiring in
  `.claude/settings.json`.

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md) — what earns a place in the core rather than in a skill, and §8 on scripts without a `make` target.
- `.claude/agents/pdf-reviewer.md` — the budget idiom this skill copies: few commands, few turns, report only.
- `.claude/hooks/skill-tests.sh` — the hook style Phase 3 follows: narrow match, silent degradation, never loud.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/session-review/`
**Version:** 1.1.0
**Created:** 2026-09-17
**Last Updated:** 2026-09-18

---

## Changelog

### 1.1.0 (2026-09-18)

Roadmap reviewed before opening, 27 tasks to 30. Every fact under *What Was
Measured Before Opening* was re-verified against the repository and the
transcript directory and all of them hold; the changes are three gaps the
review found.

Phase 3 gains two tasks and a criterion: the sweep is bounded to the top-level
`*.jsonl` files, it skips the live session — whose transcript is a few lines
old at `SessionStart` and would otherwise be frozen at nearly nothing — and it
re-sweeps a transcript that grew since its ledger was written. The cost of
refusing `SessionEnd` is now stated where the choice is made.

Phase 1 writes down the reference transcript's expected figures, because that
transcript lives outside the repository and rotates; the criterion was pinned
to a file that can disappear.

Phase 2 gains a task: the eight-thousand-token budget covers the tooling's own
output, not only the prose, so that it cannot be met by moving cost into a
command.

### 1.0.0 (2026-09-17)

Roadmap created from a design session, five phases, 27 tasks: fix the review
format and the corpus reader, measure a task from its transcript, frame the
judgement in a skill that cannot flatter itself, sweep every session into a
ledger, then put the corpus to work and carry the first findings back here.

The design was settled in conversation and its decisions are recorded above.
The facts under *What Was Measured Before Opening* were verified against this
project's own transcripts during that session, not taken from documentation.
