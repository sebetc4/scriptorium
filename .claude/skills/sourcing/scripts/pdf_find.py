#!/usr/bin/env python3
"""Which pages carry a term — and which pages have no text layer to search.

    pdf_find.py CPH6302 manuals/*.pdf
    pdf_find.py CPH6302 manuals/

Four service manuals, 79 pages, one second: the part was on pages 22, 12, 12
and 23/26. The match ignores case and spacing inside the term, because the
manuals wrote both `CPH6302` and `CPH 6302`.

**Pages with no text layer are reported on every run.** A scanned schematic
yields zero characters: a search that only reads text concludes "not in this
PDF" exactly where the answer is. Those pages are to be looked at — a contact
sheet (contact_sheet.py), then pdf_render.py.

Text extraction locates a page; it does not read a table. Datasheet tables come
out with their columns interleaved — render the page and read the image.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from core import net, pdfpage

from _sourcing import ToolError, absolute, run


def squeeze(text: str) -> str:
    return re.sub(r"\s+", "", text).casefold()


def pdfs(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for p in map(absolute, paths):
        found += sorted(p.glob("*.pdf")) if p.is_dir() else [p]
    return found


def pages_list(numbers: list[int]) -> str:
    return ", ".join(map(str, numbers))


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Locate a term in PDFs.")
    ap.add_argument("term")
    ap.add_argument("pdf", nargs="+", help="PDF files, or folders of them")
    args = ap.parse_args(argv)

    files = pdfs(args.pdf)
    if not files:
        raise ToolError("no PDF to search")
    needle = squeeze(args.term)
    total = 0
    for f in files:
        head = b""
        if f.is_file():
            with f.open("rb") as fh:
                head = fh.read(1024)
        if net.sniff(head) != "application/pdf":
            print(f"  ! {f}: not a PDF ({net.sniff(head) if head else 'missing'}) — skipped")
            continue
        texts = pdfpage.text(f)
        hits = [i + 1 for i, t in enumerate(texts) if needle in squeeze(t)]
        blind = [i + 1 for i, t in enumerate(texts) if not t.strip()]
        total += len(hits)
        found = f"page(s) {pages_list(hits)}" if hits else "not found"
        print(f"  {f}  {len(texts)} page(s) — {args.term}: {found}")
        if blind:
            print(f"      no text layer on page(s) {pages_list(blind)}: "
                  "not searched — render them to look")
    if not total:
        raise ToolError(f"“{args.term}” not found in any text layer — which proves "
                        "nothing about the pages that have none")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
