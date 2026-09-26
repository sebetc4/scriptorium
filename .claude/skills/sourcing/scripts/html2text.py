#!/usr/bin/env python3
"""HTML → readable text, trying a Discourse forum's JSON first.

    html2text.py raw/t12345-print.html
    html2text.py https://forum.example.com/t/some-thread/1499
    html2text.py raw/t12345-print.html.gz -o threads/t12345.md \\
        --url <original URL> --archive <archive URL> --conditions "…"

The most used tool of the investigation, about ten times, and the shortest.
Four details decide between readable text and an unreadable slab, all learned
the hard way:

- `<script>` and `<style>` are removed **before** the tags, or their content
  surfaces in the text;
- `<br>` and closing block tags become line breaks **before** stripping, or the
  messages run together;
- entities are unescaped **after** stripping, or an escaped `<b>` in a message
  is stripped as a tag;
- bytes are decoded with `errors="replace"`: old forums declare UTF-8 and serve
  Latin-1.

It is deliberately blunter than trafilatura, which `fetch` uses. On an archived
forum page, with the Wayback toolbar injected, guessing the "main content"
does worse than keeping everything and stripping it cleanly.

**Discourse first.** A Discourse thread at `/t/<slug>/<id>` also answers at
`/t/<slug>/<id>.json`: authors, dates and clean bodies, no fragile regex. It
worked first time on a site whose HTML pages answered 403. It costs one request,
so it is tried on every URL of that shape before the page itself.

With `-o`, the transcription is written with its provenance header — original
URL, archive URL, retrieval date and **the conditions of the collection** ("the
forum answered 500, only the Wayback Machine was reachable"). That header is
what keeps a transcription citable once the page is gone.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import json
import re
import sys
import urllib.parse

from core import net

from _sourcing import ToolError, absolute, run

DISCOURSE_PATH_RE = re.compile(r"^/t/[^/]+/\d+/?$")


def strip(markup: str) -> str:
    """The stripping order is the point; see the module docstring."""
    s = re.sub(r"(?is)<script.*?</script>", "", markup)
    s = re.sub(r"(?is)<style.*?</style>", "", s)
    s = re.sub(r"(?is)<!--.*?-->", "", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|tr|li|h[1-6]|td|th|blockquote|pre)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return s.strip()


def discourse_posts(data: dict) -> str:
    posts = (data.get("post_stream") or {}).get("posts") or []
    if not posts:
        raise ToolError("a Discourse thread with 0 post — nothing to transcribe")
    blocks = []
    if data.get("title"):
        blocks.append(f"# {data['title']}")
    for p in posts:
        body = re.sub(r"\s+", " ", strip(p.get("cooked", ""))).strip()
        blocks.append(f"### {p.get('username', '?')} — {str(p.get('created_at', ''))[:10]}\n\n{body}")
    return "\n\n".join(blocks)


def decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def from_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    if DISCOURSE_PATH_RE.match(parts.path):
        json_url = urllib.parse.urlunsplit(parts._replace(path=parts.path.rstrip("/") + ".json",
                                                          query="", fragment=""))
        try:
            response = net.get(json_url, headers={"Accept": "application/json"})
        except net.NetError:
            response = None
        if response is not None and response.status == 200:
            try:
                data = json.loads(response.body)
            except ValueError:
                data = None
            if isinstance(data, dict) and "post_stream" in data:
                print(f"  · Discourse: read through {json_url}")
                return discourse_posts(data)

    try:
        response = net.get(url)
    except net.NetError as exc:
        raise ToolError(str(exc))
    if response.status != 200:
        raise ToolError(f"the page answered HTTP {response.status}\n    {response.line()}")
    if response.mime not in ("text/html", "application/octet-stream"):
        raise ToolError(f"this URL serves {response.mime}, not a page\n    {response.line()}")
    return strip(decode(response.body))


def from_file(path) -> str:
    if not path.is_file():
        raise ToolError(f"{path}: no such file")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    if path.name.removesuffix(".gz").endswith(".json"):
        try:
            data = json.loads(raw)
        except ValueError:
            raise ToolError(f"{path}: not valid JSON")
        return discourse_posts(data)
    return strip(decode(raw))


def header(args) -> str:
    lines = ["---"]
    if args.url:
        lines.append(f"url: {args.url}")
    if args.archive:
        lines.append(f"archive: {args.archive}")
    lines.append(f"retrieved: {dt.date.today().isoformat()}")
    if args.conditions:
        lines.append(f"conditions: {json.dumps(args.conditions, ensure_ascii=False)}")
    lines.append("note: verbatim transcription; markup stripped, text untouched")
    return "\n".join(lines + ["---", "", ""])


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="HTML to readable text; Discourse JSON first.")
    ap.add_argument("source", help="a file (.html, .html.gz, .json) or an http(s) URL")
    ap.add_argument("-o", "--output", help="write the transcription, with its header")
    ap.add_argument("--url", help="original URL, for the provenance header")
    ap.add_argument("--archive", help="archive URL, for the provenance header")
    ap.add_argument("--conditions", help="how the collection went, for the header")
    args = ap.parse_args(argv)

    if urllib.parse.urlsplit(args.source).scheme in ("http", "https"):
        text = from_url(args.source)
    else:
        text = from_file(absolute(args.source))
    if not re.search(r"\w", text):
        raise ToolError(f"{args.source}: no text after stripping — nothing written")

    if not args.output:
        print(text)
        return
    output = absolute(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(header(args) + text + "\n", encoding="utf-8")
    print(f"  ✓ {output}  ({len(text.splitlines())} lines)")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
