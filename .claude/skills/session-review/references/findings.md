# Findings

A finding is the only part of a review that can leave `reviews/`. Since that
directory is not versioned, a finding reaches this repository by one road and
one only: becoming a line under `docs/roadmap/pending/`. The `carried:` field
records when that happened.

## The Shape

```yaml
- kind: skill-gap          # from the closed vocabulary below
  severity: high           # low | medium | high
  target: .claude/skills/pdf/SKILL.md
  fix: >-
    Document the `.keep` wrapper, and that the heading and lead-in sentence
    belong inside it.
  note: >-
    Three separate page-break defects, all the same cause, all found by the
    reviewer rather than by a check.
  carried: docs/roadmap/pending/pdf-pitfalls/phase-1-breaks.md   # optional
```

`kind`, `severity`, `target` and `fix` are required. `note` is optional and is
one sentence of evidence. `carried:` is written later, when the finding becomes
roadmap work; a repository path, never a link.

**A finding without a `target:` and a `fix:` is not a finding and is not
written.** It is a complaint. The target names the file that would change and
the fix says what it would say — if neither can be written, the observation
belongs in the body's prose, where nothing counts it.

`target` is a path in this repository. A finding whose target is a document
under `library/` is a defect in that document, not in the way the work is done,
and does not belong here.

## The Vocabulary

Closed. A finding that fits none of these is a signal about the format, and
belongs in the phase notes of whatever is then done about it — not in a ninth
kind invented on the spot. `corpus.py` refuses an unknown `kind` by name.

| `kind` | What it names | Worked example |
|---|---|---|
| `skill-gap` | The skill was followed and still did not say what the session needed to know. | `pdf/SKILL.md` does not mention that `--soft` is *darker* than `--muted` in the dark variant; every secondary label in a hand-drawn figure came out unreadable. Target: the skill's pitfalls. |
| `skill-drift` | The session departed from an instruction it had loaded, for a reason that turned out to be sound. The drift is evidence the instruction is wrong, not that the session was. | The `pdf` skill routes diagrams through `diagram-design`; an electronic schematic matches none of that plugin's types, so it was drawn by hand. The skill should say so. |
| `tooling-gap` | A check or a command that would have caught the defect before an eye was spent on it. | Nothing measures a figure's *printed* font size: a 760-unit viewBox at 170 mm gave 4.6 pt text, found by a delegated reviewer three steps later. |
| `tooling-noise` | A tool that reported a defect that was not one, or reported the same non-defect repeatedly. Cost without information. | "Page number in monospace" reported in three passes out of four, against a stylesheet that sets every page number in monospace. |
| `waste` | Cost spent for nothing, where the cheaper path existed at the time. Not "this was expensive" — expensive is a measure, not a finding. | A full second review pass over fifteen pages to verify fixes on six. |
| `art-direction` | A defect in `brand/` or `theme/` that reached the page: a missing glyph, a role that inverts between variants, a rule that fights another. | `≈` is in none of the art direction's fonts and fell back to Cantarell mid-line. |
| `process` | A repository convention that is missing, or that exists and was not followed. | A figure generator was written and left in `sources/`, because nothing says where one belongs. |
| `unverified` | Something was delivered resting on an assumption nobody checked, and the review is where that is said out loud. | The redrawn schematic was checked against the photograph, never against the board; two contradictory board dimensions were carried into the document unresolved. |

## Severity

Three levels, and the middle one is not a refuge.

- **high** — it cost real tokens or shipped something wrong, and it will happen
  again on the next task of this kind. At the end of a review these are read
  back to the user, who decides which are carried.
- **medium** — real, recurring, cheap each time. This is where `tooling-noise`
  usually sits: harmless once, expensive across fifty sessions.
- **low** — worth recording so that recurrence can promote it. A `low` finding
  seen in six reviews is a `high` finding nobody noticed.

Severity is the session's judgement of the finding, never of the session. There
is no severity for "I could have done better".

## Recurrence Is The Real Signal

One review's findings are anecdotes. `aggregate.py` ranks them by how often the
same `kind` lands on the same `target`, which is why both fields are
constrained and why `target` is a path rather than a sentence. Two reviews
naming the same file for the same reason say something neither of them could.
