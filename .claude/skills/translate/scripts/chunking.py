"""Splitting a document's body into chunks that carry their context.

An engine that receives a sentence alone translates it without knowing what
"it" refers to, which term the previous paragraph settled, or that the section
is about a river bank rather than a savings bank. So the body is cut at block
boundaries, never inside one — a paragraph, a list, a table, a fenced code
block, an admonition with its indented body — packed up to a budget, preferably
starting at a heading. Each chunk carries:

- `context_before`: the whole blocks just before it, up to a size — to read,
  not to translate;
- `headings`: the headings it sits under, so an engine knows what the section
  is about.

The chunks join back into the body byte for byte. A block larger than the
budget is kept whole in a chunk of its own and flagged `oversized`: cutting a
paragraph in two would lose exactly the context this module exists to keep.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
DEFAULT_BUDGET = 6000
DEFAULT_CONTEXT = 1200


@dataclass
class Chunk:
    index: int
    text: str
    context_before: str = ""
    headings: list[str] = field(default_factory=list)
    oversized: bool = False


def blocks(body: str) -> list[str]:
    """The body as blocks, each carrying the blank lines that follow it."""
    lines = body.splitlines(keepends=True)
    out: list[list[str]] = []
    fence: str | None = None
    blank_run = False
    for line in lines:
        stripped = line.strip()
        if fence is not None:
            out[-1].append(line)
            m = FENCE_RE.match(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and stripped == m.group(1):
                fence = None
            continue
        if not stripped:
            if not out:
                out.append([])
            out[-1].append(line)
            blank_run = True
            continue
        indented = line.startswith(("    ", "\t"))
        if not out or (blank_run and not indented and out[-1]):
            # A block with only blank lines so far (the body's leading ones)
            # takes the first real line rather than standing alone.
            if not out or any(l.strip() for l in out[-1]):
                out.append([])
        out[-1].append(line)
        blank_run = False
        if m := FENCE_RE.match(line):
            fence = m.group(1)
    return ["".join(b) for b in out]


def _heading(block: str) -> tuple[int, str] | None:
    first = block.lstrip("\n").split("\n", 1)[0]
    if m := HEADING_RE.match(first):
        return len(m.group(1)), m.group(2).strip()
    return None


def split(body: str, budget: int = DEFAULT_BUDGET,
          context: int = DEFAULT_CONTEXT) -> list[Chunk]:
    groups: list[tuple[list[str], bool]] = []
    current: list[str] = []
    size = 0
    for block in blocks(body):
        if len(block) > budget:
            # The headings just before an oversized block introduce it: they
            # travel with it rather than closing the previous chunk.
            carried = _trailing_headings(current)
            if current[:len(current) - len(carried)]:
                groups.append((current[:len(current) - len(carried)], False))
            groups.append((carried + [block], True))
            current, size = [], 0
            continue
        starts_section = _heading(block) is not None and size >= budget / 2
        if current and (size + len(block) > budget or starts_section):
            carried = _trailing_headings(current)
            if len(carried) < len(current):
                groups.append((current[:len(current) - len(carried)], False))
                current = carried
                size = sum(map(len, current))
        current.append(block)
        size += len(block)
    if current or not groups:
        groups.append((current, False))

    chunks: list[Chunk] = []
    before: list[str] = []
    stack: dict[int, str] = {}          # level → the heading in effect
    for i, (group, oversized) in enumerate(groups):
        in_effect = dict(stack)
        if group and (h := _heading(group[0])):
            _nest(in_effect, *h)
        headings = [in_effect[level] for level in sorted(in_effect)]
        chunks.append(Chunk(i, "".join(group), context_of(before, context), headings, oversized))
        for block in group:
            if h := _heading(block):
                _nest(stack, *h)
        before.extend(group)
    return chunks


def _trailing_headings(group: list[str]) -> list[str]:
    """The heading blocks that end a group — they belong with what follows."""
    n = 0
    for block in reversed(group):
        if _heading(block) is None:
            break
        n += 1
    return group[len(group) - n:] if n else []


def _nest(stack: dict[int, str], level: int, title: str) -> None:
    """A heading replaces the one at its level and closes every deeper one."""
    for deeper in [l for l in stack if l >= level]:
        del stack[deeper]
    stack[level] = title


def context_of(before: list[str], limit: int) -> str:
    """The whole blocks just before, up to `limit` characters — at least one."""
    taken: list[str] = []
    total = 0
    for block in reversed(before):
        text = block.strip()
        if not text:
            continue
        if taken and total + len(text) + 2 > limit:
            break
        taken.insert(0, text)
        total += len(text) + 2
    return "\n\n".join(taken)
