#!/usr/bin/env python3
"""Crop a region in fractions and enlarge it — or two photos, side by side.

    crop.py photo.jpg --region 0.05,0.15,0.62,0.85 --width 1500 -o detail.png
    crop.py a.jpg --compare b.png --region 0.05,0.50,0.24,0.78 --width 760 -o cmp.png

Reading a PCB's silkscreen, a hand-drawn schematic, one line of a parts list.
The region is in fractions of the image, never pixels, so a detail is aimed at
without knowing the image's size. The enlargement is LANCZOS: on 0.5 mm text it
decides between readable and not. That is what read `DT2`, `DT37`, `C188` on
the photos and settled three contradictory designations in the written sources.

`--compare` crops the same region of a second photo, normalises both to the
same width, and lays them side by side. Two photos of the same board area, by
two people, on two machines: the silkscreen settles what the forums disagree
on. Without the common width the comparison is skewed by scale, so it is
required.

The crop itself is core/imaging.crop.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from core import imaging

from _sourcing import ToolError, absolute, region, run

GAP = 20


def open_image(path: Path) -> Image.Image:
    try:
        with Image.open(path) as im:
            im.load()
            return im.convert("RGB")
    except FileNotFoundError:
        raise ToolError(f"{path}: no such file")
    except (UnidentifiedImageError, OSError):
        raise ToolError(f"{path}: not a readable image — an error page saved "
                        "under an image name?")


def cut(img: Image.Image, where, width: int | None, path: Path) -> Image.Image:
    try:
        return imaging.crop(img, where, width)
    except ValueError as exc:
        raise ToolError(f"{path}: {exc}")


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Fractional crop and enlargement.")
    ap.add_argument("image")
    ap.add_argument("--region", required=True, help="x0,y0,x1,y1 in fractions")
    ap.add_argument("--width", type=int, help="enlarge (LANCZOS) to this width")
    ap.add_argument("--compare", metavar="IMAGE",
                    help="crop the same region of a second image, side by side")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)

    where = region(args.region)
    src, output = absolute(args.image), absolute(args.output)
    left = cut(open_image(src), where, args.width, src)

    if args.compare:
        if not args.width:
            raise ToolError("--compare needs --width: both crops are normalised to "
                            "it, or the comparison is skewed by scale")
        other = absolute(args.compare)
        right = cut(open_image(other), where, args.width, other)
        out = Image.new("RGB", (2 * args.width + GAP, max(left.height, right.height)), "white")
        out.paste(left, (0, 0))
        out.paste(right, (args.width + GAP, 0))
        left = out

    output.parent.mkdir(parents=True, exist_ok=True)
    left.save(output)
    print(f"  ✓ {output}  ({left.width}×{left.height})")


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
