# Phase 5 Report: The Documentation That Follows

**Phase:** [phase-5-the-documentation.md](phase-5-the-documentation.md)
**Start Commit:** 6425b23

---

## Work Log

### 2026-09-20

Phase opened. The four reports before this one were read in full, as this
phase's *Before Starting* requires: they are its material, because what it
describes is what the roadmap turned out to build rather than the contract
Phase 0 wrote before anything moved.

What this phase inherits:

- **Three statements that became false**, named in its own tasks: `CLAUDE.md`'s
  opening sentence, `docs/architecture.md` §1's tree where `library/` is "outside
  this roadmap's scope", and §9's glossary where *document* and *source
  material* are both defined against the old shape.
- **Two decisions left here by earlier phases.** §11 sits after §10 because the
  document's prose refers to its sections by number and inserting would have
  renumbered them silently — Phase 0 recorded it and left the choice here. And
  §8's table now carries a revision note about `clean`, which Phase 2 added
  rather than rewriting a section.
- **One addition from Phase 4**: `docs/document.md` should say what the guard
  refuses and why, or a person meets the anatomy twice — once as prose, once as
  a hook that stopped their edit.
- The manual should make *may I edit it* a column, which Phase 0 could only
  answer in prose.

**`docs/document.md`, 244 lines, written for someone who has never seen the
repository.** Five directories at a glance, then one section each, then the life
of a document: what `make new`, `import`, `fetch`, `rederive`, `build`,
`review`, `epub`, `preview`, `translate` and `clean` each read and write, and
what is left after. Then where things are refused, and the cases that do not
fit.

The table carries four columns, not three. *Yours to edit* is the one Phase 0
could only answer in prose, and it is the question a person actually asks. The
answers are not symmetrical: `document/` is yours because it is the deliverable,
`sources/` because it is yours outright, `study/` and `generators/` because
nothing stops you, `.work/` pointlessly because it is remade.

**The three false statements, and two more found on the way.** `CLAUDE.md`'s
opening sentence, `docs/architecture.md` §1's tree and §9's glossary were the
three the phase knew about. Two others turned up: `README.md` still defined a
document as "any directory under `library/` holding an `index.md`", and
`docs/architecture.md` and `.claude/skills/pdf/SKILL.md` both routed on "does the
operation end in an `index.md` under `library/`" — true of the intent, false of
the path. The routing rules now say "a document", which is what they meant.

§9's glossary gained three entries rather than only losing a wrong one: *study*,
*workspace* and *disposable* are terms this roadmap put into the repository's
vocabulary and the glossary is where a translator or a newcomer looks them up.

**Two links had been broken since the previous roadmap closed.**
`docs/architecture.md` and `docs/local-translation.md` both point at the
`repo-overhaul` roadmap's README under `roadmap/on-progress/` — where it has not
been since that roadmap moved to `completed/`. Nothing checked: `check_links.py`
runs over `docs/roadmap/*/*/*.md` and `CLAUDE.md` at a phase closure, and never
over `docs/*.md`. Fixed, and the closure's own verification now includes
`docs/*.md` and `README.md`.

**§11 stays where it is, and §1 points at it.** Phase 0 put it last because this
document's prose refers to its sections by number and inserting one would have
renumbered the rest in silence; Phase 0 left the decision here. Moving it would
buy a better reading order and cost a silent rewrite of seven cross-references
in a document nobody re-reads end to end. §1's tree now names §11 on the
`library/` line, §10's superseded bullet says so in place, and §11 itself points
at the manual. A reader arriving at any of the three gets to the right place in
one hop.

**The test pins the agreement, not the words.** `core/doc.py` holds the five
constants; `docs/document.md`, `CLAUDE.md` and `docs/architecture.md` must name
all five, and the manual must name every `make` target that writes into a
document. Pinning a filename would buy nothing — a rename moves the code and the
prose in one commit — so what is pinned is the join between them. Both tests
were proved to fail for the right reason: renaming a role in the prose, and
dropping a target from the manual.

`make test`: 510 passed. `check_links.py` over the documents, the roadmaps,
`CLAUDE.md` and `README.md`: 47 links, 0 broken.

---

## Decisions

- **`docs/document.md` is the manual; `docs/architecture.md` §11 is the
  argument.** The manual states, the argument reasons. A manual that argues is
  not consulted and an architecture note that lists filenames goes stale in a
  week — that boundary was written into Phase 5's constraints before either
  existed, and it held.

- **§11 stays last.** The cost of moving it is a silent renumbering of seven
  cross-references; the benefit is reading order in a document read by section.
  §1, §10 and §11 now point at each other and at the manual.

- **The glossary gained the roadmap's vocabulary.** *study*, *workspace*,
  *disposable*. A term a repository starts using and does not define is a term
  the next person guesses at.

- **`check_links.py` now runs over `docs/*.md` and `README.md` too.** Two links
  had been broken since the previous roadmap closed, because the closure's
  verification only ever looked at the roadmap folder.

---

## Files Changed

**Added**

- `docs/document.md`
- `docs/roadmap/on-progress/document-anatomy/phase-5-the-documentation-report.md`

**Modified**

- `CLAUDE.md`
- `README.md`
- `docs/architecture.md`
- `docs/local-translation.md`
- `tests/test_documentation.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/fetch/SKILL.md`
- `.claude/skills/translate/SKILL.md`
- `.claude/skills/sourcing/SKILL.md`
- `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/on-progress/document-anatomy/phase-5-the-documentation.md`

`.claude/skills/epub/SKILL.md` was read against the anatomy and needed nothing:
it describes what reflows, not where a file lives.

---

## Problems And Deviations

- **Two more false statements than the phase expected**, in `README.md` and in
  two routing rules. Found by grepping for the old definition rather than by
  working from the list — the list was written in Phase 0 from what was known
  then.

- **Two links broken since the previous roadmap closed.** The closure ritual's
  `check_links.py` never looked at `docs/*.md`. Fixed, and the glob widened.

- **The first acceptance criterion cannot be verified from inside.** "A person
  who has never seen this repository can place any file of a document from
  `docs/document.md` alone" is a fact about a reader. What was done instead: the
  manual answers the four questions in a table, walks every command, and names
  the three cases that do not fit rather than leaving them for the reader to
  discover. It is ticked on that basis, and the next person to arrive is the
  real test.

All six tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

No phase follows. The roadmap closes with this one.


## Assessment

This phase had the least to invent and the most to reconcile, and the
reconciling found more than the inventing. Three statements were known to be
false; five were. Two links had been dead since a roadmap closed a week ago,
because the check that would have caught them runs over the roadmap folder and
not over the documents the roadmap is about.

That is the roadmap's own lesson arriving one last time, in the mildest possible
form. Four times now something has been true, moved, and gone on being asserted
by a file nobody re-read: an SVG path, an EPUB image name, a guard's journal,
and now two links and a definition. The anatomy does not fix that — it makes the
assertions fewer and gives them one place to live. The test added here is the
smallest useful version of the fix: the five constants in `core/doc.py` and the
three documents that claim to describe them must agree, and the manual must name
every command that writes into a document.

What the roadmap leaves for whoever comes next: `docs/document.md` is the page to
keep true. It is the only document in the repository written for a person who
does not already know how this works, and the day it stops matching
`core/doc.py` the test will say so — which is more than any of the four silent
breakages got.
