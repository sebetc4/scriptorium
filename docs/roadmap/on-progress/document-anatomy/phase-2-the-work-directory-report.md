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

---

## Problems And Deviations

---

## Changes To Later Phases

---

## Assessment
