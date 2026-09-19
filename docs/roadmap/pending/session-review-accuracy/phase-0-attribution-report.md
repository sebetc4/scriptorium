# Phase 0 Report: What Belongs To The Task

**Phase:** [phase-0-attribution.md](phase-0-attribution.md)
**Start Commit:** 80e9771

---

## Work Log

### 2026-09-20

Phase opened. This is the roadmap's first phase, so there is no predecessor: its
`README.md` was read instead, and the review that produced it —
`reviews/2026-09-18-53a9d27e-roadmap-phase-1.md` on the working machine, whose
`measured:` block carries the figures this phase has to correct.

The reference transcript, session `53a9d27e`, is still in this project's
transcript directory. The acceptance criterion that rests on it — 147 API calls
and 125 Bash calls across its four slices — is therefore verifiable rather than
a record of what the fix was meant to reproduce.

**The rule, and why it is about the act rather than the subject.** The old
exclusion serialised a tool call's input to JSON and looked for `metrics.py`,
`corpus.py`, `aggregate.py`, `session-review` or `reviews/` anywhere in it. Any
mention of a path matched: reading one of those files, editing one, running its
tests, grepping it.

The new rule asks what the call *does*. A Bash command that executes one of the
three scripts — a python interpreter, its flags, then a path ending in the
script — the `session-review` skill being invoked, or a write under `reviews/`.
A test runner invoked with `-m` does not match, because the token after the
flags is the runner and not a script.

**A second defect, found while measuring.** The exclusion was applied record by
record. One message is written as one record per content block, so a message
whose tool call sits in one record and whose thinking sits in another had its
call dropped and its turn counted — half excluded, which is neither. It is a
turn that is excluded, not a line of the file, so `tooling_messages()` now makes
a first pass and collects the ids, and the second pass skips every record of
those messages.

**The figures.** Session `53a9d27e`, the four slices of 2026-09-18, bounded
09:16:00 to 10:09:00:

| | API calls | Bash calls |
|---|---|---|
| before this phase | 106 | 43 |
| after | **132** | **110** |
| raw, no exclusion at all, same bounds | 141 | 119 |
| the criterion as written | 147 | 125 |

The fix recovers 26 API calls and 67 Bash calls — two thirds of the commands
that session ran had been discarded. What stays excluded, 9 and 9, are the turns
that genuinely executed the tooling.

**The criterion's figures cannot be reproduced, for two reasons that have
nothing to do with the fix.** The first: the four slices end at 10:09, and the
session ran until 17:49 — 190 API calls and 159 Bash calls in total. Slice
totals were never going to equal session totals. The second: 147/125 was
measured on 2026-09-19 over the whole file, which has grown since.
Session-review's own Phase 1 said this would happen — "that transcript is
neither versioned nor permanent" — and it happened to the roadmap that quoted
it.

---

## Decisions

- **The exclusion asks what a call does, not what it names.** Running the
  tooling is a command that executes one of the three scripts, the skill being
  invoked, or a write into the corpus. Everything else — reading, editing,
  testing, grepping — is the task.

- **A turn is excluded, not a record.** The transcript writes one record per
  content block; anything that decides per record will drop half of a message.
  Any later reader of a transcript in this repository should take the same
  precaution, and `tooling_messages()` is the shape to copy.

- **A tooling run is excluded even when its intent was to test the tooling**,
  and the figures above include nine such turns. The alternative was considered
  and refused: exclude only inside a slice where a review actually happened,
  marked by a write under `reviews/` or the skill being invoked. It would have
  measured that session at its raw 141/119, and it is right in purpose — there
  is nothing to not-bill when no review happened. It was refused because it
  makes two identical commands measure differently depending on their
  neighbours, which is the conversation-shape inference the `session-review`
  roadmap ruled out at its opening. It is written down here so the next reader
  can overturn it on the argument rather than rediscover it.

---

## Files Changed

**Added**

- `docs/roadmap/pending/session-review-accuracy/phase-0-attribution-report.md`

**Modified**

- `.claude/skills/session-review/scripts/metrics.py`
- `.claude/skills/session-review/tests/test_metrics.py`
- `docs/roadmap/pending/session-review-accuracy/README.md`
- `docs/roadmap/pending/session-review-accuracy/phase-0-attribution.md`

---

## Problems And Deviations

- **The acceptance criterion "Session `53a9d27e` measures 147 API calls and 125
  Bash calls across its four slices" is left unticked.** Its figures were taken
  over the whole file on 2026-09-19; the four slices cover 09:16 to 10:09 and
  the session ran to 17:49. Both halves of the gap are measured and written
  above. The fix is verified on what can be verified: the same bounds, the same
  method, before and after.

- **A second defect was fixed that the phase had not named** — the per-record
  exclusion. It is in scope by the phase's own wording, which excludes *a turn*,
  and it accounts for part of the recovery.

- **The five reviews already in the corpus keep their figures.** The roadmap's
  *Deliberately Out Of Scope* says so: their blocks record what the instrument
  said at the time, and a corrected instrument produces corrected blocks from
  the same transcript whenever anyone wants them. The consequence, not stated
  there, is that `aggregate.py`'s medians currently mix measurements taken
  before and after this fix. With one `pdf` review and four `roadmap` reviews,
  no baseline is yet load-bearing.

All five tasks are done; three of four acceptance criteria hold.

---

## Changes To Later Phases

No phase follows. The roadmap closes with this one.

---

## Assessment

The instrument was under-measuring itself by two thirds of its commands, and the
rule that caused it reads as obviously correct until you ask what it matches. It
matched a *path*, and a path appears in a command that runs a file, a command
that reads it, a command that tests it and a command that greps it. Naming four
scripts was enough to make the error invisible for four phases.

The second defect is the one worth carrying. Excluding record by record when the
transcript writes one record per content block means excluding half a message:
the tool call goes, the turn stays. Nothing about the first defect hints at the
second; it surfaced because the corrected figures still looked odd and were
checked against a raw count taken a different way. That is the same habit that
found every silent breakage in the previous roadmap — measure it twice, by two
routes, and look at the gap.

What is left open, and it is a question rather than a defect: a turn that runs
the tooling is excluded even when running it *was* the work. Nine turns of the
reference session are in that position. The alternative is written down under
Decisions with the argument against it, and whoever disagrees has the figures to
argue from.
