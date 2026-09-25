# Phase 0: The Manifest

---

## Status

**Current Status:** 🔴 Not Started (0% — 0/12)
**Started:** {{START_DATE}}
**Completed:** {{COMPLETION_DATE}}
**Blocked By:** —

---

## While Working

Keep `phase-0-manifest-report.md` current as the work happens — after each
significant step, and before every commit, pause, or end of session.

---

## Objective

Give every directory of the library a manifest that the tool keeps in step
with the disk, and make `make check-library` hold the library to it. This
phase runs on the fixture library only: the user's library gets its
manifests in Phase 3.

---

## Overview

### Why This Phase Matters
Everything later reads the manifests: the navigation of Phase 1, the skill of
Phase 2, the discussion of Phase 4. What they hold, who writes each part, and
how they stay true to the disk are settled here, once. A manifest that drifts
from its directory is worse than none. It would say, with authority, what is
no longer there.

### What It Enables
Phase 1 answers questions from the manifests. Phase 3 writes them for the
user's library with `sync` and `describe`. From this phase on, `make
check-library` reports a manifest that has drifted, an id that leads nowhere,
and a citation placed where it does not belong.

### Out of Scope
The navigation commands (Phase 1). `unused`, `remove` and `rename` (Phase 2).
Any write into the user's `library/` (Phase 3).

---

## Tasks

### The format
- [ ] Write the manifest's reading, writing and validation in the core: `manifest.yaml` with `id`, `name`, `description` and `items`, each item with `id`, `name`, `description`, `path`, `kind`, and a source's `sha256`
- [ ] Tell a topic from an entry by what its directory holds, and compute an entry's default items: one per direct child of each role and one per file at its root, `.work/` and the manifest itself excluded
- [ ] Resolve the item that covers a file by the longest matching path, so that an item naming one file inside a covered directory takes that file out of it
- [ ] Generate ids: the prefix the agent gives (lowercase ASCII words joined by hyphens), a hyphen, and 8 characters the tool draws from an alphabet without `0`, `o`, `1`, `l` or `i`, unique across the library
- [ ] Name and describe the anatomy's standard files from the tool: `document/index.md`, `cover.md`, `theme.css`, `study/extracted.md`, `meta.json`, `NOTES.md`, `discussion/`, `translate/`, `glossary.yaml`

### Writing
- [ ] Write `sync`, for one entry or the whole library: create the missing manifests, add the uncovered files as items to describe, follow a renamed source by its digest, flag a vanished or changed source — a second run changes nothing, and no run touches a name or a description
- [ ] Write `describe`: set the name and description of a topic, an entry or an item, creating its id at the first naming
- [ ] Make `.claude/hooks/protect-paths.sh` refuse a direct edit of a manifest under `library/`, pointing at the tool

### The check
- [ ] Extend `make check-library` with the defects: a directory without a manifest or with an unreadable one, a malformed or duplicate id, a topic or entry without a name or a description, two items for one path, an item whose path is gone, an `id:` citation that leads nowhere or sits in `document/`
- [ ] Add to its report, without failing on them, the counts of what remains to do: uncovered files, items to describe, sources changed since they were described
- [ ] Give the fixture library its manifests, and one fixture per defect the check must catch

### Documentation
- [ ] Document the manifest, the ids and the `id:` citations in `docs/document.md`, and record them in `docs/architecture.md`: §11 (the manifest at an entry's root, the topics above it), §2 (the catalogue in the core), the glossary

---

## Technical Details

### Files to Modify
```
core/catalogue.py                        new: the manifest, ids, sync, describe — split if it grows
core/library.py                          the new checks and counts
tests/test_catalogue.py                  new
tests/test_library.py                    the new checks
tests/fixtures/library/                  a manifest in every directory, and the defect fixtures
.claude/hooks/protect-paths.sh           refuse a direct edit of a manifest
docs/document.md                         the manifest, ids, citations
docs/architecture.md                     §2, §11, the glossary
```

### Dependencies
None.

### Constraints
- Nothing is written into the user's `library/`: the suite runs on the
  fixture library, per `CLAUDE.md`.
- `make check-library` stays read-only. Writing is `sync` and `describe`.
- The tool never writes a name or a description it was not given, except for
  the anatomy's standard files.
- `sync` reads a source only to compute its digest, and never changes it.

---

## Acceptance Criteria

- [ ] `make test` passes
- [ ] On the fixture library, `make check-library` reports no defect, and reports each defect fixture against the entry it concerns
- [ ] `sync` run a second time changes nothing
- [ ] A source renamed on disk keeps its id, name and description after `sync`
- [ ] A direct edit of a manifest under `library/` is refused by the hook
