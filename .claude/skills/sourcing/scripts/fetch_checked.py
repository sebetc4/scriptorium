#!/usr/bin/env python3
"""Download a file only if it is the file: probe, check the bytes, try mirrors.

    fetch_checked.py URL [URL …] -o documents/notice.pdf
    fetch_checked.py URL [URL …] -o file.bin --expect application/pdf
    fetch_checked.py --probe URL [URL …]

Several `.pdf` URLs answered HTTP 200 with HTML — a signup wall, an error page,
a redirect page. A script that trusts the status and the extension archives
error pages believing it archives documents. So every response is probed and
its type read from the bytes (core/net.py), and the URLs are tried in order
until one serves the expected type: one maker's document took four attempts,
five aggregators answered 403, and an obscure mirror served it. The chain stops
at the first real hit; the URLs after it are never requested.

The expected type comes from the output name (`.pdf`, `.png`, `.jpg`, `.html`…)
or from `--expect`. Nothing is written unless a URL served it — not an empty
file, not the last error page.

`--probe` is the first move of any investigation: one line per URL, nothing
kept. It is how a whole forum was found answering 500 in three seconds, and the
work moved to the archives instead of a dozen failed downloads.
"""
from __future__ import annotations

import argparse
import sys

from core import net

from _sourcing import ToolError, absolute, run

MAX_BYTES = 200 * 1024 * 1024
EXPECTED = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
            ".svg": "image/svg+xml", ".html": "text/html", ".htm": "text/html"}


def probe(urls: list[str]) -> None:
    answered = 0
    for url in urls:
        try:
            r = net.get(url, max_bytes=MAX_BYTES)
        except net.NetError as exc:
            print(f"  ✗ {exc}")
            continue
        answered += 1
        print(f"  {r.line()} → {r.mime}")
    if not answered:
        raise ToolError("no URL answered at all")


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Checked download through a mirror chain.")
    ap.add_argument("urls", nargs="+", metavar="URL", help="tried in order")
    ap.add_argument("-o", "--output", help="where the first real file is written")
    ap.add_argument("--expect", metavar="MIME", help="the type to accept, if the name does not say")
    ap.add_argument("--probe", action="store_true", help="one line per URL, nothing written")
    args = ap.parse_args(argv)

    if args.probe:
        return probe(args.urls)
    if not args.output:
        raise ToolError("-o is required, unless --probe")
    output = absolute(args.output)
    expect = args.expect or EXPECTED.get(output.suffix.lower())
    if not expect:
        raise ToolError(f"{output.name}: its name says no type — pass --expect, "
                        "e.g. --expect application/pdf")

    for url in args.urls:
        try:
            r = net.get(url, max_bytes=MAX_BYTES)
        except net.NetError as exc:
            print(f"  ✗ {exc}")
            continue
        print(f"  {r.line()} → {r.mime}")
        if r.status != 200:
            continue
        if r.mime != expect:
            print(f"    not {expect}: skipped")
            continue
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(output.name + ".part")
        partial.write_bytes(r.body)
        partial.replace(output)
        print(f"  ✓ {output}  ({r.size // 1024} kB, from {r.effective_url})")
        return
    raise ToolError(f"no URL served {expect} — nothing written")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
