#!/usr/bin/env python3
"""Capture a web page as a document of the library.

    python .claude/skills/fetch/scripts/fetch.py https://example.org/article watch/article --lang fr

Like the PDF import, this tool produces an ordinary document — `index.md` +
`assets/` — rather than any particular format: `make build` is what then applies
the art direction. It does not translate; it retrieves, cleans and structures.

    library/<topic>/<slug>/
      index.md              front matter + extracted content, to review
      sources/page.html.gz  the page exactly as it was received
      study/extracted.md    the raw extraction, an immutable reference
      study/meta.json       provenance: URL, date, digest, metadata
      assets/               the downloaded and recompressed images
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import gzip
import hashlib
import io
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import trafilatura
import trafilatura.utils
from PIL import Image

# ROOT from the core, not from this file's parents: it lives inside a skill.
from core.doc import (ENTRY, LIBRARY, ROOT, SOURCES, STUDY, doc_dir,
                      find_docs)
from core import net
from core.imaging import store

IMG_RE = re.compile(r'!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+"([^"]*)")?\s*\)')
LANG_RE = re.compile(r'<html[^>]*\blang=["\']([a-zA-Z-]{2,8})["\']')
DATA_URI_RE = re.compile(r"^data:image/([\w+.-]+);base64,(.*)$", re.S)
MAX_IMAGES = 80
IMAGE_TIMEOUT = 20
IMAGE_MAX_BYTES = 12 * 1024 * 1024
MIN_IMAGE_PX = 64       # below this: an icon, a bullet or a tracking pixel
IMAGE_PAUSE = 0.25      # s between two requests: a burst gets rate-limited
RETRY_CODES = {408, 425, 429, 500, 502, 503, 504}
RETRY_WAITS = (1.0, 3.0, 7.0)


class FetchError(Exception):
    pass


# --------------------------------------------------------------------------
# Retrieval
# --------------------------------------------------------------------------
def retrieve(url: str) -> net.Response:
    """The page, refused out loud unless it really is a page.

    The status and the extension prove nothing: a `.pdf` link answering 200 can
    be a signup wall, and a dead forum still serves an HTML error page. What
    came back is read from the bytes (core/net.py), and anything that is not an
    HTML page stops here, before a single file is written.
    """
    try:
        response = net.get(url)
    except net.NetError as exc:
        raise FetchError(f"page unreachable — {exc}")
    probe = f"\n    {response.line()}"

    if not 200 <= response.status < 300:
        raise FetchError(f"the page answered HTTP {response.status}{probe}")
    mime = response.mime
    if mime == "application/pdf":
        raise FetchError("this URL serves a PDF, not a web page — rebuild it as a "
                         "document with `make import SRC=<file.pdf> DOC=… TO=…`"
                         + probe)
    claimed_pdf = (urllib.parse.urlparse(response.effective_url).path.lower().endswith(".pdf")
                   or urllib.parse.urlparse(url).path.lower().endswith(".pdf")
                   or "pdf" in response.content_type.lower())
    if claimed_pdf and mime == "text/html":
        raise FetchError("a .pdf URL answered text/html — a signup wall, an error "
                         "page or a redirect, not the document" + probe)
    if mime != "text/html" and not (mime == "application/octet-stream"
                                    and "html" in response.content_type.lower()):
        raise FetchError(f"this URL serves {mime}, not a web page{probe}")
    return response


def fetch_rendered(url: str) -> str:
    """Headless-browser rendering, for the client-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise FetchError(
            "--render needs Playwright, which is absent from the environment:\n"
            "    .venv/bin/pip install playwright\n"
            "    .venv/bin/playwright install chromium")

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            raise FetchError(f"browser unavailable ({exc}).\n"
                             "    .venv/bin/playwright install chromium")
        try:
            page = browser.new_page(user_agent=net.UA)
            page.goto(url, wait_until="networkidle", timeout=45000)
            return page.content()
        finally:
            browser.close()


def detect_language(html: str, markdown: str) -> str:
    """The page's language: what it declares, failing that what its text says.

    No hard-coded fallback: a language wrongly assumed throws the hyphenation
    off silently, and ends up displayed nowhere it would be checked.
    """
    if m := LANG_RE.search(html):
        return m.group(1).split("-")[0].lower()
    try:
        import py3langid
        code, _ = py3langid.classify(markdown[:5000])
        return code
    except Exception:
        return ""


def looks_client_rendered(html: str, markdown: str) -> bool:
    """A lot of markup for very little text: the page assembles itself in JS.

    The threshold is relative: a documentation page commonly yields 1 to 2 kB of
    useful text, which is normal for 20 kB of HTML and suspect for 300.
    """
    return len(html) > 50_000 and (len(markdown) < 2000
                                   or len(markdown) < len(html) * 0.01)


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------
def has_text(md: str) -> bool:
    """Whether a Markdown extraction holds anything to read.

    Not the same as being non-empty: an extraction made only of image
    references, or of Markdown markers, would pass `md.strip()` and produce a
    document with nothing in it.
    """
    return bool(re.search(r"\w", IMG_RE.sub("", md)))


def extract(html: str, url: str) -> tuple[str, dict, str]:
    """Markdown, metadata, and the extraction mode that was kept.

    Precise extraction discards what is off-topic but sometimes loses every
    image. When that happens and the page manifestly holds some, the extraction
    is redone in wide mode: text to prune beats missing illustrations.
    """
    common = dict(url=url, output_format="markdown",
                  include_images=True, include_tables=True, include_links=False)
    md = trafilatura.extract(html, **common) or ""
    mode = "precise"

    if not IMG_RE.search(md) and html.count("<img") > 3:
        wide = trafilatura.extract(html, favor_recall=True, **common) or ""
        if IMG_RE.search(wide):
            md, mode = wide, "wide (the images were missing in precise mode)"

    if not has_text(md):
        raise FetchError("the extraction has no text — nothing to make a document "
                         "of. If the page assembles itself in JavaScript, run "
                         "again with --render.")

    meta = trafilatura.extract_metadata(html, default_url=url)
    data = meta.as_dict() if meta else {}
    clean = {}
    for k, v in data.items():
        if isinstance(v, (str, int, float)) and str(v).strip():
            clean[k] = v
        elif isinstance(v, (list, tuple)) and v:
            clean[k] = [str(x) for x in v]
    return md, clean, mode


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------
def load_image(src: str, base: str) -> tuple[Image.Image | None, bytes | None]:
    """Yield a PIL image, or raw bytes for an SVG."""
    if m := DATA_URI_RE.match(src):
        raw = base64.b64decode(m.group(2), validate=False)
        if m.group(1) == "svg+xml":
            return None, raw
        return Image.open(io.BytesIO(raw)), None

    full = urllib.parse.urljoin(base, src)
    if urllib.parse.urlparse(full).scheme not in ("http", "https"):
        raise FetchError(f"scheme refused: {full[:60]}")

    # An image server readily rate-limits bursts: retry, giving more and more
    # ground, rather than abandoning the illustration.
    for wait in (*RETRY_WAITS, None):
        try:
            r = net.get(full, max_bytes=IMAGE_MAX_BYTES, timeout=IMAGE_TIMEOUT,
                        headers={"Referer": base})
        except net.NetError as exc:
            if wait is None or "too large" in str(exc):
                raise FetchError("image too heavy" if "too large" in str(exc) else str(exc))
            time.sleep(wait)
            continue
        if r.status in RETRY_CODES and wait is not None:
            time.sleep(wait)
            continue
        break
    if not 200 <= r.status < 300:
        raise FetchError(f"HTTP {r.status}")

    # Read from the bytes: an image link answering an HTML error page would
    # otherwise surface as an obscure “cannot identify image file”.
    mime = r.mime
    named_svg = "svg" in r.content_type or full.lower().split("?")[0].endswith(".svg")
    if mime == "image/svg+xml" or (named_svg and mime == "application/octet-stream"):
        return None, r.body
    if not mime.startswith("image/"):
        raise FetchError(f"answered {mime}, not an image")
    return Image.open(io.BytesIO(r.body)), None


def localize_images(md: str, base: str, assets: Path) -> tuple[str, int, list[str]]:
    """Download the images, recompress them, and rewrite the references."""
    seen: dict[str, str] = {}
    by_src: dict[str, str | None] = {}
    failures: list[str] = []
    count = 0

    def replace(m: re.Match) -> str:
        nonlocal count
        alt, src, title = m.group(1), m.group(2), m.group(3)
        if src not in by_src:
            if count >= MAX_IMAGES:
                by_src[src] = None
            else:
                try:
                    time.sleep(IMAGE_PAUSE)
                    img, svg = load_image(src, base)
                    if svg is not None:
                        count += 1
                        name = f"img-{count:03d}.svg"
                        (assets / name).write_bytes(svg)
                        by_src[src] = name
                    elif min(img.size) < MIN_IMAGE_PX:
                        by_src[src] = None          # icon, bullet, tracking pixel
                    else:
                        count += 1
                        by_src[src] = store(img, assets, count, seen)
                except Exception as exc:
                    by_src[src] = None
                    reason = str(exc) or type(exc).__name__
                    failures.append(f"{src[:90]} — {reason}")

        name = by_src[src]
        if name is None:
            return ""
        return f'![{alt or "Image"}](assets/{name} "{title or "Figure — to be captioned"}")'

    md = IMG_RE.sub(replace, md)
    return re.sub(r"\n{3,}", "\n\n", md), len(set(filter(None, by_src.values()))), failures


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


def yaml_str(v) -> str:
    v = str(v).replace('"', "'").replace("\n", " ").strip()
    return f'"{v}"' if v else '""'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Capture a web page.")
    ap.add_argument("url", nargs="?")
    ap.add_argument("path", nargs="?",
                    help="destination under library/, e.g. watch/article")
    ap.add_argument("--rederive", metavar="DOC",
                    help="re-extract a captured document from its "
                         "sources/page.html.gz, writing only study/extracted.md")
    ap.add_argument("--lang", metavar="CODE",
                    help="target language; by default the page's own")
    ap.add_argument("--render", action="store_true",
                    help="go through a headless browser (JS-assembled pages)")
    ap.add_argument("--preset", default="report")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    # Re-derivation: the page as received is in `sources/`, and only the
    # extraction is rewritten. `study/meta.json` is not — it carries the date
    # of the capture, the HTTP status and the certificate's verification, and
    # nothing recomputes those — and neither is `index.md`.
    if args.rederive:
        try:
            dest, = find_docs([args.rederive])
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        received = dest / SOURCES / "page.html.gz"
        if not received.is_file():
            return 0            # not a capture: nothing here to re-derive
        meta_path = dest / STUDY / "meta.json"
        url = ""
        if meta_path.is_file():
            stored = json.loads(meta_path.read_text(encoding="utf-8"))
            url = stored.get("url") or stored.get("effective_url") or ""
        html = gzip.decompress(received.read_bytes()).decode("utf-8", "replace")
        md, _, _ = extract(html, url)
        out = dest / STUDY / "extracted.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"✓ {out.relative_to(ROOT)}")
        return 0

    if not (args.url and args.path):
        ap.error("url and path are required without --rederive")

    if urllib.parse.urlparse(args.url).scheme not in ("http", "https"):
        print("error: the URL must be http or https", file=sys.stderr)
        return 1
    if args.lang and not re.fullmatch(r"[a-z]{2,3}(-[A-Za-z]{2,4})?", args.lang):
        print(f"error: “{args.lang}” is not a language code", file=sys.stderr)
        return 1

    parts = [slugify(p) for p in Path(args.path).parts if p not in (".", "..")]
    dest = LIBRARY.joinpath(*parts)
    if (doc_dir(dest) / ENTRY).exists() and not args.force:
        print(f"error: the document already exists — {dest.relative_to(ROOT)} "
              f"(--force to overwrite)", file=sys.stderr)
        return 1

    try:
        response = retrieve(args.url)
        print(f"  {response.line()}")
        html = (fetch_rendered(args.url) if args.render
                else trafilatura.utils.decode_file(response.body))
        md, meta, mode = extract(html, args.url)
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if response.effective_url != args.url:
        print(f"  ! redirected: {args.url} → {response.effective_url}")
    if not response.tls_verified:
        print("  ! the host's certificate could not be verified: captured over an "
              "unverified connection, which study/meta.json records")

    hint = ""
    if not args.render and looks_client_rendered(html, md):
        hint = ("the page looks client-rendered: very little text for a lot of "
                "markup. Run again with --render.")

    # `sources/` keeps the page as it was received — a tool acquiring on the
    # user's behalf; what is computed from it goes to `study/`
    # (docs/architecture.md §11).
    assets = doc_dir(dest) / "assets"
    source_dir, study_dir = dest / SOURCES, dest / STUDY
    for p in (assets, source_dir, study_dir):
        p.mkdir(parents=True, exist_ok=True)

    (study_dir / "extracted.md").write_text(md, encoding="utf-8")
    body, n_images, failures = localize_images(md, args.url, assets)

    # The bytes as received, not decoded and re-encoded: they are the proof of
    # what was captured, and a page that changes or disappears cannot be asked
    # again. Through a browser, the proof is the DOM the browser assembled.
    received = html.encode("utf-8") if args.render else response.body
    (source_dir / "page.html.gz").write_bytes(gzip.compress(received))
    # Recorded under the same key as the PDF import: `translate` reads the source
    # language from here, so it is stated once and never asked again.
    page_lang = str(meta.get("language") or "").split("-")[0].lower() \
        or detect_language(html, md)
    (study_dir / "meta.json").write_text(json.dumps({
        "url": args.url,
        "effective_url": response.effective_url,
        "http_status": response.status,
        "content_type": response.content_type,
        "tls_verified": response.tls_verified,
        "fetched": dt.datetime.now().isoformat(timespec="seconds"),
        "mode": "browser" if args.render else "static",
        "extraction": mode,
        "sha256_html": hashlib.sha256(received).hexdigest(),
        "html_bytes": len(received),
        "source_language": page_lang,
        "metadata": meta,
        "images": n_images,
        "image_failures": failures,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    title = meta.get("title") or parts[-1].replace("-", " ").capitalize()

    notes = [f"CAPTURED, NOT REVIEWED — {n_images} image(s), {mode} extraction.",
             f"Source: {args.url}",
             "The extracted content keeps the site's own structure: headings to "
             "move back into the repository's hierarchy, navigation blocks to "
             "delete.",
             "The received page is kept in sources/page.html.gz; "
             "study/extracted.md keeps the extraction intact.",
             "The URL and the capture date are not carried onto the cover: "
             "offer them to the user if the document should display them."]
    if page_lang and args.lang and page_lang != args.lang:
        notes.append(f"Page in “{page_lang}”, document targeted at “{args.lang}”: "
                     "translate the body in place.")
    elif page_lang and not args.lang:
        notes.append(f"Page in “{page_lang}”, taken as it is. Offer the user a "
                     "translation before reviewing.")
    elif not page_lang:
        notes.append("The page's language could not be determined: fill in "
                     "`lang:`, which the hyphenation depends on.")
    if hint:
        notes.append(hint)
    if failures:
        notes.append(f"{len(failures)} image(s) not retrieved — see "
                     "study/meta.json.")

    front = "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        f"date: {dt.date.today().isoformat()}",
        f"preset: {args.preset}",
        f"lang: {args.lang or page_lang}" if (args.lang or page_lang)
        else "lang:                 # LANGUAGE UNDETERMINED — fill this in",
        "theme: light          # light | dark | both — to ask the user",
        f"source: {yaml_str(args.url)}",
        "---",
        "",
        "<!--",
        *(f"  {n}" for n in notes),
        "-->",
        "",
        "",
    ])
    (doc_dir(dest) / ENTRY).write_text(front + body, encoding="utf-8")

    rel = dest.relative_to(ROOT)
    print(f"  ✓ {rel}/index.md")
    print(f"    {len(html) // 1024} kB of HTML → {len(body) // 1024} kB of Markdown, "
          f"{n_images} image(s), {mode} extraction")
    print(f"    page language: {page_lang or 'undetermined'}")
    if failures:
        print(f"    {len(failures)} image(s) not retrieved")
    if hint:
        print(f"    ! {hint}")
    print(f"    review index.md, then: make build DOC={'/'.join(parts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
