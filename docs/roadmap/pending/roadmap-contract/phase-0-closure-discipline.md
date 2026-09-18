# Phase 0: What A Closure Must Not Rediscover

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/4)
**Started:**
**Completed:**
**Blocked By:** —

---

## Before Starting This Phase

This is the first phase. Read this roadmap's `README.md`, and the four phase
reports of `docs/roadmap/*/session-review/`, where the same defect is recorded
four times with its audit verdict.

---

## Objective

Write into this repository's roadmap contract the two facts that four
consecutive closures each had to be told by an auditor.

---

## Overview

### Why This Phase Matters
Four phases closed in this repository on 2026-09-18. The `roadmap-auditor`
returned `FAIL` on three of them and all three failures were the same section —
`## Files Changed` disagreeing with `git diff` from the phase's start commit.
The cause was found only on the third: a phase is opened during the previous
phase's closure, **before that closure is committed**, so `git rev-parse HEAD`
at that moment is one phase behind and the diff sweeps in the previous phase's
work.

It is written down in one phase report, where the next roadmap in this
repository will not look for it. The contract in `CLAUDE.md` is where a person
opening a phase actually reads.

### What It Enables
A closure that passes its audit the first time.

### Out of Scope
The `roadmap` skill itself. It is installed outside this repository and is
replaced on update, exactly like `diagram-design`. What this repository can
state, it states in its own contract.

---

## Tasks

- [ ] Add to `CLAUDE.md`'s `## Roadmaps` block: a phase's start commit is the commit that closed the phase before it
- [ ] Add: `## Files Changed` is computed at closure from `git diff -M --name-status <start commit>` and `git ls-files --others --exclude-standard`, never from memory, and includes the files that opening the next phase changes
- [ ] Check that both additions survive `test_claude_md_carries_the_roadmap_contract`, and extend that test if the contract grows a field
- [ ] Record in the report whether the next closure in this repository passed its audit on the first run

---

## Technical Details

### Files to Modify
```
CLAUDE.md                     the ## Roadmaps block
tests/test_documentation.py   if the contract grows a field the test should pin
```

### Dependencies
None.

### Constraints
`CLAUDE.md` is read at the start of every session in this repository: the
addition is two lines, not a section. The contract's three required keys and
their format are the `roadmap` skill's, not this repository's, and are not
touched.

---

## Acceptance Criteria

- [ ] Both facts are in `CLAUDE.md`, inside the `## Roadmaps` block
- [ ] `make test` passes
- [ ] The next phase closed in this repository passes its audit on the first run, or the report says what it failed on instead

---

## Notes
