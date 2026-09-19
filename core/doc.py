#!/usr/bin/env python3
"""The document: discovery, front matter, Markdown → HTML, token map.

This module is the upstream half shared by both output backbones:

    pdf/scripts/build.py   paginated   Markdown → HTML → PDF (WeasyPrint)
    epub/scripts/epub.py   reflowable  Markdown → XHTML → EPUB 3

Both under .claude/skills/. This module is core because both need it.

It knows nothing about the destination format. In particular it **does not
inline SVG**: the paginated backbone inlines them so the cascade reaches them,
the EPUB one rasterises them. Each backbone decides.
"""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library"
OUT = ROOT / "out"
THEME = ROOT / "theme"
ENTRY = "index.md"
# A document is a root directory holding five roles, and the build reads one of
# them (docs/architecture.md §11). Everything under `document/` is what a reader
# ends up with; `sources/`, `study/`, `generators/` and `.work/` sit beside it
# and the build never opens them.
DOCUMENT = "document"
# Everything a command can make again, inside the document because that is what
# it is about, hidden because it is disposable, and the only directory
# `make clean` removes from a document.
WORK = ".work"
# `epub` is not a preset but the reflowable output's stylesheet: it lives in
# theme/ to stay inside the cascade, without being offered as a register.
PRESETS = {p.stem for p in THEME.glob("*.css")} - {"base", "page", "code", "epub"}

MD_EXTENSIONS = [
    "extra",            # tables, footnotes, attr_list, def_list, fenced_code, abbr
    "admonition",
    "sane_lists",
    "smarty",
    "toc",
    "codehilite",
    "core.mdext:FiguresExtension",
    "core.mdext:IconsExtension",
]
MD_CONFIG = {
    "toc": {"toc_depth": "1-3", "permalink": False},
    # noclasses=False: the Pygments classes are styled by theme/code.css, so
    # with the art direction's roles rather than an imported palette.
    "codehilite": {"guess_lang": False, "noclasses": False},
    "smarty": {"substitutions": {
        "left-single-quote": "‘", "right-single-quote": "’",
        "left-double-quote": "« ", "right-double-quote": " »"}},
}

DEFAULTS = {
    "preset": "report",
    "lang": "fr",
    "toc": None,       # None = derived from the preset
    "cover": None,     # None = derived from the preset
    "head": None,      # title banner when there is no cover
    "theme": "light",
}
# Presets with neither a cover nor a table of contents by default
LIGHTWEIGHT = {"onepager", "letter"}
THEMES = {"light", "dark", "both"}


class DocError(Exception):
    pass


# --------------------------------------------------------------------------
# Discovery and reading
# --------------------------------------------------------------------------
def doc_dir(d: Path) -> Path:
    """The one directory of a document that the build reads.

    Every path inside a document goes through here rather than being built at
    the call site, so that the layout is stated once.
    """
    return d / DOCUMENT


def is_doc(d: Path) -> bool:
    return (d / DOCUMENT / ENTRY).is_file()


def find_docs(targets: list[str]) -> list[Path]:
    """Resolve CLI paths into document roots.

    A root is the directory *holding* `document/`, not `document/` itself: its
    name is the slug, and its path under `library/` is the output path. Given
    the entry or the directory that holds it, both resolve to the root.
    """
    if not targets:
        roots = [LIBRARY]
    else:
        roots = []
        for t in targets:
            p = Path(t)
            if not p.is_absolute():
                p = (ROOT / p).resolve() if (ROOT / p).exists() else (LIBRARY / p).resolve()
            if p.is_file() and p.name == ENTRY:
                p = p.parent
            if p.name == DOCUMENT and (p / ENTRY).is_file():
                p = p.parent
            if not p.exists():
                raise DocError(f"path not found: {t}")
            roots.append(p)

    found: list[Path] = []
    for r in roots:
        if is_doc(r):
            found.append(r)
        else:
            # `document/` and not just the entry: an index.md a user keeps in
            # their own material is not a document, and `sources/` is theirs.
            found.extend(sorted(p.parent.parent
                                for p in r.rglob(f"{DOCUMENT}/{ENTRY}")))
    if not found:
        where = ", ".join(targets) or str(LIBRARY.relative_to(ROOT))
        raise DocError(f"no document ({DOCUMENT}/{ENTRY}) found in: {where}")
    # de-duplicate, preserving order
    return list(dict.fromkeys(found))


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise DocError("front matter must be a YAML mapping")
    return meta, parts[2].lstrip("\n")


def load_doc(d: Path) -> tuple[dict, str]:
    meta, body = split_front_matter(
        (doc_dir(d) / ENTRY).read_text(encoding="utf-8"))
    fm = {**DEFAULTS, **meta}

    if fm["theme"] not in THEMES:
        raise DocError(f"unknown theme “{fm['theme']}” "
                       f"(expected: {', '.join(sorted(THEMES))})")
    if fm["preset"] not in PRESETS:
        raise DocError(f"unknown preset “{fm['preset'] }” "
                       f"(available: {', '.join(sorted(PRESETS))})")
    if fm["toc"] is None:
        fm["toc"] = fm["preset"] not in LIGHTWEIGHT
    if fm["cover"] is None:
        fm["cover"] = fm["preset"] not in LIGHTWEIGHT
    if fm["head"] is None:
        fm["head"] = not fm["cover"]
    fm.setdefault("title", d.name.replace("-", " ").capitalize())
    fm.setdefault("slug", d.name)
    return fm, body


def out_dir(d: Path, kind: str = "pdf") -> Path:
    """A document's output directory, under out/<kind>/<relative path>."""
    return OUT / kind / d.relative_to(LIBRARY)


def work_dir(d: Path, kind: str) -> Path:
    """A document's disposable working directory, `<root>/.work/<kind>/`."""
    return d / WORK / kind


def work_dirs(library: Path | None = None) -> list[Path]:
    """Every `.work/` of the library — exactly what `clean()` may remove.

    Taken from the document roots rather than from a glob for `.work`: a
    directory of that name inside `sources/` is the user's, whatever it is
    called, and nothing here deletes it.
    """
    library = LIBRARY if library is None else library
    roots = sorted(p.parent.parent
                   for p in library.rglob(f"{DOCUMENT}/{ENTRY}"))
    return [r / WORK for r in roots if (r / WORK).is_dir()]


def clean(targets: list[str] | None = None) -> list[Path]:
    """Remove the build outputs and the documents' `.work/`, and nothing else.

    With targets, only those documents' `.work/`, and `out/` is left alone:
    a clean that can only be total is a clean nobody runs.

    This deletes inside `library/`, which is user content and is not versioned.
    What it may remove is decided here, by the layout, and never by a pattern
    written at the call site.
    """
    removed = []
    if targets:
        wanted = {d / WORK for d in find_docs(targets)}
        paths = [w for w in work_dirs() if w in wanted]
    else:
        paths = work_dirs()
        if OUT.exists():
            paths.append(OUT)
    for path in paths:
        shutil.rmtree(path)
        removed.append(path)
    return removed


# --------------------------------------------------------------------------
# HTML assembly
# --------------------------------------------------------------------------
def e(v) -> str:
    return html.escape(str(v), quote=True)


# --------------------------------------------------------------------------
# Art-direction tokens
# --------------------------------------------------------------------------
DECL_RE = re.compile(r"--([\w-]+)\s*:\s*([^;}]+)")
VAR_RE = re.compile(r"var\(\s*--([\w-]+)\s*(?:,\s*([^)]*))?\)")
XML_HEAD_RE = re.compile(r"<\?xml.*?\?>|<!DOCTYPE[^>]*>", re.S)


def block(css: str, selector: str) -> str:
    """The body of a stylesheet's first `selector { … }` rule."""
    i = css.find(selector)
    if i < 0:
        return ""
    j, k = css.find("{", i), css.find("}", i)
    return css[j + 1:k] if 0 <= j < k else ""


def token_map(d: Path, fm: dict) -> dict[str, str]:
    """The variables' effective values, in cascade order.

    WeasyPrint does not resolve `var()` inside an SVG, so diagrams are written
    with roles and substituted here — which makes them follow the art direction
    *and* a document's local override.
    """
    tokens: dict[str, str] = {}
    css = (ROOT / "brand" / "tokens.css").read_text(encoding="utf-8")
    sources = [block(css, ":root")]
    theme = fm.get("theme")
    if theme in ("dark", "epub"):
        sources.append(block(css, f'[data-theme="{theme}"]'))
    local = doc_dir(d) / "theme.css"
    if local.exists():
        sources.append(block(local.read_text(encoding="utf-8"), ":root"))
    for src in sources:
        for name, value in DECL_RE.findall(src):
            tokens[name] = value.strip()
    return tokens


def subst_vars(svg: str, tokens: dict[str, str]) -> str:
    def one(m: re.Match) -> str:
        value = tokens.get(m.group(1))
        if value is not None:
            return value
        return (m.group(2) or "").strip() or "currentColor"
    # two passes: one variable may reference another
    for _ in range(2):
        svg, n = VAR_RE.subn(one, svg)
        if not n:
            break
    return svg


def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexa: str) -> float:
    """The relative sRGB luminance of a `#rrggbb` colour."""
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast(a: str, b: str) -> float:
    """The contrast ratio between two colours, in the WCAG sense."""
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def grey_level(hexa: str) -> int:
    """The grey (0-255) a monochrome screen renders for this colour.

    This is the measure that counts on an e-reader: two tints the eye tells
    apart can land on the same grey — or worse, on two greys of very different
    strength, with nothing having decided it.
    """
    L = luminance(hexa)
    s = L * 12.92 if L <= 0.0031308 else 1.055 * L ** (1 / 2.4) - 0.055
    return round(s * 255)


# --------------------------------------------------------------------------
# Admonition icons
# --------------------------------------------------------------------------
# Attributes are stripped from the opening <svg> tag only, and only when
# preceded by a space: without that constraint, `width` would also match the
# “width” inside `stroke-width`, leaving a truncated attribute and the icon at
# its default stroke.
ROOT_ATTR_RE = re.compile(r'\s+(?:width|height|class)="[^"]*"')
STROKE_W_RE = re.compile(r'\s+stroke-width="[^"]*"')

# One icon per admonition type. Writing an icon in the title yourself turns
# the automatic one off for that admonition.
ADMONITION_ICONS = {
    "note": "info",
    "info": "info",
    "important": "circle-alert",
    "warning": "triangle-alert",
    "attention": "triangle-alert",
    "caution": "triangle-alert",
    "danger": "octagon-alert",
    "error": "circle-x",
    "tip": "lightbulb",
    "hint": "lightbulb",
    "success": "circle-check",
    "check": "circle-check",
    "question": "circle-help",
    "example": "code",
    "quote": "quote",
    "abstract": "clipboard-list",
    "summary": "clipboard-list",
}
# Colour role per admonition type. The icon has to follow its frame, its
# colour being fixed at build time. Must stay identical to the three admonition
# groups in theme/base.css. Any type absent from this table is neutral.
ADMONITION_ROLE = {
    "important": "accent", "success": "accent", "check": "accent",
    "warning": "alert", "caution": "alert", "attention": "alert",
    "danger": "danger", "error": "danger",
}
ADMONITION_RE = re.compile(
    r'(<div class="admonition ([^"]*)">\s*<p class="admonition-title">)(?!\s*<span class="icon)')


def admonition_icons(doc_html: str) -> str:
    """Prefix each admonition's title with its type's icon."""
    def sub(m: re.Match) -> str:
        classes = m.group(2).split()
        for cls in classes:
            name = ADMONITION_ICONS.get(cls)
            if name:
                role = next((ADMONITION_ROLE[c] for c in classes
                             if c in ADMONITION_ROLE), "muted")
                return (f'{m.group(1)}<span class="icon icon-{role}" '
                        f'data-icon="{name}"></span>')
        return m.group(0)

    return ADMONITION_RE.sub(sub, doc_html)


ICONS = ROOT / "brand" / "icons"
ICON_SPAN_RE = re.compile(
    r'<span class="(icon[^"]*)"\s+data-icon="([a-z0-9-]+)"\s*>\s*</span>')
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
SVG_OPEN_RE = re.compile(r"<svg\b([^>]*)>", re.S)
LI_ICON_RE = re.compile(r'<li>(\s*)(<svg class="icon)')


def render_icon(name: str, cls: str, tokens: dict[str, str],
                color: str | None = None) -> str | None:
    """A Lucide SVG ready to inline, or None if the icon does not exist.

    `color` forces the glyph's colour. The EPUB passes `currentColor`: on an
    e-reader in night mode a fixed tint would become unreadable, whereas the
    glyph has to stay readable — it is what carries the admonition's meaning,
    the tint being only a reinforcement carried by the rule.
    """
    f = (ICONS / f"{name}.svg").resolve()
    if not f.is_file() or f.parent != ICONS.resolve():
        return None
    if color is None:
        role = next((c[5:] for c in cls.split() if c.startswith("icon-")), "ink")
        color = tokens.get(role, tokens.get("ink", "#000"))

    svg = COMMENT_RE.sub("", f.read_text(encoding="utf-8")).strip()
    m = SVG_OPEN_RE.match(svg)
    if not m:
        return None

    stroke = tokens.get("icon-stroke", "2")
    head = ROOT_ATTR_RE.sub("", m.group(1))   # the size comes from the CSS
    head = STROKE_W_RE.sub("", head)
    head = f' class="{cls}"{head} stroke-width="{stroke}"'
    return (f"<svg{head}>" + svg[m.end():]).replace("currentColor", color)


def inline_icons(doc_html: str, tokens: dict[str, str], rel: str,
                 color: str | None = None) -> str:
    def sub(m: re.Match) -> str:
        svg = render_icon(m.group(2), m.group(1), tokens, color)
        if svg is None:
            # unknown name: render the source text rather than lose it
            print(f"  · {rel} — unknown Lucide icon: {m.group(2)}", file=sys.stderr)
            return f":{m.group(2)}:"
        return svg

    doc_html = ICON_SPAN_RE.sub(sub, doc_html)
    # A list entry opening on an icon has its bullet replaced by that icon.
    # `attr_list` cannot target a <ul> and `:has()` does not exist in
    # WeasyPrint, so the marking happens here, entry by entry, which leaves a
    # mixed list behaving correctly.
    return LI_ICON_RE.sub(r'<li class="icon-item">\1\2', doc_html)


# --------------------------------------------------------------------------
# Markdown → HTML
# --------------------------------------------------------------------------
def convert(md_text: str, tokens: dict[str, str], rel: str,
            icon_color: str | None = None) -> tuple[str, str]:
    """Markdown → HTML, icons resolved. Returns (html, table of contents).

    The <img src="*.svg"> are left in place: each backbone handles them.
    """
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)
    html_body = md.convert(md_text)
    html_body = inline_icons(admonition_icons(html_body), tokens, rel, icon_color)
    return html_body, getattr(md, "toc", "")
