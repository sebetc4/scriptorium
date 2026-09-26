"""Images: writing extracted ones, cropping, and laying out a contact sheet.

`store` is shared by the PDF import and the web capture. `crop` and
`contact_sheet` are the bricks the sourcing tools stand on — kept here rather
than in the skill so that a second copy never appears (docs/architecture.md §2).

A source document readily stores photographs as PNG, which makes them an order
of magnitude heavier. What is photographic is recompressed to JPEG, and line
art, screenshots and anything carrying transparency are left as PNG — the places
where JPEG shows.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

JPEG_QUALITY = 88
MAX_IMAGE_PX = 2400     # beyond this, the image exceeds what a page can show
FLAT_COLORS = 4096      # below this colour count: line art or a screenshot, not a photo


def store(img: Image.Image, assets: Path, index: int,
          seen: dict[str, str]) -> str:
    """Write the image in the format that suits it, and return its name.

    `seen` maps a content digest to a filename: one visual repeated through the
    document is written only once.
    """
    if max(img.size) > MAX_IMAGE_PX:
        ratio = MAX_IMAGE_PX / max(img.size)
        img = img.resize((max(1, round(img.width * ratio)),
                          max(1, round(img.height * ratio))), Image.LANCZOS)

    # Transparency is read from the mode, not from the `transparency` key: that
    # one only exists for a palette. An LA or RGBA PNG — typically line art on a
    # transparent background — therefore passed as opaque and its background
    # turned black.
    has_alpha = (img.mode in ("RGBA", "LA", "PA")
                 or (img.mode == "P" and "transparency" in img.info))
    if has_alpha:
        # Flattened onto white rather than kept: on a dark background, black
        # line art on transparency becomes invisible. A white patch stays
        # readable in both themes.
        img = Image.alpha_composite(
            Image.new("RGBA", img.size, (255, 255, 255, 255)), img.convert("RGBA"))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    digest = hashlib.sha1(img.tobytes()).hexdigest()
    if digest in seen:
        return seen[digest]

    flat = img.mode == "L" or img.getcolors(FLAT_COLORS) is not None
    if flat:
        name = f"img-{index:03d}.png"
        img.save(assets / name, optimize=True)
    else:
        name = f"img-{index:03d}.jpg"
        img.save(assets / name, quality=JPEG_QUALITY, optimize=True)
    seen[digest] = name
    return name


def to_png(img: Image.Image) -> bytes:
    """PNG bytes, optimised. The tail every rasterising caller shares."""
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# --------------------------------------------------------------------------
# Crop
# --------------------------------------------------------------------------
Region = tuple[float, float, float, float]


def crop(img: Image.Image, region: Region, width: int | None = None) -> Image.Image:
    """Cut `region` out of `img`, optionally enlarged to `width` pixels.

    The region is `(x0, y0, x1, y1)` in **fractions** of the image, never in
    pixels: a detail is aimed at without knowing the image's dimensions, and the
    same fractions aim at the same place on a thumbnail and on the original.

    The enlargement is LANCZOS. On printed text half a millimetre high, the
    difference from the default resampling decides between readable and not.
    """
    x0, y0, x1, y1 = region
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise ValueError(f"region {region}: expected 0 ≤ x0 < x1 ≤ 1 and "
                         "0 ≤ y0 < y1 ≤ 1, in fractions of the image")
    w, h = img.size
    box = (round(w * x0), round(h * y0), round(w * x1), round(h * y1))
    if box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError(f"region {region} holds no pixel of a {w}×{h} image")
    out = img.crop(box)
    if width:
        out = out.resize((width, max(1, round(out.height * width / out.width))),
                         Image.LANCZOS)
    return out


# --------------------------------------------------------------------------
# Contact sheet
# --------------------------------------------------------------------------
LABEL_HEIGHT = 26       # px: the band above each thumbnail that carries its name
CELL_PAD = 4


def contact_sheet(items: list[tuple[str, Image.Image]], columns: int = 4,
                  cell: tuple[int, int] = (560, 340)) -> Image.Image:
    """Lay out labelled thumbnails in a grid, on white.

    Each `(label, image)` becomes one cell: the label written in the band at
    the top, the image shrunk to fit below it. **The label is not optional** —
    without it, the interesting image is seen without knowing which one it is.

    The defaults give a 2240 px wide sheet at four columns. Aim for about 2000:
    a wider sheet is scaled down to be looked at, and the labels stop being
    readable.
    """
    if not items:
        raise ValueError("a contact sheet needs at least one image")
    cw, ch = cell
    rows = -(-len(items) // columns)
    sheet = Image.new("RGB", (columns * cw, rows * ch), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    for i, (label, img) in enumerate(items):
        x, y = (i % columns) * cw, (i // columns) * ch
        thumb = img.convert("RGB")
        thumb.thumbnail((cw - 2 * CELL_PAD, ch - LABEL_HEIGHT - CELL_PAD), Image.LANCZOS)
        sheet.paste(thumb, (x + CELL_PAD, y + LABEL_HEIGHT))
        draw.text((x + CELL_PAD + 2, y + 4), label, fill="black", font=font)
    return sheet
