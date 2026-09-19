# Summary — Session Review Accuracy

---

## Where We Started

`metrics.py` discarded every turn whose tool call mentioned the review tooling,
so that a review would not bill a task for the cost of reviewing it. The rule
serialised the call's input to JSON and looked for `metrics.py`, `corpus.py`,
`aggregate.py`, `session-review` or `reviews/` anywhere in it.

Any mention matched. Reading one of those files matched, editing one matched,
running its tests matched, grepping it matched. The four phases that built the
instrument were therefore work *on* the review tooling, and the instrument threw
most of them away: 106 API calls of 141 and 43 Bash calls of 119 across the four
slices it was measured on.

The error had a direction. The discarded turns are always work, so the measure
was always short, and always in the flattering direction — which is the failure
mode the whole `session-review` roadmap exists to prevent. It was recorded in
four reviews, ranked first by `aggregate.py` on recurrence, and carried here.

---

## Where We Landed

The exclusion asks what a tool call *does*: a Bash command that executes one of
the three scripts, the `session-review` skill being invoked, or a write under
`reviews/`. Reading, editing, testing or grepping those same files is the task,
and is counted.

On the same four slices of session `53a9d27e`: **132 API calls and 110 Bash
calls**, against 106 and 43 before, and a raw 141 and 119 with no exclusion at
all. Two thirds of that session's commands had been discarded and are back.

512 tests, two of them new: one that a turn editing or testing the instrument is
counted, one that a turn running it is not.

---

## What Each Phase Delivered

**Phase 0 — what belongs to the task.** The rule rewritten around the act rather
than the subject, and a second defect found while verifying the first: the
exclusion was applied record by record, and a transcript writes one record per
content block, so a message whose call sat in one record and whose thinking sat
in another had its call dropped and its turn counted. `tooling_messages()` makes
a first pass now, and a turn is excluded rather than a line of the file.

---

## What We Learned

**A rule that matches a name cannot tell an act apart.** Four script names in a
tuple, and a substring search: it reads as obviously correct, and it conflates
running a file with reading it, editing it and testing it. The fix is not a
longer list of names — it is asking what the call does, which the transcript
records plainly enough.

**Decide per turn, not per record.** A transcript writes one message as one
record per content block. Anything that decides record by record will act on
half a message: here the tool call was excluded and the turn was counted. This
is the second time the same property of the format has produced a defect — the
first was usage summed once per record instead of once per message, which
inflated every token figure — and both were found by measuring twice and looking
at the gap.

**A reference transcript is not a fixture.** The acceptance criterion named 147
API calls and 125 Bash calls. Those figures were taken over the whole file a day
earlier; the four slices cover eight of the session's fourteen hours, and the
file grew after the measurement. `session-review`'s own Phase 1 had written that
this would happen, and it happened to the roadmap that quoted it. A figure taken
from a live transcript should be recorded with its bounds and the moment it was
taken, or it is not reproducible.

---

## What We Are Leaving Open

- **A turn that runs the tooling is excluded even when running it was the
  work.** Nine turns of the reference session are in that position: `metrics.py`
  was executed to test it, not to review anything. The alternative — exclude
  only inside a slice where a review actually happened, marked by a write under
  `reviews/` or the skill being invoked — is right in purpose and was refused
  because it makes two identical commands measure differently depending on their
  neighbours, which the `session-review` roadmap ruled out at its opening. The
  argument and the figures are in the phase report, for whoever wants to
  overturn it.

- **The five reviews in the corpus keep the figures the old rule produced.**
  This roadmap's *Deliberately Out Of Scope* says so. The consequence is that
  `aggregate.py`'s medians currently mix measurements taken before and after the
  fix; with one `pdf` review and four `roadmap` reviews, no baseline is yet
  load-bearing, and a corrected instrument produces corrected blocks from the
  same transcripts whenever anyone wants them.
