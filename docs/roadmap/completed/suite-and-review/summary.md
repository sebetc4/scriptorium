# Summary — Suite and Review

---

## Where We Started

The roadmap was split out of Phase 0 of discussion-and-illustration, which had
hit two problems it could not solve inside its own scope.

The first was that `make test` depended on the user's library. A rename of a
topic by the user turned the suite red, with 18 failures and 5 errors caused
by no code. Every roadmap closure runs `make test`, so every phase in the
repository was blocked. The suite also wrote a real EPUB into `out/` for each
`report` document on every run.

The second was that nothing checked whether a skill fires when it should. The
`discussion` skill had been seen to fire at the opening and at the resume of a
discussion, but nothing measured whether it stayed silent on an ordinary
exchange, and no other skill's triggering was measured at all. The user chose
to have the session reviews check it, then asked to use the same roadmap to
improve the triggering of every skill.

---

## Where We Landed

`make test` depends on the repository alone. It reads fictional documents
versioned under `tests/fixtures/library/`, through a temporary copy, and
writes nothing under `out/` or `library/`. It passes on a checkout with no
`library/` at all. The user's library is checked on request by a read-only
`make check-library`, which reports no defect today: at the user's request,
the documents it had flagged were repaired, and the style guide moved out of
the library to `brand/style-guide/`.

Every session review now accounts for the skills its task loaded. It reads
them from the transcript's `Skill` calls, says what each brought, and asks
whether a job ran without the skill that covers it. Either failure is a
`trigger` finding against the description at fault.

Every one of the seven skills' descriptions passes the trigger check of
`docs/architecture.md` §5, and `tests/test_triggers.py` holds it there: a
phrase no other description carries, and the neighbours each must name. A
skill added later fails the test until it has its row. The suite has grown
from 546 tests to 579.

---

## What Each Phase Delivered

**Phase 0 — A Suite Independent of the Library.** It moved every test that
read `library/` onto two fixture documents, and the checks that were really
about the user's library into `make check-library`, in `core/library.py`. The
phase found more coupling than the failures had shown:
- three tests read the whole library without ever failing;
- four scripts printed paths in a form that breaks outside the repository;
- an unanchored ignore rule would have hidden the fixtures.

The proof was a checkout with no library: 546 tests passed and nothing was
written.

**Phase 1 — Skill Triggers in the Session Review.** It added a fifth printed
obligation to `session-review`, a `loaded:` measure, and the `trigger`
finding kind. Running the tool on the 15 real transcripts showed two defects
the fixtures could not: the 50-line cap was cutting the obligations off the
end of the output, and `corpus.py` refused a review of a discussion. Both
were fixed. Before its own tasks, and at the user's request, the phase
repaired `maialen/euskara` and `electribe-2` and moved the style guide.

**Phase 2 — A Trigger Audit of Every Skill.** It audited the seven
descriptions against §5 and against each other, using the loads read from the
transcripts. One real misfire came out: a repair reported by
`make check-library` was done without `pdf`, whose description had no verb
for fixing. The fix, and two overlaps found by the audit, became one clause
each in `pdf`, `fetch` and `session-review`. The phase also wrote the
repository-level test and gave §5 its seven rows.

---

## What We Learned

- **A test that reads user content cannot fail for the right reason.** Its
  failures follow the user's reorganisations, and its passes hide coupling:
  three whole-library tests here had never failed once. Fixtures carry the
  defects their check must catch, with exact counts, so that the fixture
  cannot drift into merely passing.
- **Run the instrument on real data before calling it done.** Both defects
  Phase 1 found were invisible on the fixtures and obvious on the first real
  transcript that was long enough.
- **Read what the harness writes before choosing a measure.**
  `attributionSkill` looked like "the skills loaded" and was "the last skill
  loaded, on every later turn". Only the `Skill` tool call is a load.
- **A discriminating phrase counts only where it is said positively.** Two of
  the audit's apparent overlaps were one skill's negative clause naming its
  neighbour's job. A uniqueness test has to choose phrases from the positive
  half of each description.
- **Misfires come from how a request is worded, not from what the job is.**
  The one misfire found was a document repair framed as "fix what the check
  reports": the job was `pdf`'s, but the wording matched none of its verbs.
  The descriptions are now tested against overlaps met in real requests, and
  the reviews are where the next ones will be met.

---

## What We Are Leaving Open

- **The third case of `discussion`**, that it never fires on an ordinary
  exchange, rests on two sessions. The reviews will add to it, since each
  must now account for every skill loaded.
- **The phrase test is lexical.** It proves that phrases are unique, not that
  a session will read them as intended; only the reviews measure that.
- **The style guide's three review findings** (a straight apostrophe, an
  arrow in a fallback font, a loose line) predate its move and are the user's
  call.
- **Whether `electribe-2`'s pasted conversation becomes a source**, with a
  real document written through `discussion`, is the user's decision.
- **The discussion-and-illustration roadmap**, which waited on this one's
  Phase 1, can resume. Its archive architecture was never in this roadmap's
  scope.
