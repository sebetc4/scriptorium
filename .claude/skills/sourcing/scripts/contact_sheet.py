#!/usr/bin/env python3
"""A contact sheet: a folder of images, or a PDF's pages, in one look.

    contact_sheet.py <folder|file.pdf> -o sheet.png [--pages 3-12] [--columns 4]

The best benefit-to-effort ratio of the whole toolkit: fifteen photos from one
thread, fifteen from another, nine pages of drawings — each time one sheet,
one look, two images kept. Every thumbnail carries its filename, or its page number.

Past PER_SHEET thumbnails the sheet is split, `sheet-01.png`, `sheet-02.png`:
a taller sheet is scaled down to be looked at, and the labels stop being
readable. The layout itself is core/imaging.contact_sheet; a PDF's pages are
rendered by core/pdfpage.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from core import imaging, pdfpage

from _sourcing import ToolError, absolute, run

CELL = (560, 340)
PER_SHEET = 16
PDF_SCALE = 2           # enough to sort pages; reading one is pdf_render.py
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}


def folder_items(folder: Path) -> list[tuple[str, Image.Image]]:
    items, unreadable = [], []
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            with Image.open(f) as im:
                im.load()
                items.append((f.name, im.copy()))
        except (UnidentifiedImageError, OSError):
            unreadable.append(f.name)
    for name in unreadable:
        print(f"  ! {name}: not a readable image — an error page saved under an image name?")
    return items


def page_range(text: str | None, count: int) -> range:
    if not text:
        return range(count)
    first, _, last = text.partition("-")
    try:
        start, stop = int(first), int(last or first)
    except ValueError:
        raise ToolError(f"--pages “{text}”: expected N or N-M")
    if not 1 <= start <= stop <= count:
        raise ToolError(f"--pages “{text}”: the document has {count} page(s)")
    return range(start - 1, stop)


def pdf_items(pdf: Path, pages: str | None) -> list[tuple[str, Image.Image]]:
    count = len(pdfpage.text(pdf))
    return [(f"page {i + 1}", pdfpage.render_page(pdf, i, scale=PDF_SCALE))
            for i in page_range(pages, count)]


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Contact sheet of a folder of images or of a PDF.")
    ap.add_argument("source", help="a folder of images, or a PDF")
    ap.add_argument("-o", "--output", required=True, help="the sheet, a .png")
    ap.add_argument("--pages", help="for a PDF: a page or a range, e.g. 3-12")
    ap.add_argument("--columns", type=int, default=4)
    args = ap.parse_args(argv)

    source, output = absolute(args.source), absolute(args.output)
    if source.is_dir():
        items = folder_items(source)
    elif source.suffix.lower() == ".pdf" and source.is_file():
        items = pdf_items(source, args.pages)
    else:
        raise ToolError(f"{source}: neither a folder nor a PDF")
    if not items:
        raise ToolError(f"{source}: no image to lay out")

    batches = [items[i:i + PER_SHEET] for i in range(0, len(items), PER_SHEET)]
    output.parent.mkdir(parents=True, exist_ok=True)
    for n, batch in enumerate(batches, 1):
        target = (output if len(batches) == 1
                  else output.with_name(f"{output.stem}-{n:02d}{output.suffix}"))
        imaging.contact_sheet(batch, columns=args.columns, cell=CELL).save(target)
        print(f"  ✓ {target}  ({len(batch)} thumbnail(s))")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
