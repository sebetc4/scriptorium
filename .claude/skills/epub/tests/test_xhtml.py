"""The embedded XHTML must be well-formed XML."""
import pytest

from core import doc

import epub


def test_a_valid_fragment_passes():
    doc.check_xhtml("<p>hello</p><br />", "test")


def test_an_unclosed_tag_raises():
    with pytest.raises(doc.DocError):
        doc.check_xhtml("<p>hello", "test")


def test_named_entities_outside_xml_are_resolved():
    """&nbsp; does not exist in XML: it must be resolved, not rejected."""
    doc.check_xhtml("<p>a&nbsp;b &mdash; c</p>", "test")


def test_the_five_xml_entities_stay_valid():
    doc.check_xhtml("<p>a &amp; b &lt; c &gt; d &quot;e&quot;</p>", "test")


def test_an_inline_svg_passes():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
           '<circle cx="12" cy="12" r="10" /></svg>')
    doc.check_xhtml(f"<p>{svg}</p>", "test")


def test_every_document_of_a_library_converts_to_well_formed_xhtml(fixture_library):
    """The conversion itself, on documents that carry icons, admonitions,
    footnotes, a code block, a wide table and inlined figures."""
    for d in doc.find_docs([]):
        fm, body = doc.load_doc(d)
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
        doc.check_xhtml(html, str(doc.relative(d)))


def test_raw_html_left_unbalanced_in_the_markdown_is_refused():
    """Markdown passes raw HTML through untouched: an unclosed tag written by
    hand reaches the XHTML, and only the check stands between it and the EPUB."""
    html, _ = doc.convert("<div>\n\nOpened, never closed.\n", {}, "test",
                          icon_color="currentColor")
    with pytest.raises(doc.DocError, match="malformed XHTML"):
        doc.check_xhtml(html, "test")
