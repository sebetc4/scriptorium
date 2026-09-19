#!/usr/bin/env python3
"""Import an external PDF as a document of the library.

    python .claude/skills/pdf/scripts/ingest.py source.pdf watch/wto-report --lang fr

It produces an ordinary document — `index.md` + `assets/` — rather than any
particular format: `make build` is what then applies the repository's art
direction to it.

    library/<topic>/<slug>/
      index.md              front matter + extracted text, to translate in place
      sources/extracted.md  the raw extraction, an immutable reference
      sources/meta.json     provenance: path, digest, pages, metadata
      assets/               the extracted images

The tool does not translate: it structures. Translation happens afterwards, on
the Markdown, where the meaning is reachable and the formatting already
normalised.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf
from PIL import Image

# ROOT from the core, not from this file's parents: it lives inside a skill.
from core.doc import ENTRY, LIBRARY, ROOT, doc_dir
from core.imaging import store

BULLET_RE = re.compile(r"^\s*[•‣▪◦·–—*]\s+")
NUMBER_RE = re.compile(r"^\s*(\d{1,2})[.)]\s+")
HYPHEN_END_RE = re.compile(r"\w[-\u2010\u00ad]$")
SPACED_RE = re.compile(r"^(?:\S ){3,}\S$")
FLAG_ITALIC, FLAG_BOLD = 2, 16
MARGIN_BAND = 0.08      # top and bottom bands where running heads are hunted
MIN_IMAGE_PX = 64       # below this: a bullet, a rule or an artefact, not an image
VECTOR_BUSY = 40        # above this: the page carries a notable vector drawing
PAGE_SCALE = 1.6        # rendering of the source pages, for visual review
from core.imaging import MAX_IMAGE_PX  # noqa: F811  (re-read here for the framing)
TILE_GAP = 0.6          # pt: beyond this, two neighbouring images are two images
TILE_ALIGN = 0.5        # pt: alignment tolerance of the perpendicular edges
ROW_OVERLAP = 0.6       # share of vertical overlap that makes one row
ZOOM_RANGE = (1.0, 6.0)

# The private use area: a badly encoded font files its glyphs there. The
# original character cannot be recovered — it is removed and counted.
PUA_RE = re.compile(r"[\ue000-\uf8ff\U000f0000-\U000ffffd]")


# --------------------------------------------------------------------------
# Collection
# --------------------------------------------------------------------------
def spans_of(page) -> list[dict]:
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if span["text"].strip():
                    out.append(span)
    return out


def body_size(doc) -> float:
    """The reference body size: the size carrying the most characters."""
    weight: Counter[float] = Counter()
    for page in doc:
        for span in spans_of(page):
            weight[round(span["size"], 1)] += len(span["text"].strip())
    return weight.most_common(1)[0][0] if weight else 10.0


def heading_levels(doc, body: float) -> dict[float, int]:
    """Sizes clearly above the body → heading levels, in descending order."""
    weight: Counter[float] = Counter()
    for page in doc:
        for span in spans_of(page):
            size = round(span["size"], 1)
            if size >= body * 1.12:
                weight[size] += len(span["text"].strip())
    # a size seen three times or fewer is an accident, not a level
    sizes = sorted((s for s, w in weight.items() if w > 3), reverse=True)
    return {size: min(i + 1, 6) for i, size in enumerate(sizes[:4])}


def running_text(doc) -> set[str]:
    """Running heads and footers: same lines, in the margin, on ≥ 40% of pages."""
    seen: Counter[str] = Counter()
    for page in doc:
        h = page.rect.height
        top, bottom = h * MARGIN_BAND, h * (1 - MARGIN_BAND)
        lines = set()
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            y = block["bbox"][1]
            if y > top and block["bbox"][3] < bottom:
                continue
            text = " ".join(s["text"] for l in block["lines"] for s in l["spans"]).strip()
            if text:
                lines.add(re.sub(r"\d+", "#", text))
        seen.update(lines)
    threshold = max(2, len(doc) * 0.4)
    return {t for t, n in seen.items() if n >= threshold}


# --------------------------------------------------------------------------
# Formatting
# --------------------------------------------------------------------------
PUA_SEEN: Counter[str] = Counter()


def clean(text: str) -> str:
    found = PUA_RE.findall(text)
    if found:
        PUA_SEEN.update(found)
        text = PUA_RE.sub("", text)
    return text


def emphasize(span: dict) -> str:
    text = clean(span["text"])
    if not text.strip():
        return text
    lead = " " if text[0] == " " else ""
    trail = " " if text[-1] == " " else ""
    core = text.strip()
    flags = span["flags"]
    if flags & FLAG_BOLD:
        core = f"**{core}**"
    if flags & FLAG_ITALIC:
        core = f"*{core}*"
    return f"{lead}{core}{trail}"


def join_lines(lines: list[str]) -> str:
    """Re-join a paragraph's lines, repairing the hyphenation."""
    out = ""
    for line in lines:
        line = line.strip()
        if not out:
            out = line
        elif HYPHEN_END_RE.search(out):
            out = out[:-1] + line
        else:
            out = f"{out} {line}"
    return out


def unspace(text: str) -> str:
    """“R E F E R E N C E” → “REFERENCE”.

    A letter followed by a space, repeated: this is letter-spacing, which the
    PDF materialises as real spaces.
    """
    return re.sub(r"\s+", "", text) if SPACED_RE.match(text.strip()) else text


def render_group(group: list[dict], levels: dict[float, int]) -> str:
    """A group of homogeneous lines → heading, list entry or paragraph."""
    size = group[0]["size"]
    raw_first = group[0]["raw"]

    level = levels.get(size)
    if level and len(group) <= 3:
        title = unspace(re.sub(r"[*_]", "", join_lines([l["text"] for l in group])))
        return f"{'#' * level} {title.strip()}"

    if m := NUMBER_RE.match(raw_first):
        rest = join_lines([l["text"] for l in group])
        return f"{m.group(1)}. {NUMBER_RE.sub('', rest, count=1).strip()}"
    if BULLET_RE.match(raw_first):
        rest = join_lines([l["text"] for l in group])
        return f"- {BULLET_RE.sub('', rest, count=1).strip()}"

    return unspace(join_lines([l["text"] for l in group]))


def table_markdown(rows: list[list]) -> str:
    rows = [[(c or "").replace("\n", " ").replace("|", "\\|").strip() for c in r]
            for r in rows if any(c for c in r)]
    if len(rows) < 2:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head, *body_rows = rows
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in body_rows]
    return "\n".join(out)


# --------------------------------------------------------------------------
# Extracting one page
# --------------------------------------------------------------------------
def inside(bbox, boxes) -> bool:
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return any(b[0] <= cx <= b[2] and b[1] <= cy <= b[3] for b in boxes)


def image_boxes(page) -> list[dict]:
    """What the page *shows*, rather than what the file stores.

    A PDF rarely displays an image as it is: it crops it, or cuts it into
    adjacent tiles. Extracting the stored object therefore yields a distorted
    image, or the same photograph in two pieces. The reasoning here is on the
    display rectangles, merging the abutting tiles.
    """
    boxes = []
    for info in page.get_images(full=True):
        xref, w, h = info[0], info[2], info[3]
        for rect in page.get_image_rects(xref):
            if rect.width < 8 or rect.height < 8:
                continue
            boxes.append({"rect": pymupdf.Rect(rect), "px": [(w, h)]})

    # Two tiles of one photograph touch exactly and share their perpendicular
    # edges; two neighbouring photographs keep a gutter between them.
    merged = True
    while merged:
        merged = False
        for i, a in enumerate(boxes):
            for j, b in enumerate(boxes[i + 1:], i + 1):
                if adjacent(a["rect"], b["rect"]):
                    a["rect"] |= b["rect"]
                    a["px"] += b["px"]
                    boxes.pop(j)
                    merged = True
                    break
            if merged:
                break

    return [b for b in boxes
            if b["rect"].width >= MIN_IMAGE_PX / 6 and b["rect"].height >= MIN_IMAGE_PX / 6]


def adjacent(a, b) -> bool:
    """True if a and b are two abutting tiles of the same image."""
    def touch(lo1, hi1, lo2, hi2):
        return -TILE_GAP <= lo2 - hi1 <= TILE_GAP or -TILE_GAP <= lo1 - hi2 <= TILE_GAP

    aligned_x = abs(a.x0 - b.x0) <= TILE_ALIGN and abs(a.x1 - b.x1) <= TILE_ALIGN
    aligned_y = abs(a.y0 - b.y0) <= TILE_ALIGN and abs(a.y1 - b.y1) <= TILE_ALIGN
    return ((aligned_x and touch(a.y0, a.y1, b.y0, b.y1))
            or (aligned_y and touch(a.x0, a.x1, b.x0, b.x1)))


def rows_of(boxes: list[dict]) -> list[list[dict]]:
    """Group into rows the images sharing a horizontal band."""
    rows: list[list[dict]] = []
    for box in sorted(boxes, key=lambda b: (round(b["rect"].y0, 1), b["rect"].x0)):
        r = box["rect"]
        placed = False
        for row in rows:
            ref = row[0]["rect"]
            overlap = min(r.y1, ref.y1) - max(r.y0, ref.y0)
            if overlap > ROW_OVERLAP * min(r.height, ref.height):
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])
    for row in rows:
        row.sort(key=lambda b: b["rect"].x0)
    return rows


def write_box(page, box: dict, assets: Path, index: int,
              seen: dict[str, str]) -> str | None:
    """Render the page area exactly as it is displayed, and write it."""
    rect = box["rect"]
    # Sample at the source's density: neither interpolate nor lose detail.
    zoom = max((w / rect.width for w, _ in box["px"]), default=2.0)
    zoom = max(min(zoom, ZOOM_RANGE[1], MAX_IMAGE_PX / rect.width), ZOOM_RANGE[0])
    try:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=rect)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    except Exception:
        return None

    return store(img, assets, index, seen)


def lines_of(page, body: float, running: set[str], boxes: list) -> list[dict]:
    """The useful text lines: outside the running margins, outside tables."""
    out = []
    h = page.rect.height
    top, bottom = h * MARGIN_BAND, h * (1 - MARGIN_BAND)
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            x0, y0, x1, y1 = line["bbox"]
            raw = "".join(s["text"] for s in spans).strip()
            size = max(round(s["size"], 1) for s in spans)

            # A running head or a folio: small, and hugging the page edge.
            if (y1 <= top or y0 >= bottom) and size <= body:
                continue
            if raw.isdigit() or re.sub(r"\d+", "#", raw) in running:
                continue
            if inside(line["bbox"], boxes):
                continue

            out.append({"y0": y0, "y1": y1, "x0": x0, "size": size, "raw": clean(raw),
                        "text": "".join(emphasize(s) for s in spans).strip()})
    out.sort(key=lambda l: (round(l["y0"], 1), l["x0"]))
    return out


def group_lines(lines: list[dict]) -> list[list[dict]]:
    """Re-join the lines into paragraphs.

    A PDF does not encode paragraphs: it encodes lines. The break is inferred
    from a change of body size, an abnormal leading, or a bullet at the start of
    a line.
    """
    groups: list[list[dict]] = []
    for line in lines:
        if groups:
            prev = groups[-1][-1]
            gap = line["y0"] - prev["y1"]
            same_size = abs(line["size"] - prev["size"]) < 0.6
            starts_item = bool(BULLET_RE.match(line["raw"]) or NUMBER_RE.match(line["raw"]))
            if same_size and gap <= prev["size"] * 0.9 and not starts_item:
                groups[-1].append(line)
                continue
        groups.append([line])
    return groups


def page_markdown(doc, page, assets: Path, levels: dict[float, int],
                  body: float, running: set[str], seen: dict[str, str],
                  counter: list[int]) -> list[str]:
    try:
        found = list(page.find_tables().tables)
    except Exception:
        found = []
    boxes = [t.bbox for t in found]

    elements: list[tuple[float, float, str]] = []
    for t in found:
        md = table_markdown(t.extract())
        if md:
            elements.append((t.bbox[1], t.bbox[0], md))

    for group in group_lines(lines_of(page, body, running, boxes)):
        md = render_group(group, levels)
        if md:
            elements.append((group[0]["y0"], group[0]["x0"], md))

    # A row of images in the original stays a row: several images in the same
    # Markdown paragraph form a figure of several panels.
    for row in rows_of(image_boxes(page)):
        names = []
        for box in row:
            counter[0] += 1
            name = write_box(page, box, assets, counter[0], seen)
            if name is None:
                counter[0] -= 1
            else:
                names.append(name)
        if not names:
            continue
        lines = [f'![Image](assets/{n})' for n in names[:-1]]
        lines.append(f'![Image](assets/{names[-1]} "Figure — to be captioned")')
        elements.append((row[0]["rect"].y0, row[0]["rect"].x0, "\n".join(lines)))

    elements.sort(key=lambda e: (round(e[0], 1), e[1]))
    return [e[2] for e in elements]


# --------------------------------------------------------------------------
# Document
# --------------------------------------------------------------------------
def slugify(s: str) -> str:
    s = s.lower().strip()
    for a, b in (("à", "a"), ("â", "a"), ("é", "e"), ("è", "e"), ("ê", "e"),
                 ("ë", "e"), ("î", "i"), ("ï", "i"), ("ô", "o"), ("ö", "o"),
                 ("û", "u"), ("ü", "u"), ("ù", "u"), ("ç", "c")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "document"


def yaml_str(v: str) -> str:
    v = str(v).replace('"', "'").strip()
    return f'"{v}"' if v else '""'


def main() -> int:
    ap = argparse.ArgumentParser(description="Import an external PDF.")
    ap.add_argument("source", type=Path, help="the PDF to import")
    ap.add_argument("path", help="destination under library/, e.g. watch/wto-report")
    # No default value: the destination language is the user's decision, not the
    # tool's assumption.
    ap.add_argument("--lang", required=True, metavar="CODE",
                    help="target language, short code: fr, en, de, es…")
    ap.add_argument("--preset", default="report")
    ap.add_argument("--pages", help="range to import, e.g. 1-20")
    ap.add_argument("--force", action="store_true", help="overwrite an existing destination")
    ap.add_argument("--no-page-images", action="store_true",
                    help="do not render the source pages to PNG")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z]{2,3}(-[A-Za-z]{2,4})?", args.lang):
        print(f"error: “{args.lang}” is not a language code "
              f"(expected: fr, en, pt-BR…)", file=sys.stderr)
        return 1
    if not args.source.is_file():
        print(f"error: not found — {args.source}", file=sys.stderr)
        return 1

    parts = [slugify(p) for p in Path(args.path).parts if p not in (".", "..")]
    dest = LIBRARY.joinpath(*parts)
    if (doc_dir(dest) / ENTRY).exists() and not args.force:
        print(f"error: the document already exists — {dest.relative_to(ROOT)} "
              f"(--force to overwrite)", file=sys.stderr)
        return 1

    doc = pymupdf.open(args.source)
    first, last = 0, len(doc) - 1
    if args.pages:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", args.pages.strip())
        if not m:
            print("error: --pages expects “12” or “3-18”", file=sys.stderr)
            return 1
        first = int(m.group(1)) - 1
        last = int(m.group(2) or m.group(1)) - 1
    first, last = max(0, first), min(len(doc) - 1, last)

    assets = doc_dir(dest) / "assets"
    source_dir = dest / "sources"
    for p in (assets, source_dir):
        p.mkdir(parents=True, exist_ok=True)

    body = body_size(doc)
    levels = heading_levels(doc, body)
    running = running_text(doc)

    pages_dir = source_dir / "pages"
    if not args.no_page_images:
        pages_dir.mkdir(exist_ok=True)

    chunks: list[str] = []
    seen: dict[str, str] = {}      # digest of the rendering -> filename
    counter = [0]
    vector_pages: list[int] = []
    for i in range(first, last + 1):
        page = doc[i]
        chunks += page_markdown(doc, page, assets, levels, body, running,
                                seen, counter)
        # A vector drawing is not an image: it does not extract. The page is
        # reported so it can be redrawn with the diagram-design skill.
        if len(page.get_drawings()) > VECTOR_BUSY:
            vector_pages.append(i + 1)
        if not args.no_page_images:
            page.get_pixmap(matrix=pymupdf.Matrix(PAGE_SCALE, PAGE_SCALE)).save(
                pages_dir / f"p{i + 1:03d}.png")

    # Two identical consecutive blocks are an artefact of the page split.
    # Consecutive list entries form a single list.
    item = re.compile(r"^(?:- |\d{1,2}\. )")
    text: list[str] = []
    for c in chunks:
        if text and c == text[-1]:
            continue
        if text and item.match(c) and item.match(text[-1].split("\n")[-1]):
            text[-1] += "\n" + c
        else:
            text.append(c)
    extracted = "\n\n".join(text).strip() + "\n"

    try:
        import py3langid
        source_lang = py3langid.classify(extracted[:5000])[0]
    except Exception:
        source_lang = ""

    meta = doc.metadata or {}
    title = (meta.get("title") or "").strip() or args.source.stem.replace("-", " ")
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()

    (source_dir / "extracted.md").write_text(extracted, encoding="utf-8")
    (source_dir / "meta.json").write_text(json.dumps({
        "source": str(args.source),
        "sha256": digest,
        "imported": dt.date.today().isoformat(),
        "pages_total": len(doc),
        "pages_imported": [first + 1, last + 1],
        "pdf_metadata": {k: v for k, v in meta.items() if v},
        "body_size": body,
        "heading_sizes": {str(k): v for k, v in levels.items()},
        "images": len(seen),
        "vector_pages": vector_pages,
        "assets_kb": round(sum(f.stat().st_size for f in assets.glob("*")) / 1024),
        "unmapped_chars": sum(PUA_SEEN.values()),
        "source_language": source_lang,
        "page_images": None if args.no_page_images else "sources/pages/",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    notes = [f"IMPORTED, NOT TRANSLATED — {len(text)} blocks, {len(seen)} image(s).",
             f"Translate this body in place into: {args.lang}. The intact",
             "reference stays in sources/extracted.md; do not modify it."]
    if not args.no_page_images:
        notes.append("Source pages as images: sources/pages/ — look at them to "
                     "restore what the text alone loses (borderless tables, "
                     "columns, admonitions).")
    if vector_pages:
        notes.append("Vector drawings not extracted, to be redrawn with "
                     f"diagram-design: page(s) {', '.join(map(str, vector_pages))}.")
    if PUA_SEEN:
        notes.append(f"{sum(PUA_SEEN.values())} unreadable character(s) removed: the "
                     "source font encodes them in the private use area. Restore "
                     "them by looking at the page images.")

    front = "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        f"date: {dt.date.today().isoformat()}",
        f"preset: {args.preset}",
        f"lang: {args.lang}",
        "theme: light          # light | dark | both (both produces two PDFs)",
        f"source: {yaml_str(args.source.name)}",
        "---",
        "",
        "<!--",
        *(f"  {n}" for n in notes),
        "-->",
        "",
        "",
    ])
    (doc_dir(dest) / ENTRY).write_text(front + extracted, encoding="utf-8")

    rel = dest.relative_to(ROOT)
    print(f"  ✓ {rel}/index.md")
    print(f"    {last - first + 1} page(s) → {len(text)} blocks, {len(seen)} image(s)")
    print(f"    body {body} pt, heading levels: "
          f"{', '.join(f'{k}pt→h{v}' for k, v in levels.items()) or 'none'}")
    weight = sum(f.stat().st_size for f in assets.glob("*")) / 1024
    if seen:
        print(f"    images: {len(seen)} for {weight / 1024:.1f} MB")
    if vector_pages:
        print(f"    vector drawings not extracted: page(s) "
              f"{', '.join(map(str, vector_pages))} — to be redrawn")
    if source_lang and source_lang != args.lang:
        print(f"    source in “{source_lang}”, document targeted at “{args.lang}”")
    if PUA_SEEN:
        print(f"    {sum(PUA_SEEN.values())} undecodable character(s) removed "
              f"(font with private encoding) — check against the page images")
    if not args.no_page_images:
        print(f"    pages rendered in {rel}/sources/pages/ — look at them before translating")
    print(f"    translate index.md into {args.lang}, then: make build DOC={'/'.join(parts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
