#!/usr/bin/env python3
"""The corpus read across reviews, rather than one review at a time.

One review's findings are anecdotes. What this prints is what only a corpus can
say: what a kind of task costs here, which target keeps coming back, which
findings were written and never carried anywhere, and how much of the work
nobody sat down to review at all.

Text on stdout, in the idiom of `make list`. No chart, no HTML, no artifact:
this is read in a terminal by someone deciding what to fix next.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corpus  # noqa: E402

# The measures a baseline is worth printing for. Each is a dotted path into
# `measured:`, read through `Review.measure()`, so an absent one is absent and
# never a zero.
BASELINE = [
    ("fresh", "tokens.fresh"),
    ("cached", "tokens.cache_read"),
    ("output", "tokens.output"),
    ("delegated", "subagents.fresh"),
    ("turns", "turns"),
    ("images", "images"),
]


def as_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def baselines(reviews: list[corpus.Review]) -> list[str]:
    """What a task of each skill costs here, as the median of what they cost.

    The median and not the mean: one session that went badly wrong should move
    a baseline, not define it.
    """
    by_skill: dict[str, list[corpus.Review]] = defaultdict(list)
    for review in reviews:
        by_skill[review.skill].append(review)

    rows = [f"{'skill':<12}{'n':>3}" + "".join(f"{name:>11}"
                                               for name, _ in BASELINE)]
    for skill, group in sorted(by_skill.items()):
        line = f"{skill:<12}{len(group):>3}"
        for _, measure in BASELINE:
            values = [r.measure(measure) for r in group]
            values = [v for v in values if v is not None]
            line += f"{statistics.median(values):>11,.0f}" if values else f"{'—':>11}"
        rows.append(line)
    return rows


def findings(reviews: list[corpus.Review]) -> list[str]:
    """Ranked by recurrence first, severity second.

    Recurrence is the signal a single review cannot produce: two reviews naming
    the same file for the same reason say something neither of them could. That
    is why `kind` is a closed vocabulary and `target` a path — so that the same
    complaint written twice lands in the same bucket.
    """
    weight = {"high": 3, "medium": 2, "low": 1}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for review in reviews:
        for finding in review.findings:
            groups[(finding["kind"], finding["target"])].append(finding)

    rows = []
    for (kind, target), group in sorted(
            groups.items(),
            key=lambda kv: (-len(kv[1]),
                            -max(weight.get(f.get("severity"), 0) for f in kv[1]),
                            kv[0])):
        worst = max(group, key=lambda f: weight.get(f.get("severity"), 0))
        carried = sum(1 for f in group if f.get("carried"))
        mark = "carried" if carried else "not carried"
        rows.append(f"{len(group):>3}×  {worst['severity']:<7}{kind:<15}"
                    f"{target}  ({mark})")
        rows.append(f"     {worst['fix']}")
    return rows


def never_carried(reviews: list[corpus.Review]) -> list[str]:
    """High findings nobody turned into roadmap work.

    `reviews/` is not versioned: a finding that is never carried changes
    nothing, whatever it said. This list is the backlog the corpus is owed.
    """
    seen: dict[tuple[str, str], list[str]] = defaultdict(list)
    for review in reviews:
        for finding in review.findings:
            if finding.get("severity") == "high" and not finding.get("carried"):
                seen[(finding["kind"], finding["target"])].append(
                    str(review.meta["date"]))
    return [f"{len(dates)}×  {kind:<15}{target}  (first seen {min(dates)})"
            for (kind, target), dates in
            sorted(seen.items(), key=lambda kv: -len(kv[1]))]


def around(reviews: list[corpus.Review], pivot: date) -> list[str]:
    """Before and after a date: did the thing that was carried change anything?

    A finding is carried, a roadmap acts on it, and this is the only way to ask
    whether that was worth the trouble. It compares medians, and says how many
    reviews each side rests on, because two against one is not evidence.
    """
    rows = []
    for skill in sorted({r.skill for r in reviews}):
        group = [r for r in reviews if r.skill == skill]
        before = [r for r in group if (d := as_date(r.meta["date"])) and d < pivot]
        after = [r for r in group if (d := as_date(r.meta["date"])) and d >= pivot]
        if not before or not after:
            continue
        line = f"{skill:<12}{len(before):>3} → {len(after):<3}"
        for name, measure in BASELINE[:4]:
            was = [v for v in (r.measure(measure) for r in before) if v is not None]
            now = [v for v in (r.measure(measure) for r in after) if v is not None]
            if not was or not now:
                line += f"{'—':>11}"
                continue
            change = statistics.median(now) / statistics.median(was)
            line += f"{name} ×{change:.2f}".rjust(11)
        rows.append(line)
    if not rows:
        rows = [f"no skill has reviews on both sides of {pivot}"]
    return rows


def coverage(reviews: list[corpus.Review], ledger_dir: Path) -> list[str]:
    rows = []
    for row in corpus.coverage(reviews, ledger_dir):
        gaps = ", ".join(f"{a:%Y-%m-%d %H:%M}–{b:%H:%M}"
                         for a, b in row["uncovered"]) or "—"
        rows.append(f"{row['session'][:8]}  {row['turns']:>4} turns  "
                    f"{row['reviews']} review(s)  uncovered: {gaps}")
    if not rows:
        return ["no ledger yet"]
    covered = sum(1 for r in corpus.coverage(reviews, ledger_dir)
                  if not r["uncovered"])
    return rows + ["", f"{covered}/{len(rows)} session(s) fully reviewed"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The corpus, read across reviews.")
    ap.add_argument("--dir", type=Path, default=corpus.REVIEWS)
    ap.add_argument("--ledger-dir", type=Path, default=corpus.LEDGER)
    ap.add_argument("--skill", help="restrict the baselines to one skill")
    ap.add_argument("--coverage", action="store_true",
                    help="which sessions of the ledger carry a review")
    ap.add_argument("--around", metavar="YYYY-MM-DD",
                    help="compare the reviews before and after a date")
    args = ap.parse_args(argv)

    try:
        reviews = corpus.load(args.dir)
    except corpus.ReviewError as e:
        print(f"aggregate: {e}", file=sys.stderr)
        return 1

    if args.coverage:
        print("\n".join(coverage(reviews, args.ledger_dir)))
        return 0

    if not reviews:
        print("no review yet")
        return 0

    if args.around:
        pivot = as_date(args.around)
        if pivot is None:
            print(f"aggregate: not a date: {args.around}", file=sys.stderr)
            return 1
        print("\n".join(around(reviews, pivot)))
        return 0

    if args.skill:
        reviews = [r for r in reviews if r.skill == args.skill]

    print("\n".join(baselines(reviews)))
    if rows := findings(reviews):
        print("\nfindings, by recurrence then severity\n")
        print("\n".join(rows))
    if rows := never_carried(reviews):
        print("\nhigh findings never carried\n")
        print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
