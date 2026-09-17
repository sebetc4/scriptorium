"""The protected zones: what an engine must never be given to translate.

A code block, a code span, an icon name, an admonition type, a link target, an
attribute list, raw HTML, a footnote label, a table's separator row. Each is
replaced by a placeholder, `⟦n⟧`, before the engine sees the text, and put back
afterwards. What the engine never sees, it cannot translate, "fix" or reflow:
that holds for a model that understands Markdown and, above all, for one that
does not.

An unknown icon name — a `:word:` in the source text that is not a Lucide icon
— is protected like a real one. The build renders it as source text and reports
it; a translation that "corrected" it would hide the report.

The front matter is not masked but read: its keys are never offered, and only
the strings a reader sees on the page — `title`, `subtitle`, `eyebrow`,
`footer` — are translated, then written back into their own line, so the other
keys, the comments and the layout of the block are left exactly as they were.
"""
from __future__ import annotations

import json
import re

import yaml


class ZoneError(Exception):
    """A placeholder was lost, doubled or invented — or cannot be placed."""


OPEN, CLOSE = "⟦", "⟧"
TOKEN_RE = re.compile(r"⟦(\d+)⟧")

# One alternation, scanned left to right: at any position, the zone that starts
# first wins, so a code span inside a fenced block is part of the block. Order
# among alternatives only matters for zones starting at the same character.
ZONE_RE = re.compile(r"""
    (?P<fence>^[ \t]*(?P<mark>`{3,}|~{3,})[^\n]*\n.*?^[ \t]*(?P=mark)[ \t]*$)
  | (?P<comment><!--.*?-->)
  | (?P<span>(?P<tick>`+)(?!`).+?(?<!`)(?P=tick)(?!`))
  | (?P<autolink><https?://[^>\s]+>)
  | (?P<tag></?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>)
  | (?P<admonition>^[ \t]*(?:!!!|\?\?\?\+?)[ \t]+[\w-]+)
  | (?P<footnote>\[\^[^\]\s]+\]:?)
  | (?P<attrs>\{:[^}\n]*\})
  | (?P<target>\]\([^)\s]+)
  | (?P<url>https?://[^\s<>()\[\]]+[^\s<>()\[\].,;:!?'"])
  | (?P<separator>^[ \t]*\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-{3,}:?[ \t]*)*\|?[ \t]*$)
  | (?P<icon>:[a-z0-9][a-z0-9-]*(?:\.[a-z]+)?:)
""", re.M | re.S | re.X)


def token(n: int) -> str:
    return f"{OPEN}{n}{CLOSE}"


def protect(text: str, start: int = 1) -> tuple[str, dict[str, str]]:
    """The text with every protected zone replaced, and the table to restore it.

    `start` numbers the placeholders from an offset, so that the chunks of one
    document share one table without two placeholders colliding.
    """
    if OPEN in text or CLOSE in text:
        raise ZoneError(f"the text already contains “{OPEN}” or “{CLOSE}”, "
                        "the placeholder marks: it cannot be protected safely")
    table: dict[str, str] = {}

    def replace(m: re.Match) -> str:
        t = token(start + len(table))
        table[t] = m.group(0)
        return t

    return ZONE_RE.sub(replace, text), table


def restore(text: str, table: dict[str, str]) -> str:
    """Put the zones back, refusing a placeholder lost, doubled or invented."""
    seen = TOKEN_RE.findall(text)
    counts: dict[str, int] = {}
    for n in seen:
        counts[token(int(n))] = counts.get(token(int(n)), 0) + 1
    problems = []
    unknown = sorted(t for t in counts if t not in table)
    if unknown:
        problems.append(f"unknown placeholder(s) {', '.join(unknown)}")
    missing = [t for t in table if t not in counts]
    if missing:
        problems.append(f"missing placeholder(s) {', '.join(missing)}")
    doubled = sorted(t for t, c in counts.items() if c > 1 and t in table)
    if doubled:
        problems.append(f"placeholder(s) present more than once {', '.join(doubled)}")
    if problems:
        raise ZoneError("; ".join(problems))
    return TOKEN_RE.sub(lambda m: table[m.group(0)], text)


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------
DISPLAYED = ("title", "subtitle", "eyebrow", "footer")


def _line_value(line: str, key: str) -> tuple[str, str, str] | None:
    """`(before, value source, after)` for a `key: value  # comment` line."""
    m = re.match(rf"^({re.escape(key)}:[ \t]*)(.*)$", line)
    if not m:
        return None
    before, rest = m.groups()
    try:
        full = (yaml.safe_load(line) or {}).get(key)
    except yaml.YAMLError:
        return None
    if not isinstance(full, str):
        return None
    for c in re.finditer(r"[ \t]+#", rest):
        candidate = rest[:c.start()]
        try:
            if (yaml.safe_load(f"k: {candidate}") or {}).get("k") == full:
                return before, candidate, rest[c.start():]
        except yaml.YAMLError:
            continue
    return before, rest, ""


def front_matter_strings(front: str) -> dict[str, str]:
    """The displayed strings of a front matter block, by key."""
    found = {}
    for line in front.splitlines():
        for key in DISPLAYED:
            if (parts := _line_value(line, key)) is not None:
                found[key] = yaml.safe_load(f"k: {parts[1]}")["k"]
    return found


def _scalar(value: str) -> str:
    """The value as plain YAML when that reads back identically, else quoted."""
    plain = value.strip() == value and not value.startswith(("'", '"'))
    if plain:
        try:
            if (yaml.safe_load(f"k: {value}") or {}).get("k") == value:
                return value
        except yaml.YAMLError:
            pass
    return json.dumps(value, ensure_ascii=False)


def set_front_matter_strings(front: str, strings: dict[str, str]) -> str:
    """Write translated strings back into their own lines, nothing else moved."""
    out = []
    for line in front.splitlines(keepends=True):
        body, newline = (line[:-1], "\n") if line.endswith("\n") else (line, "")
        for key, value in strings.items():
            if (parts := _line_value(body, key)) is not None:
                before, _, after = parts
                body = f"{before}{_scalar(value)}{after}"
                break
        out.append(body + newline)
    return "".join(out)
