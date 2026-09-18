# Phase 4 Report: The Corpus In Use

**Phase:** [phase-4-corpus.md](phase-4-corpus.md)
**Start Commit:** 0df5266

---

## Work Log

### 2026-09-18

Phase opened. Phase 3's file and report were read in full: 6/6 tasks, 6/6
acceptance criteria, no restructuring pending. Per the convention Phase 2 wrote
down, this phase's start commit is `0df5266`, the commit that closed Phase 3.

**The hook proved itself before any of this phase's work began.** The ledger
entry for session `53a9d27e` — the session that built phases 0 to 3 — was
written by the `SessionStart` hook of the session that wrote this report. That
is Phase 3's criterion "the next session writes its complete one" demonstrated
outside a test, which no test could have done.

**`aggregate.py` first**, since it reads what the rest of the phase produces:
baselines per skill, findings ranked by recurrence before severity, the backlog
of high findings nobody carried, coverage, and a before-and-after around a date.
Fifteen tests. Two of its own defects were found by running it on the real
corpus rather than on fixtures, and both were fixed here: the backlog listed the
same finding once per review instead of once with a count, and coverage reported
a sliver of a second uncovered for an exactly-reviewed session, because a review
writes its bounds to the second and the ledger writes them to the microsecond.

**Then the reviews.** Five: the re-review of session `4c7bb3d0` with the real
tooling, and four of session `53a9d27e`, one per phase, each bounded by the
user request that opened it. The four are what makes a median exist — and they
are also the substitute evidence for the task this phase could not do.

**The instrument found a defect in itself, and it is the phase's main result.**
`metrics.py` discards any turn whose tool input mentions the review tooling, so
that a review does not bill a task for the cost of reviewing it. The rule is a
substring match, and the work of phases 0 to 3 *was* the review tooling. Measured
against the transcript by hand:

| Slice | API calls | Bash calls |
|---|---|---|
| Phase 0 | 37 of 50 | 15 of 43 |
| Phase 1 | 38 of 48 | 20 of 43 |
| Phase 2 | 17 of 22 | 5 of 17 |
| Phase 3 | 14 of 21 | 3 of 16 |
| Session | **106 of 147** | **43 of 125** |

A third of the API calls and two thirds of the commands were discarded as
tooling. The error has a direction — the discarded turns are always work — so
the measure is always flattering, which is the exact failure mode this roadmap
was built against. It is recorded in all four reviews, ranked first by
`aggregate.py` on recurrence, and carried.

**The re-review of `4c7bb3d0` added accuracy and no insight.** Its seven
findings are the hand-written review's own improvements, reframed with a target
and a fix. Nothing came out of the instrument that the session had not already
reached by hand. The acceptance criterion anticipated this and asked for it to
be recorded as a result, which is what it is: the instrument's contribution to
that session is the figures, not the conclusions.

The figures are the contribution, and they are large. "≈ 109,500 tokens" for the
four delegated passes, and this roadmap's own 196,578 fresh and 727,020 cached,
are both wrong. The passes read 91,911 fresh and 288,210 cached. Both wrong
figures reproduce to the token by the arithmetic that made them.

**The loop closed.** The user was shown the ranked findings and chose four:
three `high` and the `medium` that had recurred four times. Three roadmaps now
exist under `docs/roadmap/pending/` — `session-review-accuracy`,
`pdf-review-cost` (two phases) and `roadmap-contract` — and each review's
`carried:` names the phase file its finding went to. `aggregate.py` reports an
empty high-severity backlog.

`make test`: 485 passed.

---

## Decisions

- **The hand-written review of 2026-09-17 is kept as the origin document**, at
  `reviews/.origin/`, and `agent-reviews/` is gone from `.gitignore`. Not
  converted — `reviews/2026-09-17-4c7bb3d0-round-led-d4017.md` is its
  conversion, written from the same session with the real tooling. Not retired
  either: it is the only record of what a careful session produces without an
  instrument, and this roadmap's whole argument rests on comparing the two. It
  sits under a dotted directory so that `corpus.load()`'s glob does not try to
  parse it.

- **Two defects in this phase's own reports were fixed here rather than
  carried.** The out-of-scope rule protects production skills from being changed
  by a review; it is not a reason to ship a report that prints a false gap. Both
  fixes are one line and both are tested.

- **The four roadmap reviews slice one session by task, not by session.** This
  is the format's own rule exercised for the first time: four user requests,
  four tasks, four reviews, each starting where the previous stopped. The
  cursor worked; nothing had to be inferred from the shape of the conversation.

- **Findings were carried only after the user chose them.** The skill's loop
  says the session lists and the user decides, and this phase is the first time
  that mattered. Three of ten findings were left in the corpus deliberately.

---

## Files Changed

**Added**

- `.claude/skills/session-review/scripts/aggregate.py`
- `.claude/skills/session-review/tests/test_aggregate.py`
- `docs/roadmap/on-progress/session-review/phase-5-other-skills.md`
- `docs/roadmap/pending/session-review-accuracy/README.md`
- `docs/roadmap/pending/session-review-accuracy/phase-0-attribution.md`
- `docs/roadmap/pending/pdf-review-cost/README.md`
- `docs/roadmap/pending/pdf-review-cost/phase-0-targeted-pass.md`
- `docs/roadmap/pending/pdf-review-cost/phase-1-svg-preflight.md`
- `docs/roadmap/pending/roadmap-contract/README.md`
- `docs/roadmap/pending/roadmap-contract/phase-0-closure-discipline.md`

**Modified**

- `.claude/skills/session-review/scripts/corpus.py`
- `.gitignore`
- `docs/roadmap/on-progress/session-review/README.md`
- `docs/roadmap/on-progress/session-review/phase-3-ledger-report.md`
- `docs/roadmap/on-progress/session-review/phase-4-corpus.md`
- `docs/roadmap/on-progress/session-review/phase-4-corpus-report.md`

Five reviews and one origin document were written under `reviews/`, which is
not versioned and appears in neither list. `agent-reviews/` was removed.

---

## Problems And Deviations

- **The task "Review one task under each of `translate`, `fetch` and `epub`" was
  moved to Phase 5**, which was added with the user's approval and waits for the
  work to exist. No session in this project's transcripts has ever used those
  three skills: the ledger shows `pdf`, `roadmap`, `superpowers` and
  `update-config` and nothing else. Writing those reviews would have meant
  inventing the sessions they describe, which is the one thing this roadmap
  exists to prevent. Four reviews of a `roadmap` task were written instead, and
  they did strain the format — see below.

- **The acceptance criterion "Four skills have at least one review" is left
  unticked**, for the same reason, and travels with the task to Phase 5.

- **Three strains on the format were recorded, and none was acted on.** A format
  amended here is amended once, and one session of evidence is not enough to
  spend that. They are Phase 5's standing hypotheses:
  1. **No `kind` fits a defect in the instrument's own measurement.** The
     under-counting was filed as `unverified`, which is a stretch: that kind is
     for something delivered on an unchecked assumption, and this is a wrong
     number. `findings.md` says a finding that fits none of the eight is a
     signal about the format, recorded in the notes rather than given a ninth
     kind on the spot. This is that signal.
  2. **`target` must be a path in this repository, and the real target was
     outside it.** The start-commit defect belongs to the `roadmap` skill, which
     is installed outside this repository. The finding was retargeted at
     `CLAUDE.md`, which is a legitimate fix and not the same fix.
  3. **`document` and `images` mean nothing for a task that produces no
     document.** Both are simply absent from the four `roadmap` reviews, which
     the format allows — but a baseline table with a permanently empty column
     for half the corpus is a question the format has not answered.

- **Two defects in this phase's own scripts were found by running them on the
  real corpus**, not by their tests: `never_carried` repeated one finding once
  per review, and `coverage` reported a sub-second gap as uncovered. Both fixed
  and tested.

---

## Changes To Later Phases

- `phase-5-other-skills.md`: **added**, with the user's approval, to receive the
  task moved out of this phase. Its `**Blocked By:**` names what it waits for.
  Its three tasks are the one task of this phase split per skill, and its
  constraints carry the three strains above as hypotheses to confirm or drop.

---

## Assessment

The instrument works, and the most useful thing it did was contradict the people
who built it — twice. The roadmap's headline figures were wrong and it found
that in Phase 1; its own exclusion rule was wrong and it found that here, by
measuring the session that wrote it and coming up a third short.

What it did not do is have an idea. The re-review of `4c7bb3d0` reached exactly
the conclusions the hand-written review had already reached, and the honest
reading is the one the acceptance criterion offered in advance: the instrument
adds accuracy, not insight. That is worth having — "≈ 109,500" and 196,578 were
both confident and both wrong — but it sets the expectation for everything
afterwards. The corpus will not find the problems; it will settle arguments
about their size, and it will notice when the same complaint has been written
six times.

The part that has not been tested is the part that matters most for the corpus's
future: nothing here was measured against a baseline, because the baselines were
written by this phase. Every obligation that fires on a median fired on nothing.
The second review of a `pdf` task is the first real test of this instrument, and
it has not happened yet.

The roadmap does not close. Phase 5 waits on work that has not been done, which
is the correct state for it to be in: the alternative was to write three reviews
of sessions that never existed, and this roadmap began because a session
invented four numbers it could not see.
