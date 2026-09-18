# Phase 2 Report: The Skill

**Phase:** [phase-2-skill.md](phase-2-skill.md)
**Start Commit:** 584c06f

---

## Work Log

### 2026-09-18

Phase opened. Phase 1's file and report were read in full: 7/7 tasks, six of
seven acceptance criteria met, one left unticked on purpose because the phase
file's reference table was wrong and the script is right. No restructuring
pending.

The start commit recorded above is `584c06f`, the commit that closed Phase 1,
not `d6014e1` — HEAD at the instant this phase was opened. Every phase of this
roadmap is opened during the previous one's closure, before that closure is
committed, so HEAD at that moment is always one phase behind and makes the
previous phase's work look like this one's. The convention from here on: a
phase's start commit is the commit that closed the phase before it.

Read first: `sourcing/SKILL.md`, named by the phase as the model for a
description that states what a skill is not for, and `.claude/agents/pdf-reviewer.md`,
named as the model for a budget — few commands, few turns, report only.

**The obligations came before the prose, and that changed the design.** The
phase asks for six obligations and for a suite in which "the obligations fire on
the thresholds they claim to". A rule that only exists as a sentence in a
`SKILL.md` cannot fire and cannot be tested; a session under budget pressure
reads it as advice. So four of the six were made arithmetic: `metrics.owed()`
takes the tally, the corpus and the skill, and returns the duties those measures
trigger, printed under `# owed by the review` by `metrics.py --owed`.

The four that fire: the largest costs, ranked from the measures; every measure
past one and a half times its median, named with its ratio; every non-zero waste
and friction counter, one line each; and a standing line for the user's
corrections, which no transcript can count and which only the session can. The
fifth — no finding without a target and a fix — was already enforced by
`corpus.py` in Phase 0, so the skill states it and the suite checks that the
refusal happens. The sixth, no section for what went well, is a rule about
writing that no script can check on prose; the suite checks that the skill says
it.

**The empty corpus needed a rule of its own.** Phase 1's report warned that the
first reviews would print "no baseline yet", which disarms the median
obligation. Leniency there would be a design in which the instrument is weakest
exactly when the corpus is least able to correct it. So with no baseline the
first obligation widens: three largest costs become five, stated in the output
itself. The duty does not disappear, it changes shape.

Adding `--owed` took the default output from 38 lines to 43 on the reference
session, still under the fifty the previous phase's criterion set, and the
suite pins that with a slice engineered to fire every counter at once.

`SKILL.md` came to 122 lines. The description states the negative in the form
the acceptance criterion needs — "not part of doing the work", "builds nothing,
fixes nothing", "never runs while a task is still in progress" — and the suite
asserts each of those phrases, since the description is the only thing standing
between this skill and every ordinary session in the repository.

`session-review` was added to `CLAUDE.md`'s *Which skill* table and to
`README.md`'s skill table, both marked as outside the production chain, which
`test_claude_md_and_readme_point_at_every_skill` requires the moment a
`SKILL.md` exists. `make test`: 455 passed, the skill's own suite 15 of them.

---

## Decisions

- **Four of the six obligations are computed, not written.** `metrics.owed()`
  fires them from the measures. Phase 4's `aggregate.py` and any later
  obligation go through it rather than adding prose to `SKILL.md`: a rule that
  cannot fire cannot be tested, and a rule that cannot be tested is advice.

- **`--owed` lives in `metrics.py` rather than in a script of its own.** The
  skill's budget allows two commands; a separate script would have spent one of
  them on a pipe, and every obligation needs the tally and the medians that
  `metrics.py` already holds.

- **An empty corpus widens the first obligation rather than relaxing it.**
  Three costs become five while no baseline exists. Phase 4 will be the first
  to run against a corpus that has one, and is where the transition can be
  observed.

- **The skill names one command, not two.** `metrics.py --owed --skill <skill>`
  produces the block, the comparison table and the obligations in one call;
  `corpus.py` is run afterwards only to check that what was written parses. The
  budget's "two commands" is therefore a ceiling that the ordinary case does
  not reach.

- **The review is written at the end of its task.** Stated in the skill with
  its reason: compaction takes what only the session knows, which is the half
  no script can rebuild. This is the degraded case the phase asked to be
  written down.

---

## Files Changed

**Added**

- `.claude/skills/session-review/SKILL.md`
- `.claude/skills/session-review/tests/test_skill.py`
- `docs/roadmap/on-progress/session-review/phase-3-ledger-report.md`

**Modified**

- `.claude/skills/session-review/scripts/metrics.py`
- `CLAUDE.md`
- `README.md`
- `docs/roadmap/on-progress/session-review/README.md`
- `docs/roadmap/on-progress/session-review/phase-2-skill.md`
- `docs/roadmap/on-progress/session-review/phase-2-skill-report.md`
- `docs/roadmap/on-progress/session-review/phase-3-ledger.md`

The last two entries of each group are Phase 3, opened during this closure: its
status moved to 🟡 and its report was created.

---

## Problems And Deviations

- **Two acceptance criteria are left unticked, and neither can be met from
  inside this phase.** "A session asked to write a PDF does not load this skill;
  a session asked to review a finished task does" is a fact about later
  sessions: what this phase could do — a description that states the negative,
  asserted phrase by phrase in the suite — it did. "A review written under the
  skill costs under eight thousand tokens, tooling output included" says in its
  own words that it is measured by the next review, and no review exists yet.
  Phase 4 observes both, and they are named here rather than ticked on the
  strength of a design that has never been exercised.

- **The report's start commit was corrected** from `d6014e1` to `584c06f`,
  for the reason given in the Work Log. Phase 1's report had the same
  correction made by hand; this is the second time, so the rule is now written
  down rather than rediscovered.

- **`metrics.py` was modified during this phase**, though it is Phase 1's file
  and Phase 1 is closed. `--owed` needed the tally and the medians, and a phase
  closing does not freeze the code it wrote — only its report. Phase 1's suite
  still passes unchanged.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 3's
hook needs `--ledger`, which Phase 1 delivered and this phase did not touch.

---

## Assessment

The skill exists and its obligations have teeth, which was the whole risk of
this phase. The thing being guarded against is a session writing a warm account
of its own work under a heading called "review", and prose alone cannot stop
that — a session that is tired, or over budget, or pleased with itself will read
a rule as a suggestion. Four of the six obligations now arrive as printed output
from arithmetic it did not perform, which is a different kind of instruction.

The empty-corpus rule is the part most likely to matter later. It would have
been easy to let the median obligation simply not fire on a young corpus, and
the result would have been an instrument at its weakest during the very reviews
that shape the baselines everything afterwards is compared against.

What Phase 3 needs to know first: `metrics.py --ledger` is already exactly what
the hook has to write — it ignores the review cursor, reads the whole
transcript, and carries `bytes`, the size it was computed from, so the re-sweep
decision is `size on disk != size recorded` and needs no other state. The
session running the hook must write no ledger for itself, which `bytes` also
settles: at `SessionStart` the live transcript is a few lines old, and a ledger
written then would freeze it at nearly nothing while looking complete. Skip the
live session by its `CLAUDE_CODE_SESSION_ID`, and the next session will find it
grown and sweep it whole.
