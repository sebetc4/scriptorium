# Phase 1 Report: What A Check Can See Without An Eye

**Phase:** [phase-1-svg-preflight.md](phase-1-svg-preflight.md)
**Start Commit:** 14dd6ba

---

## Work Log

### 2026-09-20

Phase opened. Phase 0's file and report were read in full: 4/4 tasks, 4/4
acceptance criteria, no restructuring pending, and its closure audit did not run
— the agent hit this account's session limit, and its checks were done by hand.

**Two of the three checks this phase asked for already exist, and are better
than what was asked for.** That was established before any code was written, by
measuring rather than by reading the phase file.

An SVG is *inlined* into the page — `build.py` replaces `<img src="*.svg">` with
the SVG itself so its `var(--role)` resolve against the document's cascade — so
**its text lands in the PDF's text layer like any other text**. Measured on the
schematic of `round-led-d4017`: 140 spans under 7 pt on that page, at 6.0 to
6.8 pt, all of them figure labels, all of them visible to the checks.

- **The printed font size**, which the phase asked to compute from the viewBox
  and the placed width, is already *measured* by `tiny-text` against
  `MIN_TEXT_SIZE = 5.0 pt`. Computing it would be a prediction of a number the
  text layer states.
- **A glyph the art direction's fonts have not got** is already named by
  `font` — seen firing on `guide-de-style` as *"Cantarell sets → — not a family
  of the art direction"*, and pinned here on an SVG label carrying `≈`, the
  glyph the original finding was about.

The phase's premise was stale, and knowably so: the finding that produced this
roadmap came from a session of 2026-09-17 that ran **before** `review.py` gained
its eight text-layer checks the same day. Neither of those two tasks needed code;
they needed a test each, so that "already covered" is a fact the suite keeps
true rather than a claim in a report.

**The third check was genuinely missing, and is written.** `overlapping-text`
compares the bounding boxes of the body spans of a page and names the two that
are printed on top of each other. Two precautions, because a check that cries
wolf costs more than the defect it names:

- spans sharing a baseline are consecutive text on one line and are skipped;
- an overlap counts only past 30 % of the smaller box's area.

Run over the whole library — eight documents, fifteen PDFs — it reports
**nothing**, in 13 seconds. A check that is silent everywhere may be inert, so
it is pinned from both sides: two labels 2 units apart in an SVG are reported
with both their texts, the same two labels placed apart are not, and three
justified paragraphs are not.

**The hole neither the old checks nor the new one can see.** An SVG the build
*declines* to inline is rendered as a picture: its roles stay unresolved and its
text never reaches the text layer, so `tiny-text`, `font` and
`overlapping-text` all go blind on it at once. `build.py` returned silently in
all three cases — not a file, outside `document/`, over 512 kB. It now names the
figure and the reason on stderr. Sixteen SVGs exist in the library and the
largest is 73 kB, so nothing is affected today; the point is that nothing said
so.

**Where the checks run, which the phase asked to decide.** Inside `make review`,
against the built PDF, and not before the build:

- the text layer gives the **printed** size, in points on the page, where a
  pre-build check would compute it from the viewBox and a placed width that only
  the CSS knows — a prediction against a measurement;
- Phase 0 made the checks run in both passes, so a check added here is inherited
  by the verification pass at no cost;
- the build already reports the one thing a pre-build check would own: a figure
  it could not inline.

The inherited task was done too: `tests/test_documentation.py` now gathers every
file this repository reads as an instruction — `README.md`, `CLAUDE.md`, every
`SKILL.md`, **every `.claude/agents/*.md`** and every `docs/*.md` — and fails on
a path a document no longer has. `.claude/agents/` was outside every glob the
`document-anatomy` roadmap checked, which is how a stale `index.md` path
survived a roadmap that was looking for stale paths.

`make test`: 524 passed, from 515 at the phase's start.

---

## Decisions

- **Nothing was reimplemented.** Two of the three checks existed; the phase
  closed them with a test each rather than with a second implementation. A
  measurement of the built page beats a prediction from the source, and having
  two of them would have meant two answers to the same question.

- **`overlapping-text` reports from the text layer alone, without confirmation
  on an image.** It is listed among the textual checks in the agent's file. Two
  boxes overlapping past 30 % of the smaller is not a judgement call, and the
  three fixtures show it does not fire on ordinary prose.

- **The checks live in `make review`, against the built PDF.** Reasons above.
  The corollary is that a figure is checked only once it has been built, which
  is the trade: a prediction before the build would be cheaper and wrong more
  often.

- **The build speaks when it declines to inline.** It is the only moment the
  information exists, and it is the only figure the checks cannot reach.

---

## Files Changed

**Added**

- `docs/roadmap/completed/pdf-review-cost/phase-1-svg-preflight-report.md`
- `docs/roadmap/completed/pdf-review-cost/summary.md`

**Modified**

- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/scripts/build.py`
- `.claude/skills/pdf/tests/test_review.py`
- `.claude/skills/pdf/tests/test_pdf_layout.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/agents/pdf-reviewer.md`
- `tests/test_documentation.py`

**Renamed**

The roadmap closes with this phase, so its folder moves to `completed/` in the
same pass; the first and last were modified in passing.

- `docs/roadmap/on-progress/pdf-review-cost/README.md` → `docs/roadmap/completed/pdf-review-cost/README.md`
- `docs/roadmap/on-progress/pdf-review-cost/phase-0-targeted-pass.md` → `docs/roadmap/completed/pdf-review-cost/phase-0-targeted-pass.md`
- `docs/roadmap/on-progress/pdf-review-cost/phase-0-targeted-pass-report.md` → `docs/roadmap/completed/pdf-review-cost/phase-0-targeted-pass-report.md`
- `docs/roadmap/on-progress/pdf-review-cost/phase-1-svg-preflight.md` → `docs/roadmap/completed/pdf-review-cost/phase-1-svg-preflight.md`

---

## Problems And Deviations

- **Tasks 1 and 3 were closed by measurement and a test, not by the code they
  asked for.** Both checks already existed, in a better form. Writing the
  viewBox arithmetic would have added a second, less accurate answer to a
  question the text layer already answers. The phase's premise dated from before
  those checks existed.

- **The closure audit did not run for either phase.** The
  `roadmap-auditor` agent hit this account's session limit. Both closures
  were verified by hand against the same checklist: no unticked task or
  criterion, `## Files Changed` computed from `git diff` after the folder
  move plus `git ls-files --others`, both narrative sections non-empty,
  the Assessment closing on what comes next, statuses and dates set, a new
  changelog entry above the last, and `progress.py --check` clean.

- **`build.py` was changed, which the phase's *Files to Modify* did not list.**
  It named `review.py` and the pdf suite. The blind spot the new checks share is
  created in the build and can only be reported there.

---

## Changes To Later Phases

No phase follows. The roadmap closes with this one.

---

## Assessment

The phase's result is that most of what it was asked to build was already there,
and that this was knowable in one measurement — print the span sizes of a page
carrying a schematic and see the figure's labels in the text layer.

The reason the roadmap asked anyway is worth keeping. Its finding was carried
from a review of a session that ran on 2026-09-17, hours before `review.py`
gained the checks that cover it. The corpus did its job — the finding was real
when it was written — and nothing re-examined it between the writing and the
work. A finding carried from a review is a statement about a moment, and the
phase that acts on it should start by asking whether it is still true. That cost
one command here; it would have cost a reimplementation if the phase had been
executed as written.

What the roadmap leaves: `overlapping-text` is the only new check, and it is
silent on every document in the library today. It will earn its place the next
time a figure is drawn by hand — which is what the finding was about — and until
then its three fixtures are the only evidence it works.
