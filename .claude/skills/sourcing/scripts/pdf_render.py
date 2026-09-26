#!/usr/bin/env python3
"""Render one PDF page at high resolution, and crop it to read a detail.

    pdf_render.py manual.pdf 4 --scale 6 --region 0.34,0.48,0.72,0.80 -o detail.png

The procedure is two steps: find the page at `scale=2` (contact_sheet.py on the
PDF), then read it at `scale=6` with a crop. At 6, an A3 drawing is some
7000 × 5000 px, and its smallest labels and values become readable.

Pages count from 1, as a reader of the document counts them. The rendering is
core/pdfpage.render_page; the crop is core/imaging.crop.
"""
from __future__ import annotations

import argparse
import sys

from core import imaging, net, pdfpage

from _sourcing import ToolError, absolute, region, run

DEFAULT_SCALE = 6


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Render a PDF page, optionally cropped.")
    ap.add_argument("pdf")
    ap.add_argument("page", type=int, help="the page number, from 1")
    ap.add_argument("--scale", type=float, default=DEFAULT_SCALE)
    ap.add_argument("--region", help="x0,y0,x1,y1 in fractions of the page")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)

    src, output = absolute(args.pdf), absolute(args.output)
    where = region(args.region) if args.region else None
    if not src.is_file():
        raise ToolError(f"{src}: no such file")
    with src.open("rb") as fh:
        mime = net.sniff(fh.read(1024))
    if mime != "application/pdf":
        raise ToolError(f"{src}: {mime}, not a PDF — an error page or a signup wall "
                        "saved under a .pdf name?")
    try:
        image = pdfpage.render_page(src, args.page - 1, scale=args.scale)
    except IndexError:
        count = len(pdfpage.text(src))
        raise ToolError(f"{src}: page {args.page} does not exist, the document has {count}")
    if where:
        try:
            image = imaging.crop(image, where)
        except ValueError as exc:
            raise ToolError(f"{src}, page {args.page}: {exc}")

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"  ✓ {output}  ({image.width}×{image.height})")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
