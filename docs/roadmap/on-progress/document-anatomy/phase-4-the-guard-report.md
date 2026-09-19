# Phase 4 Report: Keeping It True

**Phase:** [phase-4-the-guard.md](phase-4-the-guard.md)
**Start Commit:** 0680597

---

## Work Log

### 2026-09-19

Phase opened. Phase 3's file and report were read in full: 8/8 tasks, 5/5
acceptance criteria, no restructuring pending. The library is now in the shape
the anatomy describes; nothing yet keeps it that way.

What this phase inherits, and the two traps its predecessor named:

- **The anatomy test must skip on a fresh clone**, where `library/` is empty or
  absent, like the rest of the suite that reads documents kept outside the
  repository.
- **The guard must not refuse acquisition.** `make import` copies a PDF into
  `sources/` and `make fetch` writes `page.html.gz` there, and both are
  legitimate. The distinction is about *which tool is writing*, not about the
  path — which is why `protect-paths.sh` can make it and a test reading the
  filesystem afterwards cannot.
- A `sources/` that no tool writes a derived file into is the condition this
  phase exists to defend, and Phase 3 delivered it.

### 2026-09-20

**The guard already covered `sources/`, and it was broken.** `protect-paths.sh`
refused `library/*/sources/*` before this phase began, so the task looked close
to done. Two things were wrong with it.

Its message was the old world's: "sources/ is the immutable record of an import
or a capture: edit index.md instead" — which is now `study/`'s description, and
points at a path that moved.

And its second guard had stopped firing. An investigation's pieces were
recognised by a `NOTES.md` sitting beside `raw/`; Phase 3 moved the journal to
`study/NOTES.md`, and the check turned off for every investigation, in silence.
Reproduced on a synthetic tree before changing anything: exit 2 with the journal
at the root, exit 0 with it in `study/`. One document was still protected — by
accident, because `electronique/repair/electribe-2/sources` has a slug that is
literally `sources`, so the first rule catches it. Any other investigation was
open.

The guard is now written against the anatomy rather than against filename
patterns: it refuses `sources/`, which is the user's, and `.work/`, which a
command remakes and `make clean` empties; it allows `document/`, `study/` and
`generators/`. Both journal locations are recognised. Six probes, one per case,
and each is a test.

**Acquisition is untouched, and by construction rather than by care.**
`protect-paths.sh` is a `PreToolUse` hook on `Edit|Write|NotebookEdit`: it sees
an edit made by hand and never a script's write through Bash. `make import` and
`make fetch` therefore acquire into `sources/` without the guard being consulted
at all. Verified end to end all the same — an import wrote its PDF into
`sources/`, its extraction into `study/`, its pages into `.work/`.

**The test names one exception, and names it rather than widening the rule.**
`electronique/repair/electribe-2/sources` keeps an investigation's `datasheets/`,
`images/`, `raw/` and `threads/` at its root instead of in `sources/`: it is a
`sourcing` session's own material promoted to a document, so its root *is* the
investigation. Reshaping it would mean rearranging user content nobody asked to
have rearranged. It is one entry in the test, with the reason, and the day the
document is reshaped the test says whether anything still needs it.

Both failing paths were proved rather than assumed: a stray file at a document's
root, and a derived file in `sources/`, each fails by name.

**The last rebuild.** 15 PDFs and 8 EPUBs, compared against the fingerprints
Phase 1 took before anything moved: zero differences. Four phases,
five directories, and nothing a reader sees has changed.

`make test`: 508 passed.

---

## Decisions

- **The guard names the anatomy's directories, not file patterns.** What it
  refuses is a role — the user's, and the disposable — so a new kind of file
  inside either is covered the day it appears. The previous version listed
  `raw|datasheets|images`, and would have missed the fourth name someone
  invented.

- **The investigation walk is kept, repointed, and not replaced.** The general
  rule cannot reach `electribe-2`, whose pieces sit at its root. Keeping a
  legacy check for a legacy shape is cheaper and more honest than pretending the
  anatomy covers it.

- **The exception is data in the test, not a loosened rule.** A set keyed by the
  document's path, with the reason above it. Widening `ROLES` would have made
  every document able to hold those four names.

---

## Files Changed

**Added**

- `tests/test_anatomy.py`
- `docs/roadmap/on-progress/document-anatomy/phase-4-the-guard-report.md`

**Modified**

- `.claude/hooks/protect-paths.sh`
- `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/on-progress/document-anatomy/phase-4-the-guard.md`

---

## Problems And Deviations

- **Phase 3 broke the investigation guard and nothing noticed.** Moving
  `NOTES.md` to `study/` turned off the check that protects an investigation's
  pieces, and 499 tests passed over it. It is fixed here, and it is the third
  silent breakage this roadmap has produced — after the SVG inlining and the
  EPUB image names, both in Phase 1. All three were found by looking at the
  result rather than by the suite; this one is now a test.

- **The six files that needed a hand**, the phase's last task, across all four
  phases:

  1. `electronique/components/led/document/theme.css` — a per-document
     stylesheet §11 had not named. The cut settled it without hesitation: the
     build reads it, so it moved with the document. No decision was needed once
     the question was asked.
  2. `electronique/repair/electribe-2/sources` — a document whose slug is
     literally `sources`. Nothing moved for it but `index.md`, and it is the
     origin of the test's one exception.
  3. That same document's `datasheets/`, `images/`, `raw/` and `threads/`, at
     its root rather than in `sources/`. Left in place, named in the test.
  4. `.../m328/study/extracted.md` and
     `.../round-led-d4017/study/extracted.md` — restored from the backup after
     `make rederive` produced a different placeholder caption. The migration
     moves files; it does not regenerate them.
  5. `glossary.yaml` — named by `translate`'s `SKILL.md`, placed by §11 nowhere.
     Left at the document's root, with the gap stated in the skill. No document
     has one today.
  6. An investigation's `threads/` — transcriptions, derived in the strict
     sense, kept in `sources/` because Phase 3's *Out of Scope* had already
     placed them there. Moving eleven files to defend a definition would have
     been the anatomy serving itself.

All five tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 5
inherits three things to reconcile that are named in its own tasks, and one more
from this phase: `docs/document.md` should say what the guard refuses, because a
person who reads the manual and then hits the hook has been told twice or not at
all.

---

## Assessment

The phase found what it was built to find, which is the least common outcome for
a guard written after the fact. `protect-paths.sh` already refused `sources/`
before this phase opened, and the task looked like changing a message. Its
second check had been dead since Phase 3 moved a file three days earlier, and
499 tests had passed over it twice.

That is the third silent breakage of this roadmap, and the three of them share a
shape: a rule expressed as a filename pattern, and a file that moved. The SVG
inlining resolved a path against the wrong root; the EPUB named its images after
a path that gained a segment; the guard looked for a journal beside a directory
it no longer sits beside. Each time the code kept running and said nothing. The
anatomy does not prevent that — `doc_dir()` and the five constants make the
patterns fewer, not absent — but it does make them findable, because there is now
one place where a name is written down and a test that reads it back.

What Phase 5 needs to know first: it is the only phase that writes for a reader
rather than for the repository, and the reports of the five phases before it are
its material. Three statements it must reconcile are named in its own tasks;
a fourth is that `docs/architecture.md` §8 now carries a revision note about
`clean`, and §11 sits after §10 because the document's cross-references forbade
inserting it earlier — Phase 0 recorded that and left the decision here. The
manual should also say what the guard refuses and why, or a person meets the
anatomy twice: once as prose, once as a hook that stopped their edit.
