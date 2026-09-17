"""The EPUB 3 archive: structure, native table of contents, stable identifier."""
import zipfile
import xml.etree.ElementTree as ET

import epub

FM = {"title": "Les LED", "lang": "fr", "date": "2026-09-10", "slug": "led"}
CHAPS = [("Principle", '<h1 id="a">Principle</h1><h2 id="a1">Junction</h2><p>x</p>'),
         ("Wiring", '<h1 id="b">Wiring</h1><p>y</p>')]


def test_the_uid_is_deterministic():
    assert epub.doc_uid("electronique/components/led") \
        == epub.doc_uid("electronique/components/led")


def test_two_documents_have_distinct_uids():
    assert epub.doc_uid("a/b") != epub.doc_uid("a/c")


def test_the_uid_has_the_shape_of_a_urn():
    assert epub.doc_uid("a/b").startswith("urn:uuid:")


def test_the_chapter_is_complete_xhtml():
    x = epub.chapter_xhtml("T", "<p>x</p>", "fr")
    ET.fromstring(x)
    assert 'xmlns="http://www.w3.org/1999/xhtml"' in x
    assert '../styles/epub.css' in x


def test_the_table_of_contents_carries_both_levels():
    # The sub-entry level follows the split level: a document opening on h1
    # (level=1, the default) has its subheadings at h2 — the CHAPS fixture
    # above.
    nav = epub.nav_xhtml(FM, CHAPS, level=1)
    ET.fromstring(nav)
    assert 'epub:type="toc"' in nav
    assert "Principle" in nav and "Wiring" in nav
    assert "Junction" in nav                    # level 2
    assert "text/ch01.xhtml#a1" in nav

    # A document opening on ## (four in the library, title in the front
    # matter) has its chapters at h2: the sub-entries must then come from the
    # level immediately below, h3 — never from a fixed <h2>, which would list
    # every chapter as its own sub-entry.
    chaps_h2 = [("One", '<h2 id="a">One</h2><h3 id="a1">Detail</h3><p>x</p>')]
    nav2 = epub.nav_xhtml(FM, chaps_h2, level=2)
    ET.fromstring(nav2)
    assert "Detail" in nav2
    assert "text/ch01.xhtml#a1" in nav2


def test_the_opf_declares_all_the_content():
    opf = epub.content_opf(FM, CHAPS, ["cover.png", "assets-x.png"],
                           epub.doc_uid("a/b"))
    ET.fromstring(opf)
    assert 'properties="nav"' in opf
    assert 'properties="cover-image"' in opf
    assert "text/ch01.xhtml" in opf and "text/ch02.xhtml" in opf
    assert "images/assets-x.png" in opf
    assert "dcterms:modified" in opf


def test_image_ids_are_sequential_and_not_derived_from_the_name():
    # Ruling 15(b): a filename may hold a space or an exotic character, which
    # would make it an illegal XML NCName if it served as an id. The ids are
    # therefore positional — unique and legal whatever the name — while the
    # href keeps the real filename.
    opf = epub.content_opf(FM, CHAPS, ["cover.png", "photo one.png", "b.png"],
                           epub.doc_uid("a/b"))
    ET.fromstring(opf)
    assert 'id="cover-image"' in opf
    assert 'id="img-01"' in opf and 'id="img-02"' in opf
    assert 'id="img-photo one.png"' not in opf
    assert 'href="images/photo one.png"' in opf


def test_the_modification_date_is_deterministic():
    a = epub.content_opf(FM, CHAPS, ["cover.png"], "urn:uuid:x")
    b = epub.content_opf(FM, CHAPS, ["cover.png"], "urn:uuid:x")
    assert a == b
    assert "2026-09-10T00:00:00Z" in a


def test_the_mimetype_is_the_first_uncompressed_entry(tmp_path):
    p = tmp_path / "x.epub"
    epub.write_epub(p, {"OEBPS/a.xhtml": "<p/>"})
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        assert names[0] == "mimetype"
        info = z.getinfo("mimetype")
        assert info.compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/epub+zip"


def test_the_archive_is_reproducible(tmp_path):
    a, b = tmp_path / "a.epub", tmp_path / "b.epub"
    epub.write_epub(a, {"OEBPS/a.xhtml": "<p/>"})
    epub.write_epub(b, {"OEBPS/a.xhtml": "<p/>"})
    assert a.read_bytes() == b.read_bytes()


def test_the_container_points_at_the_opf():
    ET.fromstring(epub.CONTAINER_XML)
    assert "OEBPS/content.opf" in epub.CONTAINER_XML
