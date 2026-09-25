#!/usr/bin/env python3
"""Markdown -> HTML -> PDF, with the repository's art direction cascaded onto it.

Discovery: any directory under library/ holding an index.md is a document. The
depth is free and the intermediate directories are the topics, so there is no
register to keep up to date.

The stylesheet cascade, from the most general to the most specific:

    1. brand/tokens.css        the art direction — brand variables (generated)
    2. theme/base.css          typography and content elements
    3. theme/page.css          page geometry, headers, cover, table of contents
    4. theme/<preset>.css      the document's register (report, onepager, …)
    5. front matter `page:`    one-off overrides, injected into :root
    6. <doc>/theme.css         the document's local override (when present)
    7. front matter `css:`     the document's additional stylesheets

Each level only redefines what it needs: a document inherits the art direction
by default and writes down nothing but its own departure from it.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

from weasyprint import CSS, HTML

# OUT is not used here: it is re-exported for build.OUT, which the skill's
# tests/test_pdf_layout.py pins. ROOT comes from the core too: this file lives
# inside a skill, so its own parent directories say nothing about the repository.
from core.doc import (DOCUMENT, LIBRARY, OUT, ROOT, THEME, XML_HEAD_RE, DocError,
                      convert, doc_dir,
                      e, find_docs, load_doc, out_dir, shown, subst_vars,
                      token_map)
# A table of contents with a single entry is not a table of contents: it is
# only laid down from two entries on, and never when empty.
MIN_TOC_ENTRIES = 2


# --------------------------------------------------------------------------
# HTML assembly
# --------------------------------------------------------------------------
def build_cover(fm: dict) -> str:
    logo = ROOT / str(fm.get("logo") or "brand/logo.svg")
    bits = ['<section class="cover">', '<div class="cover-head">']
    if logo.exists():
        bits.append(f'<img class="logo" src="{logo.as_uri()}" alt="">')
    bits.append("</div>")

    bits.append('<div class="cover-body">')
    if fm.get("eyebrow"):
        bits.append(f'<p class="eyebrow">{e(fm["eyebrow"])}</p>')
    bits.append(f'<h1>{e(fm["title"])}</h1>')
    if fm.get("subtitle"):
        bits.append(f'<p class="subtitle">{e(fm["subtitle"])}</p>')
    bits.append("</div>")

    fields: list[tuple[str, str]] = []
    if fm.get("author"):
        fields.append(("Auteur", str(fm["author"])))
    if fm.get("date"):
        fields.append(("Date", str(fm["date"])))
    for k, v in (fm.get("meta") or {}).items():
        fields.append((str(k), str(v)))

    bits.append('<div class="cover-extra">{COVER_EXTRA}</div>')

    bits.append('<div class="cover-foot">')
    if fields:
        bits.append("<dl>")
        for k, v in fields:
            bits.append(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>")
        bits.append("</dl>")
    bits.append("</div></section>")
    return "\n".join(bits)


def build_head(fm: dict) -> str:
    """A document header, for the presets that have no cover."""
    bits = ['<header class="doc-head">']
    if fm.get("eyebrow"):
        bits.append(f'<p class="eyebrow">{e(fm["eyebrow"])}</p>')
    bits.append(f'<h1 class="no-break">{e(fm["title"])}</h1>')
    if fm.get("subtitle"):
        bits.append(f'<p class="subtitle">{e(fm["subtitle"])}</p>')
    bits.append("</header>")
    return "\n".join(bits)


# --------------------------------------------------------------------------
# Inserting the SVG into the flow
# --------------------------------------------------------------------------
IMG_RE = re.compile(r"<img\b[^>]*?src=\"([^\"]+\.svg)\"[^>]*?/?>")
CLASS_RE = re.compile(r'class="([^"]*)"')
SVG_MAX = 512 * 1024


def inline_svgs(doc_html: str, d: Path, tokens: dict[str, str]) -> str:
    """Replace <img src="*.svg"> with the SVG itself.

    An SVG referenced through <img> is an isolated document: it does not see the
    page's CSS variables. It is inlined instead, and its `var(--role)` are
    resolved against the document's cascade — so a diagram follows the art
    direction, local override included, without being regenerated.

    An SVG left un-inlined is rendered as a picture: its `var(--role)` stay
    unresolved *and* its text never reaches the PDF's text layer, so every check
    that reads that layer — `tiny-text`, `font`, `overlapping-text` — goes blind
    on it. That is worth saying out loud, which is what `declined` collects.
    """
    seq = 0
    declined: list[tuple[str, str]] = []

    def sub(m: re.Match) -> str:
        nonlocal seq
        src = m.group(1)
        if "://" in src:
            return m.group(0)
        inside = doc_dir(d).resolve()
        f = (inside / src).resolve()
        if not f.is_file():
            declined.append((src, "not found"))
            return m.group(0)
        if inside not in f.parents:
            declined.append((src, f"outside {DOCUMENT}/"))
            return m.group(0)
        if f.stat().st_size > SVG_MAX:
            declined.append((src, f"over {SVG_MAX // 1024} kB"))
            return m.group(0)

        svg = XML_HEAD_RE.sub("", f.read_text(encoding="utf-8")).strip()
        if not svg.startswith("<svg"):
            return m.group(0)

        # The internal identifiers (markers, gradients) are prefixed: two SVG
        # in the same document would otherwise define the same id.
        seq += 1
        prefix = f"s{seq}-"
        svg = re.sub(r'\bid="([^"]+)"', lambda i: f'id="{prefix}{i.group(1)}"', svg)
        svg = re.sub(r"url\(#([^)]+)\)", lambda i: f"url(#{prefix}{i.group(1)})", svg)
        svg = re.sub(r'href="#([^"]+)"', lambda i: f'href="#{prefix}{i.group(1)}"', svg)

        svg = subst_vars(svg, tokens)

        cls = CLASS_RE.search(m.group(0))
        if cls:
            svg = svg.replace("<svg", f'<svg class="{cls.group(1)}"', 1)
        return svg

    html = IMG_RE.sub(sub, doc_html)
    for src, why in declined:
        print(f"  ! {src} not inlined ({why}): its roles stay unresolved and "
              f"its text escapes every check that reads the text layer",
              file=sys.stderr)
    return html


def render_html(d: Path, fm: dict, body_md: str) -> str:
    tokens = token_map(d, fm)
    body, toc = convert(body_md, tokens, d.name)
    body = inline_svgs(body, d, tokens)

    parts = []
    if fm["cover"]:
        cover_md = doc_dir(d) / "cover.md"
        if cover_md.exists():
            extra, _ = convert(cover_md.read_text(encoding="utf-8"), tokens, d.name)
            extra = inline_svgs(extra, d, tokens)
        else:
            extra = ""
        parts.append(build_cover(fm).replace("{COVER_EXTRA}", extra))
    elif fm["head"]:
        parts.append(build_head(fm))

    if fm["toc"] and toc.count("<li") >= MIN_TOC_ENTRIES:
        parts.append(f'<nav class="toc"><h2>Sommaire</h2>{toc}</nav>')
    parts.append(f"<main>{body}</main>")

    footer = fm.get("footer") or ""
    return (
        f'<!DOCTYPE html>\n<html lang="{e(fm["lang"])}" data-theme="{e(fm["theme"])}">\n'
        f"<head><meta charset=\"utf-8\"><title>{e(fm['title'])}</title></head>\n"
        f'<body data-title="{e(fm["title"])}" data-footer="{e(footer)}">\n'
        + "\n".join(parts) + "\n</body>\n</html>\n"
    )


# --------------------------------------------------------------------------
# Stylesheets
# --------------------------------------------------------------------------
def stylesheets(d: Path, fm: dict) -> list[CSS]:
    sheets = [CSS(filename=str(ROOT / "brand" / "tokens.css")),
              CSS(filename=str(THEME / "base.css")),
              CSS(filename=str(THEME / "code.css")),
              CSS(filename=str(THEME / "page.css"))]

    preset = THEME / f"{fm['preset']}.css"
    if preset.exists() and preset.stat().st_size:
        sheets.append(CSS(filename=str(preset)))

    page = fm.get("page") or {}
    overrides = {"--page-size": page.get("size"), "--page-margin": page.get("margin"),
                 "--measure": page.get("measure"), "--size": (fm.get("type") or {}).get("size")}
    decls = "".join(f"{k}:{v};" for k, v in overrides.items() if v)
    if decls:
        sheets.append(CSS(string=f":root{{{decls}}}"))

    local = doc_dir(d) / "theme.css"
    if local.exists():
        sheets.append(CSS(filename=str(local)))
    for extra in fm.get("css") or []:
        p = doc_dir(d) / extra
        if not p.exists():
            raise DocError(f"stylesheet not found: {extra}")
        sheets.append(CSS(filename=str(p)))
    return sheets


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def build(d: Path, keep_html: bool = False) -> list[Path]:
    fm, body_md = load_doc(d)
    themes = ["light", "dark"] if fm["theme"] == "both" else [fm["theme"]]

    out = out_dir(d)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for theme in themes:
        variant = {**fm, "theme": theme}
        doc_html = render_html(d, variant, body_md)
        # A single output keeps the document's name; producing two suffixes the
        # dark variant, the light one staying the reference output.
        name = fm["slug"] + ("-dark" if theme == "dark" and len(themes) > 1 else "")
        if keep_html:
            (out / f"{name}.html").write_text(doc_html, encoding="utf-8")
        pdf = out / f"{name}.pdf"
        HTML(string=doc_html, base_url=str(doc_dir(d)) + "/").write_pdf(
            pdf, stylesheets=stylesheets(d, variant))
        written.append(pdf)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build the PDFs from the Markdown sources.")
    ap.add_argument("targets", nargs="*",
                    help="directories or topics to build (default: the whole library)")
    ap.add_argument("--html", action="store_true",
                    help="also keep the intermediate HTML (art-direction debugging)")
    ap.add_argument("--watch", action="store_true",
                    help="rebuild on every change")
    args = ap.parse_args()

    def run() -> int:
        try:
            docs = find_docs(args.targets)
        except DocError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        failed = 0
        for d in docs:
            rel = shown(d)
            try:
                pdfs = build(d, keep_html=args.html)
            except DocError as exc:
                print(f"  ✗ {rel} — {exc}", file=sys.stderr)
                failed += 1
            except Exception as exc:  # a rendering error: carry on with the others
                print(f"  ✗ {rel} — {type(exc).__name__}: {exc}", file=sys.stderr)
                failed += 1
            else:
                for pdf in pdfs:
                    kb = pdf.stat().st_size / 1024
                    print(f"  ✓ {shown(pdf)} ({kb:.0f} kB)")
        return 1 if failed else 0

    if not args.watch:
        return run()

    print("watching — Ctrl-C to stop")
    seen: dict[Path, float] = {}
    while True:
        watched = list(LIBRARY.rglob("*.md")) + list(LIBRARY.rglob("*.css")) \
            + list(THEME.glob("*.css")) + [ROOT / "brand" / "tokens.css"]
        stamp = {p: p.stat().st_mtime for p in watched if p.exists()}
        if stamp != seen:
            seen = stamp
            run()
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
