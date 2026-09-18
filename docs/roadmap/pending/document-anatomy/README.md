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
Phase 0  The Anatomy Of A Document                        🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 1  The Document, In Its Own Directory               🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 2  Everything Disposable, In One Place              🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/6)
Phase 3  What Was Received, What Was Learned, What Makes  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/7)
Phase 4  Keeping It True                                  🔴 ░░░░░░░░░░░░░░░░░░░░   0%  (0/5)
TOTAL                                                        ░░░░░░░░░░░░░░░░░░░░   0%  (0/31)
```

**Current Phase:** —
**Blocked By:** —
**Next Milestone:** Phase 0 — The Anatomy Of A Document

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
  .work/        review sheets, EPUB proofs, translation workspace, page renders
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
rewriting twelve documents' links to gain nothing.

**Durable is split in two.** `study/` is what the agent learned — extracted
text, provenance, the journal. `generators/` is code. Both survive `make clean`;
keeping them apart means neither directory has an exception to its own rule.

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
| 0 | [The Anatomy Of A Document](phase-0-the-anatomy.md) | 6 | 🔴 Not Started |
| 1 | [The Document, In Its Own Directory](phase-1-the-document-directory.md) | 7 | 🔴 Not Started |
| 2 | [Everything Disposable](phase-2-the-work-directory.md) | 6 | 🔴 Not Started |
| 3 | [Received, Learned, Making](phase-3-sources-study-generators.md) | 7 | 🔴 Not Started |
| 4 | [Keeping It True](phase-4-the-guard.md) | 5 | 🔴 Not Started |

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

**Roadmap Status:** 🔴 Not Started
**Location:** `docs/roadmap/pending/document-anatomy/`
**Version:** 1.0.0
**Created:** 2026-09-19
**Last Updated:** 2026-09-19

---

## Changelog

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
