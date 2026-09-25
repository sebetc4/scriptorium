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


def test_a_translation_glossary_at_the_root_is_not_reported(lib):
    # `translate` keeps it there: the check must not fail every translated document.
    root = make_doc(lib, "topic/slug")
    (root / "glossary.yaml").write_text("terms: {}\n", encoding="utf-8")
    assert library.check() == []


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


# --- a discussion's journal, the `discussion` skill ---------------------------

def make_journal(root, index="# D\n", topics=None, sessions=None):
    """A journal in three layers under `root/study/discussion/`."""
    journal = root / doc.STUDY / library.JOURNAL
    for sub, pages in (("topics", topics or {}), ("sessions", sessions or {})):
        (journal / sub).mkdir(parents=True)
        for name, text in pages.items():
            (journal / sub / name).write_text(text, encoding="utf-8")
    (journal / "index.md").write_text(index, encoding="utf-8")
    return journal


def test_the_fixture_journal_is_checked_and_clean(fixture_library):
    assert library.journals(fixture_library) == [
        fixture_library / "sample" / "component" / doc.STUDY]
    assert library.check() == []


def test_a_link_from_the_index_to_a_missing_topic_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    make_journal(root, index="- [Gone](topics/gone.md) — a topic renamed\n")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "journal")
    assert "study/discussion/index.md links to topics/gone.md" in d.what


def test_a_link_from_a_topic_to_a_missing_session_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    make_journal(root, index="[T](topics/t.md)\n",
                 topics={"t.md": "[Index](../index.md) · [s](../sessions/2026-01-01.md)\n"})
    d = only(library.check())
    assert "topics/t.md links to ../sessions/2026-01-01.md" in d.what


def test_links_that_resolve_urls_and_anchors_are_not_reported(lib):
    root = make_doc(lib, "topic/slug")
    make_journal(root,
                 index="[T](topics/t.md#key-points) [w](https://example.org) [h](#topics)\n",
                 topics={"t.md": "[Index](../index.md) [s](../sessions/2026-01-01.md)\n"},
                 sessions={"2026-01-01.md": "# S\n"})
    assert library.check() == []


def test_a_session_is_never_checked(lib):
    """Sessions are never rewritten: a link in one is true of the day it was written."""
    root = make_doc(lib, "topic/slug")
    make_journal(root, sessions={"2026-01-01.md": "[Old](../topics/old.md)\n"})
    assert library.check() == []


def test_a_journal_is_checked_before_its_document_exists(lib):
    """A discussion usually starts before `make new`."""
    make_journal(lib / "topic" / "slug", index="[T](topics/t.md)\n")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "journal")


def test_a_journal_without_an_index_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (make_journal(root) / "index.md").unlink()
    assert "has no index.md" in only(library.check()).what


def test_a_journal_in_one_file_is_reported(lib):
    root = make_doc(lib, "topic/slug")
    (root / doc.STUDY).mkdir()
    (root / doc.STUDY / "discussion.md").write_text("# D\n", encoding="utf-8")
    d = only(library.check())
    assert (d.where, d.kind) == ("topic/slug", "journal")
    assert "a journal in one file" in d.what


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
