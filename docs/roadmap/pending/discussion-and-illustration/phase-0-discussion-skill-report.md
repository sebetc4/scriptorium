# Phase 0 Report: The Discussion Skill

**Phase:** [phase-0-discussion-skill.md](phase-0-discussion-skill.md)
**Start Commit:** d66f0b8

---

## Work Log

### 2026-09-24

Committed the roadmap as `d66f0b8` so that this phase's diff holds its own
work only, then opened the phase.

While it opened, the user said they have a discussion to hold with an agent
to create a document. It is the real case the skill lacked: until now the
live path had no instance anywhere in the repository. The skill is drafted
first from what does not need a real case, and the discussion is then held
here, with the draft, in a fresh session. The phase file gained a task for it,
under *The first real case* (8 → 9 tasks), and the README's count and
progress block were recomputed.

Loaded `superpowers:writing-skills` to write the skill, and was about to run
a baseline subagent without it, when the user pointed out that
`skill-creator` is also installed. Compared the two, then chose
`skill-creator` as the frame, with one idea taken from `writing-skills` (see
Decisions). `library/` is gitignored, so a worktree would not hold the
transistor sources: the test runs work on a copy in the session's scratchpad.

Drafted `SKILL.md` and `assets/journal.md`. Launched three test cases —
importing the two pasted excerpts, resuming from a journal, starting a live
discussion — each with and without the skill: six runs in parallel. All six
stopped on the user's session limit (HTTP 429) before writing anything; the
fixtures were checked intact before relaunching.

While the limit reset, the user prepared their real discussion:
`library/electronics/learning/pratice/`, holding their own notes on soldering
and a photo of their joints, plus a longer copy of the notes one level up.
That showed a case the draft did not cover — what the user brings, as opposed
to what another agent said — and the skill gained a section for it: their
notes are what the user said, a photo is received material whose reading is
an agent's account, and a file left outside the layout is read, never moved.
The live-discussion test case was dropped (see Decisions); the other two were
relaunched, four runs.

Registered the skill in `CLAUDE.md`, `README.md`, `docs/architecture.md` §5
(what it is for, the `discussion` / `sourcing` boundary, what it refuses, its
trigger row) and §11 (the journal in the durable table), and in
`docs/document.md` (`study/discussion.md`). Wrote the skill's suite,
`tests/test_discussion.py`: nine tests, passing, with
`tests/test_documentation.py`.

The four runs came back. Every assertion passed in both configurations:
- in the import runs, `sources/` stayed intact, no `index.md` was written,
  claims cited their passage, nothing was presented as established, the
  missing canvas was noted, and the user was asked for their goal and reader;
- in the resume runs, each reply stated where the discussion stood, asked the
  pending question, and re-asked nothing the journal answered.

| Run | Tokens | Tool calls | Time |
|---|---|---|---|
| import, with skill | 98.9k | 18 | 288 s |
| import, without | 135.0k | 33 | 432 s |
| resume, with skill | 57.3k | 14 | 187 s |
| resume, without | 82.6k | 20 | 140 s |

The skill's measurable difference in these runs was cost and scope. The
baseline wrote a second analysis file, fetched the Gemini link and read
documents elsewhere in the library. On resume it re-read both passages and
all five images, where the run with the skill read the journal alone. The
quality was close for two reasons. First, the baseline read
`docs/architecture.md` §5 and `docs/document.md` after they had been amended
with the skill's rules, so it was not a clean baseline. Second, the user
pointed out that the fixtures are too short to show what the skill is for.
The two passages are two agents' answers to the same question, not a
discussion. The skill's value is compression: a real discussion runs to
hundreds of thousands of tokens, and a resume that re-reads it pays that
every time.

That gap was in the draft itself. It recorded the status of each claim but
not the substance worked out, so writing the document would still have
needed the transcript. The skill gained:
- a **Key points** section, holding the substance by subject: the
  explanation reached, the example chosen, the analogy rejected;
- rejected options kept with their reason under **Decisions**;
- a rule that the journal is sized by the document, not by the conversation,
  and is condensed at each pause;
- the journal's language, which a run had looked for and not found;
- on resume, a comparison of `sources/` with the journal, asking about new
  files rather than opening them.

The suite grew to ten tests.

### 2026-09-25

Measured the user's real discussion from the session transcripts.

- **The discussion session (2026-09-24, about 5 h).** The skill fired unasked
  on the first message. The conversation grew to 104k tokens of context. It
  was later resumed with `--resume`, which replays the whole conversation, so
  that resume does not test the journal. By the end, the journal at
  `electronics/notebook/study/discussion.md` was 300 lines, about 6k tokens.
  It was kept during the session, with three session lines and **Where it
  stands** rewritten. The agent moved the directory from `learning/pratice/`
  to `electronics/notebook/` only after the user authorised it.
- **The fresh-session resume (2026-09-25).** The user opened a new `claude`
  and wrote "on reprend la discussion sur le carnet d'électronique". The skill
  fired unasked. The agent made three tool calls: the skill, a `find` for the
  journal, and a `cat` of the journal and a listing of `sources/`. Context
  at the reply was 45.8k tokens, against a session baseline of 35.4k before
  any work, so the resume cost about 10k tokens (skill and journal) where the
  conversation it replaces held 104k. The reply resumed at the exact point
  where the discussion had stopped, the ring's schematic. It said that
  nothing in `sources/` had changed, and asked nothing that the journal
  already answered.
- **To watch:** in the journal, *An agent's account* runs to about 100 lines
  against about 20 for **Key points**. This did not affect the resume, but a
  longer discussion could make it cost something.

The user then raised three points.

- **The false-trigger check.** Rather than wait to notice a misfire, the user
  wants every session review to check it explicitly. The description task is
  ticked on that basis. The check moves to the new `suite-and-review`
  roadmap, Phase 1.
- **`make test` must not depend on `library/`.** A reading of every test that
  touches `library/` sorted them into three families:
  - A: tests of code that use a real document as an example;
  - B: checks of the user's library itself;
  - C: path constants.

  It also showed that `make test` writes a real EPUB into `out/epub/` for
  every `report` document on each run. The fix went to `suite-and-review`,
  Phase 0: fictional fixture documents for A, and a read-only
  `make check-library` for B.
- **A single journal file cannot last.** Either the agent keeps it small by
  overwriting old points with new ones, and the history is lost, or it grows
  without limit. The user proposed a multi-file conversation architecture:
  an archive directory, files that reference each other so the agent loads
  only what is useful, and a way back to a point raised a month earlier. The
  design agreed on is recorded under Decisions. Five tasks were added to
  this phase, under *The archive* (9 → 14 tasks).

The user asked to settle the first two points before the archive, so this
phase pauses, marked *Blocked By* `suite-and-review`. It resumes with the
archive tasks. The `discussion` skill in the working tree is the single-file
version validated on 2026-09-25.

`suite-and-review` closed the same day, and the user asked to resume. The
block was cleared. `make test` passed on 579 tests before any change.

Read the notebook journal (300 lines) to fit the three layers to a real case
before writing them. Two needs came out of it that the design recorded under
Decisions did not name:
- a resume compares `sources/` with the journal, and the single file did that
  through its session lines. Sessions are no longer read on resume, so the
  index gains a **Material** section: one line per file received;
- 13 of the notebook's 18 open questions are answered, and they stayed in
  the file. The index now keeps only the open ones, and an answered question
  goes to its session's **Answered**.

The notebook also showed where the user's statements go. Its 60 lines of
*What the user said* are mostly about one subject (the equipment, joint A,
the tip routine). So the index keeps only what frames the whole document, and
the rest goes to its topic.

Rewrote `SKILL.md` for the three layers: a table per layer, a section *What
keeps the files from drifting*, a resume that reads `index.md` alone, loads a
topic when the discussion returns to it, and looks in `sessions/` only for an
earlier point. A single-file journal is migrated once the user agrees.
`assets/journal.md` gave way to `index.md`, `topic.md` and `session.md`.

The link check went into `make check-library` (`core/library.py`,
`journals()` and `journal()`, defect kind `journal`), not into the skill. A
journal exists before `document/` does, so it is found on its own rather than
through `documents()`. The check also reports a journal still in one file.
Tested in `tests/test_library.py` (eight tests), on a fictional journal
added to the fixture document `sample/component`, which the fixture library's
clean run now checks too. The skill's suite was rewritten for three
templates: each template's `##` sections must equal the rows of its table in
the skill, and the index must carry no substance (16 tests). Updated
`docs/document.md` (the `study/` tree, the paragraph, the `journal` kind),
`docs/architecture.md` §11 and `README.md`.

`make test`: 593 passed. `make check-library` on the real library reports
one defect, the one expected: `electronics/notebook` still has its journal in
one file. That is the migration task, which waits for the user's agreement.

The user agreed, and the notebook's journal was migrated with the
`discussion` skill loaded. It became an index, six topics and four sessions.
The topics follow the outline: `poste`, `pannes`, `routine-panne`,
`trous-bouches`, `tresse-et-pastilles` and `anneau-round-led-d4017`. The
first proposal named the tips topic `achat-panne`. It became `pannes`,
because the topic also holds the established shapes and the C210-K trial.
The single file dated each point but did not say which of the three sessions
of 2026-09-24 brought it. The three session files are therefore
reconstructed from its session lines, and each one says so. The migration has
its own session file, `2026-09-25.md`.

Three things came out of the migration:
- **The single file had kept a superseded answer beside the one that
  replaced it.** A note said the tip-routine answer "replaces the previous
  answer, too quick", yet the previous one was still there and partly
  contradicted it ("the habit is not wrong"). It now sits in the session's
  **Replaced**, and the topic keeps only the current routine: the case the
  archive was designed for. The two corrected photo readings had lost their
  text, and only their quoted first words survive.
- **The user's notes had changed.** `learning/discussion.md` no longer
  exists: the user merged it into `notebook/discussion.md`, which has two new
  lines, flush-cut leads and "tin between two sessions". Both are recorded
  as said by the user, and the first opens a question, whether the joints
  hold too much solder or only look balled because the leads are cut flush.
  The open question about where that note belongs is closed, from the files
  themselves.
- **A word-level comparison of the old file with the new files** found two
  omissions, "analyser les soudures" and the answered item under *To
  establish*. Both were restored before the old file was deleted.

A resume now reads `index.md`: 131 lines and 6.4 kB, against the single
file's 300 lines, about 6k tokens. The six topics hold 42 to 58 lines each.
`make check-library`: 9 documents, no defect. Each link in the sessions,
which the check does not cover, was verified by hand once. `library/` is
gitignored, so the migration leaves no commit.

---

## Decisions

- **The user's upcoming discussion is the skill's first real case, held here
  with the draft.** A draft written without any real case would be guesswork
  on exactly what matters: how fine-grained the journal is, when it is
  written, what a resume misses. Holding the discussion first without the
  skill would cost the discussion the journal and its resume, for a baseline
  whose failures the pasted excerpts already show. The draft carries only the
  rules that do not depend on a case: where the journal lives, the three
  statuses, resuming from the file. The discussion then takes the place of
  synthetic pressure tests. The phase closes only once its lessons are folded
  into the skill.
- **`skill-creator` frames the work; `writing-skills` lends one idea.**
  `skill-creator` measures what matters most for this skill: its triggering,
  checked against near-miss queries, and the same task run with and without
  the skill, which answers the user's first question — can an agent do it
  alone? `writing-skills` is built for discipline under pressure, which is
  not this skill's failure mode. Its idea kept: an element an agent omits
  becomes a required slot in the template, not a prose reminder. Where either
  plugin's description style conflicts with `docs/architecture.md` §5 — one
  wants "Use when" only, the other a pushy description — the repository's
  rule wins: a phrase no other skill's description carries. The cost is
  bounded: three test cases, each run with and without the skill, and one
  measurement of triggering. The optimisation loop runs only if that
  measurement shows misfires.
- **The live-discussion test case is left to the user's real discussion.** A
  subagent works in a single turn and cannot answer back, so it tests the
  opening of a discussion and nothing after it. The user's soldering
  discussion tests the whole of it, including resumes. Dropping it also
  halves the cost of a relaunch on a session limit that had just been hit.
- **No second iteration on synthetic fixtures, no eval viewer, and triggering
  measured in the real sessions.** The fixtures are too short to exercise
  compression, so another round on them would measure the wrong thing. The
  user's discussion measures it directly: at the resume, the size of the
  journal set against the transcript it replaces. Two acceptance criteria now
  say so. The same sessions test triggering on the two cases that matter,
  opening and resuming, at no extra cost. A `run_eval` pass with three
  repetitions of twenty queries would cost about sixty full `claude -p`
  starts, just after a session limit. It stays available if the real
  sessions show a misfire.
- **The journal becomes a directory, `study/discussion/`, in three layers.**
  Proposed by the user on 2026-09-25 and agreed; to be built under *The
  archive*.
  ```
  study/discussion/
    index.md            the entry, and the only file a resume reads: where it
                        stands, what the user said, decisions, open questions,
                        outline, and a map of topics (one line and a link each)
    topics/<subject>.md the current state of one subject: its key points and
                        claims, and "replaced on … — see sessions/…" for what
                        changed
    sessions/<date>.md  the archive: what each session covered, decided and
                        replaced. Append-only, never rewritten, never read on
                        resume
  ```
  The rules: one fact lives in one place, its current state in its topic
  file. A superseded point is never deleted: it moves to its session's
  archive, with a link both ways. A resume reads `index.md` alone, and a
  topic is loaded only when the discussion returns to it. A point from a
  month earlier is found through index → topic → the session it came from,
  or by a text search of `sessions/`. The risk is the files drifting apart.
  "One fact, one place", links that must exist, and a test that every link
  resolves are what hold that risk. Why the single file cannot stay: kept
  small, it overwrites history; kept whole, it grows with the conversation
  instead of with the document.
- **The link check lives in `make check-library`, not in the skill.** A test
  on a fixture proves the rule once. The check on the user's journals proves
  it every time it is run, and `core/library.py` is already the read-only
  reader of the user's library (`docs/architecture.md` §2). The skill still
  ships no script. Sessions are not checked: they are never rewritten, so a
  link in one records the day it was written. That is why a topic's file name
  is permanent.
- **Three additions to the design agreed on 2026-09-25**, all taken from the
  notebook journal. The index gains **Material**, because a resume must still
  tell new files in `sources/` apart without reading the sessions. It keeps
  only the open questions and pending claims, and the closed ones go to the
  session's **Answered** or to the topic's **Established**. What the user
  said is split: the index keeps what frames the whole document, and a topic
  holds the rest. A second session on the same day is `<date>-2.md`.
- **The skill has no `conftest.py`.** A skill's conftest only puts its
  `scripts/` on the import path, and this skill has none. The suite reads
  files and imports nothing of its own.

---

## Files Changed

---

## Problems And Deviations

- **`make test` is red, for reasons outside this phase: 18 failures and 5
  errors, all tied to the state of `library/`, none to the skill or the
  documentation.** The failures:
  - `tests/test_layout.py` and some of the EPUB tests read
    `library/electronique/…`, a path the library no longer has now that the
    topic is `electronics/`;
  - `tests/test_anatomy.py` reports the four subdirectories of
    `electronics/repair/electribe-2/sources/`;
  - the whole-library EPUB tests stop on malformed XHTML in
    `maialen/euskara`.

  The skill's own suite and `tests/test_documentation.py` pass. The contract
  runs `make test` at every closure, so this phase cannot close until it is
  green. Moved on 2026-09-25 to the `suite-and-review` roadmap, Phase 0.
- **The process departed from `skill-creator`** in three ways: no eval
  viewer, no second iteration, and no triggering measurement before the real
  sessions. The reasons are under Decisions.

---

## Changes To Later Phases

- `phase-1-discussion-pilot.md`: the two transistor excerpts are now described
  as two agents' answers to the same question, as the user specified, rather
  than as two separate conversations. No task changed.

---

## Assessment
