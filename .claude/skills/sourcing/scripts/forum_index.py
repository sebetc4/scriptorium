#!/usr/bin/env python3
"""Rebuild a dead forum's title → topic id table from its archived listings.

    forum_index.py "forum.example.org/viewforum.php?f=48" --grep manual
    forum_index.py "forum.example.org/viewforum.php?f=48" -o topics.tsv --dir raw/f48

**phpBB message permalinks (`p=`) are almost never archived; topic pages (`t=`)
almost always are.** Secondary sources — articles, conversations, quotes — only
ever give `p=`. The eight starting links of the investigation were all `p=`,
with zero captures, and the forum being dead there was no redirect to follow.

What unblocked it: list every archived capture of the sub-forum's listing pages,
fetch them, and read the (topic id, title) pairs out of them. The title is then
looked up in the table, and the `t=` comes with it — `t=12345`, the thread
sought. Then wayback.py fetches the thread.

The listing's query parameters are matched exactly: `f=48` is not `f=480`.
Topics are read with the phpBB `topictitle` pattern first, then a generic one
covering `viewtopic.php?t=`, vBulletin's `showthread.php?t=` and SMF's
`index.php?topic=`. Which pattern served is printed, since templates vary and a
listing that yields nothing must be noticed, not trusted.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from core import net

from _sourcing import ToolError, absolute, run, same_size

import wayback

WORKERS = 8
PATTERNS = [
    ("phpBB topictitle",
     re.compile(r'<a\b[^>]*href="[^"]*viewtopic\.php\?[^"]*?\bt=(\d+)[^"]*"[^>]*class="[^"]*\btopictitle\b[^"]*"[^>]*>(.*?)</a>', re.S)),
    ("generic topic link",
     re.compile(r'<a\b[^>]*href="[^"]*(?:viewtopic\.php|showthread\.php|index\.php)\?[^"]*?\b(?:t|topic)=(\d+)[^"]*"[^>]*>(.*?)</a>', re.S)),
]


def topics(markup: str) -> tuple[dict[int, str], str | None]:
    for name, pattern in PATTERNS:
        found = {}
        for ident, title in pattern.findall(markup):
            clean = html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
            if clean:
                found[int(ident)] = clean
        if found:
            return found, name
    return {}, None


def same_params(original: str, wanted: dict[str, list[str]]) -> bool:
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(original).query)
    return all(query.get(k) == v for k, v in wanted.items())


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Title → topic id, from archived forum listings.")
    ap.add_argument("listing", help="the listing URL without scheme, e.g. site/viewforum.php?f=48")
    ap.add_argument("--grep", help="print only the titles containing this (case-insensitive)")
    ap.add_argument("-o", "--output", help="write the table as TSV: id<TAB>title")
    ap.add_argument("--dir", help="keep the fetched listings here, as pieces")
    args = ap.parse_args(argv)

    base, _, query = args.listing.partition("?")
    wanted = urllib.parse.parse_qs(query)
    captures = [c for c in wayback.cdx(base.split("://", 1)[-1] + "*", collapse=True)
                if same_params(c[1], wanted)]
    if not captures:
        raise ToolError(f"{args.listing}: no capture of that listing")

    def fetch(capture):
        try:
            return capture, net.get(wayback.raw_url(*capture), timeout=90)
        except net.NetError as exc:
            return capture, exc

    with ThreadPoolExecutor(WORKERS) as pool:
        results = list(pool.map(fetch, captures))

    pieces = absolute(args.dir) if args.dir else None
    if pieces:
        pieces.mkdir(parents=True, exist_ok=True)
    table: dict[int, str] = {}
    kept = []
    for (timestamp, original), r in results:
        if isinstance(r, Exception) or r.status != 200:
            print(f"  ✗ {original}: {r if isinstance(r, Exception) else r.line()}")
            continue
        found, pattern = topics(r.body.decode("utf-8", "replace"))
        print(f"  {original} ({timestamp}): {len(found)} topic(s)"
              + (f", {pattern}" if pattern else ""))
        table.update(found)
        if pieces:
            target = pieces / wayback.piece_name(timestamp, original)
            target.write_bytes(r.body)
            kept.append(target)
    for group in same_size(kept):
        print("  ! identical size, probably one error page: " + ", ".join(p.name for p in group))
    if not table:
        raise ToolError("no topic recognised in any listing — the template may differ "
                        "from the known patterns: open one listing and look")

    rows = sorted(table.items())
    if args.output:
        output = absolute(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("".join(f"{i}\t{t}\n" for i, t in rows), encoding="utf-8")
        print(f"  ✓ {output}  ({len(rows)} topics)")
    if args.grep:
        rows = [(i, t) for i, t in rows if args.grep.casefold() in t.casefold()]
        if not rows:
            raise ToolError(f"no title matches “{args.grep}” among {len(table)} topics")
    if args.grep or not args.output:
        for i, t in rows:
            print(f"{i}\t{t}")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
