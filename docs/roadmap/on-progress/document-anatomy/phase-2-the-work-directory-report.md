# Phase 2 Report: Everything Disposable, In One Place

**Phase:** [phase-2-the-work-directory.md](phase-2-the-work-directory.md)
**Start Commit:** d267827

---

## Work Log

### 2026-09-19

Phase opened. Phase 1's file and report were read in full: 7/7 tasks, 5/5
acceptance criteria, and the document count corrected from twelve to eight in
this phase's siblings. No restructuring pending.

What this phase inherits:

- **`doc_dir()` is in `core/doc.py` and `work_dir()` belongs beside it**, built
  the same way, so that `make clean` deletes by asking the layout rather than by
  matching a glob written at the call site.
- **`review.py`'s staleness check already walks `document/` only.** That was
  changed in Phase 1 for this phase's sake: once `.work/` sits inside the
  document, a review writing its own sheets there would otherwise make every PDF
  look stale forever.
- **The comparison harness is throwaway code in the session's scratchpad**, and
  it is what found both of Phase 1's silent failures. This phase moves large
  outputs and will want it again, so rebuilding it is the first task rather than
  an afterthought.

**The before state was built first, and in full.** Every document's review was
run in both variants, then `make preview` and `make preview-style`, and each
file was fingerprinted by content: 96 review files, 115 preview files. The
existing `out/review` was stale — some of it a fortnight old — and comparing
against it would have attributed old differences to this phase.

**`work_dir()`, `work_dirs()` and `clean()` went into `core/doc.py`**, with the
tests written first. The one that matters is not the happy path: a `.work`
directory a user keeps inside their own `sources/` must never be swept.
`work_dirs()` therefore reads the document roots and asks each one whether it
has a `.work/`, rather than globbing the library for the name. A glob would have
been shorter and would have deleted user content the first time someone named a
folder that way.

`make clean` calls `core.doc.clean()` and passes `DOC` through. The `Makefile`
holds no pattern: what may be removed is decided where the layout is stated.

**Then the move, and the comparison.** `review.py` and `preview.py` each changed
one line. Regenerated: 211 files under eight `.work/` directories, and the
comparison came out at 96 and 115 files, zero missing, zero extra, zero changed.
Unlike Phase 1, nothing was silently broken — the outputs are images and their
paths, and neither depends on where the document sits.

**`make clean` was then verified live, not only on a fixture.** One document
first: `make clean DOC=exemples/guide-de-style` removed that `.work/` and left
the other seven and `out/` alone. Then the full clean: seven `.work/` and `out/`
removed, and the library's 221 other files compared against a snapshot taken
just before — nothing lost, nothing changed, nothing added.

After a rebuild, `out/` holds `pdf/` and `epub/`. That is the phase in one line.

`make test`: 498 passed, up from 493 — five tests for the layout and the clean.

---

## Decisions

- **A translation workspace is durable and leaves this phase.** The user asked
  whether it belonged in `.work/` at all: translate half a hundred-page document,
  run `make clean`, lose everything. The anatomy's own rule answers it — jetable
  means a command can make it again *and* nothing is lost by making it later —
  and an engine's answers fail both halves. Re-running produces *a* translation,
  not *the* one under way, and for the `agent` engine the answers are an agent's
  own writing, file by file.

  `translate.py`'s docstring already admitted the loss — "a translation not yet
  applied is lost with it" — which made it documented behaviour rather than a
  decision. Moving it into `.work/` would have made it worse, not better: a
  `make clean` that reaches inside documents is run more readily than one that
  only empties `out/`.

  The move goes to Phase 3, which owns `study/`, together with a question this
  raised and nothing answers today: a workspace is *spent* once `apply` has run,
  and nothing retires it.

---

## Files Changed

**Added**

- `docs/roadmap/on-progress/document-anatomy/phase-2-the-work-directory-report.md`

**Modified**

- `core/doc.py`
- `Makefile`
- `docs/architecture.md`
- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/epub/scripts/preview.py`
- `.claude/skills/epub/SKILL.md`
- `tests/test_doc.py`
- `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/on-progress/document-anatomy/phase-2-the-work-directory.md`
- `docs/roadmap/on-progress/document-anatomy/phase-3-sources-study-generators.md`

`phase-3-sources-study-generators.md` is the task that left this phase, moved
mid-phase and committed then, in `9e853dc`.

`library/` is user content, outside git: the 211 files that moved into eight
`.work/` directories appear in no listing, and the comparison above is their
record.

---

## Problems And Deviations

- **A task left this phase for Phase 3, on the user's observation.** The
  translation workspace was to move to `.work/`; it is durable and moves to
  `study/` instead. The reasoning is under `## Decisions`, and the change was
  made before any work started on it. Phase 2 went from six tasks to five,
  Phase 3 from seven to eight.

- **`docs/architecture.md` §8 said `clean` was unchanged**, which stopped being
  true here: it takes a `DOC=` and it deletes inside `library/`. A revision note
  in the document's own idiom says so and points at §11. Phase 5 decides whether
  §8's table is rewritten.

- **`## Files Changed` was first computed from the wrong commit.** This phase
  has a mid-phase commit — `9e853dc`, the translation workspace leaving for
  Phase 3 — and the list was taken from it rather than from the recorded start
  commit `d267827`, which hid that commit's own changes. Caught by the closure
  audit. The section is the diff from the start commit, entirely, or it is not
  auditable at all.

- **The existing `out/review` was stale and was not used as the before state.**
  Some of it predated the library's last edits by a fortnight. Everything was
  regenerated first, which is why the comparison is worth anything.

All five tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

- `phase-3-sources-study-generators.md`: gained the task of moving the
  translation workspace to `study/translate/`, and with it a question nothing
  answers today — a workspace is spent once `apply` has run, and nothing retires
  it. Recorded before this phase's work began, not at its closure.

---

## Assessment
The phase was the easy one and it is worth saying why, because the reason is
structural rather than luck. Phase 1 moved what the build reads, so everything
downstream of it could break silently — and did, twice. This phase moved what
nothing reads: review sheets and contact sheets are looked at by a person and by
no code, so the only way to get it wrong is to lose a file, and a comparison
catches that immediately.

The part that needed care was not the move but `make clean`. It is the first
command in this repository that deletes inside `library/`, which is user content
and is not versioned, and the temptation was a two-line `find library -name
.work -exec rm -rf`. That would have worked for years and then deleted somebody's
notes the first time they named a folder `.work` inside their own `sources/`.
The rule that `sources/` is theirs is worth exactly as much as the code that
refuses to walk into it, which is why `work_dirs()` asks the document roots
instead of the filesystem.

What Phase 3 needs to know first: it is the phase that finally makes `sources/`
mean what the anatomy says, and it has three movements, not one. The derivations
of `ingest.py` and `fetch.py` leave for `study/`, the sourcing journal joins
them, `figures.py` goes to `generators/`, and the translation workspace arrives
from Phase 2. Its stop condition is the one Phase 0 wrote down and nobody has
tested: `extracted.md` is placed in `study/` on the argument that its
re-derivation is deterministic, and if that turns out to be false for either
script the phase stops and says so rather than moving a file somewhere it can be
silently destroyed. Verify it before moving anything — the migration is cheap to
redo, a wrong premise written into the anatomy is not.
