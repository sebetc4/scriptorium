"""The full assembly, on the fixture documents."""
import datetime
import zipfile

import pytest

from core import doc

import epub


@pytest.fixture(scope="module")
def component(on_fixtures):
    # Module-scoped: rasterising four diagrams is expensive.
    with on_fixtures() as library:
        return epub.build_epub(library / "sample" / "component")


def test_the_epub_is_written_in_the_right_place(fixture_tree, component):
    assert component == (fixture_tree / "out" / "epub" / "sample" / "component"
                         / "component.epub")
    assert component.is_file()


def test_the_archive_holds_the_expected_structure(component):
    with zipfile.ZipFile(component) as z:
        names = set(z.namelist())
    assert "mimetype" in names
    assert "META-INF/container.xml" in names
    assert "OEBPS/content.opf" in names
    assert "OEBPS/nav.xhtml" in names
    assert "OEBPS/cover.xhtml" in names
    assert "OEBPS/styles/epub.css" in names
    assert "OEBPS/images/cover.png" in names
    assert any(n.startswith("OEBPS/text/ch") for n in names)


def test_no_var_survives_in_the_stylesheet(component):
    with zipfile.ZipFile(component) as z:
        css = z.read("OEBPS/styles/epub.css").decode("utf-8")
    assert "var(" not in css


def test_the_diagrams_are_pngs(component):
    with zipfile.ZipFile(component) as z:
        images = [n for n in z.namelist() if n.startswith("OEBPS/images/")]
    assert len(images) >= 5                       # 4 diagrams + the cover
    assert all(n.endswith(".png") for n in images)


def test_the_transposition_threshold_is_overridable():
    """Spec §6.2: a wide table that takes transposition badly."""
    assert epub.table_threshold({}) == epub.TABLE_THRESHOLD
    assert epub.table_threshold({"epub": {"table-threshold": 12}}) == 12
    assert epub.table_threshold({"epub": None}) == epub.TABLE_THRESHOLD


def test_a_raised_threshold_leaves_a_seven_column_table_intact(fixture_library):
    d = fixture_library / "sample" / "component"
    fm, body = doc.load_doc(d)
    tokens = doc.token_map(d, {**fm, "theme": "epub"})
    html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
    assert epub.transpose_wide_tables(html) != html    # past the default: folded
    assert epub.transpose_wide_tables(html, 12) == html


def test_the_page_layout_presets_are_skipped(repo):
    """A reflowed letter is no longer a letter (spec §7.3)."""
    assert epub.EPUB_PRESETS == {"report"}


def test_rebuilding_gives_the_same_file(on_fixtures, component):
    before = component.read_bytes()
    with on_fixtures() as library:
        epub.build_epub(library / "sample" / "component")
    assert component.read_bytes() == before


def test_every_report_of_a_library_builds(fixture_library):
    built = [epub.build_epub(d) for d in doc.find_docs([])
             if doc.load_doc(d)[0]["preset"] in epub.EPUB_PRESETS]
    assert [p.name for p in built] == ["guide-de-style.epub", "component.epub"]
    assert all(p.is_file() and p.stat().st_size > 1024 for p in built)


def test_a_date_with_a_time_does_not_malform_the_timestamp():
    """Fix (b): an unquoted `date:` carrying a time gives a datetime, whose
    str() holds a space. content_opf must keep the date part only, never
    “2026-09-10 10:00:00T00:00:00Z”."""
    fm = {**{"title": "T", "lang": "fr"},
          "date": datetime.datetime(2026, 9, 10, 10, 0, 0)}
    opf = epub.content_opf(fm, [("T", "<p>x</p>")], ["cover.png"],
                           epub.doc_uid("a/b"))
    assert "2026-09-10T00:00:00Z" in opf
    assert " " not in opf.split("dcterms:modified")[1].split("</meta>")[0]
