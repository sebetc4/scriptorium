# Phase 0 Report: The Targeted Pass

**Phase:** [phase-0-targeted-pass.md](phase-0-targeted-pass.md)
**Start Commit:** 9b608dd

---

## Work Log

### 2026-09-20

Phase opened. This is the roadmap's first phase: its `README.md` and
`.claude/agents/pdf-reviewer.md` were read instead of a predecessor's report.

**The mechanism was missing a piece.** `make review … ZOOM="…"` already rendered
chosen pages alone, but it *returned before the checks ran* — zooms only. A
verification pass needs both: the pages that changed, looked at, and the checks
over the whole document, because a fix on one page reflows the ones after it and
the checks are what catch that, at the cost of no image at all.

`review.py` now runs the checks whichever shape it is asked for, then either the
zooms or the sheets. One command does a verification pass. Three tests pin it:
the pages given are the only ones rendered, no sheet is written, and a finding on
a page the pass was *not* given is still reported.

**Then the agent, and four attempts that changed nothing.** Measured on
`electronique/apprentissage/round-led-d4017`, fifteen pages, light variant — the
document the original finding came from.

| | Tokens | Calls | `Looked at:` |
|---|---|---|---|
| full pass, before any change | 32,666 | 15 | 4 sheets; zoomed 6 |
| targeted, `PAGES` added to the Input section | 31,966 | 14 | 4 sheets; zoomed 6 |
| targeted, branch made a fork at the top | 29,933 | 14 | 4 sheets; zoomed 6 |
| targeted, report template made conditional | 31,051 | 15 | 4 sheets; zoomed 6 |

Every targeted pass ran the full one. Confirmed on disk rather than taken from
the report: `.work/review/light/` held four `sheet-*.png` *and* six
`page-*.png` each time, so both commands were run.

**The diagnosis came from reading the file, which should have been the first
move.** Each attempt removed one place where the file asserted its shape and
found another — and there turned out to be a fifth thing wrong that no amount of
re-wording would have reached: **the verification pass had nowhere to learn what
counts as a defect.** Every judging criterion — margins, orphan headings,
`accent` usage, dark-variant contrast, the import comparison — lived inside
`## 2. Every sheet`, a section of the full pass. A pass told to skip sections 1
to 3 was told to skip the only description of what it was looking for.

So the file mixed two things that do not belong together: the **shape** of a
pass (which command, how many images) and the **criteria** (what is wrong on a
page). The shape differs between the passes; the criteria do not.

**Rewritten on that line.** The criteria became their own section, shared. Each
pass became a short self-contained block: its command, its images, what it must
not do. The budget stopped describing one shape and states each. Nineteen items
of the old file were checked across one by one; none was lost.

| | Tokens | Calls | Seconds | `Looked at:` |
|---|---|---|---|---|
| **verification pass, after the rewrite** | **21,619** | **8** | **45** | `pages 4 6 7 13 14 15` |
| full pass, after the rewrite | 33,339 | 14 | 109 | 4 sheets; zoomed 6 |

**−33 % of the tokens, −46 % of the tool calls, −57 % of the wall time**, and no
sheet written: six `page-*.png` on disk and nothing else. The full pass is
unchanged, within the noise of two runs of the same shape.

Measuring cost six delegated runs and about 180,000 tokens — on the roadmap
whose subject is the cost of review passes. Four of those six bought nothing.

---

## Decisions

- **The checks run whole in both shapes.** They read the text layer, cost no
  image, and are what catches a page the fix reflowed. A verification pass that
  looked only where it was told would stop covering the document exactly when
  the document had just moved.

- **A check firing on a page the pass was not given is still reported.** The
  look is confined to the pages given; the checks are not.

- **Criteria are separated from shape.** This is the change that made the
  feature work, and it generalises: an instruction file that describes one
  procedure end to end cannot grow a second one by branching, because the
  criteria are buried in the first procedure's steps. Any later agent in this
  repository that needs two shapes should be written this way from the start.

- **The second-agent restructuring is withdrawn.** It was put to the user on the
  strength of three failed attempts, and it was the wrong conclusion: the defect
  was in the file and a reading found it.

---

## Files Changed

**Added**

- `docs/roadmap/on-progress/pdf-review-cost/phase-0-targeted-pass-report.md`

**Modified**

- `.claude/agents/pdf-reviewer.md`
- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/tests/test_review.py`
- `.claude/skills/pdf/SKILL.md`

**Renamed**

The closure moves the roadmap out of `pending/`, so every file of the folder is
a rename against the start commit; the first two were modified in passing.

- `docs/roadmap/pending/pdf-review-cost/README.md` → `docs/roadmap/on-progress/pdf-review-cost/README.md`
- `docs/roadmap/pending/pdf-review-cost/phase-0-targeted-pass.md` → `docs/roadmap/on-progress/pdf-review-cost/phase-0-targeted-pass.md`
- `docs/roadmap/pending/pdf-review-cost/phase-1-svg-preflight.md` → `docs/roadmap/on-progress/pdf-review-cost/phase-1-svg-preflight.md`

---

## Problems And Deviations

- **`review.py` was changed, which the phase's *Files to Modify* did not
  anticipate.** It listed the agent's file and `pdf/SKILL.md` only. Without it a
  verification pass could not exist: `--zoom` returned before the checks ran, so
  the one command the pass needs did not exist.

- **Four delegated runs bought nothing, and the method was wrong.** Patch one
  line, re-run, patch, re-run. Reading the 161-line file once — which costs
  nothing — gave the cause immediately, including the one no re-wording would
  have fixed. When the thing behaving wrongly is a document an agent reads,
  reading it whole comes before measuring again.

- **A stale path was found by an agent, not by a test.** The file told the
  reviewer to read `library/<topic>/<slug>/index.md`, which the
  `document-anatomy` roadmap moved to `document/index.md` the day before and
  which its Phase 5 missed: `.claude/agents/` is outside every glob that phase
  checked. Fixed here. Phase 1 of this roadmap should widen the documentation
  test's reach rather than leave it to the next accident.

- **The closure audit did not run.** The `roadmap-auditor` agent hit this
  account's session limit. Everything it checks was verified by hand instead:
  no unticked task or criterion, `## Files Changed` computed from
  `git diff -M --name-status 9b608dd` plus `git ls-files --others` after the
  folder move, both narrative sections non-empty, the Assessment closing on what
  Phase 1 needs, the status and date set, a new changelog entry above the last,
  and `progress.py --check` clean. The next closure in this repository should
  run the audit on this one as well as its own.

All four tasks are done and all four acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. The
`pdf-verifier` restructuring raised mid-phase is withdrawn, for the reason under
`## Decisions`.

---

## Assessment

The feature works and saves a third of a verification pass, but the phase's
result is the reason it did not work for four attempts.

An instruction file that describes one procedure end to end cannot grow a second
procedure by branching. Not because the branch is badly worded — three
rewordings did not move it — but because the criteria are buried inside the
first procedure's steps. `## 2. Every sheet` held both "read every sheet" and
"here is what a defect looks like", so the other pass could be told to skip it
or told what to look for, and not both. Separating the shape from the criteria
fixed it in one edit, after four that could not have.

The second lesson is about method, and it cost about 125,000 tokens. Four
delegated runs were spent patching one line at a time, each one finding a
different remaining pull. A single reading of the file found all of them and the
deeper one besides. When something misbehaves outside this context, read it
whole before measuring it again.

What Phase 1 needs to know first: it adds checks to `review.py`, which this
phase has just restructured — the checks now run in both shapes, so a new one is
inherited by the verification pass for free, and that is the point of adding it
there rather than in the agent. Its subject, catching a figure's defects before
an eye is spent on them, is the other half of this roadmap's argument: this
phase made looking cheaper, Phase 1 makes some of it unnecessary. It should also
widen the documentation test to reach `.claude/agents/`, which is how a stale
path survived a roadmap that was looking for stale paths.
