# Phase 1 Report: The Measurement

**Phase:** [phase-1-measurement.md](phase-1-measurement.md)
**Start Commit:** d6014e1

---

## Work Log

### 2026-09-18

Phase opened. Phase 0's file and report were read in full: the format, the
finding vocabulary and `corpus.py` are settled, all five tasks done, five
acceptance criteria met, no restructuring pending.

What this phase inherited from it: `metrics.py` emits the `measured:` block and
nothing else, and **omits** any measure whose record shape it could not confirm
rather than writing a zero — `corpus.py` drops a review with a missing key from
a median's sample, so a zero written out of politeness corrupts every baseline
computed afterwards.

The phase opened during Phase 0's closure, before that work was committed, so
the report was created with `f22aab0` as its start commit — HEAD at that
instant, but a baseline that makes every file of Phase 0 look like a change of
this one. It is corrected above to `d6014e1`, the commit that closed Phase 0,
which is the baseline of this phase's own work.

**The transcript layout, read before writing anything.** Four probes, each
against this project's own sessions rather than against documentation: the
record types and the shape of an assistant record; `message.usage`; the
subagents directory and its `.meta.json`; and where an image actually sits.
Three findings came out of it and all three shaped the script.

The first is the one the rest of the phase turns on. **One assistant message is
written as one record per content block, and every one of those records repeats
the whole `usage` object.** Eighty-nine assistant records in this session
carried fifty-four distinct `requestId`s, and the duplicates shared their
`message.id` and their usage to the token. Any sum over records therefore
multiplies every token figure by however many blocks the model happened to
emit. Usage is deduplicated by `message.id`; content blocks are not, because
they really are distinct — a message with a thinking block and a tool call is
two records but one API call and one tool call.

The second: an image never appeared in `message.content` in this corpus. All
eleven images of the reference session sit in the `toolUseResult` of a user
record, as `{"type": "image", "file": {...}}`. Counting image blocks in
`message.content` alone would have reported zero.

The third: the permission-denial shape could not be confirmed. None of the
candidate markers appears in any transcript of this project, while
`isApiErrorMessage` does and `[Request interrupted by user]` does. So
interruptions and API errors are always emitted, a genuine zero included, and
`denials` is emitted only when something matched — the degradation the phase
asked for, made concrete.

**Then the script, then the disagreement.** Run against the reference session,
`metrics.py` reproduced two of the four figures recorded in the phase file —
eleven images, four delegated passes — and contradicted the other two. The
phase's own instruction is that a disagreement is resolved and not overwritten,
so it was resolved, and the table was wrong:

- Cache reads, four passes: the script reads 288,210. Summing the same field
  over records gives **727,020** — the figure in the table, to the token.
- Fresh tokens: the script reads 91,911. Per-record input plus cache creation
  is 180,096, plus 16,482 of per-record output gives **196,578** — the figure
  in the table, to the token. Output tokens had been counted as context.

Both reproduce exactly, which is what makes this a resolution rather than a
suspicion. The main context's figures were verified the same way, by hand with
`jq`, and the script agrees with them to the token: 46 API calls, 154,333
fresh, 5,443,404 cache reads.

The measured figures then replaced the wrong ones everywhere they had been
repeated: the phase file's table, which keeps both columns and the arithmetic
that explains the gap; the roadmap's README, whose opening argument cited them;
`references/format.md`, whose complete example is now the real output of the
script rather than an illustration; and the Phase 0 fixture, which had
enshrined 196,578 in an assertion.

**`output` was added to the `tokens:` block**, which Phase 1's task list did not
ask for. It is how the wrong figure was built, `thinking` was already recorded
and is a subset of it, and a block that reports thinking without reporting
output invites exactly the confusion that produced 196,578.

The suite came to 22 tests on transcripts built line by line, including a
`Transcript` helper that writes one record per content block so that the
deduplication trap is reproduced rather than described. `make test`: 440 passed.

---

## Decisions

- **Usage is deduplicated by `message.id`, content blocks are not.** This is the
  single most consequential line in the script. Anything later that reads a
  transcript — the ledger hook of Phase 3, `aggregate.py` in Phase 4 — goes
  through `metrics.scan()` rather than summing usage itself.

- **`denials` is emitted only when something matched; `interruptions` and
  `api_errors` always are.** The rule is the shape's provenance, not the
  counter's value: a shape confirmed on this corpus may legitimately report
  zero, a shape never observed may not. Phase 3 inherits the same rule for the
  ledger.

- **The reference figures of the phase file were wrong and the table keeps
  both columns.** Phase 4 re-reviews this session with the real tooling and
  compares against the hand-written review; it now has two wrong counts to
  compare against, not one, and the arithmetic of each is written down.

- **`output` joins the `tokens:` block.** The format changed while the corpus
  was still empty, so no migration and no `review: 2`. This is the last such
  change that is free.

- **Medians are printed apart from the block, as a comparison table with the
  ratio.** Phase 0 settled that medians are never stored; a comment inside the
  YAML would be pasted into the review and would become storage by habit. The
  table also gives Phase 2 what its obligation actually needs — the ratio, and
  a marker on anything past 1.5× — rather than a median to divide by hand.

- **A ledger entry is keyed by transcript and carries the byte size it was
  computed from.** `--ledger` ignores the review cursor and reads the whole
  transcript. Phase 3's re-sweep decision is `size on disk != size recorded`,
  and it needs nothing else.

- **The timeline is the only way prompt text leaves the script**, truncated to
  sixty characters a line, and it is off by default.

---

## Files Changed

**Added**

- `.claude/skills/session-review/scripts/metrics.py`
- `.claude/skills/session-review/tests/test_metrics.py`

**Modified**

- `.claude/skills/session-review/references/format.md`
- `.claude/skills/session-review/tests/fixtures/2026-09-17-4c7bb3d0-round-led.md`
- `.claude/skills/session-review/tests/test_corpus.py`
- `docs/roadmap/on-progress/session-review/README.md`
- `docs/roadmap/on-progress/session-review/phase-1-measurement.md`
- `docs/roadmap/on-progress/session-review/phase-1-measurement-report.md`

---

## Problems And Deviations

- **The acceptance criterion "the script reports the figures recorded under
  *The Reference Transcript*" is not ticked, and will not be.** Two of its four
  figures were wrong, the script is right, and both wrong figures were
  reproduced exactly from the transcript by the method that produced them. The
  criterion is left unticked rather than declared met against a corrected
  table: ticking it would claim an agreement that does not exist. The table now
  carries a measured column and the arithmetic of the gap.

- **The roadmap's README repeated the same two figures in its opening
  argument.** Corrected in place, with the correction stated rather than
  silently applied, since the paragraph's subject is a session that counted
  wrong.

- **`output:` was added to the format's `tokens:` block**, which no task asked
  for. Justified above; free because the corpus is empty.

- **The report's start commit was corrected** from `f22aab0` to `d6014e1`, for
  the reason given in the Work Log.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 2's
obligation on measures past 1.5× the median is already served by the comparison
table `metrics.py` prints, and Phase 3's re-sweep test is already served by the
`bytes` field of `--ledger`.

---

## Assessment

The instrument exists and it is worth more than the thing it replaces. Its first
run contradicted the roadmap that commissioned it, on the roadmap's own headline
example, and the contradiction held: both wrong figures were reproduced from the
transcript by the arithmetic that had produced them.

That is the phase's real result. The roadmap was written to stop a session
inventing numbers; it turned out that the session which wrote the roadmap had
also miscounted the same transcript, by a different route, while believing it
was reading rather than estimating. Nothing short of a script would have found
it.

What Phase 2 needs to know first: `metrics.py` prints two things, and the skill
must pay for both out of its eight thousand tokens. The `measured:` block runs
to 38 lines on the reference session and goes into the review as it stands; the
comparison table beneath it is for the session to read, not to store, and
already marks every measure past 1.5× its median with `← over 1.5×`, which is
the obligation's trigger, ready-made. `--timeline` is off by default and adds
one line per tool call — on the reference session that is more than a hundred
lines, so the skill names it as optional and does not spend its budget on it.
The corpus is still empty, so the first reviews will print "no baseline yet":
the skill needs a rule for that case, because an obligation that cannot fire is
not a lenient obligation, it is an absent one.
