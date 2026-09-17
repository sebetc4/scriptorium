# Phase 2: Skill Layout and Shared Core

---

## Status

**Current Status:** 🟢 Done (100% — 10/10)
**Started:** 2026-09-13
**Completed:** 2026-09-13
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

Build the container the five skills will live in, and prove it works on one
real module before four more phases depend on it. A skill that holds its own
scripts and its own tests is only an improvement if those tests actually run in
`make test` and those scripts actually import the shared core without a path
hack at every call site.

---

## Overview

### Why This Phase Matters

"Each skill embeds its scripts, its tests, its assets" is a layout, and a
layout has mechanics: where the package root is, how an import resolves, how
pytest finds a suite under `.claude/skills/`, what stops `__pycache__` from
appearing inside a skill directory. Every one of those has a wrong answer that
works on the first skill and breaks on the third.

Proving the mechanism once, on the smallest module with a real test file, costs
a day and saves four discoveries.

### What It Enables

Phases 3 to 7 each become the same operation applied to a different domain:
write the prose, move the modules, move the tests, turn the `make` target into
a facade. No phase after this one has to invent its own plumbing.

### Out of Scope

No skill prose is written here beyond a stub. The `SKILL.md` files created in
this phase carry their frontmatter and a single line saying what the skill is
for; the real content is each skill's own phase. Writing five skills' prose
here would put the whole roadmap's editorial work in one phase.

---

## Tasks

### The container
- [x] Create the five skill directories with a stub `SKILL.md` carrying a `name` and a `description` in frontmatter
- [x] Define and document the inside of a skill: `scripts/`, `tests/`, `assets/`, `references/` — and what goes in each
- [x] Make a skill's scripts import the shared core without a `sys.path` manipulation at each call site
- [x] Make `make test` collect the root suite and every skill's suite in one run, with a single reported result

### The shared core
- [x] Move one module and its test file into its skill, end to end, as proof of the mechanism — `make test` green after the move
- [x] ~~Reduce `lib/` to the shared core and~~ list what remains, each entry with the reason it is shared rather than owned — *amended, see Notes: `lib/` is renamed to `core/` whole; the physical reduction belongs to Phases 3-7, which each move their own module out*
- [x] Factor out the contact-sheet and page-render bricks that `make preview` and the PDF review loop currently hold twice

### Hygiene
- [x] Keep build artefacts out of the skill directories — `__pycache__`, `.pytest_cache` — and cover them in `.gitignore`
- [x] Check each stub's `description` against its neighbours: no two skills may trigger on the same request
- [x] Verification pass: `make test` green, `make build` and `make epub` unchanged on the style guide

---

## Technical Details

### Files to Modify

```
.claude/skills/pdf/SKILL.md         stub
.claude/skills/epub/SKILL.md        to be created
.claude/skills/translate/SKILL.md   to be created
.claude/skills/fetch/SKILL.md       to be created
.claude/skills/sourcing/SKILL.md    to be created
lib/                                reduced to the shared core
Makefile                            test target collects the skill suites
.gitignore
docs/architecture.md                the layout, recorded
```

### Dependencies

Phase 0's layout decision and Phase 1's English pass. Moving French files would
undo the point of splitting the two.

### Constraints

- `.claude/skills/pdf/` already exists and holds the vendored upstream skill.
  This phase does not touch its content — Phase 3 owns that. It only adds what
  the layout requires.
- `.claude/skills/pdf-doc/` stays in place and keeps working until Phase 3
  retires it. The repository is usable at every commit.
- A skill is discovered by its `SKILL.md` frontmatter. Anything the layout adds
  next to it must not interfere with that discovery.

---

## Acceptance Criteria

- [x] The five skill directories exist, each with a `SKILL.md` whose frontmatter is valid
- [x] One module and its tests live inside a skill, and `make test` runs them
- [x] `make test` reports a single result covering the root suite and the skill suites
- [ ] ~~`lib/` contains only modules used by two or more skills, or used outside every skill~~ — *deferred to Phase 7 by the amendment above; the list and its reasons are written in `docs/architecture.md` §2*
- [x] Each remaining `core/` module has a written reason for being there
- [x] The contact-sheet brick exists once, not twice
- [x] No skill directory carries a build artefact after a full test run
- [x] `make build` and `make epub` produce the same output as before the phase

---

## Notes

### The scope conflict, and how it was settled

Phase 2 as written asked for two incompatible things: *"move **one** module and
its test file into its skill, **as proof of the mechanism**"* alongside
*"**reduce `lib/` to the shared core**"*, with an acceptance criterion demanding
that `lib/` hold only what is shared. But Phases 3 to 7 each say *"move
`lib/build.py`"*, *"move `lib/epub.py`"*, *"move `lib/fetch.py`"*. Had Phase 2
really reduced the directory, the five phases after it would have had nothing
left to move.

**Settled by the user: the package is filled before it is emptied.** `lib/`
becomes `core/` whole — all ten modules — so every one of them is importable as
`core.<name>` from the first commit and no skill ever needs a transitional path
to reach a module that has not moved yet. Phases 3 to 7 then take theirs out,
and `core/` is reduced to the shared core only when Phase 7 closes.

The task and the criterion are struck through above rather than rewritten, so
the amendment is visible to whoever opens this file next.

### Why the package is called `core`

Considered: `doclib`, `pdfcreator`, `core`. The name was checked free — not
stdlib, not in the venv, no collision — before being taken.

`core` won because `docs/architecture.md` already says "the shared core"
throughout and states the placement rule in those words: the code should read
like the rule that put it there. The usual objection to a generic top-level name
applies to a published library, not to an application with a repository-local
venv and an editable install.

The objection that *did* have weight turned out to be an argument for it. During
the interim the package holds `build.py` and `epub.py`, so `from core import
epub` is transitionally false. That discomfort is useful: it keeps the
unfinished move visible, where a neutral name like `doclib` would sit
comfortably with `build.py` inside it and hide the transition entirely.

### What the mechanism actually needed — two conftests, not one

1. **A skill's tests cannot import its own scripts.** pytest puts the *test*
   file's directory on `sys.path`, never the directory of the code under test.
   Each skill carries a `tests/conftest.py` inserting `../scripts`, kept local
   rather than one root conftest inserting all five, so two skills' flat module
   names cannot collide.
2. **A skill's tests could not see the `repo` fixture either** — it lived in
   `tests/conftest.py`, which covers `tests/` and nothing else. This is the part
   the phase did not anticipate. The fix is a **second conftest at the
   repository root**: pytest loads the conftest of every directory from the
   rootdir down, so one file there serves the repository's own suite *and* every
   skill's. `tests/conftest.py` is deleted. The division is now "shared fixtures
   at the root, the path to my own scripts in my own skill".
3. **`testpaths` in `pyproject.toml`**, so `make test` is `pytest -q` with no
   argument and reports one result. `.claude` starts with a dot and pytest's
   default `norecursedirs` would skip it — naming it as a testpath makes it an
   explicit root and the problem disappears.

`preview.py` and its seven tests were the proof, chosen because it is the only
module that depends on the core with nothing depending on it: moving `check.py`
would have made `core/epub.py` import *from* a skill, which is backwards.

### The brick was held three times, not twice

The task says twice. In code it was three — `rasterize_svg`, `render_cover` and
`render_screens` each opened a PDF and computed their own scale factor from
`get_width()` — and a fourth time in prose, in `pdf-doc` §3's review loop. All
three code sites now call `core/pdfpage.py`, and **`pypdfium2` is imported in
exactly one module**. Phase 3 points the review loop at it when it rewrites that
skill.

`core/imaging.py` gained `to_png()`, the optimised-PNG tail every rasterising
caller shared. Neither `crop()` nor `contact_sheet()` was added: they have no
caller until Phase 6, and an untested function that nothing calls is the new
capability this roadmap forbids.

### The description check

The four stubs written here are mutually exclusive, each carrying a phrase no
neighbour carries — `epub` on reflow and e-ink, `fetch` on *one* URL, `sourcing`
on several sources *not known in advance*, `translate` on a document *already
in* the library. `fetch` and `sourcing` both start from a URL, so both
descriptions name the discriminator outright rather than leaving it implied.

**Two overlaps remain, both sanctioned by this phase's own constraints.** `pdf`
still carries the vendored upstream description — *"anything with PDF files"* —
which collides with `sourcing` reading a PDF as evidence; Phase 3 owns that
file. And `pdf-doc` claims EPUB output in its description, colliding head-on
with the new `epub` stub; Phase 3 retires it. Until then a request for an EPUB
can land on either. That is the price of keeping the repository usable at every
commit, and it is worth naming rather than discovering.

### Two dead imports, removed

`io` in `core/epub.py` went dead when its two `BytesIO` uses moved into
`core/imaging.to_png`. `shutil` in `core/new.py` was already dead before this
phase. Both removed.

### One near miss worth recording

`io.open(path, "w").write(io.open(path).read().replace(…))` **empties the
file**: the `"w"` handle truncates before the inner read runs.
`tests/test_harness.py` was silently reduced to zero bytes, and the suite went
from 124 to 123 **without a single failure** — a deleted test does not fail. It
was caught by diffing collected-test counts before and after, not by the suite
going red. **Count the tests; do not only read the result.**

---

### The open mechanical question

Three plausible ways to make a skill's scripts import the shared core, to be
settled in Phase 0 and applied here:

- a `pyproject.toml` making the repository an installable package, `lib/`
  becoming an importable module name;
- a `conftest.py` at the repository root inserting the path, which solves the
  tests but not the scripts run by hand;
- entry points that are always invoked through `make`, with the path set there.

The third is the least intrusive and the most fragile — it works until someone
runs a script directly, which the sourcing tools are designed to invite.
