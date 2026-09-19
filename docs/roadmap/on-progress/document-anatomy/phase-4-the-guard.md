# Phase 4: Keeping It True

---

## Status

**Current Status:** 🟢 Done (100% — 5/5)
**Started:** 2026-09-19
**Completed:** 2026-09-20
**Blocked By:** —

---

## Before Starting This Phase

**Read First:**
1. Phase 3's `## Notes` — what it found, decided, and left open.
2. Any tasks that stayed unchecked, and why.
3. Any acceptance criteria that were not actually met.

---

## Objective

Make a violation of the anatomy fail loudly, instead of accumulating quietly
until someone writes a roadmap about it.

---

## Overview

### Why This Phase Matters
A convention with no enforcement holds until the next script is written. This
repository has already proved that twice over: `sources/` became a miscellany
one script at a time, and a figure generator sat in it for weeks because nothing
could say it should not.

The four phases before this one leave the library correct. Nothing yet keeps it
that way.

### What It Enables
A new skill written in six months that cannot quietly reintroduce the problem.

### Out of Scope
Any further reorganisation. If this phase finds a file the anatomy does not
place, that is a finding about the anatomy and it goes to `## Notes` — it is not
fixed by widening a definition.

---

## Tasks

- [x] Add the test that fails when a document directory holds anything the anatomy does not place, naming the file and the document
- [x] Add `sources/` to what `protect-paths.sh` guards, so a tool writing a derived file into it is refused at the hook
- [x] Check the guard does not refuse acquisition — `make import` and `make fetch` must still be able to put received material there
- [x] Rebuild the whole library one last time and confirm every output matches what Phase 1 recorded
- [x] Record in the report every file that needed a hand across the four phases, since documents written before the anatomy will not all have fitted it

---

## Technical Details

### Files to Modify
```
tests/                          the anatomy test
.claude/hooks/protect-paths.sh  sources/ added to what it guards
```

### Dependencies
Phases 0 to 3. This phase decides nothing; it defends decisions already taken.

### Constraints
The guard must distinguish acquisition from derivation, which is a distinction
about *which tool is writing*, not about the path. `protect-paths.sh` sees the
tool call and can make it; a test reading the filesystem afterwards cannot.

The anatomy test reads `library/`, which on a fresh clone is empty or absent.
It skips rather than fails there, like the rest of the suite that reads
documents kept outside the repository.

---

## Acceptance Criteria

- [x] A stray file in a document directory fails the test, by name
- [x] A script writing a derived file into `sources/` is refused by the hook
- [x] `make import` and `make fetch` still work end to end
- [x] The test skips on a fresh clone rather than failing
- [x] `make test` passes

---

## Notes
