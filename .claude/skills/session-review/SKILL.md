---
name: session-review
description: Measure a task of this repository once it is finished, and write the review to reviews/ — what it cost, where the cost went, and what should change so that the next task of the same kind costs less. Use only after a task is done and only when a review is asked for. It is not part of doing the work: it builds nothing, fixes nothing, reviews no code and no PDF, changes no production skill, and never runs while a task is still in progress.
---

# Reviewing a finished task

**A session grading itself gives itself a good mark.** So this skill never asks
what went wrong. It measures, and the measurements set obligations the review
has to discharge. Everything below exists to keep the review from being an
account of how well things went.

One task, one review. Not one session: a conversation that builds two documents
produces two reviews, bounded by a cursor — a review starts where the previous
review of the same session stopped.

**Write the review at the end of its task, not at the end of a long session.**
What a script can rebuild from the transcript it will rebuild whenever it is
run. What only the session knows — why it deviated, what it worked around, what
it never thought to ask — is exactly what compaction takes first. A review
written three tasks late is a review of the measurements alone.

## The budget

The review is the last thing the session pays for, and it is not allowed to be
expensive. **Eight thousand tokens, everything included.**

- **Two commands.** `metrics.py` below, and nothing else unless something it
  printed is unreadable.
- **At most two file reads**, and only `references/format.md` or
  `references/findings.md` when the format is not already in mind.
- **No rebuild, no subagent, no `make`.** Reviewing is not working.
- **Prose under six hundred words.** Findings of three lines each.

**What the eight thousand cover:** everything the review puts into the context,
the tooling's own output included — the `measured:` block, the comparison table,
the obligations, and `--timeline` when it is asked for. The budget cannot be met
by moving cost out of the prose and into a command. `--timeline` is optional,
costs a line per tool call, and the budget is met without it: ask for it only
when a measure makes no sense and the sequence would explain it.

## The one command

```bash
.venv/bin/python .claude/skills/session-review/scripts/metrics.py --owed --skill <skill>
```

It prints three things, in this order:

1. **The `measured:` block.** It goes into the review as it stands. It is never
   written by hand, never corrected, never rounded. If a figure looks wrong,
   that is a finding about the script, not a number to fix in passing.
2. **The comparison table** — each measure against the median of earlier reviews
   of the same skill, with the ratio, and `← over 1.5×` on anything past that.
   The table is read, never stored: medians belong to the corpus, not to a
   review.
3. **The obligations** these measures trigger, and one line for each skill the
   slice loaded.

Add `--from` and `--to` only when the default slice is wrong — by default it
runs from the end of this session's last review to now.

## The seven obligations

The first five are printed by `--owed`, because a duty a session has to
remember is a duty a session will forget.

1. **Explain the three largest costs.** Not list them — say what they bought.
   *When the corpus has no baseline yet, three becomes five.* An obligation
   that cannot fire is not a lenient obligation, it is an absent one.
2. **Explain every measure past one and a half times its median.** The excess
   is the subject, not the measure.
3. **A finding or a justification for each non-zero waste and friction
   counter** — repeated commands, files read twice, interruptions, errors.
   "It was necessary" is a justification; it has to be written.
4. **A finding or a reason for each correction the user made.** A correction
   the session could not have avoided is said to be unavoidable, and why.
5. **Account for every skill the slice loaded.** Say what each one brought to
   the task — a rule followed, a script run, a pitfall avoided. A skill loaded
   without need is a `trigger` finding, targeting that skill's `SKILL.md`,
   whose description is what made it fire. The other direction is a question,
   because no script can see a skill that did not load: was a job of this slice
   done without the skill that covers it? If so, that is a `trigger` finding
   too. A skill that fires on a neighbour's job is worse than no skill, and the
   review is the only place anything checks it.
6. **No finding without a `target:` and a `fix:`.** Otherwise it is a
   complaint: put it in the prose, where nothing counts it.
7. **No section for what went well.** A review is an account of cost, of what
   it bought, and of what did not go as intended. There is no other section.

## Writing it

`reviews/YYYY-MM-DD-<session-prefix>-<slug>.md`. The front matter is structured
and read by machines; the body is prose and read by a person. The fields are in
`references/format.md`, the finding vocabulary in `references/findings.md` — it
is closed at nine kinds, and `corpus.py` refuses an unknown one.

The session fills `task`, `skill`, `outcome`, `corrections`, `findings` and the
prose. `metrics.py` fills `measured:`. Neither writes the other's half: what a
transcript records is never written by hand, and what a transcript cannot record
is never computed.

Check it parses before saying it is done:

```bash
.venv/bin/python .claude/skills/session-review/scripts/corpus.py
```

## Closing the loop

`reviews/` is not versioned. A finding therefore reaches this repository by one
road only: becoming a line under `docs/roadmap/pending/`.

At the end of the review, list the `severity: high` findings — one line each —
and ask the user which are carried. Write the chosen ones into
`docs/roadmap/pending/`, and fill each finding's `carried:` with the path. Carry
nothing that was not chosen.

## What this skill never does

- **Review code, or review a built PDF.** Those are `/code-review` and the
  `pdf-reviewer` agent. Point at them; do not compete with them.
- **Change a production skill.** A review proposes a target and a fix. Applying
  it is the roadmap's job, not this one's.
- **Judge without a session.** The ledger records numbers and never prose, and
  nothing here infers a cause from a measurement.
- **Price anything.** The measures are tokens. Tiers and cache rates are not
  this repository's business.
- **Reproduce the conversation.** A review names files, skills and counts.
  `reviews/` is unversioned so that it can hold what the repository must not,
  which is not a licence to fill it.
