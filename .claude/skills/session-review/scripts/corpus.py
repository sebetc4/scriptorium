#!/usr/bin/env python3
"""The corpus of reviews: read it, refuse what is malformed, compute medians.

Everything downstream reads reviews through this module. `metrics.py` asks it
for the median of a measure so that a number can be printed beside the one it
just counted; `aggregate.py` asks it for the findings. Neither parses a review
itself, and nothing parses the body: a review's prose is for a person.

The medians are the reason this belongs in the foundation rather than in the
reports. A session comparing its own cost to nothing at all will find it
reasonable. Comparing it to the median of previous tasks of the same skill is
the one defence against that which costs nothing to run.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

from core.doc import ROOT, split_front_matter

REVIEWS = ROOT / "reviews"

# The current format version. Reviews of different versions are never compared:
# a measure's meaning is part of the format that defines it.
VERSION = 1

KINDS = {
    "skill-gap",
    "skill-drift",
    "tooling-gap",
    "tooling-noise",
    "waste",
    "art-direction",
    "process",
    "unverified",
}
SEVERITIES = {"low", "medium", "high"}
OUTCOMES = {"delivered", "partial", "abandoned"}

REQUIRED = ("review", "date", "session", "slice", "task", "skill",
            "outcome", "corrections", "findings")


class ReviewError(Exception):
    """A review that cannot be trusted. Always names the file."""


@dataclass(frozen=True)
class Review:
    path: Path
    meta: dict
    body: str

    @property
    def version(self) -> int:
        return self.meta["review"]

    @property
    def skill(self) -> str:
        return self.meta["skill"]

    @property
    def measured(self) -> dict:
        return self.meta.get("measured") or {}

    @property
    def findings(self) -> list[dict]:
        return self.meta["findings"] or []

    def measure(self, path: str):
        """One measure by dotted path, or None when the review does not carry it.

        `tokens.fresh` reads a mapping. `subagents.fresh` sums the field across
        every run, because a review records runs separately and a median over
        runs of different sessions would compare nothing. Under `derived`, the
        trailing `.value` is implied: a derived measure is its number, and its
        `rule` travels with it for a reader, not for arithmetic.
        """
        node = self.measured
        parts = path.split(".")
        for i, part in enumerate(parts):
            if isinstance(node, list):
                got = [item.get(part) for item in node
                       if isinstance(item, dict) and part in item]
                if not got or not all(isinstance(v, (int, float)) for v in got):
                    return None
                node = sum(got)
                continue
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
            if (i == len(parts) - 1 and isinstance(node, dict)
                    and parts[0] == "derived"):
                node = node.get("value")
        return node if isinstance(node, (int, float)) else None


def _fail(path: Path, why: str) -> None:
    raise ReviewError(f"{path.name}: {why}")


def validate(review: Review) -> None:
    meta, path = review.meta, review.path
    for field in REQUIRED:
        if field not in meta:
            _fail(path, f"front matter has no “{field}”")
    if not isinstance(meta["review"], int):
        _fail(path, f"“review” is not a version number: {meta['review']!r}")
    if meta["outcome"] not in OUTCOMES:
        _fail(path, f"unknown outcome “{meta['outcome']}” "
                    f"(expected: {', '.join(sorted(OUTCOMES))})")
    if not isinstance(meta["slice"], dict) or not {"from", "to"} <= set(meta["slice"]):
        _fail(path, "“slice” needs a “from” and a “to”")
    if not isinstance(meta["findings"], list):
        _fail(path, "“findings” is a list, written “findings: []” when empty")

    for n, finding in enumerate(meta["findings"], 1):
        if not isinstance(finding, dict):
            _fail(path, f"finding {n} is not a mapping")
        kind = finding.get("kind")
        if kind not in KINDS:
            _fail(path, f"finding {n} has unknown kind “{kind}” "
                        f"(expected: {', '.join(sorted(KINDS))})")
        if finding.get("severity") not in SEVERITIES:
            _fail(path, f"finding {n} has unknown severity "
                        f"“{finding.get('severity')}” "
                        f"(expected: {', '.join(sorted(SEVERITIES))})")
        # The rule from references/findings.md, enforced rather than asked for:
        # without both, it is a complaint and it belongs in the prose.
        for field in ("target", "fix"):
            if not str(finding.get(field, "")).strip():
                _fail(path, f"finding {n} ({kind}) has no “{field}”")

    for run in review.measured.get("subagents") or []:
        if not isinstance(run, dict) or "type" not in run:
            _fail(path, "every entry of “measured.subagents” needs a “type”")


def read(path: Path) -> Review:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ReviewError(f"{path.name}: unreadable ({e})") from e
    try:
        meta, body = split_front_matter(text)
    except Exception as e:
        raise ReviewError(f"{path.name}: front matter is not YAML ({e})") from e
    if not meta:
        raise ReviewError(f"{path.name}: no front matter")
    review = Review(path, meta, body)
    validate(review)
    return review


def load(directory: Path | str = REVIEWS) -> list[Review]:
    """Every review of the corpus, oldest first. One bad file stops the read."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    reviews = [read(p) for p in sorted(directory.glob("*.md"))]
    return sorted(reviews, key=lambda r: str(r.meta["date"]))


def median(reviews: list[Review], measure: str, *, skill: str | None = None,
           version: int = VERSION, exclude: Path | None = None) -> float | None:
    """The median of one measure, or None when there is no baseline yet.

    None is the answer for an empty corpus *and* for a single review, and the
    distinction matters: a median of one is that one review, and a session
    compared against itself is exactly the self-flattery the corpus exists to
    prevent. A caller must be able to tell “no baseline yet” from “baseline of
    nothing”, so this returns None rather than 0.
    """
    values = [r.measure(measure) for r in reviews
              if r.version == version
              and (skill is None or r.skill == skill)
              and (exclude is None or r.path != exclude)]
    values = [v for v in values if v is not None]
    if len(values) < 2:
        return None
    return statistics.median(values)


def skills(reviews: list[Review]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in reviews:
        counts[r.skill] = counts.get(r.skill, 0) + 1
    return dict(sorted(counts.items()))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The corpus of session reviews.")
    ap.add_argument("--dir", default=REVIEWS, type=Path,
                    help="the corpus directory (default: reviews/)")
    ap.add_argument("--skill", help="restrict to one skill")
    ap.add_argument("--median", metavar="MEASURE",
                    help="print the median of one measure, e.g. tokens.fresh")
    args = ap.parse_args(argv)

    try:
        reviews = load(args.dir)
    except ReviewError as e:
        print(f"corpus: {e}", file=sys.stderr)
        return 1

    if args.median:
        value = median(reviews, args.median, skill=args.skill)
        print("—" if value is None else f"{value:g}")
        return 0

    if not reviews:
        print("no review yet")
        return 0
    for r in reviews:
        if args.skill and r.skill != args.skill:
            continue
        findings = len(r.findings)
        print(f"{r.meta['date']}  {r.skill:<9} {findings:>2} finding(s)  "
              f"{r.path.name}")
    print(f"\n{len(reviews)} review(s): "
          + ", ".join(f"{k} {v}" for k, v in skills(reviews).items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
