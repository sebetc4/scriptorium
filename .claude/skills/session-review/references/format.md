# The Review Format

One task, one review, one file: `reviews/YYYY-MM-DD-<session-prefix>-<slug>.md`.

A review has two halves and they are not written by the same author.

- **The front matter is structured and is read by machines.** `corpus.py` parses
  it, `aggregate.py` counts it, and a later review compares against it. Inside
  it, everything under `measured:` belongs to `metrics.py` and is never written
  or corrected by hand; everything else belongs to the session.
- **The body is prose and is read by a person.** No script parses it.

The line between the two is the whole point of the format. What a transcript
records is never written by hand; what a transcript cannot record is never
computed. A review that blurs the two is worth less than either half.

---

## The Fields

### Owned by the session

| Field | Type | Required | What it holds |
|---|---|---|---|
| `review` | integer | yes | Format version. `1` today. Reviews of different versions are never compared. |
| `date` | ISO date | yes | The day the task was reviewed. |
| `session` | string | yes | `CLAUDE_CODE_SESSION_ID`, in full. |
| `slice` | mapping | yes | `from:` and `to:`, ISO timestamps. The bounds of the task inside the session. |
| `task` | string | yes | What was asked, in one sentence, in the user's words rather than the agent's summary of them. |
| `skill` | string | yes | The skill the task belongs to: `pdf`, `epub`, `fetch`, `sourcing`, `discussion`, `translate`, `roadmap`, `session-review`, or `none` — `corpus.py` refuses anything else. One value — the skill the task was about, not every skill that loaded; those are under `measured.loaded`. Baselines are grouped by it. |
| `document` | string | no | `topic/slug`, when the task produced or changed one document. Absent otherwise. |
| `outcome` | enum | yes | `delivered`, `partial`, or `abandoned`. What the user ended up with, not how the session felt about it. |
| `corrections` | integer | yes | How many times the user corrected, redirected or rejected something. Counted by the session, because a transcript cannot tell a correction from a new request. |
| `findings` | list | yes | See `findings.md`. An empty list is written `findings: []` and is a claim, not a default. |

`slice` bounds one task. A conversation that builds two documents produces two
reviews, and the second starts where the first stopped. Nothing is inferred
from the shape of the conversation.

### Owned by `metrics.py`

Everything under `measured:`. Its shape:

```yaml
measured:
  tokens:            # the main context
    fresh: 157402      # input + cache_creation: what entered the context
    cache_read: 1840551
    output: 72182      # what was generated, thinking included
    thinking: 21044
  subagents:         # one entry per run, never aggregated by hand
    - type: pdf-reviewer
      fresh: 49214
      cache_read: 181755
      seconds: 50
      loaded: {pdf: 1}   # only when the run loaded a skill
  turns: 143
  tools:             # by name, calls not results
    Bash: 96
    Read: 14
  images: 11
  files_written: 7
  skills:            # assistant turns carrying each attributionSkill — the
                     # last skill loaded, which is not a load in this slice
    pdf: 118
  loaded:            # Skill tool calls: each is a load the review accounts for
    pdf: 1
  friction:
    interruptions: 0
    denials: 1
  derived:           # never presented as read: each states its rule
    active_minutes:
      value: 172
      rule: wall clock minus every gap over 5 min
    image_carry:
      value: 94000
      rule: each image's tokens times the turns it stayed in context
```

Three rules govern this block and they are not negotiable.

1. **A measure that could not be read is absent, never zero.** A zero means
   "counted, found none". A missing key means "this transcript does not record
   it". A review that writes `interruptions: 0` on a corpus where interruptions
   were never observable is lying quietly, which is the failure mode this whole
   format exists to prevent.
2. **Everything under `derived:` carries its `rule:`.** A derived measure is an
   opinion with a number attached, and the rule is what makes it arguable.
3. **Medians are not stored.** They are computed from the corpus at the moment
   a review is written, by `corpus.py`, and printed beside each measure by
   `metrics.py`. Storing one would freeze a baseline that is meant to move, and
   would let a review be compared against a median it wrote itself.

---

## The Body

Free prose, English, under six hundred words. Its sections are the session's to
choose except for one rule, which belongs to the skill rather than to the
format: **there is no section for what went well.** A review is an account of
cost and of what it bought, and of everything that did not go as intended.

The findings themselves live in the front matter, not in the body. Prose
explains; the list is what gets counted.

---

## A Complete Review

Written out in full, because a format that cannot be written by hand from its
own reference is not a format. The figures are those a real session gave
`metrics.py`; the task and the document are fictional, like every example of
this repository. Only `task`, `corrections` and the findings are written by
hand.

```markdown
---
review: 1
date: 2026-09-17
session: 4c7bb3d0-0000-4000-8000-000000000000
slice:
  from: 2026-09-17T14:17:56Z
  to: 2026-09-17T14:42:54Z
task: >-
  Add the new sources and turn the notice into a step-by-step guide — how the
  machine is installed, what each programme does, what each error means.
skill: pdf
document: home/appliances/washer
outcome: delivered
corrections: 3
measured:
  tokens:
    fresh: 154333
    cache_read: 5443404
    output: 72182
    thinking: 24684
  subagents:
    - {type: pdf-reviewer, fresh: 23075, cache_read: 74289, seconds: 44}
    - {type: pdf-reviewer, fresh: 22200, cache_read: 73117, seconds: 40}
    - {type: pdf-reviewer, fresh: 20710, cache_read: 71733, seconds: 39}
    - {type: pdf-reviewer, fresh: 25926, cache_read: 69071, seconds: 48}
  turns: 46
  tools: {Bash: 25, Read: 11, Agent: 4, Write: 2, AskUserQuestion: 2, Skill: 1}
  images: 11
  files_written: 2
  skills: {pdf: 23}
  loaded: {pdf: 1}
  friction: {interruptions: 0, api_errors: 0}
  derived:
    active_minutes:
      value: 20
      rule: wall clock minus every gap over 5 min
    context_peak:
      value: 176186
      rule: largest input of one API call, fresh and cached
    image_carry:
      value: 625600
      rule: 1600 tokens an image times the API calls it stayed in context
    build_cycles:
      value: 5
      rule: Bash commands running make build
    review_cycles:
      value: 3
      rule: Bash commands running make review
    files_read_twice:
      value: 1
      rule: files read again in the same slice
findings:
  - kind: waste
    severity: high
    target: .claude/agents/pdf-reviewer.md
    fix: >-
      Accept a page list, so a verification pass re-reads the pages that
      changed instead of the whole document.
    note: >-
      The second pass cost 46,636 fresh tokens across both variants to
      confirm fixes on six pages, all fifteen of them re-read.
  - kind: tooling-noise
    severity: medium
    target: .claude/agents/pdf-reviewer.md
    fix: List monospace page numbers among the accepted choices.
    note: Reported as a defect in three passes out of four.
---

The four delegated review passes cost 91,911 fresh tokens against 154,333
for everything the main context did — a third of the task, spent on looking.
The second pass bought two real defects for the price of the first.

The eleven images are the second item. Three of them are successive previews
of the same diagram, each carried for the rest of the conversation …
```

---

## What The Format Refuses

- **A price.** The measures are tokens. Converting them depends on tiers and
  cache rates this repository has no business tracking.
- **Prompt text.** A review names files, skills and counts. It does not
  reproduce the conversation — `reviews/` is unversioned precisely so that it
  can hold what the repository must not, and that is not a licence to fill it.
- **A grade.** No score, no mark out of ten. A number that summarises a session
  is a number nobody can argue with.
