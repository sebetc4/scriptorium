# Phase 3 Report: The Ledger

**Phase:** [phase-3-ledger.md](phase-3-ledger.md)
**Start Commit:** 12f9234

---

## Work Log

### 2026-09-18

Phase opened. Phase 2's file and report were read in full: 7/7 tasks, four of
six acceptance criteria met, two left unticked because they can only be observed
from a later session. No restructuring pending.

The start commit is `12f9234`, the commit that closed Phase 2 — the convention
Phase 2's report writes down, since a phase is always opened before the previous
closure is committed and HEAD at that instant is one phase behind.

**The hook is thin because the decisions are testable elsewhere.** The phase
asks for a hook of about twenty lines and for six acceptance criteria, five of
which are about *when not to write an entry*. A hook that decided those in shell
would be untestable in this repository's suite, so the decisions went into
`metrics.py --sweep` — which already owned `--ledger` — and the hook came out at
fourteen lines: check `.venv`, check the script, run it in the background,
exit zero. It is the `skill-tests.sh` shape: narrow match, early exit, silence
unless something matters, except that here nothing ever matters enough to speak.

The sweep takes `folder.glob("*.jsonl")` and deliberately not `rglob`: the
top-level transcripts and nothing else. `memory/` is not a session, and a
session's `subagents/` directory is reached by `subagent_runs()` through its own
session — swept directly it would be counted twice, once as a subagent and once
as a session of its own.

**Three skips, and each has a reason that is not obvious from the outside.** A
transcript of fewer than three assistant turns is a start that was abandoned or
a question answered in one turn. The live session is skipped because at
`SessionStart` its transcript is a few lines old: an entry written then would
look complete and be nearly empty — the worst of both, since a later sweep
would find it present and move on. That last part is what the `bytes` field
settles: the entry records the size it was computed from, so a session that has
grown is swept again, and a truncated or damaged entry is rewritten rather than
trusted.

Run against this project, the sweep wrote four entries in 0.11 s over some
twenty megabytes of transcripts: the live session skipped, and the two 97-byte
transcripts skipped for want of turns, exactly as the criteria predicted.

**Coverage went into `corpus.py`**, which already holds everything that reads
the corpus. For each session of the ledger it subtracts the review slices of
that session from the session's own span and returns what is left, as
timestamps. On this project: 0/4 fully reviewed, which is the honest state of a
corpus that has no reviews in it yet, and the first figure this roadmap has
produced that says something about what is *missing* rather than about what was
done.

`make test`: 470 passed, 15 of them this phase's.

---

## Decisions

- **The sweep's policy lives in `metrics.py --sweep`, not in the hook.** Every
  decision about when an entry is owed is Python and is tested; the hook is a
  guard and a background call. Phase 4's `aggregate.py --coverage` follows the
  same split: it presents `corpus.coverage()` and computes nothing itself.

- **An entry is keyed by transcript and carries `bytes`.** The re-sweep
  decision is `size on disk != size recorded`, and it needs no other state — no
  timestamp of the sweep, no record of which session wrote it. A damaged or
  unreadable entry is treated as absent, so the ledger repairs itself.

- **The live session is skipped, not partially recorded.** A partial entry that
  looks complete is worse than no entry, because the next sweep would accept
  it. Skipping costs one session of delay, which is what refusing `SessionEnd`
  already costs.

- **Coverage is named by time and nothing else.** The row holds the session, the
  turn count, the number of reviews and the uncovered spans. Nothing about what
  was done in a gap — the ledger holds numbers, and a gap is a number too.

---

## Files Changed

**Added**

- `.claude/hooks/session-ledger.sh`
- `.claude/skills/session-review/tests/test_ledger.py`
- `docs/roadmap/on-progress/session-review/phase-4-corpus-report.md`

**Modified**

- `.claude/settings.json`
- `docs/roadmap/on-progress/session-review/phase-2-skill-report.md`
- `.claude/skills/session-review/scripts/metrics.py`
- `.claude/skills/session-review/scripts/corpus.py`
- `docs/roadmap/on-progress/session-review/README.md`
- `docs/roadmap/on-progress/session-review/phase-3-ledger.md`
- `docs/roadmap/on-progress/session-review/phase-3-ledger-report.md`
- `docs/roadmap/on-progress/session-review/phase-4-corpus.md`

The last two entries of each group are Phase 4, opened during this closure: its
status moved to 🟡 and its report was created. Phase 2's report appears because
`76e968e` corrected its start commit after `12f9234` had been cut, so the
correction falls inside this phase's span rather than the one it describes.

---

## Problems And Deviations

- **The hook's logic lives in a Python script rather than in the shell**, which
  the phase's *Files to Modify* did not anticipate: it listed the hook and
  `corpus.py`, and `metrics.py` grew a `--sweep` instead. The reason is in the
  Work Log — five of the six acceptance criteria are about when *not* to write
  an entry, and shell decisions are not reachable by this repository's suite.

- **`reviews/.ledger/` now holds four entries for this project's real
  sessions**, written while testing the sweep by hand. They are outside the
  repository, as everything under `reviews/` is, and Phase 4 reads them.

Nothing else: all six tasks are done and all six acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 4's
`aggregate.py --coverage` has `corpus.coverage()` to present, and the ledger it
runs against already exists.

---

## Assessment

The ledger is the part of this roadmap with no reader. Nobody will open
`reviews/.ledger/`, and it holds nothing a person would want to read. Its value
is entirely in the second figure it makes possible: not what a reviewed task
cost, but how much of the work was never reviewed at all. Four sessions, none
covered, is a more useful sentence about this project today than any measurement
in the three phases before it.

The design choice worth carrying forward is the one about the live session. The
tempting version writes an entry for every transcript found, including the
running one, and it looks more complete; it is the version in which the
busiest sessions are recorded at their first thirty seconds and never revisited.
Skipping the live session and keying on `bytes` costs one session of delay and
makes every entry whole.

What Phase 4 needs to know first: the instrument is complete and untested
against real work, which is that phase's subject. Three things are ready for it.
`corpus.coverage()` returns rows, not text — `aggregate.py --coverage`
presents them and computes nothing. The corpus is still empty, so the first
review written under the skill will print "no baseline yet" and owe five costs
rather than three; the second review of the same skill is where the median
obligation first fires, and that transition is worth watching rather than
assuming. And the re-review of session `4c7bb3d0` now has two wrong counts to
measure itself against, not one: the hand-written review's "≈ 109,500 tokens"
and this roadmap's own 196,578 — both recorded, with the arithmetic of each.
