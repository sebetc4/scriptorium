"""Rendering a PDF page to an image, and reading its text layer, over pypdfium2.

The brick the repository held three times: the EPUB backbone rasterises its
diagrams and composes its cover through it, and the review sheets render their
six-inch screens through it. The PDF review loop, written as prose in the `pdf`
skill, calls it too (`.claude/skills/pdf/SKILL.md`, *Build, then review*).

The three code callers want the same thing — *give me this page at this pixel width*
— and each was computing the scale factor from `get_width()` itself. That
computation is the whole reason this module exists: it is the step that is easy
to get subtly wrong and impossible to notice, since a wrong scale still yields a
plausible image.
"""
from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def render(source: Path | bytes, *, width_px: int | None = None,
           scale: float | None = None) -> list[Image.Image]:
    """Every page of `source`, as PIL images.

    `width_px` targets a pixel width and derives the scale per page, so pages of
    different sizes come out at the same width. `scale` multiplies the page's
    own points instead. Exactly one of the two is given.
    """
    if (width_px is None) == (scale is None):
        raise ValueError("render() takes exactly one of width_px or scale")
    document = pdfium.PdfDocument(source)
    out = []
    for i in range(len(document)):
        page = document[i]
        factor = scale if scale is not None else width_px / page.get_width()
        out.append(page.render(scale=factor).to_pil())
    return out


def first(source: Path | bytes, *, width_px: int | None = None,
          scale: float | None = None) -> Image.Image:
    """The first page alone — the shape both EPUB callers need."""
    return render(source, width_px=width_px, scale=scale)[0]


def render_page(source: Path | bytes, index: int, *, width_px: int | None = None,
                scale: float | None = None) -> Image.Image:
    """One page alone, zero-based.

    For reading a detail: a drawing at `scale=6` is some 7000 px wide, and
    rendering every page of a manual at that scale to keep one would be waste.
    """
    if (width_px is None) == (scale is None):
        raise ValueError("render_page() takes exactly one of width_px or scale")
    document = pdfium.PdfDocument(source)
    if not 0 <= index < len(document):
        raise IndexError(f"page {index + 1} does not exist: "
                         f"the document has {len(document)}")
    page = document[index]
    factor = scale if scale is not None else width_px / page.get_width()
    return page.render(scale=factor).to_pil()


def text(source: Path | bytes) -> list[str]:
    """Each page's text layer, in page order.

    An empty string is a page with **no text layer** — a scan, or a drawing
    made of vectors. It is not a page with nothing on it: a tool that only
    extracts text would conclude "nothing in this PDF" exactly where the
    essential is. Render it instead.
    """
    document = pdfium.PdfDocument(source)
    return [document[i].get_textpage().get_text_range() for i in range(len(document))]
