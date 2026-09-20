# Summary — The Cost Of Looking At A PDF

---

## Where We Started

Reviewing one PDF document cost more than writing it. On session `4c7bb3d0`,
measured after the fact, four delegated passes read 91,911 fresh tokens against
154,333 for everything the main context did, and eleven images carried 625,600
tokens of context between them.

Two findings, carried from the review of that session, accounted for most of it:

- **A verification pass re-read the whole document.** The second round cost
  46,636 fresh tokens to confirm fixes on six pages of fifteen, because the
  agent took a document and a variant and reviewed the document.
- **Nothing checked a figure before it was looked at.** Text at 4.6 pt, three
  label collisions and a missing `≈` glyph were each found by an eye, three
  steps and eleven images later.

---

## Where We Landed

A verification pass costs **21,619 tokens against 32,666** for a full one on a
fifteen-page document: a third of the tokens, half the tool calls, 57 % of the
wall time, and six page images instead of four sheets and six zooms. The
text-layer checks still cover the whole document in both shapes, which is what
catches a page the fix reflowed.

A figure's own labels are checked like any other text, because an SVG is inlined
into the page. `tiny-text` measures a label's printed size, `font` names a glyph
the art direction has not got, and `overlapping-text` — new — names two labels
printed on top of each other. None costs an image. A figure the build declines
to inline escapes all three, and the build now says so.

524 tests, from 515.

---

## What Each Phase Delivered

**Phase 0 — the targeted pass.** `make review … ZOOM=` returned before the
checks ran, so the one command a verification pass needs did not exist;
`review.py` now runs the checks in both shapes. Four delegated attempts then
changed nothing, because the agent's file asserted its shape in four places and
kept every judging criterion inside the full pass's own steps. Separating the
criteria from the shape fixed it in one edit.

**Phase 1 — what a check can see.** Two of the three checks asked for already
existed and were closed with a test each rather than reimplemented. The third,
`overlapping-text`, is new. The blind spot the three share — a figure the build
did not inline — is now reported by the build. `tests/test_documentation.py`
reaches `.claude/agents/`.

---

## What We Learned

**An instruction file that describes one procedure cannot grow a second one by
branching.** Not because the branch is badly worded — three rewordings did not
move it — but because the criteria are buried inside the first procedure's
steps. `## 2. Every sheet` held both "read every sheet" and "here is what a
defect looks like", so the other pass could be told to skip it *or* told what to
look for, and not both. Separate the **shape** of a procedure from its
**criteria**, and two shapes cost one section each.

**When something misbehaves outside your own context, read it whole before
measuring it again.** Four delegated runs, about 125,000 tokens, were spent
patching one line at a time and re-running. A single reading of the 161-line
file found every pull at once and the deeper defect besides. Patch-and-retry is
the expensive path when the thing being patched is a document an agent reads.

**A finding carried from a review is a statement about a moment.** This
roadmap's second phase asked for two checks that had been written hours after
the session that produced the finding. The corpus was not wrong; nothing
re-examined the finding between the writing and the work. A phase acting on a
carried finding should start by asking whether it is still true — here that cost
one command, against a reimplementation if the phase had been executed as
written.

**A silent check is not evidence of a clean library.** `overlapping-text`
reports nothing on any document here. That is only worth something because three
fixtures show it firing on a real collision and staying quiet on ordinary prose.

---

## What We Are Leaving Open

- **`overlapping-text` has never fired outside its fixtures.** It will earn its
  place the next time a figure is drawn by hand, which is what the finding was
  about.
- **A figure is checked only once it is built.** A pre-build check would be
  cheaper and would have to predict the printed size from the viewBox and a
  placed width only the CSS knows. The trade was taken deliberately; the build's
  warning covers the one case that never reaches a check at all.
- **Phase 0's closure audit did not run**, the agent having hit this account's
  session limit, and its checks were done by hand. The next closure in this
  repository should audit it as well as its own.
