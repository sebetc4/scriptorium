"""One XHTML file per level-1 heading."""
from core import doc

import epub


def test_one_chapter_per_h1():
    html = '<h1 id="a">One</h1><p>x</p><h1 id="b">Two</h1><p>y</p>'
    ch = epub.split_chapters(html, "Document")
    assert [t for t, _ in ch] == ["One", "Two"]
    assert "<p>x</p>" in ch[0][1]
    assert "<p>y</p>" in ch[1][1]


def test_the_h1_stays_inside_its_chapter():
    ch = epub.split_chapters('<h1 id="a">One</h1><p>x</p>', "Document")
    assert "<h1" in ch[0][1]


def test_content_before_the_first_h1_forms_a_head_chapter():
    html = '<p>before</p><h1 id="a">One</h1><p>x</p>'
    ch = epub.split_chapters(html, "Document")
    assert len(ch) == 2
    assert ch[0][0] == "Document"
    assert "before" in ch[0][1]


def test_a_document_without_an_h1_gives_a_single_chapter():
    ch = epub.split_chapters("<p>x</p>", "Document")
    assert len(ch) == 1
    assert ch[0][0] == "Document"


def test_the_title_is_stripped_of_tags():
    ch = epub.split_chapters('<h1 id="a">One <em>two</em></h1>', "D")
    assert ch[0][0] == "One two"


def test_emptiness_before_the_first_h1_creates_no_chapter():
    ch = epub.split_chapters('\n  \n<h1 id="a">One</h1><p>x</p>', "D")
    assert len(ch) == 1


def test_the_split_level_follows_the_document():
    assert epub.heading_level('<h1 id="a">One</h1><h2 id="b">Two</h2>') == 1
    assert epub.heading_level('<h2 id="b">Two</h2><h3 id="c">Three</h3>') == 2
    assert epub.heading_level("<p>nothing</p>") == 1


def test_a_document_opening_on_h2_still_splits():
    """Four documents in the library open on ##, title in the front matter."""
    html = '<h2 id="a">One</h2><p>x</p><h2 id="b">Two</h2><p>y</p>'
    ch = epub.split_chapters(html, "Document")
    assert [t for t, _ in ch] == ["One", "Two"]
    assert "<p>x</p>" in ch[0][1]


def test_the_level_can_be_forced_explicitly():
    html = '<h1 id="a">One</h1><h2 id="b">Two</h2><h2 id="c">Three</h2>'
    assert len(epub.split_chapters(html, "D", level=2)) == 3


def test_the_sweep_covers_all_six_html_levels():
    """A document opening below h3 must not fall back to a single chapter."""
    assert epub.heading_level('<h4 id="a">Four</h4>') == 4
    assert epub.heading_level('<h6 id="a">Six</h6>') == 6
    ch = epub.split_chapters('<h4 id="a">One</h4><p>x</p><h4 id="b">Two</h4>',
                             "Document")
    assert [t for t, _ in ch] == ["One", "Two"]


def test_no_document_stays_monolithic(fixture_library):
    """None may stay in one block: the guide splits at its `##`, having no `#`,
    and the component at its three `#`."""
    for d in doc.find_docs([]):
        fm, body = doc.load_doc(d)
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
        ch = epub.split_chapters(html, fm["title"])
        assert len(ch) >= 2, f"{d.name}: {len(ch)} chapter"
