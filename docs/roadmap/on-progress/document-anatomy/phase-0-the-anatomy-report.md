# Phase 0 Report: The Anatomy Of A Document

**Phase:** [phase-0-the-anatomy.md](phase-0-the-anatomy.md)
**Start Commit:** 7439af7

---

## Work Log

### 2026-09-19

Phase opened. This is the roadmap's first phase, so there is no predecessor and
nothing to settle: the roadmap's `README.md` was read instead, in particular
*The Five Roles* and *Decisions Taken At Opening*, which this phase writes down
rather than invents.

This is also the first closure run under the `roadmap` skill 1.1.1, whose
closing ritual was reordered after four consecutive audit failures in this
repository — `## Files Changed` computed last, the audit before the commit, the
next phase opened after it.

**Where the anatomy went, and why not where it belongs.** `docs/architecture.md`
runs to ten numbered sections and its prose refers to them by number — `(§2)`,
`(§5)`, up to `§8`. Inserting a section anywhere but the end would renumber the
rest and break those references silently, which is the kind of quiet damage this
roadmap exists to stop making. The anatomy is therefore §11, appended, rather
than sitting beside §1's tree where a reader would look for it. Phase 5 owns the
reconciliation and can decide whether §11 moves or whether §1 simply points at
it.

Writing it turned up two things the roadmap's README had not said.

**The cut is about what a file is for, not who made it.** That needed saying
outright, because the natural reading of "the agent's files" and "the user's
files" is authorship, and authorship gives the wrong answer on the clearest
case: a schematic drawn by hand over an afternoon belongs in `document/assets/`
beside a photograph a script extracted from a PDF, because the document
references both and the build embeds both. Cost gives the wrong answer too. Only
consumption gives the right one.

**`extracted.md` is genuinely ambiguous, and the ambiguity is load-bearing.** It
is regenerable from `sources/`, so by the disposable rule it could live in
`.work/` — but only if regeneration is deterministic. If a library version moves
and the extraction changes, the reference a translation checked against is gone
and the file was never disposable. It is placed in `study/` on that argument, and
Phase 3's premise is now stated as something to verify rather than assume.

That case also sharpened the definition itself: a file is disposable when a
command can make it again **and nothing is lost by making it later**. The second
half is what catches the interesting cases; the first half alone would have sent
`extracted.md` to `.work/`.

**`§10` had to be answered, not left standing.** Its first bullet says of
`library/`: "Nothing here translates it, moves it, or imposes a convention on
it." §11 imposes one. Rather than rewrite a past section, §11 opens with an
italic note superseding that bullet — the idiom `architecture.md` already uses
for its own revisions, as in "*Phase 8 revised this: …*".

`CLAUDE.md` carries the five directories in one paragraph of the repo map, with
an italic note that the library is not yet in that shape. A session reading it
today would otherwise look for `document/` and not find it.

`make test`: 485 passed. `check_links.py`: 37 links, 0 broken.

**The `git mv` fix works.** The roadmap folder moved `pending/` → `on-progress/`
with `git mv`, and `git diff -M` reports every file as `R`, including the two
modified in the same closure (`R084`, `R079`). The report this section belongs to
was untracked at the moment of the move and was carried along by it, exactly as
`close-phase.md` 1.1.1 now says.

---

## Decisions

- **The anatomy is `docs/architecture.md` §11, appended.** Section numbers are
  load-bearing cross-references in that document; inserting would break them
  silently. Phase 5 decides whether it stays there.

- **The cut is consumption, not authorship.** "The build reads `document/` and
  nothing else" is the boundary, and it is stated as such with the two readings
  it displaces — who made the file, and what it cost — named and rejected. Every
  later phase places a file by asking what reads it.

- **Disposable has two halves: a command can make it again, and nothing is lost
  by making it later.** The second half is the operative one. It is what sends
  `extracted.md` to `study/` rather than `.work/`, and it gives Phase 3 a premise
  to verify rather than a rule to apply.

- **`study/` holds what the agent learned, whether derived or written.** The
  investigation journal is neither received nor derived, and inventing a sixth
  role for one file would have made the anatomy harder to remember than the
  habit it replaces.

- **The enforceable half of the `sources/` rule is the only half written as a
  rule.** No tool modifies what is in it; the user leaving the rest alone is
  stated as advice. Phase 4 guards the first and cannot guard the second.

---

## Files Changed

**Added**

- `docs/roadmap/on-progress/document-anatomy/phase-0-the-anatomy-report.md`

**Modified**

- `CLAUDE.md`
- `docs/architecture.md`

**Renamed**

The closure moves the roadmap out of `pending/`, so every file of the folder is
a rename against the start commit; the first two were modified in passing.

- `docs/roadmap/pending/document-anatomy/README.md` → `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/pending/document-anatomy/phase-0-the-anatomy.md` → `docs/roadmap/on-progress/document-anatomy/phase-0-the-anatomy.md`
- `docs/roadmap/pending/document-anatomy/phase-1-the-document-directory.md` → `docs/roadmap/on-progress/document-anatomy/phase-1-the-document-directory.md`
- `docs/roadmap/pending/document-anatomy/phase-2-the-work-directory.md` → `docs/roadmap/on-progress/document-anatomy/phase-2-the-work-directory.md`
- `docs/roadmap/pending/document-anatomy/phase-3-sources-study-generators.md` → `docs/roadmap/on-progress/document-anatomy/phase-3-sources-study-generators.md`
- `docs/roadmap/pending/document-anatomy/phase-4-the-guard.md` → `docs/roadmap/on-progress/document-anatomy/phase-4-the-guard.md`
- `docs/roadmap/pending/document-anatomy/phase-5-the-documentation.md` → `docs/roadmap/on-progress/document-anatomy/phase-5-the-documentation.md`

---

## Problems And Deviations

- **The anatomy is not where a reader would look for it.** §11 sits after §10,
  *What this document does not decide*, because the document's own cross-
  references forbid inserting a section earlier. It is recorded here rather than
  fixed: Phase 5 reconciles §1's tree and §9's glossary and is the right place to
  decide whether §11 moves.

- **One acceptance criterion is met in prose rather than in the table.** "May I
  edit it" is answered by the sentence that the user leaving the rest alone is
  advice and not a fence, not by a column beside *Written by* and *Read by the
  build*. `docs/document.md`, in Phase 5, is the manual and should make it a
  column.

All six tasks are done and all four acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 3 was
already written to verify that `extracted.md`'s derivation is reproducible; §11
now states that premise explicitly, so the phase's constraint and the anatomy
agree without either being edited.

---

## Assessment

The phase produced two documents and changed no behaviour, which was the point:
the four phases that follow carry out a contract instead of inventing one as they
go. The contract came out slightly different from the roadmap's README in one
respect that matters — the cut had to be stated as consumption rather than
ownership, because "the agent's files" and "the user's files" is the natural
reading and it places a hand-drawn SVG wrongly.

The closure is also the first evidence on the reordered ritual. The folder moved
with `git mv`, `## Files Changed` was computed once nothing else would move, and
the list came out right without a repair pass. Whether that holds through the
audit is the next thing this report will know.

What Phase 1 needs to know first: it is the only phase that touches the core, and
three things in `core/doc.py` break together the moment `index.md` moves —
`d.name` is the slug, `d.name` is also the default title, and
`d.relative_to(LIBRARY)` is the whole output path. All three break **silently**:
a build would succeed and write `out/pdf/<topic>/<slug>/document/`. The test that
a document is discovered at its root comes before the migration, not after it.
And `assets/` moves with the document, which is what keeps every relative link in
every `index.md` working untouched — that is the property to verify first, on one
document, before the other eleven move.
