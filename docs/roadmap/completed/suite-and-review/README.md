# Roadmap: Suite and Review

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
Phase 0  A Suite Independent of the Library    🟢 ████████████████████ 100%  (9/9)
Phase 1  Skill Triggers in the Session Review  🟢 ████████████████████ 100%  (6/6)
Phase 2  A Trigger Audit of Every Skill        🟢 ████████████████████ 100%  (5/5)
TOTAL                                             ████████████████████ 100%  (20/20)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** —

---

## Why This Roadmap Exists

It comes out of Phase 0 of the
[discussion-and-illustration](../../pending/discussion-and-illustration/README.md)
roadmap. That phase met two problems it could not solve inside its own
scope.

**`make test` depends on the user's library.** Part of the suite reads real
documents under `library/`, which is user content and changes at any time. A
rename by the user (`electronique/` → `electronics/`) turned `make test` red,
with 18 failures and 5 errors caused by no code. Every roadmap's closure runs
`make test`, so every phase in the repository was blocked. The suite also
writes a real EPUB into `out/epub/` for every `report` document on each run.

**Nothing checks whether a skill fires when it should.** The `discussion`
skill must fire at the opening and at the resume of a discussion, and never
on an ordinary exchange about the repository. The first two were verified on
real sessions. For the third, the user chose to have every session review
check it explicitly rather than wait to notice it. Having reached that point,
the user asked to use this roadmap to improve the triggering of every skill.

---

## Decisions Taken At Opening

**Fictional fixture documents for the tests of code.** The user accepted the
cost: a fixture is written so that its test can pass, which makes the test
weaker than one run on real content. Two things compensate. Every fixture
carries the defects its check must catch. And the real library stays under
check through a separate command.

**`make check-library` is read-only.** It checks the anatomy, the layout and
the XHTML of every document, converted in memory. It writes no EPUB and no
PDF, and never blocks `make test`. Building an EPUB stays the job of `make
epub`.

**Triggers are checked in the reviews, explicitly.** `--owed` makes each
review justify every skill it loaded. A new finding kind, `trigger`, names
both a skill loaded without need and a job done without its skill.

---

## Deliberately Out Of Scope

- Fixing the user's documents that `make check-library` flags
  (`maialen/euskara`, `electribe-2/sources/`). The user decides.
- The `discussion` skill's archive architecture. It stays in the
  discussion-and-illustration roadmap, recorded there, and resumes once this
  roadmap is done.
- The body of any skill, beyond what a `trigger` finding points at.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [A Suite Independent of the Library](phase-0-library-free-suite.md) | 9 | 🟢 Done |
| 1 | [Skill Triggers in the Session Review](phase-1-trigger-review.md) | 6 | 🟢 Done |
| 2 | [A Trigger Audit of Every Skill](phase-2-trigger-audit.md) | 5 | 🟢 Done |

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md): §2, core or skill; §5,
  the trigger check.
- [`docs/document.md`](../../../document.md): the commands.
- [discussion-and-illustration, phase 0 report](../../pending/discussion-and-illustration/phase-0-discussion-skill-report.md):
  the failures as first met, and the measurements of the `discussion` skill.

---

## Metadata

**Roadmap Status:** 🟢 Done
**Location:** `docs/roadmap/completed/suite-and-review/`
**Version:** 2.0.0
**Created:** 2026-09-25
**Last Updated:** 2026-09-25

---

## Changelog

### 2.0.0 (2026-09-25)

Roadmap closed, all three phases done. `summary.md` records where it
started, what each phase delivered, and what outlives it: that a test
reading user content cannot fail for the right reason, that an instrument is
proved on real data, and that a discriminating phrase counts only where it
is said positively. It also records what is left open, chiefly the third
case of `discussion`, which the reviews will keep measuring. The folder
moved from `docs/roadmap/on-progress/` to `docs/roadmap/completed/`. No
restructuring was pending. The discussion-and-illustration roadmap, which
waited on Phase 1, can resume.

### 1.3.0 (2026-09-25)

Phase 2 closed: every skill's description passes the §5 trigger check, and
`tests/test_triggers.py` holds it there. Each description carries a phrase
no other carries and names the neighbours it must not be confused with; a
skill added without its row fails the test. The audit read the 15
transcripts for their loads. It found one real misfire: a repair reported by
`make check-library` was done without `pdf`, whose description had no verb
for fixing. `pdf`, `fetch` and `session-review` each gained one clause, and
§5's tables list the seven skills. No phase follows.

### 1.2.0 (2026-09-25)

Phase 1 closed: every session review now accounts for the skills its task
loaded. `metrics.py` reads a load from the transcript's `Skill` calls, not
from `attributionSkill`, which only labels turns with the last skill loaded.
The `measured:` block gains `loaded:`, and `--owed` names every skill loaded
and asks whether a job ran without its skill. A new finding kind, `trigger`,
records either failure. Run on the real transcripts, the tool showed that its
50-line cap was cutting the obligations and that `corpus.py` refused `skill:
discussion`; both were fixed. `discussion` loaded in its three real sessions
and in no other session. Before the phase's own tasks, and at the user's
request, the two documents `make check-library` flagged were repaired and the
style guide moved to `brand/style-guide/`. Phase 2's last task now also reads
the loads from every transcript.

### 1.1.0 (2026-09-25)

Phase 0 closed: `make test` no longer depends on the user's library. The
suite reads two fictional documents versioned under `tests/fixtures/library/`,
through a temporary copy, and writes nothing under `out/` or `library/`. It
passes on a checkout that has no `library/` at all (546 tests). The checks
that were about the user's library moved to `make check-library`, a read-only
command in `core/library.py`; on the real library it reports five known
defects. The phase found three more tests that read the whole library without
ever failing, and an ignore rule that would have hidden the fixtures. The
roadmap moved from `pending/` to `on-progress/`.

### 1.0.0 (2026-09-25)

Roadmap created with three phases and 20 tasks. First a suite independent of
the library, with a read-only `make check-library`. Then an obligation in
`session-review` to account for every skill a session loaded. Then a trigger
audit of every skill's description.
