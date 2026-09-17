# Phase 7: The `translate` Skill

---

## Status

**Current Status:** 🟢 Done (100% — 12/12)
**Started:** 2026-09-16
**Completed:** 2026-09-16
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

Give translation its own skill, with an engine seam. Today the only engine is
the agent translating the Markdown in place; tomorrow a local model runs behind
the same contract. This phase builds the contract and wires the engine that
already exists. **It does not implement the local engine** — that work gets its
own roadmap.

---

## Overview

### Why This Phase Matters

Translation is currently a paragraph inside the import section of `pdf-doc`:
*"translate `index.md` in place, section by section"*. That is the procedure,
not the contract. It says nothing about what must not be translated, nothing
about how context is carried across paragraphs on a long document, nothing
about terminology.

Those gaps do not hurt while a model with full document context does the work.
They become the entire problem the moment a local engine translates chunk by
chunk with no memory between them. Writing the contract now, against the engine
that works, is what makes the swap a substitution rather than a rewrite.

### What It Enables

The local-model roadmap starts from a defined interface: what an engine
receives, what it returns, what it may never assume. It can then be judged on
translation quality alone rather than on integration.

### Out of Scope

- **Implementing the local engine.** No model is downloaded, no inference code
  is written, no GPU dependency enters `requirements.txt`. The seam is defined
  and the target models are recorded; the implementation is a separate roadmap.
- Extraction. `import` and `fetch` produce the untranslated Markdown; this
  skill acts on it.
- `library/` content. Documents already written in a language stay in it.

---

## Tasks

### The contract
- [x] Write `SKILL.md` in English: what translating a document of this library means, and where it sits after `import` and after `fetch`
- [x] Define the engine contract: one interface, two implementations — `agent` today, `local` tomorrow
- [x] Wire the `agent` engine: in-place translation of `index.md`, section by section, building between sections on a long document
- [x] Define how `lang:` in the front-matter, the document's hyphenation and the `TO=` of `import` and `fetch` line up, so the language is stated once and never re-asked

### What the engine must respect
- [x] Define the chunking that carries context across paragraphs rather than sending sentences alone
- [x] Define the protected zones: code blocks and spans, `:icon:` names, front-matter keys, diagram role names, admonition types
- [x] Define per-document terminology handling, and where a document's glossary lives
- [x] Define the quality control, including the two-engine cross-check the notes propose — *built and tested with a stand-in engine; never run with two real engines, since the second does not exist*

### The seam, and the handover
- [x] Write the `local` seam: what the engine receives, what it returns, and what it must never assume about the model behind it
- [x] Record in `docs/` the target engines — MADLAD-400 10B-MT and NLLB-200 3.3B — with what is known about their size and coverage, and without implementing them
- [x] Open a dedicated roadmap for the local implementation — *its five opening questions answered from this phase's decisions, not asked: see Notes*
- [x] Check that everything in `sources/translation/` has a home, and mark the archive as superseded

---

## Technical Details

### Files to Modify

```
.claude/skills/translate/SKILL.md   written in full
.claude/skills/translate/scripts/   the agent engine and the interface
.claude/skills/translate/tests/     protected zones, chunking, front-matter
docs/local-translation.md           the target engines, to be created
sources/translation/                marked superseded, kept as archive
```

### Dependencies

Phase 3 — `import` must already be inside `pdf` before `translate` can point at
what it produces.

### Constraints

- The document's structure is restored during translation, not after: the
  imported table of contents is dropped, scattered cover blocks move into
  `meta:`, text lines that were a table become a Markdown table again. The
  contract has to say whether that is the engine's job or the agent's — it is
  the agent's, and the engine must not be handed material it will mangle.
- A `:word:` in the source text can look like an icon. An unknown name renders
  as source text and the build reports it — the translation must not "fix" it.
- `sources/extracted.md` is an immutable reference. Nothing here edits it.

---

## Acceptance Criteria

- [x] A skill named `translate` holds the contract, the agent engine and its tests
- [x] Its `description` triggers on translating a document, and not on importing or capturing one
- [x] The engine interface is written down: inputs, outputs, and the assumptions an engine may not make
- [x] The agent engine runs through that interface, not beside it
- [x] The protected zones are tested: a code block, an icon name, a front-matter key and an admonition type survive a round trip untouched
- [x] The chunking preserves cross-paragraph context and is tested on a document long enough to need it
- [x] `docs/local-translation.md` records the target engines without adding a dependency
- [x] A roadmap for the local implementation exists under `docs/roadmap/pending/`
- [x] `sources/translation/` is marked superseded, nothing in it lost
- [x] `make test` is green

---

## Notes

### What the pending notes already settle

This roadmap's `sources/translation/index.md` argues for a pipeline rather than a
single call:

> original text → intelligent chunking → MADLAD-10B → NLLB check →
> terminology verification → final result

and insists that on long documents the context must be carried between
paragraphs rather than each sentence being sent independently. Both of those
are interface requirements, not model choices — which is exactly why they
belong to this phase and the model choice does not.

The two candidates recorded, for the roadmap that follows: MADLAD-400 10B-MT in
Q8_0 (~11 GB, translation-specific, T5-based, several hundred languages) as the
main engine, and NLLB-200 3.3B (~17.6 GB, 196 languages) as a comparison
engine. Both fit a 24 GB card. Nothing here commits to them.

### Why the seam is worth a phase on its own

The agent engine has a property no local model will have: it sees the whole
document, so chunking, terminology and context cost nothing to ignore. Every
requirement written here is therefore invisible today and load-bearing later.
Writing them while the working engine can validate them against real documents
is the only moment they can be checked cheaply.

### What was built

Five scripts in `.claude/skills/translate/scripts/`, 989 lines, and **79
tests**. The suite went 268 → 348, one of those in `fetch`.

- **`zones.py`** — the protected zones, as one left-to-right alternation, so a
  code span inside a fenced block is part of the block. `restore` refuses a
  placeholder that is missing, present twice or unknown. The front matter is
  read line by line rather than parsed and dumped, so the other keys, the
  comments and the padding survive. Only `title`, `subtitle`, `eyebrow` and
  `footer` are offered.
- **`chunking.py`** — blocks, never cut; chunks up to a budget, preferably
  starting at a heading and never ending on one. Each chunk carries whole
  context blocks and its headings, and the chunks join back byte for byte.
- **`engines.py`** — `Request`, the `Engine` protocol, and the six things an
  engine may not assume, in its docstring. `AgentEngine` answers through a
  request file and an answer file; `LocalEngine` raises and points to the
  hand-over. Both are in the registry and both satisfy the protocol.
- **`qc.py`** — the checks on each chunk (numbers with the decimal separator
  ignored, unchanged text, glossary, headings, list items, table cells,
  placeholders alone on their line) and a length warning. `cross_check`
  compares two engines.
- **`translate.py`** — `prepare`, `run`, `apply` and `cross-check`, with the
  workspace under `out/translate/`.

### How the agent engine goes *through* the interface

The criterion asked that the agent engine run "through that interface, not
beside it", and the agent cannot be called from Python. The resolution: its
`translate()` returns the answer file when it exists, and otherwise writes the
request and raises `Pending`. The runner treats both engines the same way:
every answer — the agent's or a model's — is validated, stored under
`responses/<engine>/`, checked by `apply`, and comparable by `cross-check`. The
tests exercise both paths: the agent's loop of requests and answers, and a
dictionary engine standing in for a model that answers at once.

### Two defects the real run found

The skill was run on a throwaway copy of `round-led-d4017`, a 3.8 kB English
kit manual. Its structure was restored first, then it was translated into
French by the agent engine, chunk by chunk, applied, built and looked at page
by page. The copy was then deleted.

1. **A chunk ended on a heading cut from its section.** "Circuit working
   principle" closed chunk 2, and its paragraph opened chunk 3. The synthetic
   long document never produced it: its headings always came past half the
   budget. A trailing heading now travels to the next chunk. The test first
   had a document too short to split, so it passed vacuously; it was caught by
   reading the chunk sizes, then fixed to fail without the change.
2. **Preparing again discarded every answer when the document or the budget
   changed — and kept every answer when only the chunking changed.** The second
   half is the dangerous one: an answer to one chunk's old text would have been
   applied to its new text. `prepare` now keeps exactly the answers whose chunk
   text is unchanged.

The review also showed a paragraph cut in two ("sans / manque") that the
extraction had split at a page break. It was not restored in the throwaway
copy, and the engine, as contracted, did not repair it. That is the evidence for
the ordering below.

### The import procedure had the order backwards

The `pdf` skill said to translate `index.md` and restore its structure "in the
same pass". This phase's constraint says an engine must not be handed material
it will mangle, so the structure comes first. The `pdf` skill's steps 2 and 3
are swapped, and "rejoin the paragraphs the extraction cut at a page break" was
added to the restoration list.

### The language, stated once

`lang:` is the target. `sources/meta.json`'s `source_language` is the source:
the PDF import already wrote it, and `fetch` now writes it too, from the page's
metadata or its detected language. `prepare` refuses:

- a document with no explicit `lang:`, rather than inherit `core/doc.py`'s
  default `fr`;
- a document whose source and target languages match, naming the line to change;
- a document already carrying `translated_from:`, the key `apply` adds.

### Decisions worth knowing

- **The workspace lives in `out/`,** not under the document: it is rebuilt by
  `prepare`, and `sources/` is provenance. The cost, stated in the skill: `make
  clean` loses a translation not yet applied.
- **`meta:` is not translated.** Its columns are proposed to the user with the
  rest of the cover.
- **No `make` target**, as `docs/architecture.md` §8 already ruled for the
  engine.
- **The glossary is `glossary.yaml` beside `index.md`,** versioned with the
  document it serves.

### The hand-over

`docs/local-translation.md` records the two candidates — figures **explicitly
marked as not re-verified**, and licences still to check — plus the pipeline
and what was not kept from the notes. It also names the two problems a real
model will meet and the agent does not: placeholders that a sentence-trained
model may not preserve, and context for a model that takes no prompt.

`docs/roadmap/pending/local-translation/` has three phases and 18 tasks:
verify and benchmark, the engine, the cross-check in practice. **Its five
opening questions were not asked.** The roadmap skill requires them, and this
session could not ask; they were answered from this phase's decisions, and the
roadmap's changelog says so and leaves them open to amendment.

### Every point of `sources/translation/`, and its home

| Notes | Home |
|---|---|
| MADLAD-400 10B-MT Q8_0, size, VRAM, llama.cpp + GGUF | `docs/local-translation.md` §2, marked unverified; roadmap Phase 0 |
| NLLB-200 3.3B as the comparison engine, its size, its research-model caveat | `docs/local-translation.md` §2 |
| the pipeline: chunking → MADLAD → NLLB → terminology → result | `docs/local-translation.md` §3; `chunking.py`, `cross-check`, `qc.py` |
| context carried between paragraphs on long documents | `chunking.py`; `Request.context_before`, `previous_translation` |
| preserve meaning, terminology, numbers, names, formatting; do not summarise | `engines.py` contract; `qc.py` numbers, glossary, structure |
| "MADLAD is not always better than NLLB": benchmark 20 passages | roadmap `local-translation`, Phase 0 |
| explicit FR ↔ EN direction | `lang:` and `source_language`, *The language, stated once* |
| the Windows procedure, `.srt` and `.docx` files | not kept, with the reason, `docs/local-translation.md` §4 |

The archive carries a "superseded" notice in French and is otherwise untouched.
