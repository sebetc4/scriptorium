#!/usr/bin/env python3
"""An Imgur album in full through the API, and a page's Imgur images as originals.

    imgur_album.py zEsqp                         # list
    imgur_album.py https://imgur.com/a/zEsqp --download raw/mcv
    imgur_album.py --scan raw/t94641-full.html   # a page's images, with context

An album page is assembled in JavaScript: its static HTML is 7 kB and cites one
image. The public API returns the whole list — 7 kB of HTML became fifteen
full-resolution images, without which the repair gallery was lost.

The `client_id` is the public Imgur web client's. It can stop working at any
moment; when Imgur refuses it, the tool says so rather than crashing.

**The thumbnail suffix.** Forum pages cite thumbnails only:
`https://i.imgur.com/<id>h.jpg` is 40 kB and unusable, `…/<id>.jpg` is the
3 MB original. An image id is seven characters, and a thumbnail appends one of
`s b t m l h`: `unthumb` strips it from an eight-character name only, so a short
id that happens to end in `h` is left alone.

`--scan` lists the Imgur images a saved page cites, as originals, each with the
text just before it — the caption, almost written. That is how every teardown
photo was matched to the chip it shows without opening twelve images.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys

from core import net

from _sourcing import ToolError, absolute, run, same_size

API = "https://api.imgur.com/post/v1/albums"
IMAGES = "https://i.imgur.com"
CLIENT_ID = "546c25a59c58ad7"
ALBUM_RE = re.compile(r"imgur\.com/(?:a|gallery)/([A-Za-z0-9]+)")
THUMB_RE = re.compile(r"(i\.imgur\.com/)([A-Za-z0-9]{7})[sbtmlh](\.[A-Za-z]+)")
IMAGE_LINK_RE = re.compile(r"https?://i\.imgur\.com/[A-Za-z0-9]{5,8}\.(?:jpe?g|png|gif|webp)")
CONTEXT_CHARS = 400


def unthumb(url: str) -> str:
    return THUMB_RE.sub(r"\1\2\3", url)


def album_media(album: str) -> list[dict]:
    ident = m.group(1) if (m := ALBUM_RE.search(album)) else album
    url = f"{API}/{ident}?client_id={CLIENT_ID}&include=media"
    try:
        r = net.get(url, headers={"Accept": "application/json"})
    except net.NetError as exc:
        raise ToolError(str(exc))
    if r.status in (401, 403, 429):
        raise ToolError(f"Imgur refused the request (HTTP {r.status}). The client_id is "
                        "the public web client's and may have been revoked or rate-limited: "
                        "take a current one from imgur.com's own requests, in "
                        "imgur_album.CLIENT_ID")
    if r.status == 404:
        raise ToolError(f"album {ident}: not found (HTTP 404)")
    if r.status != 200:
        raise ToolError(f"album {ident}: HTTP {r.status}\n    {r.line()}")
    try:
        media = json.loads(r.body).get("media") or []
    except ValueError:
        raise ToolError(f"album {ident}: the API did not answer JSON\n    {r.line()}")
    if not media:
        raise ToolError(f"album {ident}: no image in the API's answer")
    return media


def original_url(m: dict) -> str:
    return f"{IMAGES}/{m['id']}.{str(m.get('ext', 'jpg')).lstrip('.')}"


def download(media: list[dict], dest) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    problems, written = [], []
    for m in media:
        url = original_url(m)
        try:
            r = net.get(url)
        except net.NetError as exc:
            problems.append(f"{m['id']}: {exc}")
            continue
        if r.status != 200 or not r.mime.startswith("image/"):
            problems.append(f"{m['id']}: answered {r.mime}, not an image\n      {r.line()}")
            continue
        target = dest / url.rsplit("/", 1)[1]
        target.write_bytes(r.body)
        written.append(target)
        print(f"  ✓ {target}  ({r.size // 1024} kB)")
    for group in same_size(written):
        problems.append("identical size, probably one error page: "
                        + ", ".join(p.name for p in group))
    if problems:
        raise ToolError(f"{len(problems)} problem(s):\n    " + "\n    ".join(problems))


def scan(page) -> None:
    if not page.is_file():
        raise ToolError(f"{page}: no such file")
    text = page.read_text(encoding="utf-8", errors="replace")
    seen = set()
    for m in IMAGE_LINK_RE.finditer(text):
        url = unthumb(m.group(0))
        if url in seen:
            continue
        seen.add(url)
        before = re.sub(r"<[^>]+>", " ", text[max(0, m.start() - CONTEXT_CHARS):m.start()])
        context = html.unescape(re.sub(r"\s+", " ", before)).strip()[-160:]
        print(f"  {url}\n      « {context} »")
    if not seen:
        raise ToolError(f"{page}: no Imgur image cited")


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Imgur albums through the API.")
    ap.add_argument("album", nargs="?", help="an album id or URL")
    ap.add_argument("--download", metavar="DIR", help="fetch the originals into DIR")
    ap.add_argument("--scan", metavar="PAGE", help="list the Imgur images a saved page cites")
    args = ap.parse_args(argv)

    if args.scan:
        return scan(absolute(args.scan))
    if not args.album:
        raise ToolError("give an album id or URL, or --scan PAGE")
    media = album_media(args.album)
    for m in media:
        print(f"  {m['id']}  {m.get('width', '?')}×{m.get('height', '?')}  {original_url(m)}")
    if args.download:
        download(media, absolute(args.download))


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
