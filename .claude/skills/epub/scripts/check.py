#!/usr/bin/env python3
"""Mechanical checks on a built EPUB.

They bear on what actually breaks an e-book: a malformed archive, an incoherent
manifest, an unresolved CSS variable. None of that needs an eye — they are
assertions, and they run on every build, at no cost.

What these checks cannot settle — whether a diagram stays readable at six inches
— is the contact sheet's business (preview.py, beside this file).
"""
from __future__ import annotations

import posixpath
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from core import doc

CONTRAST_FLOOR = 6.5
EPUBCHECK = "epubcheck"

OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}

IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"')

# The roles whose contrast is verified. The rules are excluded: they are
# deliberately discreet, and a text-legibility floor makes no sense for them.
CHECKED_ROLES = ("accent", "alert", "danger", "link", "ink")


def validate(path: Path) -> list[str]:
    """An EPUB's anomalies. An empty list means nothing to report."""
    anomalies: list[str] = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()

        # 1. mimetype: first entry, uncompressed
        if not names or names[0] != "mimetype":
            anomalies.append("mimetype is not the archive's first entry")
        elif z.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            anomalies.append("mimetype is compressed; it must be stored as is")

        if "META-INF/container.xml" not in names:
            anomalies.append("META-INF/container.xml missing")

        # The checks that do not read the OPF run in every case: making them
        # conditional would hide a stylesheet or markup defect behind a missing
        # manifest, which has nothing to do with either.

        # 2. no residual CSS variable: RMSDK does not resolve them, and the
        #    colour would disappear in silence
        for name in names:
            if name.endswith(".css"):
                css = z.read(name).decode("utf-8")
                if "var(" in css:
                    anomalies.append(f"{name}: unresolved var()")

        # 3. well-formed XHTML
        for name in names:
            if name.endswith(".xhtml"):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as exc:
                    anomalies.append(f"{name}: malformed XHTML — {exc}")

        # 4. the manifest, in both directions
        if "OEBPS/content.opf" not in names:
            anomalies.append("OEBPS/content.opf missing")
        else:
            opf = ET.fromstring(z.read("OEBPS/content.opf"))
            manifest = {i.get("id"): i.get("href")
                        for i in opf.iterfind(".//opf:manifest/opf:item", OPF_NS)}
            spine = [r.get("idref")
                     for r in opf.iterfind(".//opf:spine/opf:itemref", OPF_NS)]

            # every manifest entry exists in the archive
            for ident, href in manifest.items():
                if f"OEBPS/{href}" not in names:
                    anomalies.append(f"declared in the manifest but absent: {href}")

            # … and conversely: a file that is present but undeclared makes the
            # archive invalid. Three entries are exempt by the format itself —
            # they are not declared there.
            declared = {f"OEBPS/{h}" for h in manifest.values()}
            outside_manifest = {"mimetype", "META-INF/container.xml",
                                "OEBPS/content.opf"}
            for name in names:
                if (name not in declared and name not in outside_manifest
                        and not name.endswith("/")):
                    anomalies.append(
                        f"present in the archive but not declared: {name}")

            # every chapter is in the spine
            for ident, href in manifest.items():
                if href.startswith("text/") and ident not in spine:
                    anomalies.append(f"chapter outside the spine: {href}")

            # every spine idref exists in the manifest
            for idref in spine:
                if idref not in manifest:
                    anomalies.append(f"spine points at an unknown id: {idref}")

            # every chapter is reachable from the table of contents
            if "OEBPS/nav.xhtml" in names:
                nav = z.read("OEBPS/nav.xhtml").decode("utf-8")
                for ident, href in manifest.items():
                    if href.startswith("text/") and href not in nav:
                        anomalies.append(f"chapter missing from the table of contents: {href}")

            # every <img src> in a chapter points at a manifest entry
            anomalies += image_reference_anomalies(z, names, manifest)

    return anomalies + role_contrast_anomalies()


def image_reference_anomalies(z, names, manifest) -> list[str]:
    """Every <img src> in a chapter must point at a manifest entry.

    The manifest check only confronts the manifest with the archive: a renamed
    or misspelt `src` leaves a dead path in the chapter without either list
    moving. The archive then ships “clean” with a missing image, and nothing
    says so before the e-reader does.
    """
    declared = {f"OEBPS/{h}" for h in manifest.values()}
    anomalies = []
    for name in names:
        if not name.endswith(".xhtml"):
            continue
        content = z.read(name).decode("utf-8", "replace")
        base = posixpath.dirname(name)
        for src in IMG_SRC_RE.findall(content):
            if "://" in src:
                continue
            target = posixpath.normpath(posixpath.join(base, src))
            if target not in declared:
                anomalies.append(
                    f"{name}: image referenced outside the manifest — {src}")
    return anomalies


def role_contrast_anomalies() -> list[str]:
    """The roles that carry meaning must stand out, and at equal strength.

    The check bears on the `colors.epub` mapping, not on the colours found in
    the stylesheet: a table rule is deliberately discreet, and applying a
    text-legibility floor to it would make no sense.
    """
    css = (doc.ROOT / "brand" / "tokens.css").read_text(encoding="utf-8")
    tokens = {k: v.strip() for k, v in
              doc.DECL_RE.findall(doc.block(css, '[data-theme="epub"]'))}
    if not tokens:
        return ['brand/tokens.css: [data-theme="epub"] block missing']

    background = tokens.get("paper", "#FFFFFF")
    anomalies = []
    for role in CHECKED_ROLES:
        v = tokens.get(role, "")
        if not v.startswith("#"):
            continue
        r = doc.contrast(v, background)
        if r < CONTRAST_FLOOR:
            anomalies.append(f"colors.epub.{role}: contrast {r:.2f} "
                             f"< {CONTRAST_FLOOR} on {background}")

    # The three signalling roles must have the same strength in greyscale:
    # otherwise one fades while the other stays firm, with nothing having
    # decided it — the defect §3 of the spec corrects.
    pairs = [(r, doc.grey_level(tokens[r])) for r in ("accent", "alert", "danger")
             if tokens.get(r, "").startswith("#")]
    if len(pairs) == 3:
        values = [v for _, v in pairs]
        if max(values) - min(values) > 8:
            detail = ", ".join(f"{r} {v}" for r, v in pairs)
            anomalies.append(
                f"colors.epub: unequal strengths in monochrome — {detail}")
    return anomalies


def epubcheck(path: Path) -> list[str] | None:
    """EPUB 3 conformance through the reference tool, if it is installed.

    It needs Java, so it stays optional — the checks above depend on nothing.
    Returns None when the tool is missing, the list of its error messages
    otherwise.
    """
    if not shutil.which(EPUBCHECK):
        return None
    r = subprocess.run([EPUBCHECK, "--quiet", str(path)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return []
    messages = [l for l in (r.stderr or r.stdout).splitlines() if l.strip()]
    # A non-zero return code WITHOUT a message must not read as a success: the
    # tool failed, and silence is not a validation.
    return messages or [f"epubcheck failed (code {r.returncode}) with no message"]
