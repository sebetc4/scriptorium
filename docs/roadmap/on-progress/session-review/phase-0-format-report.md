# Phase 0 Report: The Format

**Phase:** [phase-0-format.md](phase-0-format.md)
**Start Commit:** f22aab0

---

## Work Log

### 2026-09-18

Phase opened. No predecessor: the roadmap's `README.md` was read instead, in
particular *What Was Measured Before Opening* and *Decisions Taken At Opening*.

Before writing anything, read the four later phase files and the hand-written
review of 2026-09-17 that the roadmap descends from. That order mattered more
than expected: the format is written by Phase 0 but consumed by Phases 1 to 4,
and three of its fields exist only because a later phase needs them —
`review:` because Phase 4 may amend the format once, `skill:` because Phase 2's
obligations compare against a per-skill median, `carried:` because a finding
has no other road out of an unversioned directory.

The finding vocabulary was derived from the origin review rather than invented.
Its eleven problems and eight proposed improvements were sorted until every one
of them landed in a kind, and the kinds that emerged are the eight now in
`references/findings.md`. Each carries the origin review's own case as its
worked example, so the reference documents a vocabulary that has already been
tested against one real session instead of one imagined.

`corpus.py` was written against `core.doc.split_front_matter`, per the phase's
constraint: nothing was added to `requirements.txt`, and the front matter of a
review is parsed exactly as the front matter of a document is.

The suite came out at 27 tests on three hand-written fixtures. Writing those
fixtures from `references/format.md` alone was the check on the first
acceptance criterion, and it found one real gap in the process: the example in
`format.md` was at first not a complete review, and a fixture could not be
written from it without guessing. The reference now carries one review in full.

`make test`: 418 passed. The documentation test does not yet apply — it globs
`*/SKILL.md`, and this skill has none until Phase 2.

---

## Decisions

- **The front matter is structured, the body is prose, and no script parses the
  body.** Findings therefore live in the front matter, as a YAML list, not as
  Markdown sections. Phase 4's `aggregate.py` ranks findings by recurrence over
  `kind` and `target`; that is arithmetic over fields, and it should never
  depend on a heading a session wrote by hand. Phase 2's skill writes prose
  that explains and a list that counts.

- **Medians are computed, never stored.** They live in no review. `corpus.py`
  computes them from the corpus at the moment a review is written and
  `metrics.py` prints them beside each measure. Storing one would freeze a
  baseline meant to move, and would let a review be compared against a median
  it had itself contributed to.

- **A median needs two reviews.** `corpus.median()` returns `None` below that,
  for an empty corpus and for a corpus of one alike. A median of one review is
  that review, and a session compared against itself is precisely the
  self-flattery the corpus exists to prevent. Phase 2 reads `None` as "no
  baseline yet" and must not treat it as zero.

- **An absent measure is absent, not zero.** `Review.measure()` returns `None`
  for a key the review does not carry, and `median()` drops those reviews from
  the sample rather than counting them as zero. This is the format's central
  rule made executable: Phase 1 omits what it could not read, and the corpus
  must not quietly turn that omission into a datum.

- **`target` is a repository path, `kind` is a closed set of eight.** Both
  constraints exist for recurrence: two reviews naming the same file for the
  same reason are the only thing in this system that says something a single
  review cannot. A finding whose target is a document under `library/` is a
  defect in that document and is refused entry.

- **A finding without `target` and `fix` is refused by `corpus.py`**, not
  merely discouraged by the reference. It is the one rule of `findings.md` that
  the reader enforces, because it is the one a session under budget pressure
  would otherwise drop first.

- **Subagent runs are recorded one by one, never pre-aggregated.**
  `measure("subagents.fresh")` sums them on the way out. Phase 1 emits runs;
  Phase 4 can still price a single delegated pass.

---

## Files Changed

**Added**

- `.claude/skills/session-review/references/format.md`
- `.claude/skills/session-review/references/findings.md`
- `.claude/skills/session-review/scripts/corpus.py`
- `.claude/skills/session-review/tests/conftest.py`
- `.claude/skills/session-review/tests/test_corpus.py`
- `.claude/skills/session-review/tests/fixtures/2026-09-17-4c7bb3d0-round-led.md`
- `.claude/skills/session-review/tests/fixtures/2026-09-20-9f1e2a3b-transistor.md`
- `.claude/skills/session-review/tests/fixtures/2026-09-22-77aa11bb-capture.md`
- `docs/roadmap/on-progress/session-review/phase-0-format-report.md`
- `docs/roadmap/on-progress/session-review/phase-1-measurement-report.md`

**Modified**

- `.gitignore`

**Renamed**

The closure moved the roadmap out of `pending/`, so every file of the folder
is a rename against the start commit — two of them modified in passing.

- `docs/roadmap/pending/session-review/README.md` → `docs/roadmap/on-progress/session-review/README.md`
- `docs/roadmap/pending/session-review/phase-0-format.md` → `docs/roadmap/on-progress/session-review/phase-0-format.md`
- `docs/roadmap/pending/session-review/phase-1-measurement.md` → `docs/roadmap/on-progress/session-review/phase-1-measurement.md`
- `docs/roadmap/pending/session-review/phase-2-skill.md` → `docs/roadmap/on-progress/session-review/phase-2-skill.md`
- `docs/roadmap/pending/session-review/phase-3-ledger.md` → `docs/roadmap/on-progress/session-review/phase-3-ledger.md`
- `docs/roadmap/pending/session-review/phase-4-corpus.md` → `docs/roadmap/on-progress/session-review/phase-4-corpus.md`

`reviews/` was created on the working machine. It is empty and ignored, so it
appears in none of these lists: the corpus is not a repository artefact, and
`corpus.load()` treats a missing directory as an empty corpus rather than an
error, so a fresh clone works without it.

---

## Problems And Deviations

- **`.gitignore` keeps a line for `agent-reviews/` that the task did not ask
  for.** The task said to replace `agent-reviews` with `reviews/`. Replacing it
  outright would have made the hand-written review of 2026-09-17 visible to
  git — a file that names a document under `library/`, in a repository whose
  whole point is that `library/` is not versioned. Phase 4 decides what becomes
  of that file; until then it stays ignored, under a comment that names Phase 4
  as the line's owner. Phase 4 removes the line whichever way it decides.

- **The example in `references/format.md` was incomplete on the first pass.**
  Found by trying to write a fixture from it, which is the acceptance criterion
  itself. Fixed in the same sitting: the reference now carries one review
  written out in full.

All five tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed. The format and the vocabulary were written to
the shape Phases 1 to 4 already describe, and nothing was found that obliged
one of them to move.

---

## Assessment

The phase delivered what it set out to: a format that can be written by hand,
a reader that refuses what it cannot trust, and medians that say "no baseline
yet" rather than zero. The suite runs on three synthetic reviews and passes on
a fresh clone.

The work confirmed the roadmap's reason for putting this phase first. Two of
the format's rules — an absent measure is never zero, a median needs two
reviews — are not documentation but code in `corpus.py`, and both would have
been unwritable after ten reviews existed.

What Phase 1 needs to know first: `metrics.py` emits the `measured:` block and
nothing else, and it must **omit** any measure whose record shape it could not
confirm in the transcript. `corpus.py` is built on that promise —
`Review.measure()` returns `None` for a missing key and `median()` drops it
from the sample, so a zero written out of politeness silently corrupts every
baseline computed afterwards. The dotted paths the medians are asked for are
`tokens.fresh`, `subagents.fresh`, `tools.<Name>`, `derived.<name>`; the
trailing `.value` under `derived` is implied, and `subagents.<field>` sums
across runs. Ask `corpus.median(..., exclude=<this review's path>)` when a
review is being compared against the corpus it is about to join.
