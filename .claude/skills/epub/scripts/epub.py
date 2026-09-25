#!/usr/bin/env python3
"""Markdown → XHTML → EPUB 3, for reading on an e-reader.

The reflowable backbone, symmetrical with the `pdf` skill's build.py. The two share core/doc.py
and diverge from the HTML onwards: the paginated one inlines the SVG and lets
WeasyPrint compose pages; the reflowable one rasterises the SVG, splits at
level-1 headings, flattens the stylesheet and packages the result.

The founding constraint: most e-ink readers run on RMSDK, which does not resolve
`var()` and implements neither @media (monochrome) nor prefers-color-scheme.
There is therefore nothing to detect and nothing to branch on — one flattened
stylesheet is shipped, valid on every screen.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import uuid
import zipfile
from itertools import zip_longest
from pathlib import Path

from weasyprint import HTML

from core import doc, imaging, pdfpage

# A sibling script of this skill, not the core: the checks belong to the
# reflowable output alone. Resolved from this directory when run directly, and
# through the skill's tests/conftest.py under pytest.
import check
from core.doc import XML_HEAD_RE

ROOT = doc.ROOT
THEME = doc.THEME
EPUB_SHEET = THEME / "epub.css"

DECL_LINE_RE = re.compile(r"\s*--[\w-]+\s*:[^;}]*;?")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(css: str) -> str:
    """Strip the CSS comments before anything else.

    This stylesheet documents its own reason for existing by quoting the syntax
    it fights — `@page`, `var()`. A literal search would take that prose for
    code and delete neighbouring rules. Removing them first defuses the trap at
    source, and a stylesheet embedded in an archive has no use for author notes
    in any case.

    CSS comments do not nest, so the non-greedy match is exact rather than an
    approximation.
    """
    return COMMENT_RE.sub("", css)


def drop_at_rule(css: str, name: str) -> str:
    """Remove every `name { … }` rule, nested braces included.

    `@page` carries margin boxes (`@top-center { … }`): a naive regular
    expression would stop at the first closing brace and leave the end of the
    block in the stylesheet.
    """
    out, i = [], 0
    while True:
        j = css.find(name, i)
        if j < 0:
            out.append(css[i:])
            return "".join(out)
        out.append(css[i:j])
        k = css.find("{", j)
        if k < 0:
            return "".join(out) + css[j:]
        depth, k = 1, k + 1
        while k < len(css) and depth:
            depth += (css[k] == "{") - (css[k] == "}")
            k += 1
        i = k


def flatten_css(css: str, tokens: dict[str, str]) -> str:
    """Resolve the var(), drop the variable declarations and the @page."""
    css = strip_comments(css)
    css = drop_at_rule(css, "@page")
    css = doc.subst_vars(css, tokens)
    css = DECL_LINE_RE.sub("", css)
    return css


def epub_css(d: Path, tokens: dict[str, str]) -> str:
    """The embedded stylesheet: theme/epub.css, plus the document's departure."""
    parts = [EPUB_SHEET.read_text(encoding="utf-8")]
    local = doc.doc_dir(d) / "theme.css"
    if local.exists():
        # A document's local departure carries its content typography — the
        # formulae in components/led/, for instance. So it follows into the
        # EPUB, stripped of whatever concerns the page alone.
        parts.append(f"\n/* {local.name} */\n" + local.read_text(encoding="utf-8"))
    return flatten_css("\n".join(parts), tokens)


TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(fragment: str) -> str:
    return " ".join(TAG_RE.sub("", fragment).split())


def heading_level(html_text: str) -> int:
    """The highest heading level the document uses.

    The library follows two conventions: some documents open on `#`, others on
    `##`, their title then living in the front matter. Splitting at a fixed
    level would give half of them a single chapter — precisely the monolithic
    pagination the split is meant to avoid.

    All six HTML levels are swept, not the first three: limiting the sweep to
    the expected levels would reproduce that defect, silently, on the first
    document that opened lower.
    """
    for n in range(1, 7):
        if re.search(rf"<h{n}\b", html_text):
            return n
    return 1


def heading_re(level: int) -> re.Pattern:
    """The pattern capturing a heading at the given level."""
    return re.compile(rf"<h{level}\b[^>]*>(.*?)</h{level}>", re.S)


def heading_id_re(level: int) -> re.Pattern:
    """Capture (id, text) for the headings at the given level that carry an id."""
    return re.compile(
        rf'<h{level}\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h{level}>', re.S)


def split_chapters(html_text: str, fallback: str,
                    level: int | None = None) -> list[tuple[str, str]]:
    """Split at the highest heading level. Returns [(title, fragment), …].

    An e-reader paginates per file: splitting at the headings of the level the
    document actually uses gives it units that mean something, rather than the
    arbitrary slices Calibre would lay down by itself.
    """
    level = heading_level(html_text) if level is None else level
    pattern = heading_re(level)
    bounds = [m.start() for m in pattern.finditer(html_text)]
    if not bounds:
        return [(fallback, html_text)]

    chapters: list[tuple[str, str]] = []
    head = html_text[:bounds[0]]
    if head.strip():
        chapters.append((fallback, head))

    for i, start in enumerate(bounds):
        end = bounds[i + 1] if i + 1 < len(bounds) else len(html_text)
        fragment = html_text[start:end]
        title = strip_tags(pattern.search(fragment).group(1)) or fallback
        chapters.append((title, fragment))
    return chapters


# Past this number of columns a table no longer folds: on a six-inch screen it
# would leave roughly six characters per column. The repository's five-column
# tables, on the other hand, carry long prose that wraps by itself and gives a
# tall table, perfectly readable.
TABLE_THRESHOLD = 5

TABLE_RE = re.compile(r"<table\b.*?</table>", re.S)
ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<t([hd])\b[^>]*>(.*?)</t\1>", re.S)


def transpose_wide_tables(html_text: str,
                          threshold: int = TABLE_THRESHOLD) -> str:
    """Turn the over-wide tables into blocks, one per row.

    Each row becomes a self-contained block, titled by its first cell, the
    others rendered as label/value pairs. Nothing is lost, and the result
    reflows at any text size.

    It exists only on the EPUB output: the index.md does not change and the PDF
    keeps its full-width matrix.
    """
    def one(m: re.Match) -> str:
        table = m.group(0)
        rows = [CELL_RE.findall(r) for r in ROW_RE.findall(table)]
        rows = [l for l in rows if l]
        if not rows or len(rows[0]) <= threshold:
            return table

        headers = [c.strip() for _, c in rows[0]]
        blocks = []
        for row in rows[1:]:
            cells = [c.strip() for _, c in row]
            if not cells:
                continue
            # zip_longest rather than zip: the latter truncates to the shorter
            # of the two lists, so a row shorter than the header would lose its
            # last labels in silence. The fill keeps the label without a value,
            # or the value without a label — ugly either way, but nothing
            # disappears, which is the contract.
            pairs = "".join(
                f"<dt>{h}</dt><dd>{v}</dd>"
                for h, v in zip_longest(headers[1:], cells[1:], fillvalue=""))
            blocks.append(f'<div class="row-block">'
                         f'<p class="row-title">{cells[0]}</p>'
                         f"<dl>{pairs}</dl></div>")
        return "\n".join(blocks)

    return TABLE_RE.sub(one, html_text)


# --------------------------------------------------------------------------
# Rasterising the diagrams
# --------------------------------------------------------------------------
# Rasterisation width. Enough to stay sharp on a high-density e-reader, modest
# enough not to weigh the archive down.
RASTER_WIDTH = 1600

SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.S)
VIEWBOX_RE = re.compile(
    r'\sviewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*"')
WH_RE = re.compile(r'\s(width|height)="([\d.]+)(?:px)?"')
IMG_ANY_RE = re.compile(r'<img\b([^>]*?)\bsrc="([^"]+)"([^>]*?)/?>')


def svg_size(svg: str) -> tuple[float, float]:
    """Intrinsic dimensions: viewBox first, width/height second.

    Both patterns are bounded to the opening <svg> tag. Without that bound, the
    viewBox of an internal <symbol> or <marker> would win over the root's, and
    the page would be rasterised at its dimensions — silently. The space
    required before the attribute stops `width` also matching the “width” in
    `stroke-width`.
    """
    m = SVG_OPEN_RE.match(svg.strip())
    if not m:
        raise doc.DocError("SVG with no recognisable root tag")
    head = m.group(0)

    v = VIEWBOX_RE.search(head)
    if v:
        return float(v.group(1)), float(v.group(2))
    dims = {k: float(val) for k, val in WH_RE.findall(head)}
    if "width" in dims and "height" in dims:
        return dims["width"], dims["height"]
    raise doc.DocError("SVG with neither viewBox nor width/height: dimensions unknown")


def rasterize_svg(svg: str, width_px: int = RASTER_WIDTH) -> bytes:
    """SVG → PNG, through WeasyPrint then core.pdfpage.

    This detour avoids introducing a second SVG engine: the diagram is rendered
    by exactly the one that produces the PDF, so both outputs show the same
    image. A cairosvg would have made the two formats diverge.
    """
    w, h = svg_size(svg)
    page = (f"<style>@page{{size:{w}px {h}px;margin:0}}"
            f"html,body{{margin:0;padding:0}}"
            f"svg{{display:block;width:{w}px;height:{h}px}}</style>{svg}")
    return imaging.to_png(
        pdfpage.first(HTML(string=page).write_pdf(), width_px=width_px))


def collect_images(html_text: str, d: Path, tokens: dict[str, str],
                   width_px: int = RASTER_WIDTH) -> tuple[str, dict[str, bytes]]:
    """Rasterise the SVG, copy the other images over, rewrite the `src`.

    The output name pairs the file's stem with a digest of the full relative
    path, so two images of the same name in two subdirectories cannot overwrite
    each other in the archive's flat directory.
    """
    assets: dict[str, bytes] = {}

    def one(m: re.Match) -> str:
        before, src, after = m.group(1), m.group(2), m.group(3)
        if "://" in src:
            return m.group(0)
        inside = doc.doc_dir(d).resolve()
        f = (inside / src).resolve()
        if not f.is_file() or inside not in f.parents:
            return m.group(0)

        # The name derives from the file's stem plus a short digest of its
        # relative path. Simply replacing “/” with “-” would not be injective:
        # `assets-a/x.svg` and `assets/a-x.svg` would give the same name, and
        # the second image would overwrite the first in silence. The
        # subdirectories are not carried over as they are — a “/” would make
        # the XML identifier the manifest derives from it illegal.
        # Relative to `document/`, not to the root: the name depends on
        # where the file sits *inside* the document, so moving a document
        # does not rename every image in its archive.
        rel = str(f.relative_to(inside))
        digest = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]
        if f.suffix.lower() == ".svg":
            svg = XML_HEAD_RE.sub("", f.read_text(encoding="utf-8")).strip()
            name = f"{f.stem}-{digest}.png"
            assets[name] = rasterize_svg(doc.subst_vars(svg, tokens), width_px)
        else:
            name = f"{f.stem}-{digest}{f.suffix}"
            assets[name] = f.read_bytes()
        return f'<img{before}src="../images/{name}"{after}/>'

    return IMG_ANY_RE.sub(one, html_text), assets


# The proportions of an e-book cover, at a resolution that stays sharp on a
# high-density e-reader.
COVER_WIDTH, COVER_HEIGHT = 1600, 2560


def cover_html(fm: dict, tokens: dict[str, str]) -> str:
    """The cover, composed in HTML, to be rendered as an image.

    It is drawn for the thumbnail: at 300px wide the reduction is fivefold and
    only the title stays readable. The title therefore takes most of the
    surface, and the rest is treated as support — present at full size, effaced
    in the thumbnail, which is the right order.

    It is the only surface in the EPUB that lays down a background: it is
    rendered as an image, so it does not go through the reader's settings.
    """
    def field(key: str) -> str:
        v = fm.get(key)
        return doc.e(v) if v else ""

    block = []
    if field("eyebrow"):
        block.append(f'<p class="eyebrow">{field("eyebrow")}</p>')
    block.append(f'<h1>{field("title")}</h1>')
    if field("subtitle"):
        block.append(f'<p class="subtitle">{field("subtitle")}</p>')

    foot = f'<p class="date">{field("date")}</p>' if field("date") else ""

    return f"""<style>
@page {{ size: {COVER_WIDTH}px {COVER_HEIGHT}px; margin: 0; }}
:root {{
  --paper: {tokens.get("paper", "#FFFFFF")};
  --ink: {tokens.get("ink", "#000000")};
  --accent: {tokens.get("accent", "#36654C")};
  --muted: {tokens.get("muted", "#555555")};
  --title-size: 132px;
}}
html, body {{ margin: 0; padding: 0; }}
body {{
  width: {COVER_WIDTH}px; height: {COVER_HEIGHT}px;
  background: var(--paper); color: var(--ink);
  font-family: sans-serif;
  padding: 190px 150px; box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: space-between;
}}
.rule {{ width: 320px; height: 16px; background: var(--accent); }}
.eyebrow {{
  font-size: 46px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--accent); margin: 0 0 44px; font-weight: 700;
}}
h1 {{
  font-size: var(--title-size); line-height: 1.06; font-weight: 700;
  margin: 0; letter-spacing: -0.015em;
}}
.subtitle {{
  font-size: 54px; line-height: 1.35; color: var(--muted);
  margin: 48px 0 0; font-weight: 400;
}}
.date {{ font-size: 40px; color: var(--muted); margin: 0; }}
</style>
<body><div class="rule"></div><div>{"".join(block)}</div>{foot}</body>"""


def render_cover(fm: dict, tokens: dict[str, str]) -> bytes:
    """The cover rendered to PNG, through the same chain as the diagrams."""
    return imaging.to_png(
        pdfpage.first(HTML(string=cover_html(fm, tokens)).write_pdf(),
                      width_px=COVER_WIDTH))


# --------------------------------------------------------------------------
# EPUB 3 packaging
# --------------------------------------------------------------------------
# A namespace of the repository's own: a document's identifier must depend on
# its path alone, never on the moment it was built. The URL keeps the
# repository's former name on purpose: changing it would give every EPUB a new
# identifier, and an e-reader would take each one for a different book.
UID_NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/pdf-creator")

# A fixed timestamp on the zip entries: two builds of the same document then
# produce the same bytes. This is the floor the zip format imposes.
EPOCH = (1980, 1, 1, 0, 0, 0)

CONTAINER_XML = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def doc_uid(rel: str) -> str:
    """A stable identifier, derived from the document's path.

    A rebuild yields the same identifier, so the e-reader recognises an update
    instead of stacking a duplicate. This is what makes syncing out/epub/ to the
    device wholesale usable.
    """
    return f"urn:uuid:{uuid.uuid5(UID_NS, rel)}"


def chapter_xhtml(title: str, body: str, lang: str) -> str:
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" '
            f'lang="{doc.e(lang)}" xml:lang="{doc.e(lang)}">\n'
            f'<head><meta charset="utf-8"/><title>{doc.e(title)}</title>'
            f'<link rel="stylesheet" type="text/css" href="../styles/epub.css"/>'
            f'</head>\n<body>{body}</body>\n</html>\n')


def cover_xhtml(title: str, lang: str) -> str:
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" '
            f'lang="{doc.e(lang)}" xml:lang="{doc.e(lang)}">\n'
            f'<head><meta charset="utf-8"/><title>{doc.e(title)}</title>'
            f'<link rel="stylesheet" type="text/css" href="styles/epub.css"/>'
            f'</head>\n<body class="cover-page">'
            f'<img src="images/cover.png" alt="{doc.e(title)}"/>'
            f'</body>\n</html>\n')


def nav_xhtml(fm: dict, chapters: list[tuple[str, str]], level: int = 1) -> str:
    """The native table of contents: the e-reader shows it in its own menu.

    Two levels — the split level carries the chapters, the level immediately
    below lets the reader enter a long record without scrolling through it.

    `level` is a parameter rather than a constant, because the library follows
    two writing conventions. Three documents open on `#` (split at 1, so
    sub-entries at h2); four open on `##`, their title living in the front
    matter (split at 2, so sub-entries at h3). A fixed `<h2>` would then list
    every chapter of those four documents as its own sub-entry — precisely the
    flat table of contents level 2 was meant to avoid. So `level` must match the
    level actually passed to `split_chapters` for this document.
    """
    lang = doc.e(fm.get("lang", "fr"))
    sub_pattern = heading_id_re(level + 1)
    entries = []
    for i, (title, body) in enumerate(chapters, 1):
        href = f"text/ch{i:02d}.xhtml"
        subs = [f'<li><a href="{href}#{doc.e(sid)}">'
                f"{doc.e(strip_tags(stext))}</a></li>"
                for sid, stext in sub_pattern.findall(body)]
        inner = f"<ol>{''.join(subs)}</ol>" if subs else ""
        entries.append(f'<li><a href="{href}">{doc.e(title)}</a>{inner}</li>')

    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" '
            f'xmlns:epub="http://www.idpf.org/2007/ops" '
            f'lang="{lang}" xml:lang="{lang}">\n'
            f'<head><meta charset="utf-8"/><title>Sommaire</title>'
            f'<link rel="stylesheet" type="text/css" href="styles/epub.css"/>'
            f'</head>\n<body>\n'
            f'<nav epub:type="toc" id="toc"><h1>Sommaire</h1>'
            f'<ol>{"".join(entries)}</ol></nav>\n'
            f'</body>\n</html>\n')


def content_opf(fm: dict, chapters: list[tuple[str, str]],
                images: list[str], uid: str) -> str:
    lang = doc.e(fm.get("lang", "fr"))
    date = str(fm.get("date") or "1980-01-01")
    # An unquoted `date:` carrying a time gives a datetime, whose str() holds a
    # space: the timestamp would come out malformed and a validator would reject
    # the archive. Only the date part is kept.
    date = date.split(" ")[0].split("T")[0]
    # A timestamp derived from the document's date, never from the current
    # time: two builds must give the same file.
    modified = f"{date}T00:00:00Z"

    items = [
        '<item id="nav" href="nav.xhtml" '
        'media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="styles/epub.css" media-type="text/css"/>',
        '<item id="coverpage" href="cover.xhtml" '
        'media-type="application/xhtml+xml"/>',
    ]
    # The ids are positional, never derived from the filename: a name holding a
    # space or an exotic character would produce an illegal XML NCName and get
    # the archive rejected. The cover keeps the fixed id `cover-image`, which
    # the EPUB 2 compatibility `<meta name="cover">` below references; the other
    # images are numbered in sorted order. The href, meanwhile, always stays the
    # real filename.
    n = 0
    for name in sorted(images):
        if name == "cover.png":
            ident, props = "cover-image", ' properties="cover-image"'
        else:
            n += 1
            ident, props = f"img-{n:02d}", ""
        items.append(f'<item id="{ident}" href="images/{doc.e(name)}" '
                     f'media-type="image/png"{props}/>')
    for i, _ in enumerate(chapters, 1):
        items.append(f'<item id="ch{i:02d}" href="text/ch{i:02d}.xhtml" '
                     f'media-type="application/xhtml+xml"/>')

    spine = ['<itemref idref="coverpage"/>', '<itemref idref="nav"/>']
    spine += [f'<itemref idref="ch{i:02d}"/>' for i, _ in enumerate(chapters, 1)]

    # EPUB 3 would express a subtitle through a second dc:title carrying
    # `title-type: subtitle`. This repository's subtitle lives on the cover,
    # which is an image: declaring it here would serve no reader.

    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
            f'unique-identifier="uid" xml:lang="{lang}">\n'
            f'  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
            f'    <dc:identifier id="uid">{doc.e(uid)}</dc:identifier>\n'
            f'    <dc:title id="t">{doc.e(fm.get("title", ""))}</dc:title>\n'
            f'    <dc:language>{lang}</dc:language>\n'
            f'    <dc:date>{doc.e(date)}</dc:date>\n'
            f'    <meta property="dcterms:modified">{modified}</meta>\n'
            f'    <meta name="cover" content="cover-image"/>\n'
            f'  </metadata>\n'
            f'  <manifest>\n    ' + "\n    ".join(items) + '\n  </manifest>\n'
            f'  <spine>\n    ' + "\n    ".join(spine) + '\n  </spine>\n'
            f'</package>\n')


def write_epub(path: Path, files: dict[str, bytes | str]) -> None:
    """Write the archive. `mimetype` must be the first entry, uncompressed.

    It is the format's only structural constraint, and it is what allows an EPUB
    to be recognised from its first bytes, without decompressing it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        head = zipfile.ZipInfo("mimetype", date_time=EPOCH)
        head.compress_type = zipfile.ZIP_STORED
        z.writestr(head, "application/epub+zip")

        z.writestr(zipfile.ZipInfo("META-INF/container.xml", date_time=EPOCH),
                   CONTAINER_XML)
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name])


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------
# The presets that produce an EPUB. For `slides`, `letter` and `onepager` the
# page layout *is* the point: reflowing it would destroy it.
EPUB_PRESETS = {"report"}


def table_threshold(fm: dict) -> int:
    """The document's transposition threshold.

    Overridable through the front matter, for the wide table that would take
    transposition badly:

        epub:
          table-threshold: 12
    """
    settings = fm.get("epub") or {}
    return int(settings.get("table-threshold", TABLE_THRESHOLD))


def build_epub(d: Path) -> Path:
    """Build a document's EPUB. Returns the path written."""
    fm, body_md = doc.load_doc(d)
    rel = str(d.relative_to(doc.LIBRARY))
    tokens = doc.token_map(d, {**fm, "theme": "epub"})

    body, _ = doc.convert(body_md, tokens, d.name, icon_color="currentColor")
    body = transpose_wide_tables(body, table_threshold(fm))
    body, images = collect_images(body, d, tokens)
    doc.check_xhtml(body, rel)

    # The split level is computed once, then handed to split_chapters and to
    # nav_xhtml: the two must agree, or every chapter gets listed as its own
    # sub-entry (ruling 16).
    level = heading_level(body)
    chapters = split_chapters(body, fm["title"], level)
    images["cover.png"] = render_cover(fm, tokens)

    files: dict[str, bytes | str] = {
        "OEBPS/content.opf": content_opf(fm, chapters, list(images), doc_uid(rel)),
        "OEBPS/nav.xhtml": nav_xhtml(fm, chapters, level),
        "OEBPS/cover.xhtml": cover_xhtml(fm["title"], fm.get("lang", "fr")),
        "OEBPS/styles/epub.css": epub_css(d, tokens),
    }
    for i, (title, fragment) in enumerate(chapters, 1):
        files[f"OEBPS/text/ch{i:02d}.xhtml"] = \
            chapter_xhtml(title, fragment, fm.get("lang", "fr"))
    for name, data in images.items():
        files[f"OEBPS/images/{name}"] = data

    target = doc.out_dir(d, "epub") / f"{fm['slug']}.epub"
    write_epub(target, files)
    return target


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build the EPUBs from the Markdown sources.")
    ap.add_argument("targets", nargs="*",
                    help="directories or topics (default: the whole library)")
    args = ap.parse_args()

    try:
        docs = doc.find_docs(args.targets)
    except doc.DocError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    failures = 0
    epubcheck_absent = False
    for d in docs:
        rel = doc.shown(d)
        try:
            fm, _ = doc.load_doc(d)
            if fm["preset"] not in EPUB_PRESETS:
                print(f"  · {rel} — preset “{fm['preset']}” skipped: "
                      f"its page layout is its point")
                continue
            target = build_epub(d)
        except doc.DocError as exc:
            print(f"  ✗ {rel} — {exc}", file=sys.stderr)
            failures += 1
        except Exception as exc:
            print(f"  ✗ {rel} — {type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
        else:
            kb = target.stat().st_size / 1024
            anomalies = check.validate(target)

            # epubcheck is optional (it needs Java): None means it did not run,
            # not that it validated the archive. A silent absence would read as
            # a success — exactly the defect this check corrects.
            result = check.epubcheck(target)
            if result is None:
                epubcheck_absent = True
            else:
                anomalies += [f"epubcheck: {m}" for m in result]

            if anomalies:
                print(f"  ✗ {doc.shown(target)}", file=sys.stderr)
                for a in anomalies:
                    print(f"      {a}", file=sys.stderr)
                failures += 1
            else:
                print(f"  ✓ {doc.shown(target)} ({kb:.0f} kB)")

    if epubcheck_absent:
        print("  · epubcheck missing — EPUB 3 conformance not verified "
              "(optional, needs Java)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
