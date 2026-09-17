# Phase 1: The Local Engine

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/7)
**Started:**
**Completed:**
**Blocked By:** —

---

## Before Starting This Phase

> Read the previous phase in full before touching anything here: its notes,
> its unchecked tasks, and its unmet acceptance criteria. Skip this section
> only for the roadmap's first phase, which has no predecessor.

**Read First:**
1. The previous phase's `## Notes` section — what it found, decided, and
   left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Replace the `local` engine's `EngineUnavailable` with an engine that translates
through the model Phase 0 chose, honours the contract in `engines.py`, and goes
through the same runner and checks as the `agent` engine.

---

## Overview

### Why This Phase Matters
The seam exists and is tested; what is missing is the one class behind it.
Everything around it — chunking, zones, checks, apply — is already there to
catch what the model gets wrong.

### What It Enables
A document can be translated without an agent session, and Phase 2 can run the
two-engine cross-check.

### Out of Scope
The cross-check itself, and any change to the contract.

---

## Tasks

### The engine
- [ ] Implement `LocalEngine.translate` against the runtime chosen in Phase 0
- [ ] Apply the placeholder strategy measured in Phase 0, restoring `⟦n⟧` before returning
- [ ] Carry `context_before` and `previous_translation` to the model, and cut their translation back out of its output
- [ ] Pass the glossary and the terms to keep, as far as the model allows, and let `qc.py` catch the rest

### Tests and setup
- [ ] Test the engine against a stub of the runtime, so `make test` stays offline and GPU-free
- [ ] Say clearly when the runtime or the model is missing, with the commands that install them
- [ ] Update the `translate` skill and `docs/local-translation.md` with the engine's state and its limits

---

## Technical Details

### Files to Modify
```
.claude/skills/translate/scripts/engines.py   LocalEngine
.claude/skills/translate/tests/               the engine's suite
.claude/skills/translate/SKILL.md             the engines table
docs/local-translation.md
```

### Dependencies
Phase 0's choice of runtime, model and placeholder strategy.

### Constraints
- The contract in `engines.py` is not loosened to fit the model.
- A GPU dependency, if one is needed, is optional and documented, never required by `make setup`.

---

## Acceptance Criteria

- [ ] `translate.py run <doc> --engine local` translates a real document end to end
- [ ] Its answers pass the same placeholder validation as the agent's
- [ ] `make test` is green without a GPU and without network
- [ ] A missing runtime or model gives a clear message, not a traceback

---

## Notes

