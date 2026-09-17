#!/usr/bin/env python3
"""Reviewing an EPUB — but not screen by screen.

The repository's rule that “a document is looked at page by page” is right for
the PDF, because a PDF is a fixed artefact: a break in the wrong place, a widow,
a figure pushed to the next page are properties of that precise rendering.

An EPUB has no pages. The e-reader repaginates according to its screen and to
the text size the reader chose; reviewing “screen 23 of 47” would certify a
pagination no device will reproduce. What stays verifiable is exactly what does
not reflow — the diagrams, the transposed tables, the code blocks — and that set
is bounded.

Hence two outputs:

    contact sheet   a document's non-reflowing objects, at the real scale of a
                    six-inch screen. One or two images per document.
    style proof     the style guide in full, to be reviewed when the stylesheet
                    or the palette changes — not on every document.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from weasyprint import HTML

from core import doc, pdfpage

import epub  # a sibling script of this skill

# A six-inch e-ink screen at 300 dpi — the most widespread format, and the one a
# diagram's legibility is judged on.
SCREEN_W, SCREEN_H = 1072, 1448
MARGIN = 40

FIG_RE = re.compile(r"<figure\b.*?</figure>|<p><img\b[^>]*/></p>", re.S)
BLOCK_RE = re.compile(r'<div class="row-block">.*?</div>\s*(?=<div class="row-block">|$)',
                      re.S)
PRE_RE = re.compile(r"<pre\b.*?</pre>", re.S)


def render_screens(body: str, css: str, dest: Path, prefix: str) -> list[Path]:
    """Render a fragment through a six-inch window, one PNG per screen."""
    dest.mkdir(parents=True, exist_ok=True)
    page = (f"<style>@page{{size:{SCREEN_W}px {SCREEN_H}px;margin:{MARGIN}px}}"
            f"html{{font-size:20px}}body{{margin:0}}{css}</style>"
            f"<body>{body}</body>")
    # base_url: without it, WeasyPrint resolves the relative `src` against the
    # process's working directory rather than the sheet's directory. The images
    # are then missing in silence — it does not report an image it cannot find.
    # Which is precisely what this function used to do.
    written = []
    screens = pdfpage.render(HTML(string=page, base_url=str(dest) + "/").write_pdf(),
                             width_px=SCREEN_W)
    for i, image in enumerate(screens, 1):
        f = dest / f"{prefix}-{i:02d}.png"
        image.save(f, format="PNG", optimize=True)
        written.append(f)
    return written


def non_reflowing(d: Path) -> tuple[list[str], str, dict[str, bytes]]:
    """The objects that do not reflow, the stylesheet to apply, the images."""
    fm, body_md = doc.load_doc(d)
    tokens = doc.token_map(d, {**fm, "theme": "epub"})
    body, _ = doc.convert(body_md, tokens, d.name, icon_color="currentColor")
    body = epub.transpose_wide_tables(body, epub.table_threshold(fm))
    body, images = epub.collect_images(body, d, tokens)

    objects = FIG_RE.findall(body) + BLOCK_RE.findall(body) + PRE_RE.findall(body)
    # The src point at ../images/ inside the archive; on the sheet the PNGs are
    # written alongside, so the path is flattened.
    objects = [o.replace('src="../images/', 'src="') for o in objects]
    return objects, epub.epub_css(d, tokens), images


def non_reflowing_count(d: Path) -> int:
    return len(non_reflowing(d)[0])


def contact_sheet(d: Path) -> list[Path]:
    """One or two images per document: everything that does not reflow, to scale."""
    objects, css, images = non_reflowing(d)
    if not objects:
        return []

    dest = doc.out_dir(d, "preview")
    dest.mkdir(parents=True, exist_ok=True)
    # The images must be on disk for WeasyPrint to load them.
    for name, data in images.items():
        (dest / name).write_bytes(data)
    body = "".join(f'<p style="font:600 15px sans-serif;opacity:.6;'
                   f'margin:24px 0 6px">object {i + 1} / {len(objects)}</p>{o}'
                   for i, o in enumerate(objects))
    return render_screens(body, css, dest, "contact")


def style_screens(d: Path) -> list[Path]:
    """The style guide in full — reviewed when the art direction or sheet changes."""
    fm, body_md = doc.load_doc(d)
    tokens = doc.token_map(d, {**fm, "theme": "epub"})
    dest = doc.out_dir(d, "preview")
    dest.mkdir(parents=True, exist_ok=True)

    body, _ = doc.convert(body_md, tokens, d.name, icon_color="currentColor")
    body = epub.transpose_wide_tables(body, epub.table_threshold(fm))
    body, images = epub.collect_images(body, d, tokens)
    for name, data in images.items():
        (dest / name).write_bytes(data)
    body = body.replace('src="../images/', 'src="')
    return render_screens(body, epub.epub_css(d, tokens), dest, "style")


def main() -> int:
    ap = argparse.ArgumentParser(description="EPUB review sheets.")
    ap.add_argument("targets", nargs="*")
    ap.add_argument("--style", action="store_true",
                    help="style proof: the style guide in full")
    args = ap.parse_args()

    if args.style:
        d = doc.LIBRARY / "exemples" / "guide-de-style"
        pages = style_screens(d)
        for p in pages:
            print(f"  ✓ {p.relative_to(doc.ROOT)}")
        return 0

    try:
        docs = doc.find_docs(args.targets)
    except doc.DocError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    failures = 0
    for d in docs:
        rel = d.relative_to(doc.ROOT)
        try:
            fm, _ = doc.load_doc(d)
            if fm["preset"] not in epub.EPUB_PRESETS:
                continue
            pages = contact_sheet(d)
        except doc.DocError as exc:
            print(f"  ✗ {rel} — {exc}", file=sys.stderr)
            failures += 1
            continue
        except Exception as exc:
            print(f"  ✗ {rel} — {type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if not pages:
            print(f"  · {rel} — nothing that does not reflow")
            continue
        for p in pages:
            print(f"  ✓ {p.relative_to(doc.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
