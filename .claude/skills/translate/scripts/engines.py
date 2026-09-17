"""The engine contract: what a translation engine receives, returns, and may not assume.

One interface, two implementations:

- **`agent`** — the engine that exists today: the agent running this skill
  translates each chunk itself. It cannot be called from Python, so its side
  of the interface is a pair of files: `translate()` writes the request the
  agent reads and raises `Pending`; once the agent has written the answer
  file, `translate()` returns it. The runner validates that answer exactly as
  it would validate a model's.
- **`local`** — the seam for a local model. Not implemented: it raises
  `EngineUnavailable`, and its own roadmap fills it in.

An engine receives a `Request` and returns the translated text. What it may
**not** assume, whatever model is behind it:

1. **That it sees the document.** It sees one chunk, the blocks just before it
   as context, the headings above it, and its own previous output. Anything
   else is out of reach.
2. **That the text is plain prose.** It is Markdown with placeholders, `⟦n⟧`,
   standing for code, icons, links and markup. Every placeholder must come back
   exactly once, unchanged, and one alone on its line stays alone on its line.
3. **That the structure is its to change.** Headings, list items, table rows
   and blank lines come back as they went. The document's structure was
   restored before translation, by the agent (the `pdf` skill's import steps);
   an engine is never handed a structure to repair.
4. **That numbers, units, part references and proper names are text.** They
   come back identical, only a decimal separator may follow the target
   language.
5. **That the glossary is advice.** A term in `glossary` is translated as given;
   a term in `keep` is not translated at all.
6. **That the context is to be translated.** `context_before` and
   `previous_translation` are for reading only.

A breach of 2 to 5 is caught by the runner and `qc.py`, not trusted away.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Request:
    index: int
    total: int
    source_lang: str
    target_lang: str
    text: str
    context_before: str = ""
    previous_translation: str = ""
    headings: tuple[str, ...] = ()
    glossary: dict[str, str] | None = None
    keep: tuple[str, ...] = ()


class Pending(Exception):
    """The engine has not answered yet — the agent has a request to read."""

    def __init__(self, request_path: Path, answer_path: Path):
        super().__init__(f"waiting for {answer_path}")
        self.request_path, self.answer_path = request_path, answer_path


class EngineUnavailable(Exception):
    """The engine cannot run here."""


@runtime_checkable
class Engine(Protocol):
    name: str

    def translate(self, request: Request) -> str: ...


INSTRUCTIONS = """\
Translate the text below from {source} to {target}.

- Translate only what is between the two markers. Write nothing else in the
  answer file: no note, no explanation, no marker.
- Every placeholder such as ⟦12⟧ comes back exactly once and unchanged. It
  stands for code, an icon, a link or markup. A placeholder alone on its line
  stays alone on its line.
- Keep the Markdown structure as it is: the same headings (#), list items, table
  rows and pipes, blank lines.
- Numbers, units, part references and proper names stay identical; only the
  decimal separator may follow {target}.
- Do not summarise, add or omit anything.
- The context and your previous translation are there to be read, not
  translated: keep terminology and tone consistent with them.
"""


def render(request: Request, answer_path: Path) -> str:
    """The request as the agent reads it."""
    parts = [f"# Chunk {request.index + 1} of {request.total} — "
             f"{request.source_lang} → {request.target_lang}",
             f"Write the translation to:\n\n    {answer_path}",
             INSTRUCTIONS.format(source=request.source_lang, target=request.target_lang)]
    if request.headings:
        parts.append("## Where this chunk sits\n\n" + " › ".join(request.headings))
    if request.glossary:
        parts.append("## Glossary — use these translations\n\n" + "\n".join(
            f"- {s} → {t}" for s, t in request.glossary.items()))
    if request.keep:
        parts.append("## Never translate\n\n" + "\n".join(f"- {k}" for k in request.keep))
    if request.context_before:
        parts.append("## Context before — read, do not translate\n\n" + request.context_before)
    if request.previous_translation:
        parts.append("## Your previous translation — for consistency\n\n"
                     + request.previous_translation)
    parts.append("## Text to translate\n\n<<<<<<<< BEGIN\n" + request.text
                 + ("" if request.text.endswith("\n") else "\n") + ">>>>>>>> END")
    return "\n\n".join(parts) + "\n"


class AgentEngine:
    name = "agent"

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def request_path(self, index: int) -> Path:
        return self.workspace / "requests" / f"{index:03d}.md"

    def answer_path(self, index: int) -> Path:
        return self.workspace / "responses" / self.name / f"{index:03d}.md"

    def translate(self, request: Request) -> str:
        answer = self.answer_path(request.index)
        if answer.is_file():
            return answer.read_text(encoding="utf-8")
        path = self.request_path(request.index)
        path.parent.mkdir(parents=True, exist_ok=True)
        answer.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(request, answer), encoding="utf-8")
        raise Pending(path, answer)


class LocalEngine:
    """The seam for a local model. Its contract is this module's docstring."""
    name = "local"

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def translate(self, request: Request) -> str:
        raise EngineUnavailable(
            "the local engine is not implemented yet. The target models and the "
            "plan are in docs/local-translation.md, and the work has its own "
            "roadmap: docs/roadmap/pending/local-translation/")


ENGINES: dict[str, type] = {"agent": AgentEngine, "local": LocalEngine}
