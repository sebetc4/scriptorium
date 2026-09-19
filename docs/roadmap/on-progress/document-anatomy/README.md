# Roadmap: The Anatomy Of A Document

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
Phase 0  The Anatomy Of A Document                        🟢 ████████████████████ 100%  (6/6)
Phase 1  The Document, In Its Own Directory               🟢 ████████████████████ 100%  (7/7)
Phase 2  Everything Disposable, In One Place              🟢 ████████████████████ 100%  (5/5)
Phase 3  What Was Received, What Was Learned, What Makes  🟢 ████████████████████ 100%  (8/8)
Phase 4  Keeping It True                                  🟢 ████████████████████ 100%  (5/5)
Phase 5  The Documentation That Follows                   🟢 ████████████████████ 100%  (6/6)
TOTAL                                                        ████████████████████ 100%  (37/37)
```

**Current Phase:** Phase 5 — The Documentation That Follows
**Blocked By:** —
**Next Milestone:** —

---

## Why This Roadmap Exists

`out/` is where a person goes to find the document they asked for. It holds five
directories and three of them are not documents:

| | Written by | Size | What it is |
|---|---|---|---|
| `out/pdf` | `build.py` | 9.9 MB | the finished PDFs |
| `out/epub` | `epub.py` | 5.5 MB | the finished EPUBs |
| `out/review` | `review.py` | **25 MB** | page sheets for a reviewer's eye |
| `out/preview` | `preview.py` | 852 KB | EPUB contact sheets and style proof |
| `out/translate` | `translate.py` | empty | a workspace of text chunks and engine answers |

And the inside of a document has never been declared at all. `core/doc.py` knows
one fact — `index.md` is the entry — and the rest is habit. `sources/` holds,
undifferentiated, what the user provided, what a script derived from it, and the
code that draws its figures.

Neither costs a reader anything today. Both cost every future document and every
future skill, because nobody can say where a new kind of file belongs, and so it
lands wherever the last one did.

---

## The Five Roles

One directory per role, and none of them is a miscellany.

```
library/<topic…>/<slug>/
  document/     index.md, cover.md, assets/      the document
  sources/      what was received                the user's
  study/        extracted text, provenance, the investigation journal
  generators/   the code that draws an asset
  .work/        review sheets, EPUB proofs, page renders
```

| | Written by | Read by the build | `make clean` |
|---|---|---|---|
| `document/` | the agent, with the user | **yes, and only this** | never |
| `sources/` | the user — a tool may acquire into it, never derive | no | never |
| `study/` | the agent | no | never |
| `generators/` | the agent | no | never |
| `.work/` | the tools | no | **removed** |

**The cut that decides the rest is whether the build reads it.** It is the only
boundary the machine checks for you: a file on the wrong side of it breaks a
build, which is visible. Every other misplacement is silent.

A document has only the directories it needs. `make new` creates `document/`;
the rest appear when something has to go in them.

---

## Decisions Taken At Opening

**`sources/` belongs to the user.** They fill it with whatever they judge
relevant to the task, and no tool ever modifies what is in it. This is the half
of the rule that can be enforced, and Phase 4 enforces it. The other half —
that the user leaves the rest alone — is advice, not a fence: it is their
repository.

**A tool may acquire into `sources/`, never derive into it.** Copying an
imported PDF or saving a captured page fills the user's directory on their
behalf, and the result is received material like any other. Computing
`extracted.md` from it is not. This line does not exist today: `ingest.py` and
`fetch.py` each do both, into the same directory.

**`assets/` moves inside `document/`.** Every `index.md` links its images with a
relative path of the form `assets/img-001.jpg`. Moving the document and its
assets together leaves every relative path in every document untouched; moving them apart would mean
rewriting every document's links to gain nothing.

**Durable is split in two.** `study/` is what the agent learned — extracted
text, provenance, the journal, a translation's workspace. `generators/` is code.
Both survive `make clean`; keeping them apart means neither directory has an
exception to its own rule.

**A translation workspace is durable, not working state.** It looks like the
second — a job in progress, named after a command, written under `out/` today —
and it is the first: an engine's answers are the work itself, and re-running
gives *a* translation rather than *the* one under way. `make clean` would have
taken a half-translated hundred-page document with it. Added on 2026-09-19,
during Phase 2, from a reading of the rule the anatomy already carried.

**Each phase migrates the documents it affects**, behind a dry run shown before
it runs. The library is never left in two shapes at once.

---

## Deliberately Out Of Scope

- Any document's content. This roadmap moves files; no built PDF changes.
- The topic tree above a document. One directory is one document and the
  directories above it are topics, at any depth: settled, and unchanged.
- `out/pdf` and `out/epub`. They are the point of the repository.
- Versioning `library/`. It stays user content, outside git — which is why every
  migration here runs behind a dry run and a backup.

---

## Phases

| # | Phase | Tasks | Status |
|---|---|---|---|
| 0 | [The Anatomy Of A Document](phase-0-the-anatomy.md) | 6 | 🟢 Done |
| 1 | [The Document, In Its Own Directory](phase-1-the-document-directory.md) | 7 | 🟢 Done |
| 2 | [Everything Disposable](phase-2-the-work-directory.md) | 5 | 🟢 Done |
| 3 | [Received, Learned, Making](phase-3-sources-study-generators.md) | 8 | 🟢 Done |
| 4 | [Keeping It True](phase-4-the-guard.md) | 5 | 🟢 Done |
| 5 | [The Documentation That Follows](phase-5-the-documentation.md) | 6 | 🟢 Done |

---

## Dependencies

- `core/doc.py`: `find_docs`, the slug, the default title and `out_dir()` all
  read the directory that holds `index.md`. Phase 1 changes what that directory
  is, and all four move together.
- The four skills that write into a document — `pdf`, `epub`, `fetch`,
  `translate`. A rule none of them can follow will not hold.

---

## Related Documentation

- [`docs/architecture.md`](../../../architecture.md) — why each directory of the repository exists, and where Phase 0 writes the inside of a document.
- `.claude/hooks/protect-paths.sh` — the guard Phase 4 extends to `sources/`.

---

## Metadata

**Roadmap Status:** 🟡 In Progress
**Location:** `docs/roadmap/on-progress/document-anatomy/`
**Version:** 1.7.0
**Created:** 2026-09-19
**Last Updated:** 2026-09-20

---

## Changelog

### 1.7.0 (2026-09-20)

Phase 5 closed, 6/6, and the roadmap is complete. `docs/document.md` is new: what
a document is made of, and what `make new`, `import`, `fetch`, `rederive`,
`build`, `review`, `epub`, `preview`, `translate` and `clean` each put where. Its
table carries four columns — the fourth, *yours to edit*, is the question Phase 0
could only answer in prose.

Three statements were known to have become false; five had. `README.md` still
defined a document as a directory holding an `index.md`, and two routing rules
sent work to `pdf` on the same wording. And two links had been dead since the
`repo-overhaul` roadmap moved to `completed/`, because the closure ritual's link
check runs over the roadmap folder and never over `docs/*.md`. Both fixed, and
the glob widened.

`docs/architecture.md` §9's glossary gained the vocabulary this roadmap put into
the repository — *study*, *workspace*, *disposable* — and §11 stays last, with
§1 and §10 now pointing at it: moving it would have renumbered seven
cross-references in silence.

The documentation test pins the agreement rather than the words: the five
constants in `core/doc.py`, the three documents that describe them, and every
`make` target that writes into a document. Both halves were proved to fail for
the right reason. 510 tests.

### 1.6.0 (2026-09-20)

Phase 4 closed, 5/5. `tests/test_anatomy.py` fails when a document holds
anything the anatomy does not place, naming the file and the document, and
skips on a fresh clone where `library/` is user content that is not there.

**The guard was rewritten against the anatomy, and phase 3 had broken it.**
`protect-paths.sh` recognised an investigation by a `NOTES.md` beside its
`raw/`; moving the journal to `study/` turned that check off, in silence, for
every investigation. Reproduced — exit 2 before, exit 0 after — and both shapes
are recognised now. The guard refuses a write into `sources/`, which is the
user's, and into `.work/`, which a command remakes; it allows `document/`,
`study/` and `generators/`. Acquisition is untouched, because a script writes
through Bash and the hook only sees an edit by hand.

Rebuilt one last time: 15 PDFs and 8 EPUBs identical to what Phase 1 recorded
before any of this began. Four phases of reorganisation, and nothing a reader
sees has changed. 508 tests.

Six files needed a hand across the roadmap, and the phase report names each one.

### 1.5.0 (2026-09-19)

Phase 3 closed, 8/8. **`sources/` now means what the anatomy says.** What a tool
derived left it: `extracted.md` and `meta.json` to `study/`, the page renders to
`.work/pages/`, the sourcing journal to `study/`, `figures.py` to `generators/`,
and the translation workspace from `out/` to `study/translate/`. What was
received stayed — the imported PDFs, `page.html.gz`, an investigation's
captures, and the notes a user wrote by hand.

**The stop condition was tested before anything moved, and it held.** Importing
the same PDF twice gives seventeen identical files; three extractions of the
same captured page are identical to each other and to what is on disk. That is
what earns `extracted.md` its place in `study/`.

It also exposed the other half. `ingest.py` never copied the source PDF into
`sources/` — `meta.json` recorded a path under `pdfs/`, a directory the
repository renamed a roadmap ago — so re-derivation was never guaranteed. It
copies it now: a tool acquiring on the user's behalf, which §11 allows.
`make rederive DOC=` re-extracts from `sources/` alone and rewrites nothing
else, and each script says nothing when the document is not its own, so no
dispatch logic sits in the `Makefile`.

Two documents' extractions differ when re-derived today, by one string:
`"Figure — à légender"` became `"Figure — to be captioned"` when the repository
was translated. The extraction is deterministic; the script's wording moved.
That is precisely the case §11 names, seen in the wild, and the originals were
restored — this phase moves, it does not regenerate.

A workspace is **spent** once `apply` has written the document. Nothing removes
it automatically, and `apply` says so instead: deleting a translation is what
moving it out of `.work/` prevented.

237 library files byte-identical, 15 PDFs and 8 EPUBs unchanged, 499 tests.

### 1.4.0 (2026-09-19)

Phase 2 closed, 5/5. **`out/` holds `pdf/` and `epub/` and nothing else.** The
review sheets and the EPUB proofs moved to `<document>/.work/`, beside the
document they describe rather than in a parallel tree joined to it by a path
convention. 211 files, identical in content and at equivalent paths — 96 review
files and 115 preview files, compared one by one.

`core/doc.py` gained `work_dir()`, `work_dirs()` and `clean()`: what `make
clean` may delete is decided by the layout, never by a pattern in the
`Makefile`. `work_dirs()` reads the document roots rather than globbing for
`.work`, so a directory of that name a user keeps in their own `sources/` is
never swept — that is a test. `make clean DOC=topic/slug` removes one
document's `.work/` and leaves `out/` alone, because a clean that can only be
total is a clean nobody runs.

Verified live: a full clean removed seven `.work/` and `out/`, and the library's
221 other files came through untouched — nothing lost, nothing changed.

### 1.3.0 (2026-09-19)

Phase 1 closed, 7/7. `document/` exists: `core/doc.py` discovers a document at
its root, the slug and the output path come from that root, and `doc_dir()` is
the one place that knows where the build looks. Eight documents migrated behind
a dry run — not twelve, which the roadmap had counted wrong from a listing of
directory names.

**Two silent failures were caught by comparing outputs rather than by the
suite.** SVGs stopped being inlined, so figures still rendered but lost their
colour roles — invisible in a build that succeeds, and found only because the
PDF text layer lost every label inside a schematic. And the EPUB names its
images after a digest of their path relative to the document's root, so moving
the document renamed every image in every archive; the digest now covers the
path *inside* `document/`, which is what it always meant.

After both fixes: 15 PDFs and 292 pages content-identical, 8 EPUBs and 180
entries identical, 221 library files byte-identical. `make build` is not
byte-reproducible — two builds of the same source differ — so the comparison is
on content, which is what the criterion's second branch allows.

### 1.2.0 (2026-09-19)

Phase 0 closed, 6/6. The anatomy is written: `docs/architecture.md` §11 states
the five roles, the cut that decides the rest — the build reads `document/` and
nothing else — and the acquire / derive line that `ingest.py` and `fetch.py`
both cross today. `CLAUDE.md`'s repo map carries the five directories in a
paragraph, with an italic note that the library is not yet in that shape.

Two things came out of writing it. The cut is about **what a file is for, not
who made it**: a schematic drawn by hand over an afternoon lives beside a
photograph a script extracted, because the document references both. And
`extracted.md` is the one genuinely ambiguous file — regenerable, so it could be
disposable, but only if regeneration is deterministic, which Phase 3 now
verifies instead of assuming.

### 1.1.0 (2026-09-19)

Phase 5 added before the roadmap was opened: the documentation, written last
because it describes what the five phases before it turned out to build rather
than the contract Phase 0 wrote before anything moved. `docs/document.md` is
new — what a document is made of and what each command puts where — and three
statements that become false the moment Phase 1 runs are reconciled:
`CLAUDE.md`'s opening sentence, `docs/architecture.md` §1's tree and §9's
glossary, where *document* and *source material* are both defined against the
old shape.

### 1.0.0 (2026-09-19)

Roadmap created from a conversation about `out/`, five phases, 31 tasks: declare
the five roles a document directory has, put the document and its assets behind
one name the build reads, move everything disposable into the document's own
`.work/`, split what `sources/` confuses into received, learned and making, then
guard the result.

The design settled on one rule — `sources/` is the user's and no tool modifies
what is in it — and one distinction the repository had never drawn: a tool may
acquire into that directory on the user's behalf, and may never derive into it.

It also absorbs an uncarried finding from the `session-review` corpus: "say
where a figure generator belongs", raised because `figures.py` was left in
`sources/` with nothing to say it should not be.
