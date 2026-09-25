"""`make check-library`: the user's library, checked without writing a byte.

The suite never reads the user's library — a rename there is not a defect in
the code. This command does, on request. Its checks are tested on libraries
built for the purpose, each carrying the one defect a check must catch, and on
the fixture library, which must come out clean.
"""
import pytest

from core import doc, library


def make_doc(lib, rel, body="---\ntitle: T\n---\n\nBody.\n"):
    inside = lib / rel / doc.DOCUMENT
    inside.mkdir(parents=True)
    (inside / doc.ENTRY).write_text(body, encoding="utf-8")
    return lib / rel


@pytest.fixture
def lib(tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(doc, "LIBRARY", lib)
    monkeypatch.setattr(doc, "OUT", tmp_path / "out")
    return lib


def only(defects):
    assert len(defects) == 1, [str(d) for d in defects]
    return defects[0]


def snapshot(root):
    return {p.relative_to(root): p.stat().st_mtime_ns for p in root.rglob("*")}


# --- a clean library, and a library that is not there ----------------------

def test_the_fixture_library_is_clean(fixture_library):
    assert library.check() == []


def test_the_check_writes_nothing(fixture_library):
    tree = fixture_library.parent                 # the library and its out/
    before = snapshot(tree)
    library.check()
    assert snapshot(tree) == before


def test_an_absent_library_is_nothing_to_check(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(doc, "LIBRARY", tmp_path / "nowhere")
    assert library.check() == []
    assert library.main() == 0
    assert "nothing to check" in capsys.readouterr().out


# --- the anatomy, docs/architecture.md §11 -----------------------------------

def test_a_directory_outside_the_five_roles_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / "scans").mkdir()
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "anatomy")
    assert "scans" in d.what


def test_a_loose_file_at_a_document_root_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / "notes.md").write_text("mes notes", encoding="utf-8")
    d = only(library.check())
    assert (d.kind, "notes.md" in d.what) == ("anatomy", True)


def test_a_derived_file_in_the_users_sources_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / doc.SOURCES).mkdir()
    (root / doc.SOURCES / "extracted.md").write_text("x", encoding="utf-8")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "derived")
    assert "extracted.md" in d.what


def test_code_outside_generators_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / doc.STUDY).mkdir()
    (root / doc.STUDY / "draw.py").write_text("", encoding="utf-8")
    d = only(library.check())
    assert (d.kind, "study/draw.py" in d.what) == ("generator", True)


def test_code_inside_generators_is_not_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / doc.GENERATORS).mkdir()
    (root / doc.GENERATORS / "figures.py").write_text("", encoding="utf-8")
    assert library.check() == []


# --- the layout above the documents ------------------------------------------

def test_an_out_directory_inside_the_library_is_reported(lib):
    make_doc(lib, "topic/slug")
    (lib / "topic" / "out").mkdir()
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/out", "layout")


def test_a_singular_source_directory_is_reported(lib):
    make_doc(lib, "topic/slug")
    (lib / "topic" / "source").mkdir()
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/source", "layout")


# --- what the build would refuse ---------------------------------------------

def test_a_document_that_does_not_load_is_reported(lib):
    make_doc(lib, "topic/slug", body="---\npreset: nope\n---\n\nX\n")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "load")
    assert "nope" in d.what


def test_malformed_xhtml_is_reported(lib):
    make_doc(lib, "topic/slug", body="---\ntitle: T\n---\n\n<div>\n\nOpened.\n")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "xhtml")
    assert d.what.startswith("malformed XHTML")


# --- the report ---------------------------------------------------------------

def test_a_defect_prints_as_one_line_naming_its_document(lib):
    root = make_doc(lib, "topic/slug")
    (root / "scans").mkdir()
    line = str(only(library.check()))
    assert line.startswith("topic/slug — anatomy: ")
    assert "\n" not in line


def test_main_fails_on_a_defect_and_counts_what_it_checked(lib, capsys):
    root = make_doc(lib, "topic/slug")
    make_doc(lib, "topic/other")
    (root / "scans").mkdir()
    assert library.main() == 1
    out = capsys.readouterr().out
    assert "topic/slug — anatomy" in out
    assert "2 documents checked — 1 defect" in out


def test_main_passes_on_a_clean_library(fixture_library, capsys):
    assert library.main() == 0
    assert "2 documents checked — no defect" in capsys.readouterr().out
