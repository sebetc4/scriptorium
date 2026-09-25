# Phase 1 Report: Navigating the Library

**Phase:** [phase-1-navigation.md](phase-1-navigation.md)
**Start Commit:** eaf09bd

---

## Work Log

### 2026-09-25

Opened after Phase 0's closure, whose report says what this phase reads:
`nodes()`, `read()`, `ids()`, `covering()`, `citations()` in
`core/catalogue.py`, and the three markers `core/library.py`'s `todo()`
already computes.

Wrote the four commands in a module beside the catalogue, `core/navigate.py`,
rather than in it: the catalogue already held 600 lines, and reading the map is
a different concern from keeping it. An `Atlas` reads every manifest once per
command and indexes the ids; each command answers from it. A first run on the
fixture library gave the expected answers for `ls`, `find`, `links` and
`path`.

Gave the commands one entry point: a console script, `catalogue`, declared in
`pyproject.toml` and installed by `make setup`, which dispatches to
`core.catalogue.main`. That `main` now carries the six subcommands, the two
that write and the four that read. The `make` targets `find`, `ls`, `links`
and `path` call the same code through `-m core.catalogue`, so they work
before the console script is installed.

Wrote `tests/test_navigate.py`: a first fixture misused `catalogue.resolve`
(which returns no item for a path) and was rewritten around the atlas; then 34
passed. The measurement on a generated library — the fixture library plus 500
entries nobody asks about, built in the test's temporary directory — gave
answers of exactly the same length as on the fixture library, for every
command. But it also showed the cost: about 0.3 s per command, most of it in
the pure-Python YAML loader, and 3 s for `ls` on the topic that holds the 500
entries, which computed every line before truncating to 20. The catalogue now
reads with libyaml's loader when PyYAML has it, and `ls` computes only the
lines it shows. After both: 70 to 180 ms per command on 500 entries, against 3
to 4 ms on the fixture library.

| Command, on 500 entries | Lines | Time |
|---|---|---|
| `find guide style` | 1 | 119 ms |
| `find journal --in sample` | 2 | 91 ms |
| `find meplat --text` | 2 | 83 ms |
| `ls sample -l` | 1 | 80 ms |
| `ls sample/component -ll` | 4 | 71 ms |
| `links composant-…` | 4 | 89 ms |
| `path guide-style-…` | 1 | 70 ms |
| `find remplissage` (matches all 500) | 20 | 77 ms |
| `ls generated` (500 entries) | 20 | 179 ms |

Tried the `make` targets on the user's library, which has no manifest yet: they
answer, read-only. An entry never synced showed no new file, although all its
files are new; fixed, so `make ls AT=electronics/lab` now says `[1 to
describe, 6 new]` for `diy-tools`. Documented the commands in
`docs/document.md` and `CLAUDE.md`, and `navigate` in `docs/architecture.md`
§2. `make test`: 701 passed.

---

## Decisions

- **The commands live in `core/navigate.py`**, beside the catalogue: the
  catalogue keeps the map, `navigate` reads it, and the one imports the
  other in that direction only (`catalogue.main` imports `navigate` late).
- **The entry point is the console script `catalogue`**, which is
  `.venv/bin/catalogue` once `make setup` has run. It carries every command
  of the map, reading and writing, so that Phase 2's commands join it rather
  than making a second one.
- **An answer's bound counts its closing line**: at most 20 lines in all, the
  twentieth saying how many more there are, how to narrow the question, and
  the `--limit` that would show everything. `--limit 0` removes the bound.
- **`find` matches every word of the query as a substring**, in the name and
  the description folded together (case, accents, curly apostrophes).
  Nodes and items not named yet are never results: they have nothing to
  match. Results come in path order.
- **`find --text` searches the items whose kind is `text`, and the text files
  inside a directory item** — which is how a journal (`study/discussion/`) is
  searched. A file no item covers is not searched: the map is what is known.
  Every word must be on the same line.
- **`ls` has a fourth marker, `gone`**, for an item whose path left the disk,
  beside `to describe`, `new` and `to review`. On a topic, the markers are
  added up over everything below it. A node never synced counts as to
  describe, and every file of such an entry as new.
- **`ls` computes only the lines it shows**: on a topic of 500 entries, the
  markers of 19 of them.
- **The catalogue reads YAML with libyaml's loader when PyYAML has it**, and
  falls back to the pure-Python one. Writing is unchanged.

---

## Files Changed

**Added**

- `core/navigate.py`
- `tests/test_navigate.py`
- `docs/roadmap/on-progress/library-catalogue/phase-1-navigation-report.md`
- `assets/icon.png` — untracked before this roadmap opened, and not its work:
  left out of its commit

**Modified**

- `CLAUDE.md`
- `Makefile`
- `pyproject.toml`
- `core/catalogue.py`
- `docs/architecture.md`
- `docs/document.md`
- `docs/roadmap/on-progress/library-catalogue/README.md`
- `docs/roadmap/on-progress/library-catalogue/phase-1-navigation.md`
- `docs/roadmap/on-progress/library-catalogue/phase-2-catalogue-skill.md`

---

## Problems And Deviations

- **The tests are in `tests/test_navigate.py`**, not in
  `tests/test_catalogue.py` as the phase file planned: one test file per
  module, the repository's pattern.
- **`pyproject.toml` changed**, which the phase file did not list: it
  declares the console script. On a machine that pulls this change,
  `.venv/bin/catalogue` exists only once `make setup` has run again; the
  `make` targets do not depend on it.
- **The time of an answer still grows with the library**, although its length
  does not: every command reads every manifest, about 70 ms for 500 entries.
  The roadmap rules out an index until a search grows slow; this is far from
  it, and recorded as the figure to watch.

---

## Changes To Later Phases

- `phase-2-catalogue-skill.md`: added a constraint — the skill and the
  describing agent reach every command through `.venv/bin/catalogue`, and
  `unused`, `remove` and `rename` join it as subcommands.

---

## Assessment

The phase delivered the four commands and the proof the roadmap asked for: on
a library of 500 more entries, every answer has the length it had on the
fixture library, and a question that matches everything stops at 20 lines.
The measurement earned its place: it found two costs no output length would
have shown, and both were fixed within the phase.

What Phase 2 needs first: the skill's rules can rely on `find`, `ls -l` and
`links` as they stand, called as `.venv/bin/catalogue <command>`. The markers
`ls` shows (`to describe`, `new`, `to review`, `gone`) are the describing
agent's to-do list for an entry. `unused` will read the same citations as
`links`, from `catalogue.citations()`.
