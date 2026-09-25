# Roadmap: Discussion and Illustration Skills

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
Phase 0  The Discussion Skill             🟡 ███████████████████░  93%  (13/14)
Phase 1  Discussion Pilot — Transistor    🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/9)
Phase 2  The Drawing Brick                🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 3  The Illustration Skill           🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/10)
Phase 4  Illustration Pilot — Transistor  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/8)
TOTAL                                        █████░░░░░░░░░░░░░░░  27%  (13/48)
```

**Current Phase:** Phase 0 — The Discussion Skill
**Blocked By:** —
**Next Milestone:** Phase 0 — The Discussion Skill

---

## Why This Roadmap Exists

Two ways of making a document have grown up outside every skill.

**Documents born from a conversation.** The sources of `led`,
`instruments-diy`, `esp32` and `transistor` are passages the user copied out
of conversations with other agents. They hold the agents' answers without the
questions that prompted them: `transistor-1.md` opens on *"Oui. Je peux te
faire un vrai cours… Je te propose cette structure"*. The repository receives
the result without what the user said, without the decisions, and without
knowing which claims were ever checked. No discussion has been held in the
repository itself yet. A discussion with no external sources produces the
model's own account. Once that account is in a document, it carries the same
authority as an imported manual.

**Figures drawn by code.** `diagram-design` draws relations, not objects.
Whatever it cannot draw is written by hand in a document's `generators/`,
with no rule. The radio-fm review measured the cost. The figure generator
took two thirds of the main context: 900 lines, patched seven times. Figure
proofs were half the images carried. Every explanatory label in eight figures
was unreadable on dark paper. `radio-fm` and `round-led-d4017` each carry
their own copy of the same drawing helpers.

This roadmap adds a skill for each practice, and a pilot proves both on the
`transistor` document. That document has two pasted excerpts, a
Gemini canvas, and a subject that needs objects drawn rather than flows.

---

## Decisions Taken At Opening

**Two skills written for this repository, not an adaptation of `canvas-design`.**
The skill the user showed makes standalone art objects. It downloads fonts,
chooses its palette freely, draws a PDF by hand, outputs PNG and invents
content for effect. Every one of those contradicts the art direction or the
`pdf` skill. Only one idea is kept: on a second pass, refine what exists
rather than add.

**Discussion first.** It is thin, has no code, and every later document
benefits from it. Illustration needs real design work: a brick, a proof
command, a check extended.

**The discussion journal lives in `study/`.** The agent writes it, so it does
not go in `sources/`. It is neither received nor derived, so it is durable,
like the `NOTES.md` of `sourcing`. A pasted excerpt stays intact in
`sources/`. Because a paste carries the answers without the questions, what
the user said is asked for, never inferred from the answers.

**Three statuses per claim:** said by the user, an agent's account
(unverified) — this agent's or that of the agent a paste came from — and
established. The discussion never establishes anything
itself: it hands the claim to `sourcing`. It produces knowledge and an outline,
and `index.md` is written by `pdf`.

**A resume reads the journal, not the transcript.** `claude --resume` replays
the conversation, or the summary left after the context was compacted, which
loses details. The journal is kept small enough to be read by any session.

**Illustrations are role-based SVG drawn by code.** The code goes in
`generators/` and the SVG in `document/assets/`. No raster is generated, and
no external image model is called.

**The boundary with `diagram-design` is set by what is drawn.** Relations —
boxes, arrows, axes, data — go to `diagram-design`. An object, a material, an
electronic schematic or a cover goes to `illustration`.

**The drawing brick goes to the core, provisionally.** The document generators
that call it live outside every skill, which is the second clause of
`docs/architecture.md` §2. Phase 2 confirms or overturns this against the
rule.

**Interactive figures are deferred.** Neither WeasyPrint nor the e-readers
the EPUB targets run JavaScript. On paper, a phenomenon that varies is drawn
as small multiples. Interactive figures wait for a web output. Phase 3
records that decision, and what would reopen it.

---

## Deliberately Out Of Scope

- Interactive figures, a web output, JavaScript in a PDF or an EPUB.
- Generating raster images, or calling an external image model.
- Modifying `diagram-design`.
- Rewriting the generators of `radio-fm` and `round-led-d4017` onto the brick.
- Fetching a conversation from a share link. Gemini and ChatGPT links only
  render in a browser running JavaScript, and what reaches the repository is
  text the user copies and pastes. Phase 4's one attempt at the Gemini canvas
  is a pilot input, not a feature of the skill.
- Keeping raw session transcripts in a document.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [The Discussion Skill](phase-0-discussion-skill.md) | 14 | 🟡 In Progress |
| 1 | [Discussion Pilot — Transistor](phase-1-discussion-pilot.md) | 9 | 🔴 Not Started |
| 2 | [The Drawing Brick](phase-2-drawing-brick.md) | 7 | 🔴 Not Started |
| 3 | [The Illustration Skill](phase-3-illustration-skill.md) | 10 | 🔴 Not Started |
| 4 | [Illustration Pilot — Transistor](phase-4-illustration-pilot.md) | 8 | 🔴 Not Started |

---

## Dependencies

- The user's time: in Phase 1, the repository's first live discussion over at
  least two sessions, and the outline; in Phase 4, the figure list and the
  cover.
- `diagram-design`, unchanged, for the figures that are relations.
- The [library-catalogue](../library-catalogue/README.md) roadmap, for Phase
  1: the pilot finds the transistor's material through the map.

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md): §2, core or skill; §5,
  the skills and their boundaries; §10, what stays undecided; §11, the inside
  of a document.
- [`docs/document.md`](../../../document.md): what each command puts where.
- [The radio-fm session review](../../../../reviews/2026-09-24-dddc278e-radio-fm.md):
  the measured cost of hand-drawn figures, and the rules it learned.
- `.claude/skills/sourcing/SKILL.md`: the journal and its three statuses, which
  the discussion journal mirrors.
- `.claude/skills/pdf/SKILL.md`: the cover rule, *Inserting a diagram*.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/discussion-and-illustration/`
**Version:** 1.2.0
**Created:** 2026-09-24
**Last Updated:** 2026-09-25

---

## Changelog

### 1.2.0 (2026-09-25)

Phase 0 gained a real case and an archive. The skill was validated on the
user's notebook discussion: it fired unasked at the opening and at a
fresh-session resume, and the resume cost about 10k tokens where the
conversation held 104k. Seven phase-0 tasks were ticked earlier and two here,
the real case and the description. Five tasks were added under *The
archive*, a multi-file journal whose design is recorded in the phase-0
report (9 → 14 tasks, total 43 → 48). Phase 0 is now blocked by the new
`suite-and-review` roadmap, because `make test` depends on the user's library
and cannot pass until that dependency is removed.

### 1.1.0 (2026-09-24)

Two facts corrected the plan. First, the sources are passages the user copied
and pasted, not exports: they carry the agents' answers without the user's
questions, and no discussion has been held in the repository yet. Phase 0's
import procedure is now a procedure for a pasted excerpt, and it asks for what
the user said rather than inferring it. Phase 1 gains a task: it holds the
repository's first live discussion, not only a scoping session (8 → 9 tasks).
Second, the user cannot export the Gemini canvas. It is no longer a
dependency. Phase 4 makes one capture attempt with Playwright and otherwise
works from images (7 → 8 tasks). Total 40 → 42.

### 1.0.0 (2026-09-24)

Roadmap created with five phases and 40 tasks. First the `discussion` skill,
then its pilot on `transistor`. Then the drawing brick, the `illustration`
skill, and its pilot on the same document.
