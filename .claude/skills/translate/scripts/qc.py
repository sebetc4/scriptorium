"""Quality control: what a translated chunk must have kept.

Errors block the translation from being written into the document; warnings
are printed for the review. Every check compares a chunk's source with its
translation — both still carrying their placeholders, so markup never counts.

Errors:
- a number lost or changed — `2.1` and `2,1`, `1 000` and `1000` are the same;
- a chunk returned unchanged;
- a glossary term not translated as given, a term to keep that was translated;
- a heading, a list item or a table row lost, a row's cells changed;
- a placeholder that stood alone on its line and no longer does.

Warning:
- a length far from the source's, the sign of an omission or an addition.

`cross_check` compares two engines' translations of the same chunks and names
the chunks where they disagree: that is where a human reads first.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

import zones

NUMBER_RE = re.compile(r"\d+(?:[.,   ]\d+)*")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]", re.M)
LIST_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]", re.M)
ROW_RE = re.compile(r"^[ \t]*\|.*$", re.M)
LONE_TOKEN_RE = re.compile(r"^[ \t]*(⟦\d+⟧)[ \t]*$", re.M)
LENGTH_RATIO = (0.5, 2.0)
LENGTH_MIN = 120      # below this, one added word already swings the ratio
CROSS_RATIO = (0.67, 1.5)


@dataclass
class Finding:
    chunk: int
    level: str          # "error" | "warning"
    message: str


def numbers(text: str) -> Counter:
    """The numbers of a text, separators removed, placeholders ignored."""
    text = zones.TOKEN_RE.sub(" ", text)
    return Counter(re.sub(r"\D", "", n) for n in NUMBER_RE.findall(text))


def structure(text: str) -> dict[str, object]:
    return {
        "headings": Counter(len(m) for m in HEADING_RE.findall(text)),
        "list items": len(LIST_RE.findall(text)),
        "table rows": [row.count("|") for row in ROW_RE.findall(text)],
    }


def _contains(text: str, term: str, case: bool) -> bool:
    flags = 0 if case else re.I
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, flags) is not None


def check_chunk(index: int, source: str, target: str, source_lang: str,
                target_lang: str, glossary: dict[str, str] | None = None,
                keep: tuple[str, ...] = ()) -> list[Finding]:
    found: list[Finding] = []

    def error(message: str) -> None:
        found.append(Finding(index, "error", message))

    prose = zones.TOKEN_RE.sub("", source)
    if target.strip() == source.strip() and len(re.findall(r"[^\W\d_]", prose)) >= 20:
        error(f"returned unchanged — still in {source_lang}?")

    lost = numbers(source) - numbers(target)
    if lost:
        error("number(s) lost or changed: " + ", ".join(sorted(lost.elements())))

    for term, translation in (glossary or {}).items():
        if _contains(source, term, case=False) and not _contains(target, translation, case=False):
            error(f"glossary: “{term}” must be translated as “{translation}”")
    for term in keep:
        if _contains(source, term, case=True) and not _contains(target, term, case=True):
            error(f"“{term}” is to be kept as it is, and is missing")

    s, t = structure(source), structure(target)
    if s["headings"] != t["headings"]:
        error(f"heading count changed: {dict(s['headings'])} → {dict(t['headings'])}")
    if s["list items"] != t["list items"]:
        error(f"list items changed: {s['list items']} → {t['list items']}")
    if s["table rows"] != t["table rows"]:
        error("table rows or their cells changed")

    lone = set(LONE_TOKEN_RE.findall(source)) - set(LONE_TOKEN_RE.findall(target))
    if lone:
        error("placeholder(s) no longer on their own line: " + ", ".join(sorted(lone)))

    if len(source) >= LENGTH_MIN:
        ratio = len(target) / len(source)
        if not LENGTH_RATIO[0] <= ratio <= LENGTH_RATIO[1]:
            found.append(Finding(index, "warning",
                                 f"length ×{ratio:.2f} of the source — an omission or an addition?"))
    return found


def cross_check(sources: dict[int, str], a: dict[int, str], b: dict[int, str],
                names: tuple[str, str]) -> list[Finding]:
    """The chunks where two engines' translations disagree."""
    found = []
    for index in sorted(sources):
        ta, tb = a.get(index, ""), b.get(index, "")
        reasons = []
        if numbers(ta) != numbers(tb):
            reasons.append("numbers")
        if structure(ta) != structure(tb):
            reasons.append("structure")
        if ta and tb and not CROSS_RATIO[0] <= len(ta) / len(tb) <= CROSS_RATIO[1]:
            reasons.append(f"length ({len(ta)} against {len(tb)} characters)")
        if reasons:
            found.append(Finding(index, "warning",
                                 f"{names[0]} and {names[1]} disagree on "
                                 + ", ".join(reasons) + " — read this chunk first"))
    return found
