# Roadmap: Local Translation

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
Phase 0  Verify and Benchmark       🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 1  The Local Engine           🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 2  Cross-Check in Practice    🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                  ░░░░░░░░░░░░░░░░░░░░   0%  (0/18)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — Verify and Benchmark

---

## Why This Roadmap Exists

The `translate` skill has one working engine: the agent, translating each chunk
itself. A document of this library can therefore only be translated with an
agent session, and nothing checks one translation against another.

The repo-overhaul roadmap, Phase 7, built the seam for a second engine running
on this machine — the contract, the chunking, the protected zones, the quality
checks and the cross-check — and deliberately stopped there. This roadmap fills
the seam: a local translation model behind the `local` engine, chosen on
measurements rather than on model cards, and used as the cross-check the skill
already knows how to run.

---

## Decisions Taken At Opening

**The contract is fixed; the engine adapts to it.** `engines.py`'s docstring is
the interface. If a model cannot honour it — placeholders, context — the
engine wraps the model until it does; the contract is not loosened to fit.

**Measure before choosing.** MADLAD-400 10B-MT, its 7B variant and NLLB-200
3.3B are the candidates, the first and the last recorded in
`docs/local-translation.md`. None is chosen until Phase 0 has measured them on
this library's documents, placeholders included. The 7B is in the benchmark
because a 24 GB card has to hold the model and its context at once, and a
quantised 10B leaves little room for either.

**`make test` stays offline and GPU-free.** The engine is tested against a stub
of its runtime; a run against the real model is a documented manual check.

---

## Deliberately Out Of Scope

- Changing the engine contract, the chunking or the quality checks, except to
  fix a defect a real run exposes.
- Translating files that are not documents of this library: subtitles, office
  documents.
- Fine-tuning or training a model.
- Any installation procedure for another operating system than the one the
  library lives on.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [Verify and Benchmark](phase-0-verify-and-benchmark.md) | 6 | 🔴 Not Started |
| 1 | [The Local Engine](phase-1-local-engine.md) | 7 | 🔴 Not Started |
| 2 | [Cross-Check in Practice](phase-2-cross-check.md) | 5 | 🔴 Not Started |

---

## Dependencies

- The `translate` skill, as delivered by repo-overhaul Phase 7.
- A GPU with about 24 GB of VRAM, the machine the notes were written for.

---

## Related Documentation

- [`docs/local-translation.md`](../../../local-translation.md) — the target engines and what an engine must do.
- `.claude/skills/translate/scripts/engines.py` — the contract, in its docstring.
- `.claude/skills/translate/SKILL.md` — the procedure the engine plugs into.

---

## Metadata

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/local-translation/`
**Version:** 1.0.1
**Created:** 2026-09-16
**Last Updated:** 2026-09-18

---

## Changelog

### 1.0.1 (2026-09-18)

*Decisions Taken At Opening* named two candidates where Phase 0 scores three.
MADLAD-400 7B is now named there too, with the reason it is in the benchmark.
No task changed.

### 1.0.0 (2026-09-16)

Roadmap created by repo-overhaul Phase 7, three phases, 18 tasks: verify the
recorded figures and benchmark the candidates, including whether placeholders
survive; implement the `local` engine against the existing contract; then use
it as the two-engine cross-check on real documents.

The five opening questions were answered from the decisions and notes of
repo-overhaul Phase 7 rather than asked, because this roadmap is that phase's
recorded hand-over. They are open to amendment before Phase 0 starts.
