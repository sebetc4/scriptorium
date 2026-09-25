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
Phase 0  A Suite Independent of the Library    🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/9)
Phase 1  Skill Triggers in the Session Review  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 2  A Trigger Audit of Every Skill        🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                             ░░░░░░░░░░░░░░░░░░░░   0%  (0/20)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — A Suite Independent of the Library

---

## Why This Roadmap Exists

It comes out of Phase 0 of the
[discussion-and-illustration](../discussion-and-illustration/README.md)
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
| 0 | [A Suite Independent of the Library](phase-0-library-free-suite.md) | 9 | 🔴 Not Started |
| 1 | [Skill Triggers in the Session Review](phase-1-trigger-review.md) | 6 | 🔴 Not Started |
| 2 | [A Trigger Audit of Every Skill](phase-2-trigger-audit.md) | 5 | 🔴 Not Started |

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md): §2, core or skill; §5,
  the trigger check.
- [`docs/document.md`](../../../document.md): the commands.
- [discussion-and-illustration, phase 0 report](../discussion-and-illustration/phase-0-discussion-skill-report.md):
  the failures as first met, and the measurements of the `discussion` skill.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/suite-and-review/`
**Version:** 1.0.0
**Created:** 2026-09-25
**Last Updated:** 2026-09-25

---

## Changelog

### 1.0.0 (2026-09-25)

Roadmap created with three phases and 20 tasks. First a suite independent of
the library, with a read-only `make check-library`. Then an obligation in
`session-review` to account for every skill a session loaded. Then a trigger
audit of every skill's description.
