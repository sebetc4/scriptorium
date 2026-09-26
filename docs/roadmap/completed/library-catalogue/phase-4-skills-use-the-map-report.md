# Phase 4 Report: The Skills Use the Map

**Phase:** [phase-4-skills-use-the-map.md](phase-4-skills-use-the-map.md)
**Start Commit:** 6f9a450

---

## Work Log

### 2026-09-26

Opened from Phase 3's file and report. Nothing was pending approval. The
block is lifted: discussion-and-illustration closed its Phase 0 on the
baseline notebook session of 2026-09-26 (`f7b98772`), reviewed in
`reviews/2026-09-26-f7b98772-notebook-resume.md` — 102,719 fresh tokens,
4,053,380 cache reads, 33,556 output, 50 turns, 19 active minutes, 8 images
carried for 272,000 tokens, a context peak of 126,214. That phase's report
hands two of the review's findings to this one, as the next change to
`discussion`: how to read a photograph for detail, and the journal's
pronouns.

The `discussion` skill first, rewritten whole. A new section, *The library*,
carries the rule: answer from the agent's own knowledge when that is enough;
search when the answer depends on what the library holds — the user's own
material, a claim the document will state as established, how a document of
the library explains something; search the map, never the file system; read
only what the search points at. Material is cited by id where it served, and
nothing lists it: the **Material** row left the index's table, the section
left `assets/index.md`, whose header now cites its entry by id, and the
suite's fictional journal lost its own. The resume finds its journal with
`find`, then reads two short answers instead of any source: `sync` and `ls`
on the entry for what is new, `links` for what the journal relies on outside
it. A journal that still cites by path, or keeps a **Material** section, is
migrated on the user's word. The two findings handed over by
discussion-and-illustration went in: a photograph is read by crops at full
resolution, through `sourcing`'s `crop.py`, and the journal never names the
user by a gendered pronoun. Seven tests were added to the skill's suite.

Trying the resume on the notebook showed a gap: a file that arrives in a
directory already described — the notebook's photos arrive in
`sources/images/led-ring/` — adds no item, and `ls` marked the directory
`to review` without saying which file was new. `ls` on a directory item now
gives each file its date and, when an item of its own covers it, that
item's id; a file without one is the new one. One test in
`tests/test_navigate.py`.

Then the notebook's journal, in place: 11 of its files. Each path to
material became a link to its id, the photo renamed in Phase 3 found through
its manifest's `original:` (`20260924_123413.jpg`). In the index and the
topics the link's text is a name; in the three sessions touched it is the
path as the session wrote it, and only the target changed. The eight lines
of **Material** were each checked before the section went: the user's words
about their notes (« juste une note de ce dont je voulais te parler ») moved
to **What the user said**, the workshop draft read and not used became a
line in `pannes` and in `routine-panne`, and `tresse-et-pastilles` now cites
the photo it came from; the other lines were already cited by their topics.
Paths that are the subject of a decision — the entry's directory, where the
notes stay — were left as written, and one « selon lui » became « selon
l'utilisateur ». `links electronics/notebook`: 16 lines, every piece of
outside material the journal relies on. `make check-library`: no defect.

The `sourcing` task started from the constraint's question, and from
`electribe-2`, the only investigation in the library: its `NOTES.md` cites 16
pieces alone, by paths of the folder they were collected in. Reading the
journal to describe those pieces as items of `sources/`, the work was
stopped by the user: `electribe-2` predates the architecture, and its
"sources" are files the agent retrieved during its research — they should
not be in `sources/`, and must not skew the analysis. Nothing had been
written yet. The documentation had done exactly that: `sourcing`,
`docs/document.md` and `docs/architecture.md` §5 all took the Electribe
layout as the rule ("a `sourcing` session saves the photographs and threads
it collected" into `sources/`). The rule was turned round: an
investigation's pieces are the agent's findings and live in `study/`, beside
its `NOTES.md`; `sources/` keeps what the user gave or pointed at. The guard
already refused an edit in `study/raw/`, `datasheets/` and `images/` beside a
`NOTES.md`; a test now says so.

The user then asked for `electribe-2` to be moved into that shape. `sync`
follows a moved file by its digest only between sources, and retiring the
four items to describe them again would have drawn new ids. The catalogue
gained `move`: an item's file or directory goes to another path of its
entry, across roles, with its id, name and description and the items inside
it; a directory left empty is removed; a source keeps the digest it was
described against, an agent's file carries none. Twelve test cases in
`tests/test_catalogue.py`. The four
directories moved to `study/`, their ids kept, and the empty `sources/`
went. The paths of `NOTES.md` resolved again from `study/`. Its 16 pieces
cited alone got an item each, described from what the journal and
`images/manifest.json` say of them; its 26 path citations became links to
ids, the path kept as the link's text, and `index.md` in its inventory
became `document/index.md`, where the user's starting notes are.

`pdf` and `fetch` gained the map: look through `find` and `links` before
writing or capturing, place a new entry with `ls` on the topics, name what
the command prints as left to name with the `catalogue` skill, and never an
`id:` link in `document/`. `pdf`'s description now leaves a `manifest`, `id`
or `citation` defect to `catalogue`; `tests/test_triggers.py` and the
trigger table of `docs/architecture.md` §5 name it as `pdf`'s neighbour.
`docs/document.md`, `docs/architecture.md` and `CLAUDE.md` say where an
investigation's pieces live and what `move` does; the `catalogue` skill and
its agent name `move` among what waits for the user.

`make test`: 778 passed. `make check-library`: 9 documents, no defect, 0 to
describe. Six tasks of seven are done; the proof session is the user's.

Before the proof session, the user found the search rule wrong in kind. Its
first case read « their equipment, their kit, their project », its examples
« "my station" is a manual in `lab/` », « "the ring I built" a kit's
document in `learning/` ». The repository serves any user, for any kind of
file: what one library holds — an equipment list, projects — has no place
in a skill, a script or a rule. A count over the skills, scripts, hooks and
docs found the library's content at three levels.

The rules this phase wrote around the library were rewritten without it:
`discussion`'s search rule, `sourcing`'s section on the library, `pdf`'s
paragraph. The rule's first case is now the user's own case, as against the
subject in general; its third, a library that already treats the subject.
`discussion`'s older examples went with them — a cold joint, a datasheet,
the user's bench, a named part — and its citation example, which was a real
id of the user's library, became a fictional one. The examples this roadmap
had drawn from the library since Phase 0 — the TC22 and its manual,
capacitors, soldering tips — became fictional ones in the `catalogue`
skill, `describing.md`, the describing agent, the docstring of
`core/catalogue.py` and the catalogue section of `docs/document.md`.
`CLAUDE.md` now carries the rule among the rules no skill owns. What other
roadmaps wrote was listed for later.

The user answered with three things. The rule's third case — a subject the
library already treats — is not needed when the agent knows the answer, and
without a guard an agent would search the library at every question to learn
whether it held the answer, and spend tokens on it. `discussion` now answers
from its own knowledge by default and searches only for the user's own case,
or for the source of a claim to establish — once, when the claim is written
down. A guard follows: the journal's citations and `links` first, one search
per subject and a second only if the first missed the library's words, then
the agent's knowledge or a question to the user; each search and its result
go in the session's **Covered**, so that no session repeats it. The session
template says so.

Second, everything else that still named the library was to be fixed now, not
listed, whichever roadmap wrote it: a list in a report is how it gets
forgotten. A sweep of the repository outside `library/` and the history found
it in 36 files. `sourcing` was rewritten with its method intact and its
illustrations generic; its `datasheets/` directory became `documents/` in the
skill, the guard hook, its test and the docs, and `electribe-2`'s directory
was moved with `move`, ids kept, its journal's link texts following. The
access map keeps what serves any investigation; its entries on one subject —
component datasheet sites, synthesizer manuals, Korg's forum, ModWiggler —
went to `electribe-2`'s `NOTES.md`. Then the docstrings of the `sourcing`
scripts, `translate`'s glossary example, `session-review`'s example review
and two of its fixtures, renamed; comments in the `pdf` review script,
`epub.py`, `chunking.py`, `core/imaging.py` and `core/pdfpage.py`; the
README's examples; `docs/architecture.md` and `docs/document.md`. And the
tests: the catalogue and navigation suites moved onto a fictional household,
`translate` and `fetch` onto a bread recipe, `sourcing` onto a fictional forum
and parts, and the review tests' data drawn from the user's documents was
replaced — one address kept at the original's length, since the check it
tests measures a line. Words of the domain the repository grew in —
schematic, datasheet, silkscreen — became drawing, spec sheet, detail where
they stood for any figure or document. The fictional component of
`tests/fixtures/library/` was kept: written as fiction for the suite, it
quotes nothing of the library.

Third, `electribe-2`'s `document/index.md` — the user's starting notes and an
agent's answer — went to `sources/repair-notes.md` with `move`, its id kept,
and the empty `document/` went: the entry is no longer counted as a document.

Meanwhile the user was reorganising the library: `lab/tools/tc-22` moved
under a new topic `soldering-station`, `support` became
`soldering-helping-hands`, and `soldering-tip` and `truck/workshop-fit-out`
appeared. The notebook's journal, citing by id, followed without a change.
`make test`: 778 passed. `make check-library` reports the reorganisation in
progress: three directories without a manifest, and the tips' pages gone
from `tc-22`.

Last, the one item first kept back for the user: the core wrote the standard
names in French whatever the library's language. The Phase 0 decision —
names and descriptions in the library's language — was generalised rather
than overturned. `core/catalogue.py` holds the standard names in English and
in French; a library declares its language in `.catalogue.yaml` at its root,
English when it says nothing; the user's library and the suite's fictional
one, both French, declare `fr`. The catalogue skill, its naming rules, its
agent and `docs/document.md` say the library's language instead of French.
One test. `make test`: 779 passed.

Then, at the user's request, the library's check before anything else. A
`sync` over the whole library created the four missing manifests and
followed the Geeboon tips' pages by their digest from `tc-22` into
`soldering-tip/sources/geeboon`, id kept: the notebook's citation of them
followed without a change. New: nine files in `components/transistor`
(eight captures of the Gemini canvas and its link), two JBC cartridge
guides, and a new topic `truck` with an entry of six photos and the user's
own text. `ls` on the transistor's image directory told the new files by
their missing id, as Phase 4 made it. The text, the PDFs, the two topics and
the tips' entry were described in the conversation, the stale description
of `tc-22` rewritten; the images went to `catalogue-describer` in one call
for both entries — **68,718 tokens, 16 tool calls, 420 s**, six images
looked at, three per directory — and the truck's entry was named from its
summary. `make check-library`: no defect, 0 to describe. Its two questions
and seven rename proposals were put to the user.

The user answered by renaming the canvas directory (`canva` → `canvas`),
which `sync` followed, id kept; by asking for every capture to be read,
which the same agent did in a second call — 86,648 tokens, 8 tool calls,
126 s, its context resumed — the canvas now described
section by section; and by deleting the truck's photos, to be taken again:
their directory's item keeps its id for the new ones, described as empty
meanwhile. `make check-library`: no defect, nothing to describe or to
review. Eight rename proposals for the captures were put to the user, who
accepted them all: each renamed through `rename`, its first name kept, and
described on its own item; the canvas's description now lists its
sections. `make check-library`: no defect.

The proof session opened in a fresh session (`a9981bf3`). The discussion
skill fired on « on reprend la discussion du carnet ». It found the journal
through the map — `find carnet`, `find journal discussion` — read the index
alone, then ran `sync`, `ls` and `links` on the entry: no listing of the file
system, no topic, no session, no photo opened. It stated where the discussion
stood and asked its question. The user then asked for a review of that
opening alone (`reviews/2026-09-26-a9981bf3-notebook-resume-2.md`: 28,040
fresh tokens, 207,117 cache reads, 5 turns, a context peak of 51,131). It
raised three problems. `sync` refused the entry's id that `find` had given,
when every other command takes one — fixed in `core/catalogue.py`, an item's
id syncing its entry, with a test; the `discussion` skill now says each
command takes a path or an id. And the user's global SessionStart hook,
`~/.claude/hooks/roadmap/session_resume.py`, outside this repository,
injected this phase and its work log into a discussion that had no use for
them — reported to the user, not touched. The discussion itself, the part
the acceptance criteria measure, is still to be held.

The user went back to the same session and held it on a subject of their
own: which kit to build next, then whether the capacitance meter kit
(`learning/transistor-tester`) is harder than the M328 tester. The agent
searched only because the answer was the user's own case — their kits —
and through the map: `ls` on `electronics` and on `learning`, `ls -l` on the
two entries, `peek` on the notice by its id, then the *Montage* section of
the M328's document and one contact sheet of the notice's image pages. No
listing of the file system. Its first recommendation came from its own
knowledge of such kits, and it said so. It wrote the session's file as it
went, each search and what it found in **Covered**, and caught one gendered
pronoun it had written into the index. Reviewed a second time
(`reviews/2026-09-26-a9981bf3-next-project.md`: 24,079 fresh tokens,
1,191,844 cache reads, 17 turns, one image, a context peak of 80,202, no
measure past 1.5 times its median). Of its findings, the two that belong
here were applied: `discussion` says how to keep the pronoun rule in French,
and `describing.md` says a PDF's description names the pages with no text
layer — the notice's description now does, its pages 3-15 checked by `peek`.
The third, on where `metrics.py` starts a slice, belongs to the
session-review roadmap and was reported to the user.

Against the baseline, the proof session's two slices together: 52,119
fresh tokens against 102,719, 1,398,961 cache reads against 4,053,380, 22
turns against 50, one image against eight (4,800 tokens carried against
272,000), a context peak of 80,202 against 126,214. The subjects differ —
the baseline read photographs and catalogued two, the proof compared two
notices — and the proof carried the global hook's injection, so these
figures record the proof, not a controlled comparison. `make test`: 780
passed. `make check-library`: no defect.

---

## Decisions

- **The library is searched when the answer depends on it, and not by
  default.** Three cases, written as the roadmap's Decisions set them. The
  rule sits in a section of its own, *The library*, so that a session reads
  when to search before how.
- **Nothing lists the material.** The entry's manifest describes its own
  files, the topic a file fed cites it, and `ls` and `links` on the entry
  answer at a resume what **Material** answered. A list kept beside them
  would be a second place for the same fact.
- **A session gets its citations converted once, and nothing else.** The
  path stays as the link's text — the record as it was written — and the
  target becomes the id, so the archive never needs another change. A path
  that is the subject of a decision is left as the decision wrote it.
- **The index's header cites its entry by id**, and gives its path only
  until the entry is named.
- **A photograph is read through `sourcing`'s `crop.py`.** The brick is
  `core/imaging.crop`; the script is the one tested command that crops by
  fractions at full resolution, and a second copy of it would be the
  duplication `docs/architecture.md` §2 forbids.
- **An investigation's pieces live in `study/`, beside its `NOTES.md`.** The
  user's word: what the agent found is not what the user gave. It overturns
  the reading of `sources/` that repo-overhaul Phase 6 took from the Electribe
  investigation, which predated the anatomy. `sources/` keeps what the user
  gave or pointed at — their notes and photos, an imported PDF, a captured
  page.
- **A piece `NOTES.md` cites alone gets an item of its own**, which answers
  the constraint this phase carried; a batch cited only as a whole stays in
  its directory's item. In `NOTES.md` the path stays as the link's text.
- **`move` joins the catalogue** rather than retiring ids and drawing new
  ones: an id never changes, and nothing else can take an item from one role
  to another. It acts on the user's word, like `remove` and `rename`.
- **`ls` on a directory item marks the files that have an item of their
  own**, so that the resume's `sync` and `ls` can say which file is new.
- **No skill, script or rule is written around what a library holds.** The
  user's word, now in `CLAUDE.md`. The search rule's cases are told apart by
  where an answer comes from — the user's own case, a claim to establish, a
  subject the library already treats — never by what a library contains.
  An example is fictional, never quoted from `library/`.
- **Searching has a guard.** The agent's own knowledge is the default; a
  search serves only the user's own case, or the source of a claim to
  establish, looked for once. One search per subject; each written in the
  session's **Covered**. The case of a subject the library already treats
  was dropped, on the user's word.
- **An investigation's documents go in `documents/`**, a slot named for what
  any investigation collects, not for one field's datasheets.
- **The access map holds what serves any investigation**; what serves one
  subject goes to that investigation's `NOTES.md`, in the library.
- **A library declares its language** in `.catalogue.yaml` at its root, and
  the tool names the anatomy's files in it — English by default. A hidden
  file, so the root stays no node.

---

## Files Changed

**Added**

- `assets/icon.png` — staged before this phase opened, and not its work: left out of its commit
- `docs/roadmap/on-progress/library-catalogue/phase-4-skills-use-the-map-report.md`
- `tests/fixtures/library/.catalogue.yaml`

**Modified**

- `.claude/agents/catalogue-describer.md`
- `.claude/hooks/protect-paths.sh`
- `.claude/skills/catalogue/SKILL.md`
- `.claude/skills/catalogue/references/describing.md`
- `.claude/skills/catalogue/tests/test_catalogue_skill.py`
- `.claude/skills/discussion/SKILL.md`
- `.claude/skills/discussion/assets/index.md`
- `.claude/skills/discussion/assets/session.md`
- `.claude/skills/discussion/assets/topic.md`
- `.claude/skills/discussion/tests/test_discussion.py`
- `.claude/skills/epub/scripts/epub.py`
- `.claude/skills/epub/tests/test_cover.py`
- `.claude/skills/epub/tests/test_package.py`
- `.claude/skills/fetch/SKILL.md`
- `.claude/skills/fetch/tests/test_capture.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/pdf/scripts/review.py`
- `.claude/skills/pdf/tests/test_mapped.py`
- `.claude/skills/pdf/tests/test_review.py`
- `.claude/skills/session-review/references/findings.md`
- `.claude/skills/session-review/references/format.md`
- `.claude/skills/sourcing/SKILL.md`
- `.claude/skills/sourcing/references/access-map.md`
- `.claude/skills/sourcing/scripts/archive_images.py`
- `.claude/skills/sourcing/scripts/contact_sheet.py`
- `.claude/skills/sourcing/scripts/crop.py`
- `.claude/skills/sourcing/scripts/fetch_checked.py`
- `.claude/skills/sourcing/scripts/forum_index.py`
- `.claude/skills/sourcing/scripts/html2text.py`
- `.claude/skills/sourcing/scripts/imgur_album.py`
- `.claude/skills/sourcing/scripts/pdf_find.py`
- `.claude/skills/sourcing/scripts/pdf_render.py`
- `.claude/skills/sourcing/scripts/wayback.py`
- `.claude/skills/sourcing/tests/test_archive_images.py`
- `.claude/skills/sourcing/tests/test_fetch_checked.py`
- `.claude/skills/sourcing/tests/test_forum_index.py`
- `.claude/skills/sourcing/tests/test_html2text.py`
- `.claude/skills/sourcing/tests/test_imgur_album.py`
- `.claude/skills/sourcing/tests/test_pdf_tools.py`
- `.claude/skills/sourcing/tests/test_wayback.py`
- `.claude/skills/translate/SKILL.md`
- `.claude/skills/translate/scripts/chunking.py`
- `.claude/skills/translate/tests/test_chunking.py`
- `.claude/skills/translate/tests/test_engines.py`
- `.claude/skills/translate/tests/test_qc.py`
- `.claude/skills/translate/tests/test_translate.py`
- `.claude/skills/translate/tests/test_zones.py`
- `CLAUDE.md`
- `README.md`
- `core/catalogue.py`
- `core/imaging.py`
- `core/navigate.py`
- `core/pdfpage.py`
- `docs/architecture.md`
- `docs/document.md`
- `docs/roadmap/on-progress/library-catalogue/README.md`
- `docs/roadmap/on-progress/library-catalogue/phase-4-skills-use-the-map.md`
- `tests/fixtures/library/sample/component/study/discussion/index.md`
- `tests/test_anatomy.py`
- `tests/test_catalogue.py`
- `tests/test_doc.py`
- `tests/test_navigate.py`
- `tests/test_net.py`
- `tests/test_pdfpage.py`
- `tests/test_triggers.py`

**Renamed**

- `.claude/skills/session-review/tests/fixtures/2026-09-17-4c7bb3d0-round-led.md` → `.claude/skills/session-review/tests/fixtures/2026-09-17-4c7bb3d0-teaching-guide.md`
- `.claude/skills/session-review/tests/fixtures/2026-09-20-9f1e2a3b-transistor.md` → `.claude/skills/session-review/tests/fixtures/2026-09-20-9f1e2a3b-primer.md`

Outside git, since `library/` and `reviews/` are ignored: the notebook's
journal migrated to `id:` citations (index, seven topics, three sessions);
`electribe-2` reorganised — its pieces moved from `sources/` to `study/`,
`datasheets/` renamed `documents/`, sixteen pieces given items of their
own, its `NOTES.md` citing by id and holding the subject's own access
knowledge, its starting notes moved to `sources/repair-notes.md`; the
library's `.catalogue.yaml` created (`language: fr`); the manifests of the
user's reorganisation synced, named and described, eight canvas captures
renamed; and the proof session's two reviews.

---

## Problems And Deviations

- **Work beyond the plan**, each for a reason given above: the `move`
  command, the change to `ls`, the rule that an investigation's pieces live
  in `study/`, `electribe-2` reorganised on the user's word, and the two
  findings of the baseline review folded into `discussion`.
- **A premise of the documentation was false.** `sourcing`,
  `docs/document.md` and `docs/architecture.md` §5 said an investigation
  saves its pieces into `sources/`, a rule read off `electribe-2`, which
  predated the anatomy. The user caught it as this phase began to build on
  it; nothing had been written. Fixed in the three documents and in
  `CLAUDE.md`.
- `electribe-2`'s `document/index.md` held the user's starting notes and an
  agent's answer, not a document: moved to `sources/` on the user's word.
- **The search rule was first written around the user's library**, its
  cases and examples taken from their topics and equipment, like examples
  this roadmap had written since Phase 0. The user caught it before the
  proof session; rewritten, and the rule is in `CLAUDE.md`.
- **What other roadmaps had written around the library was fixed here too**,
  on the user's word — 36 files (Work Log). Beyond this phase's plan.
- The standard names the core wrote in French follow the library's
  language now: Phase 0's decision generalised, not overturned (Work Log).
  Nothing that names the user's library is left in the repository outside
  `library/` and the history; the suite's fictional component is fiction by
  construction, quoting nothing.
- **`make check-library` was red for a while**, from the user's
  reorganisation of their library, not from this phase's work: synced,
  named and described at the user's request, green at this closure.
- **The proof's outside material was found through `ls`**, on the map's
  topics and entries, where the criterion names `find` or `links`: the
  user's question surveyed a topic, which `ls` answers. `find` and `links`
  ran at the opening. What the criterion guards holds — the map, never the
  file system.
- **The proof was held on another subject than the index's next question**
  (the next kit rather than the transistor), and in two slices, the first
  reviewed after the opening alone. Its cost is recorded against the
  baseline with those differences said.
- **Left open, outside this roadmap**: the user's global SessionStart hook
  injects a roadmap's phase and work log into every session of the
  repository; and `metrics.py` starts a slice at the previous task's end,
  charging a review's own cost to the next task — the session-review
  roadmap's.

---

## Changes To Later Phases

None: this is the roadmap's last phase. Outside it, the
discussion-and-illustration roadmap's Phase 1, blocked by this phase, can
open; its own opening clears its `**Blocked By:**`.

---

## Assessment

The skills use the map. `discussion` answers from its own knowledge by
default, searches the library only for the user's own case or a claim's
source, and keeps a guard against searching again; it cites by id, resumes
from `sync`, `ls` and `links` on its entry, and no longer keeps a list of
material. The notebook's journal was migrated, and followed two
reorganisations of the library without a change. `sourcing` keeps an
investigation's findings in `study/` and cites them by id; `pdf` and `fetch`
look through the map and never put an id in `document/`. The proof session
found the user's kits through the map, read two notices and one section, and
answered from its own knowledge where the map had nothing to add.

Two corrections by the user shaped the phase more than its plan did. An
investigation's pieces are the agent's findings, not the user's sources —
which moved `electribe-2` into `study/` and gave the catalogue `move`. And
nothing in the repository may be written around what one library holds:
the rules, the examples, the tests and the core's standard names were
rewritten so that any user, with any kind of file in any language, reads the
same repository.

What comes next needs to know first: the map is complete and in use, `sync`
takes an id like every other command, and a library declares its language
in `.catalogue.yaml`. The discussion-and-illustration roadmap's transistor
pilot is unblocked.
