# Phase 1 Report: Skill Triggers in the Session Review

**Phase:** [phase-1-trigger-review.md](phase-1-trigger-review.md)
**Start Commit:** 00a356a

---

## Work Log

### 2026-09-25

Opened the phase from `00a356a`, the commit that closed Phase 0, after
reading Phase 0's file and report. No restructuring was pending.

Before starting the phase's own tasks, the user asked for three changes
outside its scope. They are recorded here because they fall inside its diff.

**The two findings of `make check-library`, fixed.**
- `maialen/euskara`: its raw HTML held 31 `<img … alt="">` never closed as
  XML requires, and one stray `</div>` (117 opening tags, 118 closing). Both
  were fixed in `document/index.md`. The rebuilt PDF is pixel-identical to the
  previous one on all 7 pages, at 72 and 100 dpi.
- `electronics/repair/electribe-2`: the anatomy migration had taken the
  investigation folder, `electribe-2/sources/`, for the document's root,
  because it held an `index.md`. The root moved up one level:
  - `document/` and `study/` moved to `electribe-2/`;
  - the investigation's pieces (`datasheets/`, `images/`, `raw/`, `threads/`)
    stayed in `sources/`;
  - an empty `assets/` and the old `.work/` were removed.

  Every file was kept apart from the 6 of `.work/`, checked against a listing
  taken before the move. The rebuilt PDF has the same 18 pages, and its text
  differs only in its title, from "Sources" to "Electribe 2". The stale
  outputs under `out/…/electribe-2/sources/` were removed.
- `make check-library` now reads: 9 documents checked, no defect.

**A glossary is tolerated at a document's root.** Reading the `translate`
skill showed that it keeps `glossary.yaml` beside `document/`, as
`docs/document.md` says. `make check-library` would have reported every
translated document, so `TOLERATED` in `core/library.py` admits it, and a test
holds it.

**The style guide left the user's library.** The user did not want an
`exemples/` topic in a library they are organising.
- The guide is now `brand/style-guide/`, the one document the repository owns,
  named once as `core.doc.STYLE_GUIDE`.
- `doc.relative()` places a repository document from the root, so
  `make build DOC=brand/style-guide` writes to `out/pdf/brand/style-guide/`.
- A targeted `make clean` removes any document's `.work/`, and a full one
  removes the guide's too.
- `.work/` is ignored.
- `make preview-style` reads the guide there.
- Four stale statements in the guide were corrected: two `pdfs/` paths, the
  place of a document's `theme.css`, and a hexadecimal value in an example
  that contradicted the rule the guide documents.
- Its review reports the same three findings as the old copy did, on the
  same five pages.
- `library/exemples/` was removed once a diff showed that nothing but those
  four corrections separated it from the new copy. The frozen fixture copy
  under `tests/fixtures/` is unchanged.

`make test`: 550 passed. That work was committed as `1458ee5`; the phase's
own tasks start after it.

**What a load is, read from the transcripts first.** `metrics.py` counted
`attributionSkill`, and the first question was whether that says which skills
a slice loaded. It does not. All 15 transcripts of the project were read for
their `Skill` tool calls, their `attributionSkill` values and any
`<command-name>` block:
- every load in the corpus is a `Skill` tool call, whose result is followed by
  a `Base directory for this skill` meta message;
- `attributionSkill` labels each later turn with the last skill loaded, so it
  carries a skill into slices that loaded nothing (this session's turns are
  all `roadmap`, loaded once);
- no skill typed by the user as a slash command appears anywhere: the only
  `<command-name>` hits are inside the Skill tool's own description;
- one subagent loaded a skill: a `general-purpose` run of `ea4ab267` loaded
  `pdf`.

**The obligation, test first.** Tests were written red, then:
- `Tally.loaded` counts the `Skill` calls of the slice. The review's own
  `session-review` load is already excluded by the tooling rule.
- A subagent run that loaded a skill carries `loaded:` in its entry.
- The `measured:` block gains `loaded: {…}`, absent when nothing loaded.
- `--owed` prints one line naming every skill loaded, with its count and, for
  a subagent, its run type. A second line, printed on every slice, asks
  whether a job ran without the skill that covers it.
- `corpus.py` accepts `trigger` (nine kinds) and, found on the way,
  `skill: discussion`.
- `SKILL.md` has seven obligations, the fifth being this one;
  `references/findings.md` has the `trigger` row with an example in each
  direction; `references/format.md` documents `loaded` and the new skill
  value; `docs/architecture.md` §5 says the reviews measure the trigger table.

**The line cap cut the obligations.** Run on every transcript, the output of
three whole-session slices (`1920d99a`, `6510c9b8`, `ea4ab267`) reached 53 to
54 lines. The 50-line cap cut the end, which is where the obligations are:
`6510c9b8` lost three lines, the question about a job done without its skill
among them. The loads were first printed one line per skill, which made it
worse. Now the loads share one line, and the cap cuts the output before the
obligations, never inside them. A test holds it with sixty subagent runs.

**The real discussion sessions.** `metrics.py --transcript <t> --owed --skill
discussion`, run on the three transcripts that hold them:
- `03bbff2b`, the notebook's opening (2026-09-24, 14:24 to 19:19): 38 turns,
  `loaded: {discussion: 1}`, printed as
  `` say what each skill loaded brought to the task — `discussion` (1×) ``;
- `3e933365`, a second transcript that starts in the same minute, with the
  same load at 14:24:09, and stops at 15:47: the same line, and
  `api_errors: 1` owed;
- `a9d72882`, the fresh-session resume (2026-09-25, 08:48): 4 turns, the same
  line.

All three loads are the skill's own job; what each brought is measured in
the discussion-and-illustration Phase 0 report. Across the 15 transcripts,
`discussion` loaded in these three and nowhere else. Two sessions since it
exists were ordinary exchanges about the repository (`ea4ab267` and this
one), and it did not load in either. That is the first evidence on the third
case, never firing on an ordinary exchange. It is weak evidence: two
sessions.

`make test`: 563 passed.

---

## Decisions

- **electribe-2 was reshaped, not re-read.** Its `document/index.md` is a
  pasted ChatGPT conversation, and its journal speaks of a final document
  that was never written. Moving the conversation to `sources/` would have
  left no document to build. The root moved up one level and nothing else
  changed. Whether the conversation becomes a source and a real document is
  written, with the `discussion` skill, is the user's decision.
- **The style guide lives in `brand/`**, beside the art direction it shows,
  rather than under `docs/`, which holds prose about the repository.
- **The guide's three review findings were left as they were**: a straight
  apostrophe in the subtitle, an arrow set in a fallback font, a loose line.
  They predate the move. The frozen fixture copy relies on one of them: the
  targeted-pass test needs a finding past page 1. Fixing them in the living
  guide is the user's call.
- **A load is a `Skill` tool call, never an `attributionSkill`.** The
  attribution says which skill a turn ran under, not that it loaded then. A
  slash command typed by the user was never observed, so it is not counted,
  per the rule of `metrics.py` that an unconfirmed shape is not counted. The
  first review that meets one says so.
- **`loaded` is a new measure, with no format version bump.** It adds a key
  and changes the meaning of none, and older reviews without it read as "not
  recorded", per rule 1 of `references/format.md`.
- **A subagent's load is owed with its run**, named "in a `<type>` run",
  because it is a trigger decision too, taken on a description the
  subagent read.
- **The loads share one line, and the cap never cuts an obligation.** The
  obligations are why `--owed` exists; what the cap cuts now is the end of
  the `measured:` block, with the marker saying how many lines went.
- **The question on a missing skill is asked of every slice**, loads or not:
  no transcript records a skill that should have loaded.
- **The ledger does not record loads.** Its entries are written once and
  swept again only when a transcript grows, so older entries would never
  carry them. Phase 2 reads the loads from the transcripts instead; its task
  says so.

---

## Files Changed

Computed against `00a356a`. The files marked † belong to the work the user
asked for before the phase's own tasks, committed as `1458ee5`. The changes
under `library/` are not listed: that directory is not versioned.

**Added**
- `brand/style-guide/document/assets/.gitkeep` †
- `brand/style-guide/document/assets/chaine.svg` †
- `brand/style-guide/document/cover.md` †
- `brand/style-guide/document/index.md` †
- `docs/roadmap/on-progress/suite-and-review/phase-1-trigger-review-report.md`
- `assets/icon.png`: untracked, dated 2026-09-21, before this phase; neither
  written nor committed by it.

**Modified**
- `.claude/skills/epub/SKILL.md` †
- `.claude/skills/epub/scripts/epub.py` †
- `.claude/skills/epub/scripts/preview.py` †
- `.claude/skills/session-review/SKILL.md`
- `.claude/skills/session-review/references/findings.md`
- `.claude/skills/session-review/references/format.md`
- `.claude/skills/session-review/scripts/corpus.py`
- `.claude/skills/session-review/scripts/metrics.py`
- `.claude/skills/session-review/tests/test_corpus.py`
- `.claude/skills/session-review/tests/test_metrics.py`
- `.claude/skills/session-review/tests/test_skill.py`
- `.claude/skills/sourcing/SKILL.md` †
- `.gitignore` †
- `CLAUDE.md` †
- `README.md` †
- `core/doc.py` †
- `core/library.py` †
- `docs/architecture.md`: † and this phase (§5, the trigger check measured)
- `docs/document.md` †
- `docs/roadmap/on-progress/suite-and-review/README.md`
- `docs/roadmap/on-progress/suite-and-review/phase-1-trigger-review.md`
- `docs/roadmap/on-progress/suite-and-review/phase-2-trigger-audit.md`
- `tests/test_doc.py` †
- `tests/test_library.py` †

---

## Problems And Deviations

- **The 50-line cap cut the obligations** on 3 of the 15 transcripts. The
  defect predates this phase, and this phase's lines made it worse. Fixed, and
  held by a test.
- **`corpus.py` refused `skill: discussion`.** The skill was added in
  `5e337cd` without its value in `SKILLS`, so the first review of a
  discussion would have been refused. Fixed, with a test, and the value added
  to `references/format.md`.
- **The obligation asks, it does not decide.** No script can tell whether a
  load was needed or a skill was missing. The check on the third case of the
  `discussion` skill stays observational: two ordinary sessions so far, with
  no misfire.
- **The style guide's three review findings are left open**: a straight
  apostrophe, an arrow in a fallback font, a loose line. They predate the
  move, and fixing them in the living guide is the user's call (see
  Decisions).
- **The first worked example against `pdf` was rewritten.** Its "other
  direction" fix proposed adding "update" to the description, which already
  says it. The final example is a one-line caption edit.

---

## Changes To Later Phases

- `phase-2-trigger-audit.md`: the last task now also folds in the loads that
  `metrics.py --transcript <t> --owed` reads from every transcript,
  reviewed or not. The corpus holds one review, so reviews alone would give
  the audit almost nothing.

---

## Assessment

The phase delivered what it set out to. Every review now owes an account of
each skill its task loaded, and a `trigger` finding has a kind, a target (the
`SKILL.md` whose description fired) and a worked example. The skill's suite
grew by 13 tests, and `make test` passes with 563.

Two defects came out of running the tool on real transcripts rather than
fixtures. The line cap was silently cutting obligations, and `discussion`
was missing from the corpus's skills. Neither would have shown on the
fixtures alone.

What Phase 2 needs first:
- a load is a `Skill` tool call, readable from any transcript with
  `metrics.py --transcript`;
- the corpus holds a single review, so the audit's real data is the 15
  transcripts;
- in them, `discussion` loaded only on its own job;
- the skills loaded outside the repository's own (`superpowers:*`,
  `skill-creator`, `update-config`) are not this repository's to audit, but
  they show up in the same line.
