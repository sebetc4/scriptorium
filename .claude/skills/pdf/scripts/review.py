#!/usr/bin/env python3
"""The review loop of a built PDF, made cheap to look at.

Reading every page image of a document costs some 1,600 tokens a page, paid
again on every later turn of a conversation. This script splits the review in
two, so that the eye is spent where it is needed:

- `checks()` reads the PDF's text layer — no image, no token — and names the
  pages that look wrong: a table of contents whose numbers are off, a blank
  page, text past the text block, a heading left at the bottom of a page, a
  missing running header or page number, an icon name left as text. A check
  **points at a page, it does not judge it**: the look at that page does.
- `sheets()` lays the pages out four to an image, sized under the pixel budget
  past which an image is scaled down before being looked at: the layout of every
  page, for a quarter of the cost.
- `zoom()` renders chosen pages alone, at the full useful resolution.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from core import imaging, pdfpage
from core.doc import OUT, ROOT, DocError, find_docs, load_doc, out_dir

# Past about 1.15 megapixels an image is scaled down before the model sees it,
# and its cost stops growing: a sheet or a zoom is sized just under that line.
MAX_PIXELS = 1_150_000
SHEET_COLUMNS = SHEET_ROWS = 2


@dataclass(frozen=True)
class Finding:
    page: int      # 1-based, as a reader counts
    kind: str
    detail: str

    def __str__(self) -> str:
        return f"p.{self.page} — {self.kind} — {self.detail}"


# The running header and the page number are set small, in the page margins.
RUNNING_ZONE = 0.12      # of the page height, at the top and at the bottom
RUNNING_SIZE = 0.85      # of the body size, at most
HEADING_SIZE = 1.15      # of the body size, at least
EDGE_TOLERANCE = 2.0     # pt past the text block before a word is reported
MIN_LINES_FOR_EDGES = 10
PAGE_NUMBER_RE = re.compile(r"^\d+\s*/\s*\d+$")
TRAILING_NUMBER_RE = re.compile(r"(\d+)\s*$")
ICON_RE = re.compile(r"(?<![\w:]):[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z]+)?:(?![\w:])")
MONOSPACED = 8           # PyMuPDF span flag


def _spans(page: pymupdf.Page) -> list[dict]:
    return [s for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", []) for s in line["spans"] if s["text"].strip()]


def _body_size(doc: pymupdf.Document) -> float:
    sizes = Counter()
    for page in doc:
        for s in _spans(page):
            sizes[round(s["size"], 1)] += len(s["text"])
    return sizes.most_common(1)[0][0] if sizes else 0.0


def _zone(page: pymupdf.Page, bbox) -> str | None:
    height = page.rect.height
    if bbox[3] < height * RUNNING_ZONE:
        return "top"
    if bbox[1] > height * (1 - RUNNING_ZONE):
        return "bottom"
    return None


def _running_positions(doc: pymupdf.Document, body: float) -> set[tuple[str, int]]:
    """Where the running header and page number sit: small text in the top or
    bottom band, at a height found on most pages. A caption set small near the
    foot of one page is not running — it does not come back on the next."""
    counts: Counter = Counter()
    for page in doc:
        counts.update({(zone, round(s["bbox"][3])) for s in _spans(page)
                       if s["size"] <= body * RUNNING_SIZE
                       and (zone := _zone(page, s["bbox"]))})
    return {key for key, n in counts.items() if n >= max(2, len(doc) // 2)}


def _running(page, span, positions) -> str | None:
    zone = _zone(page, span["bbox"])
    y = round(span["bbox"][3])
    if zone and any((zone, y + d) in positions for d in (-1, 0, 1)):
        return zone
    return None


def _toc(page: pymupdf.Page, number: int) -> list[Finding]:
    # WeasyPrint writes several links for one entry — the whole line, its text,
    # its number — all to the same target: an entry is their union.
    # The boxes differ in height (the line has padding, its text does not), so
    # they are merged when they overlap vertically, not when their tops match.
    entries: list[tuple[int, pymupdf.Rect]] = []
    for link in page.get_links():
        target = link.get("page")
        if target is None or target < 0:
            continue
        rect = pymupdf.Rect(link["from"])
        for i, (other, merged) in enumerate(entries):
            if other == target and rect.y0 < merged.y1 and merged.y0 < rect.y1:
                entries[i] = (other, merged | rect)
                break
        else:
            entries.append((target, rect))
    found = []
    for target, rect in entries:
        text = page.get_textbox(rect).strip()
        match = TRAILING_NUMBER_RE.search(text)
        if not match:
            continue
        printed = int(match.group(1))
        title = " ".join(text[:match.start()].split())
        if printed != target + 1:
            found.append(Finding(number, "toc",
                                 f"“{title}” reads {printed}, its target is on page {target + 1}"))
    return found


def _edges(doc: pymupdf.Document) -> tuple[float, float] | None:
    """The text block's left and right edges, as the document itself sets them:
    where most lines start and where most lines end."""
    starts, ends = Counter(), Counter()
    for page in doc:
        lines: dict[tuple[int, int], list] = {}
        for w in page.get_text("words"):
            if _zone(page, w[:4]) is None:
                lines.setdefault((w[5], w[6]), []).append(w)
        for words in lines.values():
            starts[round(min(w[0] for w in words))] += 1
            ends[round(max(w[2] for w in words))] += 1
    if sum(starts.values()) < MIN_LINES_FOR_EDGES:
        return None
    return starts.most_common(1)[0][0], ends.most_common(1)[0][0]


def _overflow(page: pymupdf.Page, number: int, edges) -> list[Finding]:
    left, right = edges
    for w in page.get_text("words"):
        if w[0] < left - EDGE_TOLERANCE or w[2] > right + EDGE_TOLERANCE:
            side = "left" if w[0] < left - EDGE_TOLERANCE else "right"
            return [Finding(number, "overflow",
                            f"“{w[4]}” runs past the text block's {side} edge")]
    return []


def _orphan_heading(page: pymupdf.Page, body_spans: list[dict], number: int,
                    body: float) -> list[Finding]:
    lines: dict[float, list[dict]] = {}
    for s in body_spans:
        lines.setdefault(round(s["bbox"][3]), []).append(s)
    if len(lines) < 2:
        return []
    bottom = max(lines)
    last = lines[bottom]
    if max(s["size"] for s in last) < body * HEADING_SIZE:
        return []
    # An image under the heading is its content: the heading is not stranded.
    if any(image["bbox"][1] >= bottom - 1 for image in page.get_image_info()):
        return []
    text = " ".join(s["text"].strip() for s in last)
    return [Finding(number, "orphan-heading", f"“{text}” ends the page, its text is on the next")]


def _icons(body_spans: list[dict], number: int) -> list[Finding]:
    found = []
    for s in body_spans:
        if s["flags"] & MONOSPACED or "mono" in s["font"].lower():
            continue
        for match in ICON_RE.finditer(s["text"]):
            found.append(Finding(number, "icon", f"“{match.group(0)}” left as text"))
    return found


def checks(pdf: Path) -> list[Finding]:
    doc = pymupdf.open(pdf)
    body = _body_size(doc)
    edges = _edges(doc)
    positions = _running_positions(doc, body)
    findings: list[Finding] = []
    has_number, has_header = {}, {}
    for index, page in enumerate(doc):
        number = index + 1
        spans = _spans(page)
        running = [(s, _running(page, s, positions)) for s in spans]
        body_spans = [s for s, zone in running if zone is None]
        has_header[number] = any(zone == "top" for _, zone in running)
        has_number[number] = any(zone == "bottom" and PAGE_NUMBER_RE.match(s["text"].strip())
                                 for s, zone in running)

        findings += _toc(page, number)
        if not body_spans and not page.get_images():
            findings.append(Finding(number, "blank", "nothing on the page but its running header and number"))
        if edges:
            findings += _overflow(page, number, edges)
        if number < len(doc):
            findings += _orphan_heading(page, body_spans, number, body)
        findings += _icons(body_spans, number)

    # A running element missing from a page is only a defect where the other
    # pages carry it; the cover never does.
    for kind, present in (("header", has_header), ("page-number", has_number)):
        rest = [n for n in present if n > 1]
        if rest and sum(present[n] for n in rest) * 2 > len(rest):
            findings += [Finding(n, kind, f"this page has no running {kind.replace('-', ' ')}")
                         for n in rest if not present[n]]
    return sorted(findings, key=lambda f: f.page)


# --------------------------------------------------------------------------
# Sheets and zoom
# --------------------------------------------------------------------------
def _aspect(pdf: Path) -> float:
    page = pymupdf.open(pdf)[0]
    return page.rect.height / page.rect.width


def _thumb_width(aspect: float) -> int:
    """The widest page thumbnail that keeps a full sheet under MAX_PIXELS.

    A cell is the thumbnail plus its padding and label band; the sheet is
    SHEET_COLUMNS × SHEET_ROWS cells: solve (t + 2p)(a·t + L + p) · C·R = M.
    """
    pad, label, cells = imaging.CELL_PAD, imaging.LABEL_HEIGHT, SHEET_COLUMNS * SHEET_ROWS
    a, b, c = aspect, aspect * 2 * pad + label + pad, 2 * pad * (label + pad) - MAX_PIXELS / cells
    return int((-b + math.sqrt(b * b - 4 * a * c)) / (2 * a))


def sheets(pdf: Path, dest: Path) -> list[Path]:
    """Every page, four to an image, labelled with its page number."""
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("sheet-*.png"):
        old.unlink()
    aspect = _aspect(pdf)
    thumb = _thumb_width(aspect)
    cell = (thumb + 2 * imaging.CELL_PAD,
            int(thumb * aspect) + imaging.LABEL_HEIGHT + imaging.CELL_PAD)
    images = pdfpage.render(pdf, width_px=thumb * 2)
    per_sheet = SHEET_COLUMNS * SHEET_ROWS
    written = []
    for start in range(0, len(images), per_sheet):
        batch = [(f"p.{start + i + 1}", image)
                 for i, image in enumerate(images[start:start + per_sheet])]
        target = dest / f"sheet-{start // per_sheet + 1:02d}.png"
        imaging.contact_sheet(batch, columns=SHEET_COLUMNS, cell=cell).save(target)
        written.append(target)
    return written


def zoom(pdf: Path, numbers: list[int], dest: Path) -> list[Path]:
    """The asked pages (1-based), each alone, as large as the budget allows."""
    count = len(pymupdf.open(pdf))
    missing = [n for n in numbers if not 1 <= n <= count]
    if missing:
        raise IndexError(f"no page {', '.join(map(str, missing))}: the document has {count}")
    dest.mkdir(parents=True, exist_ok=True)
    width = int(math.sqrt(MAX_PIXELS / _aspect(pdf))) - 1
    written = []
    for n in numbers:
        target = dest / f"page-{n:02d}.png"
        pdfpage.render_page(pdf, n - 1, width_px=width).save(target)
        written.append(target)
    return written


# --------------------------------------------------------------------------
# A document's PDFs
# --------------------------------------------------------------------------
def variants(pdf_dir: Path, slug: str, theme: str) -> list[tuple[str, Path]]:
    """The built PDFs of a document, by variant — as build.py names them."""
    if theme == "both":
        named = [("light", pdf_dir / f"{slug}.pdf"), ("dark", pdf_dir / f"{slug}-dark.pdf")]
    else:
        named = [(theme, pdf_dir / f"{slug}.pdf")]
    return [(variant, pdf) for variant, pdf in named if pdf.exists()]


def stale(pdf: Path, doc: Path) -> bool:
    """Whether a source file changed after the PDF was built.

    `sources/` is left out: it is the immutable record of an import or a
    capture, not something the build reads.
    """
    newest = max((f.stat().st_mtime for f in doc.rglob("*")
                  if f.is_file() and "sources" not in f.relative_to(doc).parts), default=0)
    return pdf.stat().st_mtime < newest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Review a built PDF cheaply: text-layer checks, then pages four to a sheet.")
    ap.add_argument("doc", help="the document, as <topic>/<slug>")
    ap.add_argument("--variant", choices=["light", "dark"],
                    help="only this variant (default: every built one)")
    ap.add_argument("--zoom", type=int, nargs="+", metavar="PAGE",
                    help="render these pages alone, at full resolution, instead")
    args = ap.parse_args(argv)

    try:
        docs = find_docs([args.doc])
        if len(docs) != 1:
            raise DocError(f"{args.doc} holds {len(docs)} documents: name one, as <topic>/<slug>")
        [doc] = docs
        fm, _ = load_doc(doc)
    except DocError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    rel = doc.relative_to(ROOT / "library")
    built = [(v, pdf) for v, pdf in variants(out_dir(doc), doc.name, fm["theme"])
             if not args.variant or v == args.variant]
    if not built:
        print(f"error: nothing built — run make build DOC={rel}", file=sys.stderr)
        return 1

    failed = 0
    for variant, pdf in built:
        dest = OUT / "review" / rel / variant
        if stale(pdf, doc):
            print(f"error: {pdf.relative_to(ROOT)} is older than its sources "
                  f"— run make build DOC={rel}", file=sys.stderr)
            failed += 1
            continue
        if args.zoom:
            try:
                for image in zoom(pdf, args.zoom, dest):
                    print(image.relative_to(ROOT))
            except IndexError as exc:
                print(f"error: {exc}", file=sys.stderr)
                failed += 1
            continue
        found = checks(pdf)
        report = "\n".join(str(f) for f in found)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "checks.txt").write_text(report + "\n" if report else "", encoding="utf-8")
        count = len(pymupdf.open(pdf))
        print(f"{pdf.relative_to(ROOT)} — {count} pages — {variant}")
        print(f"checks: {len(found)} finding{'s' * (len(found) != 1)}")
        for f in found:
            print(f"  {f}")
        for i, sheet in enumerate(sheets(pdf, dest)):
            first = i * SHEET_COLUMNS * SHEET_ROWS + 1
            last = min(first + SHEET_COLUMNS * SHEET_ROWS - 1, count)
            pages = f"p.{first}" if first == last else f"p.{first}–{last}"
            print(f"sheet: {sheet.relative_to(ROOT)} ({pages})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
