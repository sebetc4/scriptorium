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
    assert all((p / doc.DOCUMENT / doc.ENTRY).is_file() for p in found)


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


# --------------------------------------------------------------------------
# The anatomy: a document is a root holding `document/` (architecture §11)
# --------------------------------------------------------------------------
def make_doc(library, rel, body="---\ntitle: T\n---\n\nBody.\n"):
    """A document in the declared shape: the entry inside `document/`."""
    inside = library / rel / doc.DOCUMENT
    inside.mkdir(parents=True)
    (inside / doc.ENTRY).write_text(body, encoding="utf-8")
    return library / rel


@pytest.fixture
def library(tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(doc, "LIBRARY", lib)
    monkeypatch.setattr(doc, "OUT", tmp_path / "out")
    return lib


def test_a_document_is_discovered_at_its_root_not_at_its_entry(library):
    root = make_doc(library, "topic/slug")
    assert doc.find_docs([]) == [root]


def test_the_slug_is_the_root_directory(library):
    root = make_doc(library, "topic/slug")
    fm, _ = doc.load_doc(root)
    assert fm["slug"] == "slug"
    assert fm["title"] == "T"


def test_the_default_title_comes_from_the_root_directory(library):
    root = make_doc(library, "topic/round-led", body="---\npreset: report\n---\n\nX\n")
    fm, _ = doc.load_doc(root)
    assert fm["title"] == "Round led"
    assert fm["slug"] == "round-led"


def test_the_output_path_carries_no_document_segment(library):
    root = make_doc(library, "topic/slug")
    assert doc.out_dir(root).parts[-2:] == ("topic", "slug")


def test_a_path_to_the_entry_resolves_to_the_root(library):
    root = make_doc(library, "topic/slug")
    assert doc.find_docs([str(root / doc.DOCUMENT / doc.ENTRY)]) == [root]


def test_a_path_to_the_document_directory_resolves_to_the_root(library):
    root = make_doc(library, "topic/slug")
    assert doc.find_docs([str(root / doc.DOCUMENT)]) == [root]


def test_an_entry_outside_document_is_not_a_document(library):
    # An index.md a user keeps in their own material is not a document, and
    # `sources/` is theirs to fill: discovery must not reach into it.
    root = make_doc(library, "topic/slug")
    (root / "sources").mkdir()
    (root / "sources" / doc.ENTRY).write_text("---\ntitle: X\n---\n\nX\n",
                                              encoding="utf-8")
    assert doc.find_docs([]) == [root]


def test_a_library_with_no_document_raises(library):
    topic = library / "topic"
    topic.mkdir()
    with pytest.raises(doc.DocError, match=doc.DOCUMENT):
        doc.find_docs([str(topic)])
