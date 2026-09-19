# Phase 3 Report: What Was Received, What Was Learned, What Makes

**Phase:** [phase-3-sources-study-generators.md](phase-3-sources-study-generators.md)
**Start Commit:** a917aa9

---

## Work Log

### 2026-09-19

Phase opened. Phase 2's file and report were read in full: 5/5 tasks, 5/5
acceptance criteria, and one task that arrived here mid-phase rather than at its
closure — the translation workspace, which is durable.

What this phase inherits:

- **Three movements, not one.** The derivations of `ingest.py` and `fetch.py`
  leave for `study/`, the sourcing journal joins them, `figures.py` goes to
  `generators/`, and the translation workspace arrives from Phase 2.
- **A stop condition nobody has tested.** Phase 0 placed `extracted.md` in
  `study/` on the argument that its re-derivation is deterministic. If that is
  false for either script, the phase stops and says so rather than moving a file
  somewhere it can be silently destroyed. Verify it before moving anything.
- **A question Phase 2 raised and nothing answers**: a translation workspace is
  spent once `apply` has run, and nothing retires it.
- `glossary.yaml` is a file the anatomy still does not place. Phase 1 left it at
  the document's root and said so in `translate`'s `SKILL.md`.

**The stop condition first, before touching anything.** Phase 0 placed
`extracted.md` in `study/` on the argument that its re-derivation is
deterministic, and Phase 2's report said to verify it rather than assume it.
Both halves were tested:

- the same PDF imported twice gives seventeen identical files, `extracted.md`
  and the extracted images included;
- the same captured page extracted three times gives the same Markdown, and the
  same Markdown as the `extracted.md` already on disk.

The premise holds. It also has a second half nobody had looked at.

**`ingest.py` never copied the source PDF into `sources/`.** `meta.json` records
a path, and on the oldest import that path is
`pdfs/electronique/.../round-led-d4017.pdf` — a directory the repository renamed
during the `repo-overhaul` roadmap. The re-derivation was therefore never
guaranteed for an import: it depended on the user having kept the source by
hand, which the tool neither did nor said. The import copies it now — a tool
acquiring into `sources/` on the user's behalf, which §11 allows and deriving
does not — and that is what makes the task's wording, "re-runnable from
`sources/` alone", true rather than aspirational.

**`make rederive DOC=` runs both scripts and each says nothing when the document
is not its own.** No dispatch logic in the `Makefile`, and none in `core/`
either: `ingest.py` looks for a PDF in `sources/`, `fetch.py` for a
`page.html.gz`, and whichever finds its input does the work. When an import has
lost its PDF, `ingest.py` says so and stops rather than passing in silence.

`--rederive` writes `study/extracted.md` and `.work/pages/` and nothing else:
not `meta.json`, which carries the import date and the provenance that nothing
recomputes; not `index.md`, which is the work since; not `document/assets/`,
whose images go to a temporary directory and are discarded. Verified against
aged timestamps: nine files rewritten, nine untouched.

**The migration.** Four documents of eight were affected; the dry run listed
every move and everything that stays. `sources/` kept the imported PDFs, the
captured page, an investigation's datasheets, images, raw captures and thread
transcriptions — the phase's own *Out of Scope* settles those: acquired on the
user's behalf, as received as anything else — and the notes a user wrote by
hand.

**Then the two documents that did not come back identical.** Running
`make rederive` over the library, `m328` and `round-led-d4017` produced an
`extracted.md` differing from the stored one. The difference is one string:
`"Figure — à légender"` became `"Figure — to be captioned"` when the repository
was translated to English. The extraction is deterministic; the script's own
wording moved between the import and today.

That is exactly the case §11 describes — "a library version moves, an extraction
changes" — met in the wild, and with the tool's own literal rather than a
dependency. It is the argument for `study/` rather than `.work/`, made concrete:
had those files been disposable, a `make clean` would have replaced a reference
a translation had checked against with a slightly different one, silently. The
originals were restored from the backup: this phase moves files, it does not
regenerate them.

237 library files compared byte for byte against the backup: nothing lost,
nothing changed. 15 PDFs and 8 EPUBs rebuilt and compared: zero differences.
`make test`: 499 passed.

---

## Decisions

- **A tool may copy what it was given into `sources/`.** `ingest.py` now keeps
  the source PDF there. It is acquisition, not derivation, and without it the
  re-derivation `study/` rests on is a promise the tool cannot keep.

- **`make rederive` has no dispatcher.** Each script decides whether the
  document is its own and exits quietly when it is not. A dispatcher would have
  had to know what an import and a capture look like, which is exactly what each
  skill already knows.

- **`meta.json` is never re-derived.** The import date, the fetch timestamp, the
  HTTP status and the certificate's verification are facts about a moment. §11
  calls the file durable by necessity; the code now matches.

- **A translation workspace is spent once `apply` has written the document, and
  nothing removes it.** `apply` says so instead. A tool that deletes a
  translation is the thing the workspace was moved out of `.work/` to prevent,
  and that argument does not stop applying the minute the work succeeds.

- **An investigation's thread transcriptions stay in `sources/`.** They are
  derived from the raw captures in the strict sense, and the phase's *Out of
  Scope* had already placed them: acquired on the user's behalf, in a directory
  that is theirs. Moving eleven of them to defend a definition would have been
  the anatomy serving itself.

---

## Files Changed

**Added**

- `docs/roadmap/on-progress/document-anatomy/phase-3-sources-study-generators-report.md`

**Modified**

- `core/doc.py`
- `Makefile`
- `CLAUDE.md`
- `README.md`
- `docs/architecture.md`
- `.claude/agents/pdf-reviewer.md`
- `.claude/skills/pdf/scripts/ingest.py`
- `.claude/skills/pdf/SKILL.md`
- `.claude/skills/fetch/scripts/fetch.py`
- `.claude/skills/fetch/SKILL.md`
- `.claude/skills/fetch/tests/test_capture.py`
- `.claude/skills/translate/scripts/translate.py`
- `.claude/skills/translate/SKILL.md`
- `.claude/skills/translate/tests/test_translate.py`
- `tests/test_doc.py`
- `docs/roadmap/on-progress/document-anatomy/README.md`
- `docs/roadmap/on-progress/document-anatomy/phase-3-sources-study-generators.md`

`library/` is user content, outside git: the files that moved in four documents
appear in no listing, and the comparison above is their record.

---

## Problems And Deviations

- **The re-derivation does not reproduce two documents' stored extraction**, for
  the reason given at length in the Work Log: the script's placeholder caption
  changed when the repository was translated. The originals were restored, and
  the finding is the phase's best evidence rather than a defect in it.

- **`ingest.py` was changed beyond moving its targets**: it now copies the
  source PDF into `sources/`. Without it, task 6 — "re-runnable from `sources/`
  alone" — could not be honoured for an import, since nothing had ever put the
  source there.

- **Two bugs of my own, found by running the thing rather than by the suite.**
  `fetch.py --rederive` was refused by the URL check that ran before it, and
  `ingest.py` mistook a capture for an import because `sha256_html` contains
  `sha256`. Both fixed; the second is now keyed on `pages_total`, which only an
  import writes.

- **The retirement of a spent workspace is decided but not implemented.** The
  rule is written in three places and `apply` states it; nothing deletes
  anything. Deleting a translation automatically is what this roadmap just moved
  the workspace out of `.work/` to prevent, and a two-line convenience is not
  worth reopening that.

All eight tasks are done and all five acceptance criteria hold.

---

## Changes To Later Phases

No later phase file was changed, and no restructuring is proposed. Phase 4's
guard inherits a `sources/` that no tool writes a derived file into, which is
the condition it exists to defend.

---

## Assessment
The phase's result is not the migration, which was four documents and a dry run.
It is that the premise the anatomy rests on was tested twice and answered
differently each time.

Asked as "is the extraction deterministic", the answer is yes, and firmly: the
same input gives the same output, down to the extracted images. Asked as "does
re-deriving reproduce what is on disk", the answer is no for two documents out of
three, because the script's own wording changed between the import and today.
Both answers are correct and they are answers to different questions. The one
that governs where a file lives is the second, and §11 had already said so in
the abstract: a file is disposable when a command can make it again *and nothing
is lost by making it later*. Nobody had seen it happen. Now it is in the record,
with the string that caused it.

The other thing worth carrying: `ingest.py` had recorded, for two years, a
provenance path that stopped existing when the repository reorganised. Nothing
noticed, because nothing ever read it back. A field written once and never read
is not provenance, it is a comment — and the fix was not to correct the path but
to keep the file it points at.

What Phase 4 needs to know first: the guard has a harder job than it looks. The
test that a document holds nothing the anatomy does not place must skip on a
fresh clone, where `library/` is empty or absent, like the rest of the suite that
reads documents kept outside the repository. And the hook that refuses a derived
write into `sources/` must not refuse acquisition — `make import` copies a PDF
there, `make fetch` writes `page.html.gz` there, and both are legitimate. The
distinction is about which tool is writing, not about the path, which is why
`protect-paths.sh` can make it and a test reading the filesystem afterwards
cannot.
