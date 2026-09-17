"""core/doc.py's extraction must be of constant behaviour."""
import pytest

from core import doc


def test_front_matter_separates_meta_from_body():
    meta, body = doc.split_front_matter("---\ntitle: X\n---\n\n# T\n")
    assert meta == {"title": "X"}
    assert body == "# T\n"


def test_absent_front_matter_returns_the_text_intact():
    meta, body = doc.split_front_matter("# T\n")
    assert meta == {}
    assert body == "# T\n"


def test_front_matter_that_is_not_a_mapping_raises():
    with pytest.raises(doc.DocError):
        doc.split_front_matter("---\n- a\n- b\n---\ncorps\n")


def test_load_doc_applies_the_defaults(repo):
    d = repo / "library" / "exemples" / "guide-de-style"
    fm, _ = doc.load_doc(d)
    assert fm["preset"] == "report"
    assert fm["slug"] == "guide-de-style"
    assert fm["lang"]


def test_find_docs_finds_the_whole_library():
    found = doc.find_docs([])
    assert len(found) >= 7
    assert all((p / "index.md").is_file() for p in found)


def test_token_map_resolves_the_roles(repo):
    d = repo / "library" / "exemples" / "guide-de-style"
    fm, _ = doc.load_doc(d)
    tokens = doc.token_map(d, fm)
    assert tokens["accent"].startswith("#")
    assert "ink" in tokens


def test_subst_vars_substitutes_and_falls_back_to_currentcolor():
    assert doc.subst_vars('fill="var(--accent)"', {"accent": "#123456"}) \
        == 'fill="#123456"'
    assert doc.subst_vars('fill="var(--inconnu)"', {}) == 'fill="currentColor"'


def test_convert_does_not_inline_the_svg(repo):
    """convert() leaves the <img src="*.svg"> in place: each backbone decides."""
    html, _ = doc.convert('![x](assets/y.svg)', {}, "test")
    assert ".svg" in html


def test_icon_color_forces_the_glyph_colour(repo):
    tokens = {"accent": "#36654C", "ink": "#1D211C", "icon-stroke": "2.25"}
    svg = doc.render_icon("info", "icon icon-accent", tokens, color="currentColor")
    assert svg is not None
    assert "currentColor" in svg
    assert "#36654C" not in svg
