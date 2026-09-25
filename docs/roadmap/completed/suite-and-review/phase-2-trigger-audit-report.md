# Phase 2 Report: A Trigger Audit of Every Skill

**Phase:** [phase-2-trigger-audit.md](phase-2-trigger-audit.md)
**Start Commit:** 7a9962f

---

## Work Log

### 2026-09-25

Opened the phase from `7a9962f`, the commit that closed Phase 1, after
reading Phase 1's file and report. No restructuring was pending.

**The data first (task 5).** The corpus holds one review, from before
Phase 1, and no `trigger` finding. The 15 transcripts were therefore read for
their loads, the document jobs visible in their tool calls (`make build`,
`review`, `import`, `fetch`, `epub`, `new`, edits under `library/`), and
their opening request:
- the loads match the jobs in 13 transcripts;
- two of the others loaded nothing and hold no turn;
- `ad37becc` (2026-09-20, "work on these notes") loaded nothing, but
  `discussion` did not exist yet;
- `1920d99a` and `53a9d27e` ran every `make` target under `roadmap` alone,
  but they were building the tools, not a document, and edited nothing under
  `library/`;
- **one misfire in the other direction**: in `ea4ab267`, on 2026-09-25 from
  10:04, the session repaired `maialen/euskara/document/index.md`, rebuilt it,
  and ran `make review` on the style guide without `pdf` loaded. Measured
  over that slice: 134 turns, no image read, no `loaded` line. The outcome was
  right (a pixel-identical rebuild), but the job was `pdf`'s. The request came
  as "fix what `make check-library` reports", and `pdf`'s description has no
  verb for that: write, create, update, rebuild.
- `discussion` loaded in its three real sessions and nowhere else. Its
  opening request, "talk about my solder joints to make a document of them",
  also matches `pdf`'s "create a document", which does not name `discussion`
  among its neighbours.

**The audit (task 1)**, each description against §5 and against the other
six:
- `pdf` names neither `discussion` (the opening above) nor fixing a document
  (the misfire above).
- `session-review` names no neighbour skill: "reviews no PDF" is right, but
  says nothing about which skill does.
- `fetch` does not say that a PDF behind a URL is not its job. Its body
  refuses one and points to `make import`, but only after the skill has
  loaded.
- `sourcing` shares "sources that are not known in advance" with `fetch`,
  where it is a negative clause. The phrase cannot be the discriminator; "an
  answer has to be established and cross-checked" is, and no other
  description carries it. No rewrite needed.
- `epub`, `translate` and `discussion` pass: each has a phrase of its own and
  names its neighbours.
- §5's table has no `session-review` row.

**The test before the rewrites (task 3).** `tests/test_triggers.py` reads
each description as a line, the way Claude Code reads it: YAML refused
several of them, which hold a `: `. It holds two tables:
- `DISCRIMINATORS`: each skill's phrase, present in its own description and
  absent from the six others;
- `NEIGHBOURS`: the skills each description must name.

A skill without a row in both fails, as does a §5 table without a row for
every skill. The first draft failed on `pdf` in an unexpected way: "paginated
PDF" is also in `epub`'s negative clause. The phrase became "paginated PDF
document". "At least one neighbour" held the audit's overlaps too loosely,
so each skill now has a list of its own. Run before the rewrites, the test
failed exactly on `pdf`, `fetch`, `session-review` and §5.

**The rewrites (task 2)**, one clause each, bodies untouched:
- `pdf`: "fix" among the verbs, with "a repair that a check such as `make
  check-library` reports"; and "a subject the user still wants to talk
  through (`discussion`)" among the negatives, worded so as not to borrow
  `discussion`'s own phrase;
- `fetch`: "A PDF, even behind a URL, is imported with the `pdf` skill.";
- `session-review`: "reviews no code and no PDF (a built PDF is the `pdf`
  skill's)".

All seven stay under 1,024 characters; `pdf` is the longest at 818. The
harness reloaded the three at once.

**§5 (task 4).** The heading now says seven skills, the *What each is for*
table gains `session-review`, and the trigger table gains its row. `pdf`
gets "fix" and "a subject still being talked through", `fetch` gets "a PDF,
even behind a URL". A paragraph records the test, the three overlaps it came
from, and the rule that a phrase counts only where it is said positively.
Two stale mentions of five skills were corrected (the tree and the directory
table).

`make test`: 579 passed.
---

## Decisions

- **The descriptions are read as a line, not as YAML.** Several are not
  valid YAML, and Claude Code loads them anyway. Quoting them all would have
  touched seven files for a property the harness does not need; the test
  reads them as the harness does.
- **Each skill's neighbours are listed, not counted.** "At least one" would
  have passed `pdf` without `discussion`, the one overlap measured on a real
  opening request. A new overlap met in a review adds a name to
  `NEIGHBOURS`.
- **`sourcing` was left as it was.** Its real phrase, "established and
  cross-checked", is already its own; the shared "not known in advance" is a
  negative clause in `fetch`, not an overlap.
- **The `ea4ab267` misfire went into the description, not into a review.**
  No review of that session exists, and the fix is one verb. The bodies stay
  out of scope, per the phase.
- **The two stale "five skills" in `docs/architecture.md` were corrected.**
  They are outside §5 but state a fact this phase changes. The
  "five, settled at the roadmap's opening" of the migration roadmap's scope
  is history, and stays.

---

## Files Changed

Computed against `7a9962f`.

**Added**
- `tests/test_triggers.py`
- `docs/roadmap/on-progress/suite-and-review/phase-2-trigger-audit-report.md`
- `assets/icon.png`: untracked, dated 2026-09-21, before this roadmap's
  phases; neither written nor committed by this one.

**Modified**
- `.claude/skills/fetch/SKILL.md`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/session-review/SKILL.md`
- `docs/architecture.md`
- `docs/roadmap/on-progress/suite-and-review/README.md`
- `docs/roadmap/on-progress/suite-and-review/phase-2-trigger-audit.md`

---

## Problems And Deviations

- **No review since Phase 1 produced a `trigger` finding**, because no
  review has been written since. Task 5 was carried out on the transcripts,
  as Phase 1 had arranged; the one misfire they hold is fixed in `pdf`'s
  description.
- **The phrase test is lexical.** It proves that a phrase is unique, not that
  a session will read it as intended. Whether the new clauses fire correctly
  can only be measured by the reviews, which `session-review` now requires to
  account for every load.
- **The third case of `discussion` (never firing on an ordinary exchange)
  still rests on two sessions.** Left open: the reviews will add to it.

---

## Changes To Later Phases

No later phase: this is the roadmap's last. Nothing was changed elsewhere,
and no restructuring is pending.

---

## Assessment

The phase delivered what it set out to:
- every description of the seven skills passes the §5 check, and a test
  holds it there;
- a skill added later fails that test until it has its row;
- the three rewrites each come from an overlap met in a real session, not
  from a reading of the descriptions alone.

The audit's main lesson is methodological: a phrase counts only where it is
said positively. Two apparent overlaps were a skill's negative clause
quoting its neighbour's job.

The roadmap is complete. The discussion-and-illustration roadmap was waiting
on its Phase 1 and can resume.
