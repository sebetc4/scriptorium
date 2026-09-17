#!/usr/bin/env python3
"""The Wayback Machine through its CDX index: what is archived, and fetching it.

    wayback.py list "korgforums.com/forum/phpBB3/viewtopic.php?t=105619*"
    wayback.py check URL [URL …]
    wayback.py get URL [URL …] --dir raw/threads [--both]

Without it, the investigation had no primary source at all. It is a first-rank
tool, not a last resort.

- **CDX, not `wayback/available`.** The latter answers 429 after a few requests;
  CDX took some thirty without flinching.
- **`list`** takes a pattern: a trailing `*` matches by prefix, otherwise
  exactly. Captures that were errors are filtered out.
- **`check`** tells, for a batch of URLs, which have a capture — before
  downloading anything. Two topics out of twelve had none: known in five
  seconds, rather than learned from ten downloads.
- **`get`** fetches the latest capture of each URL, as the site served it
  (the `id_` form, without the archive's toolbar). For a phpBB thread it
  **prefers the print view** (`&view=print`) when that is archived: the whole
  thread on one page, 16 kB of clean text against 91 kB. The print view loses
  the attachment links, so `--both` also fetches the normal view, for a thread
  whose value is in its pictures.
- **Sizes are checked across the batch.** An archived thread's pages 2–4
  answered one 4,684-byte error page each; three identical sizes fail the run.

phpBB message permalinks (`p=`) are almost never archived, topic pages (`t=`)
almost always. When all that is known is a `p=`, forum_index.py rebuilds the
title → `t=` table from the archived listings.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core import net

from _sourcing import ToolError, absolute, run, same_size

CDX = "http://web.archive.org/cdx/search/cdx"
ARCHIVE = "https://web.archive.org/web"
CDX_TIMEOUT = 60
WORKERS = 6             # beyond 6 to 8 parallel requests, servers drop connections
# The index sheds load with a 503 or a 429 now and then — met live, on the second
# request of a batch. Worth waiting for, never worth abandoning the batch over.
RETRY_CODES = {429, 500, 502, 503, 504}
RETRY_WAITS = (2.0, 5.0, 10.0)


def cdx(pattern: str, *, collapse: bool = False, limit: int = 2000) -> list[tuple[str, str]]:
    """`(timestamp, original)` for every successful capture matching `pattern`."""
    params = {"url": pattern, "fl": "timestamp,original,statuscode",
              "filter": "statuscode:200", "limit": str(limit)}
    if collapse:
        params["collapse"] = "urlkey"
    for wait in (*RETRY_WAITS, None):
        try:
            r = net.get(f"{CDX}?{urllib.parse.urlencode(params)}", timeout=CDX_TIMEOUT)
        except net.NetError as exc:
            if wait is None:
                raise ToolError(f"the CDX index did not answer for {pattern} — {exc}")
        else:
            if r.status not in RETRY_CODES or wait is None:
                break
        time.sleep(wait)
    if r.status != 200:
        raise ToolError(f"the CDX index answered HTTP {r.status} for {pattern}\n    {r.line()}")
    rows = []
    for line in r.body.decode("utf-8", "replace").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            rows.append((parts[0], parts[1]))
    return rows


def archive_url(timestamp: str, original: str) -> str:
    """The capture as a reader opens it — the URL to cite."""
    return f"{ARCHIVE}/{timestamp}/{original}"


def raw_url(timestamp: str, original: str) -> str:
    """The capture as the site served it: `id_` stops the Wayback Machine from
    injecting its toolbar, which would otherwise open every transcription. It is
    also the truer piece — the bytes that were archived, nothing added."""
    return f"{ARCHIVE}/{timestamp}id_/{original}"


def print_view(url: str) -> str | None:
    """The phpBB print view of a thread URL, or None if it is not one."""
    if "viewtopic.php" not in url or "view=print" in url:
        return None
    return url + ("&" if "?" in url else "?") + "view=print"


def latest(url: str) -> tuple[str, str] | None:
    rows = cdx(url)
    return max(rows) if rows else None


def piece_name(timestamp: str, original: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", original.split("://", 1)[-1]).strip("-")[:120]
    return f"{slug}-{timestamp}.html"


def download(capture: tuple[str, str], dest: Path) -> tuple[Path | None, str]:
    timestamp, original = capture
    try:
        r = net.get(raw_url(timestamp, original), timeout=90)
    except net.NetError as exc:
        return None, f"✗ {original}: {exc}"
    if r.status != 200:
        return None, f"✗ {original}: {r.line()}"
    target = dest / piece_name(timestamp, original)
    target.write_bytes(r.body)
    return target, f"✓ {target}  ({r.size // 1024} kB)"


def cmd_list(args) -> None:
    rows = cdx(args.pattern, collapse=True)
    if not rows:
        raise ToolError(f"{args.pattern}: no capture")
    for timestamp, original in rows:
        print(f"  {timestamp}  {archive_url(timestamp, original)}")


def cmd_check(args) -> None:
    found, unanswered = 0, []
    for url in args.urls:
        try:
            rows = cdx(url)
        except ToolError as exc:
            unanswered.append(str(exc))
            print(f"  ? {url}  the index did not answer")
            continue
        if rows:
            found += 1
            print(f"  ✓ {url}  {len(rows)} capture(s), latest {max(rows)[0]}")
        else:
            print(f"  ✗ {url}  no capture")
    if unanswered:
        raise ToolError(f"{len(unanswered)} URL(s) left unchecked — a missing capture is "
                        "not established for them:\n    " + "\n    ".join(unanswered))
    if not found:
        raise ToolError("no capture for any URL of the batch")


def cmd_get(args) -> None:
    dest = absolute(args.dir)
    wanted: list[tuple[str, str]] = []
    for url in args.urls:
        printed = print_view(url)
        printed_capture = latest(printed) if printed else None
        if printed_capture:
            wanted.append(printed_capture)
        if args.both or not printed_capture:
            capture = latest(url)
            if capture:
                wanted.append(capture)
            elif not printed_capture:
                print(f"  ✗ {url}  no capture")
    if not wanted:
        raise ToolError("no capture to fetch — nothing written")

    dest.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(WORKERS) as pool:
        results = list(pool.map(lambda c: download(c, dest), wanted))
    written = [p for p, _ in results if p]
    for _, message in results:
        print(f"  {message}")
    problems = [m for p, m in results if not p]
    for group in same_size(written):
        problems.append("identical size, probably one error page archived several times: "
                        + ", ".join(p.name for p in group))
    if not written:
        raise ToolError("no capture could be fetched")
    if problems:
        raise ToolError("\n    ".join(problems))


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="The Wayback Machine through CDX.")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("list", help="captures matching a pattern (trailing * = prefix)")
    p.add_argument("pattern")
    p = sub.add_parser("check", help="which URLs of a batch have a capture")
    p.add_argument("urls", nargs="+")
    p = sub.add_parser("get", help="fetch the latest capture, print view preferred")
    p.add_argument("urls", nargs="+")
    p.add_argument("--dir", required=True)
    p.add_argument("--both", action="store_true", help="also the normal view of a phpBB thread")
    args = ap.parse_args(argv)
    {"list": cmd_list, "check": cmd_check, "get": cmd_get}[args.command](args)


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
