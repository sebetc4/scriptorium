"""The embedded XHTML must be well-formed XML."""
import pytest

from core import doc

import epub


def test_a_valid_fragment_passes():
    epub.check_xhtml("<p>hello</p><br />", "test")


def test_an_unclosed_tag_raises():
    with pytest.raises(doc.DocError):
        epub.check_xhtml("<p>hello", "test")


def test_named_entities_outside_xml_are_resolved():
    """&nbsp; does not exist in XML: it must be resolved, not rejected."""
    epub.check_xhtml("<p>a&nbsp;b &mdash; c</p>", "test")


def test_the_five_xml_entities_stay_valid():
    epub.check_xhtml("<p>a &amp; b &lt; c &gt; d &quot;e&quot;</p>", "test")


def test_an_inline_svg_passes():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
           '<circle cx="12" cy="12" r="10" /></svg>')
    epub.check_xhtml(f"<p>{svg}</p>", "test")


def test_the_whole_library_produces_well_formed_xhtml(repo):
    """The test that counts: the seven real documents, converted then parsed."""
    for d in doc.find_docs([]):
        fm, body = doc.load_doc(d)
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
        epub.check_xhtml(html, str(d.relative_to(repo)))
