"""The cover: an image that still holds up as a 300px thumbnail."""
import io

from PIL import Image

from core import doc

import epub

FM = {"title": "Le pain", "subtitle": "Doser et ne pas le brûler",
      "eyebrow": "Fiche technique", "date": "2026-09-10", "lang": "fr"}


def tokens(fixture_tree):
    d = fixture_tree / "library" / "exemples" / "guide-de-style"
    fm, _ = doc.load_doc(d)
    return doc.token_map(d, {**fm, "theme": "epub"})


def test_the_html_carries_the_title_and_the_eyebrow(fixture_tree):
    h = epub.cover_html(FM, tokens(fixture_tree))
    assert "Le pain" in h
    assert "Fiche technique" in h


def test_the_html_escapes_the_dangerous_characters(fixture_tree):
    h = epub.cover_html({**FM, "title": "A & B <x>"}, tokens(fixture_tree))
    assert "A &amp; B" in h
    assert "<x>" not in h


def test_the_title_dominates_the_composition(fixture_tree):
    """At a 300px thumbnail, only the title stays readable: it must dominate."""
    h = epub.cover_html(FM, tokens(fixture_tree))
    assert "--title-size: 132px" in h


def test_render_yields_a_png_at_the_right_dimensions(fixture_tree):
    png = epub.render_cover(FM, tokens(fixture_tree))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    im = Image.open(io.BytesIO(png))
    assert abs(im.width - epub.COVER_WIDTH) <= 2
    assert abs(im.height - epub.COVER_HEIGHT) <= 2


def test_the_cover_is_not_blank(fixture_tree):
    """A blank cover would pass every preceding test."""
    png = epub.render_cover(FM, tokens(fixture_tree))
    im = Image.open(io.BytesIO(png)).convert("L")
    assert len(im.getcolors(maxcolors=100000) or []) > 3


def test_a_document_without_a_subtitle_passes(fixture_tree):
    png = epub.render_cover({"title": "T", "lang": "fr"}, tokens(fixture_tree))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
