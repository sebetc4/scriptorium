# Local translation — the target engines

Handed over by Phase 7 of the [repo-overhaul roadmap](roadmap/on-progress/repo-overhaul/README.md).
Nothing described here is implemented. No model is downloaded, no inference
code exists, and no dependency was added to `requirements.txt`. The work that
implements it has its own roadmap: [local-translation](roadmap/pending/local-translation/README.md).

What *is* built is the seam: the `local` engine in
`.claude/skills/translate/scripts/engines.py`, which raises until that roadmap
fills it in, and the contract it has to honour.

---

## 1. What an engine must do

The contract is `engines.py`'s docstring, and it is the authority. In short, an
engine receives a `Request`:

| Field | What it holds |
|---|---|
| `text` | one chunk of Markdown, with placeholders `⟦n⟧` for code, icons, links and markup |
| `source_lang`, `target_lang` | short codes, `en`, `fr` |
| `context_before` | the whole blocks just before the chunk — to read, not to translate |
| `previous_translation` | the engine's own translation of the chunk before |
| `headings` | the headings the chunk sits under |
| `glossary`, `keep` | terms to translate as given, terms never to translate |

and returns the translated chunk. It may not assume that it sees the document,
that the text is plain prose, that the structure is its to change, that numbers
and references are text, that the glossary is advice, or that the context is to
be translated. The runner and `qc.py` catch a breach; they do not trust it away.

Two consequences for a model that knows nothing about Markdown or placeholders:

- **The placeholders have to survive tokenisation and generation.** A
  translation model trained on plain sentences may drop, merge or translate
  `⟦12⟧`. The implementation has to measure that before anything else, and is
  free to swap the placeholders for something the model preserves better, as
  long as it swaps them back before returning.
- **The context has to reach a model with no prompt.** A pure MT model takes a
  source sentence and a language tag, not instructions. Carrying
  `context_before` and `previous_translation` means feeding them as preceding
  input and cutting their translation back out of the output — or accepting a
  shorter context. Which one works is an experiment, not a decision to take
  here.

## 2. The target engines

As recorded in the notes this roadmap consumed (2026-09-12), for a machine with
a 24 GB GPU. The figures come from the models' pages at that date and were **not
re-verified** when this document was written; the implementing roadmap checks
them first.

### Main engine — MADLAD-400 10B-MT

| | |
|---|---|
| Model | `google/madlad400-10b-mt` |
| Kind | translation-specific, T5-based (encoder–decoder) |
| Coverage | more than 400 languages; the target language is set by a prefix tag |
| Quantised | GGUF Q8_0 about 11 GB, about 11.3 GB of VRAM fully offloaded (`thirteenbit/madlad400-10b-mt-gguf`, `NikolayKozloff/madlad400-10b-mt-Q8_0-GGUF`) |
| Runtime considered | llama.cpp with GGUF, rather than Ollama, because Q8_0 checkpoints are published and documented for it |
| Why Q8_0 | the VRAM allows it; Q4 to Q6 would trade quality for nothing |

Its model card says quality varies with the language and the domain. That the
10B is better than NLLB for English ↔ French on this library's documents is
**not established**.

### Comparison engine — NLLB-200 3.3B

| | |
|---|---|
| Model | `facebook/nllb-200-3.3B` |
| Coverage | 200 languages (196 in the notes' count) |
| Size | official checkpoint about 17.6 GB |
| Role | second engine for the cross-check, not the main one |
| Caveat | Meta presents it as a research model, not intended for specialised texts or document translation |

**The licences are to be checked before either model is used**, and recorded
here: they decide whether a translated document may be shared.

## 3. The pipeline the notes argue for

```
source text → chunking → MADLAD-10B → NLLB check → terminology check → result
```

Every step but the two models already exists in the skill: `chunking.py`,
`translate.py cross-check`, and `qc.py`'s glossary, number and structure
checks. The local engine plugs in as the MADLAD step; a second local engine,
or the `agent` engine, is the check.

## 4. What the notes proposed, and what was not kept

- **A benchmark before choosing.** Some twenty representative passages, French
  ↔ English, scored on fidelity, fluency, terminology and meaning errors, across
  MADLAD 10B Q8, MADLAD 7B Q8 and NLLB 3.3B. Kept: it is the implementing
  roadmap's first phase.
- **A strict instruction prompt** ("preserve meaning, terminology, numbers…").
  Recorded but not kept as such: MADLAD and NLLB are not instruction-following
  models. What the prompt asked for is enforced by the checks instead.
- **A Windows installation procedure and a script translating `.txt`, `.srt`,
  `.docx`.** Not kept. This repository translates documents of its library, on
  the machine the library lives on, through the `translate` skill.
