"""What every sourcing tool holds, written once.

The investigation these tools come from met the same two failures in every
kind of script, and both were silent (sources/sourcing/outillage-sourcing.md
§8, in the repo-overhaul roadmap):

1. **Absolute paths.** The working directory is reset between two tool calls: a
   relative write in a background task lands elsewhere, and nothing says so.
   Every path a tool receives is resolved at once, and printed resolved.
2. **Fail loudly on an empty result.** "0 messages transcribed" written to a
   file believed full; three files of identical size that were three error
   pages. A tool that finds nothing raises `ToolError` and exits 1.

Named with a leading underscore: a helper of this skill's tools, not a tool.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path


class ToolError(Exception):
    """A result the user must not mistake for a success."""


def run(main: Callable[[list[str] | None], object], argv: list[str] | None = None) -> int:
    """Run a tool's main, turning a `ToolError` into a message and status 1."""
    try:
        main(argv)
    except ToolError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def absolute(path: str | Path) -> Path:
    """The path resolved now, against the working directory of this call."""
    return Path(path).expanduser().resolve()


def region(text: str) -> tuple[float, float, float, float]:
    """`x0,y0,x1,y1` in fractions of the image — never pixels."""
    try:
        values = tuple(float(v) for v in text.split(","))
    except ValueError:
        raise ToolError(f"region “{text}”: four numbers expected, e.g. 0.05,0.15,0.62,0.85")
    if len(values) != 4:
        raise ToolError(f"region “{text}”: four fractions expected, x0,y0,x1,y1")
    x0, y0, x1, y1 = values
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ToolError(f"region “{text}”: fractions of the image, with "
                        "0 ≤ x0 < x1 ≤ 1 and 0 ≤ y0 < y1 ≤ 1 — not pixels")
    return values


SAME_SIZE_THRESHOLD = 3


def same_size(paths: Iterable[Path]) -> list[list[Path]]:
    """Groups of three or more files with rigorously identical sizes.

    Checking each file alone misses it; across a batch it is plain: three
    archived pages of a thread at 4,684 bytes each were three copies of the
    same error page. Two is a coincidence worth nothing; three is a suspicion.
    """
    by_size: dict[int, list[Path]] = defaultdict(list)
    for p in paths:
        if p.is_file():
            by_size[p.stat().st_size].append(p)
    return [group for _, group in sorted(by_size.items())
            if len(group) >= SAME_SIZE_THRESHOLD]
