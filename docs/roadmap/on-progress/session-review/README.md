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
Phase 0  The Format                 🟢 ████████████████████ 100%  (5/5)
Phase 1  The Measurement            🟢 ████████████████████ 100%  (7/7)
Phase 2  The Skill                  🟢 ████████████████████ 100%  (7/7)
Phase 3  The Ledger                 🟢 ████████████████████ 100%  (6/6)
Phase 4  The Corpus In Use          🟡 █░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                  █████████████████░░░  83%  (25/30)
```

**Current Phase:** Phase 4 — The Corpus In Use
**Blocked By:** —
**Next Milestone:** Phase 4 — The Corpus In Use

---

## Why This Roadmap Exists

Five skills carry this repository's work, and nothing measures them. When a
document costs twice what it should, when a check cries wolf for the third
time, when an instruction in a `SKILL.md` sends the agent somewhere it should
not go — the session that lived it is the only witness, and it closes.

One such witness statement exists: a session review written by hand on
2026-09-17. It is the origin of this roadmap, and it is also its best argument,
because half of it is wrong. It estimates four `pdf-reviewer` passes at
"≈ 109,500 tokens". The transcript of that session records **91,911 fresh
tokens and 288,210 cache reads** for those passes. The agent counted correctly
everything it could see pass — tool calls, duration, images — and invented the
rest.

Those two figures read 196,578 and 727,020 when this roadmap was written, and
that was the second wrong count of the same session: a transcript writes one
record per content block and repeats the whole `usage` on each, so summing over
records inflates every token figure. Phase 1 found it, and it is recorded in
that phase's file. The argument for this roadmap is not weakened by its own
example being wrong twice — it is the argument.

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
| One assistant message is written as one record per content block, each repeating the whole `usage` | Verified in Phase 1, after it invalidated this roadmap's own reference figures. Usage is deduplicated by `message.id`; content blocks are not. |
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
| 0 | [The Format](phase-0-format.md) | 5 | 🟢 Done |
| 1 | [The Measurement](phase-1-measurement.md) | 7 | 🟢 Done |
| 2 | [The Skill](phase-2-skill.md) | 7 | 🟢 Done |
| 3 | [The Ledger](phase-3-ledger.md) | 6 | 🟢 Done |
| 4 | [The Corpus In Use](phase-4-corpus.md) | 5 | 🟡 In Progress |

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

**Roadmap Status:** 🟡 In Progress
**Location:** `docs/roadmap/on-progress/session-review/`
**Version:** 1.5.0
**Created:** 2026-09-17
**Last Updated:** 2026-09-18

---

## Changelog

### 1.5.0 (2026-09-18)

Phase 3 closed, 6/6. `.claude/hooks/session-ledger.sh` runs on `SessionStart`
and sweeps this project's transcripts in the background, writing a ledger entry
for each one that owes one. The decision logic lives in `metrics.py --sweep`,
where it can be tested; the hook is fourteen lines that exit zero whatever
happens.

The sweep takes the top-level `*.jsonl` and nothing else — never `memory/`,
never a session's `subagents/`, which `metrics.scan` reaches through its own
session. It skips a transcript of fewer than three assistant turns and the live
session, whose transcript is a few lines old at `SessionStart` and would
otherwise be frozen at nearly nothing while looking complete. An entry is keyed
by transcript and carries the `bytes` it was computed from, so a session that
has grown is swept again and measured whole, and a damaged entry is rewritten
rather than trusted.

`corpus.py --coverage` names, per session of the ledger, the spans nobody sat
down to review — by time, never by content. On this project's four eligible
transcripts it reports 0/4 fully reviewed, which is the honest state of a corpus
that has no reviews in it yet.

15 tests for the ledger, 470 for the repository.

### 1.4.0 (2026-09-18)

Phase 2 closed, 7/7. The skill exists: `SKILL.md`, 122 lines, with a
description that states in the negative what it never does, a budget of eight
thousand tokens that names the tooling's own output as part of what it covers,
and the rule that a review belongs at the end of its task rather than at the end
of a long session, because compaction takes the half no script can rebuild.

**The obligations are arithmetic, not good faith.** Four of the six are fired by
`metrics.py --owed` from the measures themselves — the largest costs, every
measure past one and a half times its median, every non-zero waste and friction
counter, every correction the user made. The fifth is enforced by `corpus.py`,
which refuses a finding without a target and a fix. The sixth is a rule about
writing and is stated. With an empty corpus the median obligation cannot fire,
so the first one widens from three costs to five: an obligation that cannot fire
is not a lenient obligation, it is an absent one.

`session-review` is named in `CLAUDE.md` and `README.md` as outside the
production chain. Its suite is 15 tests, and the repository's is 455.

Two acceptance criteria are left unticked, both because they can only be
observed from a later session: that the description keeps the skill from
loading during ordinary work, and that a review costs under eight thousand
tokens measured by the next one. Phase 4 observes both.

### 1.3.0 (2026-09-18)

Phase 1 closed, 7/7. `scripts/metrics.py` turns a slice of a transcript into the
`measured:` block: tokens for the main context and for each delegated run
separately, tool calls by name, images, skill spans, friction, and derived
measures that each print their rule. `--ledger` gives Phase 3 its session-level
JSON, `--timeline` is off by default and truncated to sixty characters a line.
The suite is 22 tests on transcripts built line by line.

**The roadmap's own reference figures were wrong, and the instrument found it.**
A transcript writes one record per content block and repeats the whole `usage`
on each; the figures were summed over records, and the fresh column counted
output tokens as context. Both wrong figures reproduce exactly by that method.
The four delegated passes read 91,911 fresh tokens and 288,210 cached, not
196,578 and 727,020. Corrected in the README's opening argument, in the phase
file's table — which keeps both columns and the arithmetic of the gap — in
`references/format.md`, whose example is now the script's real output, and in
the Phase 0 fixture that had enshrined the figure in an assertion.

One acceptance criterion is left unticked on purpose: the script does not
reproduce that table, and the table was what was wrong. `output:` joined the
format's `tokens:` block while the corpus is still empty, so no migration.

### 1.2.0 (2026-09-18)

Phase 0 closed, 5/5. The review format, the finding vocabulary and the corpus
reader exist: `references/format.md` carries one complete review written out in
full, `references/findings.md` closes the `kind` vocabulary at eight — each with
the origin review's own case as its worked example — and `scripts/corpus.py`
reads the corpus through `core.doc`, adding nothing to `requirements.txt`. Its
suite is 27 tests on three hand-written fixtures and reads no transcript.

Two of the format's rules are code rather than prose: a measure the transcript
does not carry is absent and never zero, and a median needs two reviews, so an
empty corpus and a corpus of one both answer "no baseline yet". Phase 1 depends
on both.

One deviation, recorded in the phase report: `.gitignore` keeps a line for
`agent-reviews/` beside the new `reviews/`, so that the hand-written review does
not become visible to git before Phase 4 decides what becomes of it.

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
