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
from core.doc import (ROOT, DocError, doc_dir, find_docs, load_doc, out_dir,
                      token_map, work_dir)

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
LINES_AFTER_HEADING = 2  # a heading followed by no more than this, at a page's foot, is stranded
FULL_PAGE = 0.80         # of the page height: a page whose text reaches this far is full
NEAR_BLANK = 0.25        # of the document's usual fill, at most
LOOSE_FACTOR = 4.0       # a line's word spacing, against the page's usual one
MIN_LOOSE_WORDS = 5
SHORT_FRAGMENT = 2       # letters carried to the next line by a hyphenation break
CONTINUATION_LINES = 3   # lines searched for the rest of a hyphenated word
MIN_TEXT_SIZE = 5.0      # pt
# Two text boxes overlapping by this much of the smaller one are on top of each
# other rather than merely adjacent. Consecutive spans of one line touch and
# sometimes overlap by a hair; a label sitting on another label does not.
OVERLAP_RATIO = 0.30
SAMPLES = 4              # occurrences quoted in one finding
HYPHEN = "‐"        # the hyphen WeasyPrint adds at a hyphenation break
PAGE_NUMBER_RE = re.compile(r"^\d+\s*/\s*\d+$")
TRAILING_NUMBER_RE = re.compile(r"(\d+)\s*$")
ICON_RE = re.compile(r"(?<![\w:]):[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z]+)?:(?![\w:])")
URL_RE = re.compile(r"https?://|www\.|\w\.(?:com|org|net|io|fr|de|html?)\b")
APOSTROPHE_RE = re.compile(r"\w'\w")
MONOSPACED = 8           # PyMuPDF span flag


@dataclass
class _Page:
    """What the checks read of one page, gathered once."""
    number: int
    page: pymupdf.Page
    body: list[dict]                   # spans outside the running header and footer
    lines: list[list[dict]]            # body spans grouped by baseline, top to bottom
    word_lines: list[list[tuple]]      # body words by visual line; each word ends with (size, code)
    has_header: bool
    has_number: bool
    toc_entries: list[tuple[int, int, str]]   # (target page, printed number, title)


def _spans(page: pymupdf.Page) -> list[dict]:
    return [s for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", []) for s in line["spans"] if s["text"].strip()]


def _mono(span: dict) -> bool:
    return bool(span["flags"] & MONOSPACED) or "mono" in span["font"].lower()


def _body_font(doc: pymupdf.Document) -> str:
    """The family most of the text is set in, weight and style aside."""
    fonts = Counter()
    for page in doc:
        for s in _spans(page):
            fonts[_family(s["font"])] += len(s["text"])
    if not fonts:
        return ""
    name = fonts.most_common(1)[0][0]
    return re.sub(r"(regular|bold|italic|semibold|medium|light|oblique)+$", "", name)


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


def _running(page, bbox, positions) -> str | None:
    zone = _zone(page, bbox)
    y = round(bbox[3])
    if zone and any((zone, y + d) in positions for d in (-1, 0, 1)):
        return zone
    return None


def _toc_entries(page: pymupdf.Page) -> list[tuple[int, int, str]]:
    # WeasyPrint writes several links for one entry — the whole line, its text,
    # its number — all to the same target. Their boxes differ in height (the
    # line has padding, its text does not), so they are merged when they overlap
    # vertically, not when their tops match.
    boxes: list[tuple[int, pymupdf.Rect]] = []
    for link in page.get_links():
        target = link.get("page")
        if target is None or target < 0:
            continue
        rect = pymupdf.Rect(link["from"])
        for i, (other, merged) in enumerate(boxes):
            if other == target and rect.y0 < merged.y1 and merged.y0 < rect.y1:
                boxes[i] = (other, merged | rect)
                break
        else:
            boxes.append((target, rect))
    entries = []
    for target, rect in boxes:
        text = page.get_textbox(rect).strip()
        match = TRAILING_NUMBER_RE.search(text)
        if match:
            entries.append((target, int(match.group(1)), " ".join(text[:match.start()].split())))
    return entries


def _span_of(word: tuple, spans: list[dict]) -> tuple[float, bool]:
    """The size of the span a word sits in, and whether that span is code."""
    x, y = (word[0] + word[2]) / 2, (word[1] + word[3]) / 2
    for s in spans:
        b = s["bbox"]
        if b[0] <= x <= b[2] and b[1] <= y <= b[3]:
            return s["size"], _mono(s)
    return 0.0, False


def _visual_lines(words: list[tuple]) -> list[list[tuple]]:
    """Words grouped into the lines a reader sees, top to bottom, left to right.

    Not PyMuPDF's own lines: it splits a heavily justified line into one line
    per word — the very line a spacing check is after. A word joins a line when
    its vertical middle falls within the line's height; inline code, set on
    another font, sits a point or two off the text's baseline.
    """
    lines: list[list[tuple]] = []
    for w in sorted(words, key=lambda w: (w[1], w[0])):
        middle = (w[1] + w[3]) / 2
        for line in lines:
            if line[0][1] <= middle <= line[0][3]:
                line.append(w)
                break
        else:
            lines.append([w])
    return [sorted(line, key=lambda w: w[0]) for line in sorted(lines, key=lambda l: l[0][1])]


def _gather(doc: pymupdf.Document, body_size: float) -> list[_Page]:
    positions = _running_positions(doc, body_size)
    pages = []
    for index, page in enumerate(doc):
        spans = _spans(page)
        zones = [(s, _running(page, s["bbox"], positions)) for s in spans]
        body = [s for s, zone in zones if zone is None]
        by_baseline: dict[int, list[dict]] = {}
        for s in body:
            by_baseline.setdefault(round(s["bbox"][3]), []).append(s)
        words = [w + _span_of(w, body) for w in page.get_text("words")
                 if _running(page, w[:4], positions) is None]
        pages.append(_Page(
            number=index + 1, page=page, body=body,
            lines=[by_baseline[y] for y in sorted(by_baseline)],
            word_lines=_visual_lines(words),
            has_header=any(zone == "top" for _, zone in zones),
            has_number=any(zone == "bottom" and PAGE_NUMBER_RE.match(s["text"].strip())
                           for s, zone in zones),
            toc_entries=_toc_entries(page)))
    return pages


def _quote(items: list[str]) -> str:
    shown = ", ".join(f"“{i}”" for i in items[:SAMPLES])
    return shown + (f" and {len(items) - SAMPLES} more" if len(items) > SAMPLES else "")


# --- The checks, one page at a time -------------------------------------------
def _toc(p: _Page) -> list[Finding]:
    return [Finding(p.number, "toc", f"“{title}” reads {printed}, its target is on page {target + 1}")
            for target, printed, title in p.toc_entries if printed != target + 1]


def _edges(pages: list[_Page]) -> tuple[float, float] | None:
    """The text block's left and right edges, as the document itself sets them:
    where most lines start and where most lines end."""
    starts, ends = Counter(), Counter()
    for p in pages:
        for words in p.word_lines:
            starts[round(min(w[0] for w in words))] += 1
            ends[round(max(w[2] for w in words))] += 1
    if sum(starts.values()) < MIN_LINES_FOR_EDGES:
        return None
    return starts.most_common(1)[0][0], ends.most_common(1)[0][0]


def _overflow(p: _Page, edges) -> list[Finding]:
    left, right = edges
    for words in p.word_lines:
        for w in words:
            if w[0] < left - EDGE_TOLERANCE or w[2] > right + EDGE_TOLERANCE:
                side = "left" if w[0] < left - EDGE_TOLERANCE else "right"
                return [Finding(p.number, "overflow", f"“{w[4]}” runs past the text block's {side} edge")]
    return []


def _family(font: str) -> str:
    return re.sub(r"[^a-z0-9]", "", font.split("+")[-1].lower())


def _is_heading(line: list[dict], body: float, body_font: str) -> bool:
    """Larger than the text and set in another family: a displayed formula is
    larger too, but in the text's family."""
    return any(s["size"] >= body * HEADING_SIZE and not _family(s["font"]).startswith(body_font)
               for s in line)


def _orphan_heading(p: _Page, following: _Page | None, body: float, body_font: str) -> list[Finding]:
    """A heading at the foot of a full page, with at most a line or two of its
    section under it — the rest of the section on the next page."""
    if following is None or len(p.lines) < 2:
        return []
    last = max(i for i in range(len(p.lines)) if _is_heading(p.lines[i], body, body_font)) \
        if any(_is_heading(line, body, body_font) for line in p.lines) else None
    if last is None or last == 0 or len(p.lines) - 1 - last > LINES_AFTER_HEADING:
        return []
    heading_bottom = max(s["bbox"][3] for s in p.lines[last])
    page_bottom = max(s["bbox"][3] for s in p.lines[-1])
    if page_bottom < p.page.rect.height * FULL_PAGE and last < len(p.lines) - 1:
        return []   # the section's line or two end a page that is not full: it is short, not cut
    # An image under the heading is its content.
    if any(image["bbox"][1] >= heading_bottom - 1 for image in p.page.get_image_info()):
        return []
    # A section that ends here, the next one opening the following page, is complete.
    if last < len(p.lines) - 1 and following.lines and _is_heading(following.lines[0], body, body_font):
        return []
    text = " ".join(s["text"].strip() for s in p.lines[last])
    return [Finding(p.number, "orphan-heading", f"“{text}” is left at the foot of the page, its section on the next")]


def _fill(p: _Page) -> float:
    boxes = [s["bbox"] for s in p.body] + [i["bbox"] for i in p.page.get_image_info()]
    if not boxes:
        return 0.0
    return (max(b[3] for b in boxes) - min(b[1] for b in boxes)) / p.page.rect.height


def _near_blank(pages: list[_Page]) -> list[Finding]:
    """A page holding a few lines among full ones. The cover, the last page and a
    table of contents are short by nature."""
    candidates = [p for p in pages[1:-1] if len(p.toc_entries) < 2 and p.body]
    if len(candidates) < 2:
        return []
    fills = sorted(_fill(p) for p in candidates)
    usual = fills[len(fills) // 2]
    return [Finding(p.number, "near-blank", f"the text fills {_fill(p):.0%} of the page, "
                                            f"against {usual:.0%} on most pages")
            for p in candidates if _fill(p) < usual * NEAR_BLANK]


def _hyphenation(p: _Page, following_lines) -> list[Finding]:
    urls, short = [], []
    for i, words in enumerate(p.word_lines[:-1]):
        end = words[-1]
        if not end[4].endswith(HYPHEN):
            continue
        # The rest of the word opens one of the next lines, at or left of where
        # the cut word stands: a paragraph's next line starts back at the margin.
        # In a table the next line a reader sees may belong to a column further
        # right — it is passed over.
        rest = [line[0] for line in p.word_lines[i + 1:i + 1 + CONTINUATION_LINES]
                if line[0][0] <= end[0] + EDGE_TOLERANCE]
        if not rest:
            continue
        before, after = end[4][:-1], rest[0][4]
        joined = before + after
        if URL_RE.search(joined):
            urls.append(f"{before}-/{after}")
        else:
            # French typesetting forbids carrying two letters over; leaving two
            # before the break ("in-/connue") is correct.
            tail = re.match(r"\w+", after)
            if tail and len(tail.group()) <= SHORT_FRAGMENT:
                short.append(f"{before}-/{after}")
    found = []
    if urls:
        found.append(Finding(p.number, "url-hyphen", f"an address cut with a hyphen it does not have: {_quote(urls)}"))
    if short:
        found.append(Finding(p.number, "short-hyphen", f"a hyphenation carries two letters or fewer over: {_quote(short)}"))
    return found


def _loose_lines(p: _Page, body: float) -> list[Finding]:
    """Running text justified to gaps far wider than the page's usual ones.

    Only words set at the body size and not as code: a table's columns, a
    diagram's labels and a code block's alignment are spaced on purpose.
    """
    def text(w) -> bool:
        return abs(w[8] - body) < 0.3 and not w[9]

    gaps_by_line = []
    for words in p.word_lines:
        # Only the space between two neighbouring words of text: dropping the
        # code first would turn the space it takes into a gap.
        gaps = sorted(b[0] - a[2] for a, b in zip(words, words[1:]) if text(a) and text(b))
        if len(gaps) >= MIN_LOOSE_WORDS - 1:
            gaps_by_line.append((gaps[len(gaps) // 2], words))
    if len(gaps_by_line) < 3:
        return []
    usual = sorted(g for g, _ in gaps_by_line)[len(gaps_by_line) // 2]
    loose = [" ".join(w[4] for w in words) for gap, words in gaps_by_line
             if gap > max(usual * LOOSE_FACTOR, body * 0.5)]
    if not loose:
        return []
    return [Finding(p.number, "loose-line", f"word spacing stretched past {LOOSE_FACTOR:.0f}× the page's: "
                                             f"{_quote([line[:60] for line in loose])}")]


def _fonts(p: _Page, allowed: set[str]) -> list[Finding]:
    families = {_family(f) for f in allowed}
    foreign: dict[str, set[str]] = {}
    for s in p.body:
        if not any(_family(s["font"]).startswith(f) for f in families):
            foreign.setdefault(s["font"].split("+")[-1], set()).update(c for c in s["text"] if not c.isspace())
    return [Finding(p.number, "font", f"{font} sets “{''.join(sorted(chars))[:12]}” — "
                                      f"not a family of the art direction")
            for font, chars in sorted(foreign.items())]


def _apostrophes(p: _Page) -> list[Finding]:
    words = [m.group() for s in p.body if not _mono(s)
             for m in re.finditer(r"\S*\w'\w\S*", s["text"])]
    if not words:
        return []
    return [Finding(p.number, "apostrophe", f"straight apostrophe where the text uses ’: {_quote(words)}")]


def _tiny_text(p: _Page) -> list[Finding]:
    tiny = [s for s in p.body if s["size"] < MIN_TEXT_SIZE]
    if not tiny:
        return []
    smallest = min(s["size"] for s in tiny)
    return [Finding(p.number, "tiny-text", f"text set down to {smallest:.1f} pt: "
                                           f"{_quote([s['text'].strip() for s in tiny])}")]


def _overlapping_text(p: _Page) -> list[Finding]:
    """Text printed on top of other text.

    A hand-drawn figure places its labels at fixed coordinates, and two of them
    can land on each other: the schematic of `round-led-d4017` had three such
    collisions, each found by an eye, three steps and eleven images later. The
    text layer knows where every box is, so this costs no image at all.

    Spans sharing a baseline are consecutive text on one line — they touch, and
    that is not a collision.
    """
    spans = [s for s in p.body if s["text"].strip()]
    found: list[Finding] = []
    for i, a in enumerate(spans):
        ax0, ay0, ax1, ay1 = a["bbox"]
        for b in spans[i + 1:]:
            bx0, by0, bx1, by1 = b["bbox"]
            if by0 >= ay1:
                break                       # spans come sorted: nothing below can reach
            if abs(ay1 - by1) < 0.5 and abs(ay0 - by0) < 0.5:
                continue                    # one line, consecutive
            w = min(ax1, bx1) - max(ax0, bx0)
            h = min(ay1, by1) - max(ay0, by0)
            if w <= 0 or h <= 0:
                continue
            smaller = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
            if smaller and w * h >= OVERLAP_RATIO * smaller:
                found.append(Finding(
                    p.number, "overlapping-text",
                    f"“{a['text'].strip()[:30]}” and “{b['text'].strip()[:30]}” "
                    f"are printed on top of each other"))
    return found


def _icons(p: _Page) -> list[Finding]:
    return [Finding(p.number, "icon", f"“{m.group(0)}” left as text")
            for s in p.body if not _mono(s) for m in ICON_RE.finditer(s["text"])]


def checks(pdf: Path, fonts: set[str] | None = None) -> list[Finding]:
    """The pages to look at, read from the text layer.

    `fonts` holds the art direction's families; without it, fonts are not
    checked — a fixture or a foreign PDF has no art direction to hold to.
    """
    doc = pymupdf.open(pdf)
    body = _body_size(doc)
    body_font = _body_font(doc)
    pages = _gather(doc, body)
    edges = _edges(pages)
    findings: list[Finding] = []
    for i, p in enumerate(pages):
        following = pages[i + 1] if i + 1 < len(pages) else None
        findings += _toc(p)
        if not p.body and not p.page.get_image_info():
            findings.append(Finding(p.number, "blank", "nothing on the page but its running header and number"))
        if edges:
            findings += _overflow(p, edges)
        findings += _orphan_heading(p, following, body, body_font)
        findings += _hyphenation(p, following)
        findings += _loose_lines(p, body)
        if fonts:
            findings += _fonts(p, fonts)
        findings += _apostrophes(p)
        findings += _tiny_text(p)
        findings += _overlapping_text(p)
        findings += _icons(p)
    findings += _near_blank(pages)

    # A running element missing from a page is only a defect where the other
    # pages carry it; the cover never does.
    rest = pages[1:]
    for kind, present in (("header", lambda p: p.has_header), ("page-number", lambda p: p.has_number)):
        if rest and sum(map(present, rest)) * 2 > len(rest):
            findings += [Finding(p.number, kind, f"this page has no running {kind.replace('-', ' ')}")
                         for p in rest if not present(p)]
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

    Only `document/` is walked, because it is the only directory the build
    reads (docs/architecture.md §11). What the user received, what the agent
    learned and what a command can make again all sit beside it and none of
    them changes the page.
    """
    newest = max((f.stat().st_mtime for f in doc_dir(doc).rglob("*")
                  if f.is_file()), default=0)
    return pdf.stat().st_mtime < newest


def art_direction_fonts(tokens: dict[str, str]) -> set[str]:
    """The first family of each font role — the ones the art direction chose.
    The families after it in the stack are fallbacks: a glyph set in one of
    them is a glyph the chosen family lacks."""
    families = set()
    for role in ("font-serif", "font-sans", "font-mono"):
        stack = tokens.get(role) or tokens.get(f"--{role}") or ""
        first = stack.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var("):
            families.add(first)
    return families


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
        dest = work_dir(doc, "review") / variant
        if stale(pdf, doc):
            print(f"error: {pdf.relative_to(ROOT)} is older than its sources "
                  f"— run make build DOC={rel}", file=sys.stderr)
            failed += 1
            continue
        # The checks run whole, with or without a page list. They read the text
        # layer and cost no image, and a fix on one page reflows the ones after
        # it: a pass that looked only where it was told would stop covering the
        # document exactly when the document had just moved.
        found = checks(pdf, fonts=art_direction_fonts(token_map(doc, fm)) or None)
        report = "\n".join(str(f) for f in found)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "checks.txt").write_text(report + "\n" if report else "", encoding="utf-8")
        count = len(pymupdf.open(pdf))
        print(f"{pdf.relative_to(ROOT)} — {count} pages — {variant}")
        print(f"checks: {len(found)} finding{'s' * (len(found) != 1)}")
        for f in found:
            print(f"  {f}")
        if args.zoom:
            # A targeted pass: the pages that were given, at full resolution,
            # and no sheets — the sheets are how a reviewer *finds* a doubtful
            # page, and this one already knows which pages to look at.
            try:
                for image in zoom(pdf, args.zoom, dest):
                    print(image.relative_to(ROOT))
            except IndexError as exc:
                print(f"error: {exc}", file=sys.stderr)
                failed += 1
            continue
        for i, sheet in enumerate(sheets(pdf, dest)):
            first = i * SHEET_COLUMNS * SHEET_ROWS + 1
            last = min(first + SHEET_COLUMNS * SHEET_ROWS - 1, count)
            pages = f"p.{first}" if first == last else f"p.{first}–{last}"
            print(f"sheet: {sheet.relative_to(ROOT)} ({pages})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
