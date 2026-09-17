"""Markdown extensions specific to this repository.

`figures`: a paragraph containing nothing but images becomes a <figure>, with
the Markdown title as its caption. It makes this writable in the content:

    ![Processing flow](assets/flow.svg "Figure 1 — Processing flow"){: .diagram }

and yields a figure/figcaption block styled by theme/base.css, with no HTML in
the Markdown.

Several images in the *same* paragraph — so on consecutive lines, with no blank
line between them — form a figure of several panels, laid out in a row under one
shared caption. This is how an import restores the images the source document
placed side by side.

`icons`: `:lucide-name:` inserts an icon, `:lucide-name.accent:` colours it with
an art-direction role (`accent`, `alert`, `danger`, `muted`, `soft`, `ink` —
default `ink`). The extension only leaves a marker; core/doc.py is what
substitutes the SVG and resolves the colour, WeasyPrint being able to resolve
neither `var()` nor `currentColor` inside an SVG. Going through an inline
processor rather than a substitution on the HTML is what guarantees that a
`:word:` inside a code block stays intact.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor

ICON_RE = r":([a-z][a-z0-9-]*)(?:\.(accent|alert|danger|muted|soft|ink))?:"


class _Figures(Treeprocessor):
    def run(self, root: ET.Element) -> None:
        for parent in root.iter():
            for i, child in enumerate(list(parent)):
                if child.tag != "p" or not len(child):
                    continue
                imgs = list(child)
                # a paragraph holding only images, with no text around them
                if any(c.tag != "img" for c in imgs):
                    continue
                if (child.text or "").strip() or any((c.tail or "").strip() for c in imgs):
                    continue

                classes = " ".join(filter(None, (c.attrib.pop("class", "") for c in imgs)))
                # one caption per figure, whatever the number of panels
                caption = next((c.attrib.pop("title", "") for c in imgs
                                if c.attrib.get("title")), "")
                for c in imgs:
                    c.attrib.pop("title", None)
                    c.tail = None

                fig = ET.Element("figure")
                fig.set("class", " ".join(filter(None,
                        ["figure", "row" if len(imgs) > 1 else "", classes])))
                for c in imgs:
                    fig.append(c)
                if caption:
                    ET.SubElement(fig, "figcaption").text = caption
                fig.tail = child.tail
                parent[i] = fig


class FiguresExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_Figures(md), "figures", 4)


def makeExtension(**kwargs):
    return FiguresExtension(**kwargs)


class _Icon(InlineProcessor):
    def handleMatch(self, m, data):
        el = ET.Element("span")
        role = m.group(2)
        el.set("class", f"icon icon-{role}" if role else "icon")
        el.set("data-icon", m.group(1))
        el.text = ""
        return el, m.start(0), m.end(0)


class IconsExtension(Extension):
    def extendMarkdown(self, md):
        # after `escape` and the links, before `emphasis`: an icon name holds
        # neither `_` nor `*`, so the relative order is of no consequence.
        md.inlinePatterns.register(_Icon(ICON_RE, md), "lucide", 175)
