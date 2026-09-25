"""The catalogue: a manifest in every directory of the library, ids to cite by.

Each test builds the small library it needs in a temporary directory: `sync`
and `describe` write, and the fixture library is shared by the session.
"""
import pytest

from core import catalogue as cat
from core import doc


def put(root, rel, content="x"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def lib(tmp_path, monkeypatch):
    lib = tmp_path / "library"
    lib.mkdir()
    monkeypatch.setattr(doc, "LIBRARY", lib)
    return lib


@pytest.fixture
def station(lib):
    """An entry with every kind of child: roles, a root file, a stray directory."""
    e = lib / "lab" / "tools" / "tc-22"
    put(e, "sources/manuel.pdf", "%PDF manuel")
    put(e, "sources/pannes/p1.jpg", "jpeg 1")
    put(e, "sources/pannes/p2.jpg", "jpeg 2")
    put(e, "document/index.md", "---\ntitle: T\n---\n")
    put(e, "document/assets/.gitkeep", "")
    put(e, "study/NOTES.md", "# Notes")
    put(e, "study/schema.md", "# Schéma")
    put(e, "notice.txt", "notice")
    put(e, ".work/review/sheet.png", "png")
    return e


def items(entry):
    return {i.path: i for i in cat.read(entry).items}


def snapshot(root):
    return {p.relative_to(root): p.stat().st_mtime_ns for p in root.rglob("*")}


# --- the format -------------------------------------------------------------

def test_a_manifest_round_trips_through_its_yaml():
    m = cat.Manifest(id="tc22-abcdefgh", name="Station", description="Une station.",
                     items=[cat.Item(path="sources/b.pdf", kind="pdf", sha256="00"),
                            cat.Item(path="sources/a", kind="directory", files=2)])
    text = cat.dump(m)
    assert text.startswith(cat.HEADER)
    back = cat.parse(text)
    assert (back.id, back.name, back.description) == (m.id, m.name, m.description)
    assert [i.path for i in back.items] == ["sources/a", "sources/b.pdf"]   # sorted
    assert back.items[0].files == 2


def test_a_topic_manifest_has_no_items_key():
    text = cat.dump(cat.Manifest(id="labo-abcdefgh", name="Labo", description="d"))
    assert "items" not in text
    assert cat.parse(text).items is None


def test_an_unnamed_manifest_is_its_header_alone():
    assert cat.dump(cat.Manifest()) == cat.HEADER
    assert cat.parse(cat.HEADER) == cat.Manifest()


@pytest.mark.parametrize("text, what", [
    ("[1, 2]", "not a mapping"),
    ("name: [\n", "not YAML"),
    ("title: X\n", "unknown key title"),
    ("items: 3\n", "items is not a list"),
    ("items:\n  - kind: pdf\n", "item 1 has no path"),
    ("items:\n  - path: a\n", "item 1 has no kind"),
    ("items:\n  - {path: a, kind: pdf, colour: red}\n", "unknown key colour"),
    ("items:\n  - {path: a, kind: directory, files: many}\n", "files is not a count"),
    ("items:\n  - {path: a, kind: directory, files: true}\n", "files is not a count"),
    ("name: [a]\n", "name is not text"),
])
def test_a_malformed_manifest_is_refused_with_its_reason(text, what):
    with pytest.raises(cat.ManifestError, match=what):
        cat.parse(text)


# --- the tree -----------------------------------------------------------------

def test_a_directory_is_a_topic_or_an_entry_by_what_it_holds(lib):
    put(lib, "a/b/sources/x.pdf")
    put(lib, "a/single/only.pdf")
    put(lib, "a/empty/.gitkeep", "")
    kinds = {cat.where(lib, d): k for d, k in cat.nodes(lib)}
    # `a/empty` holds nothing visible: nothing to describe, so no node.
    assert kinds == {"a": "topic", "a/b": "entry", "a/single": "entry"}


def test_a_topic_with_its_manifest_is_still_a_topic(lib):
    put(lib, "a/b/sources/x.pdf")
    put(lib, "a/manifest.yaml", cat.HEADER)
    assert dict((cat.where(lib, d), k) for d, k in cat.nodes(lib))["a"] == "topic"


def test_the_inside_of_an_entry_is_never_a_node(lib, station):
    assert [cat.where(lib, d) for d, _ in cat.nodes(lib)] == [
        "lab", "lab/tools", "lab/tools/tc-22"]


def test_default_items_are_the_role_children_and_the_root_files(station):
    assert cat.default_paths(station) == [
        "document/assets", "document/index.md", "notice.txt",
        "sources/manuel.pdf", "sources/pannes", "study/NOTES.md", "study/schema.md"]


def test_a_directory_outside_the_roles_is_an_item_of_its_own(lib):
    e = lib / "components" / "capacitor"
    put(e, "images/a.jpg")
    put(e, "sources/b.pdf")
    assert cat.default_paths(e) == ["images", "sources/b.pdf"]


def test_the_longest_path_covers_a_file():
    items = [cat.Item("sources/pannes", "directory"),
             cat.Item("sources/pannes/p1.jpg", "image")]
    assert cat.covering(items, "sources/pannes/p1.jpg").path == "sources/pannes/p1.jpg"
    assert cat.covering(items, "sources/pannes/p2.jpg").path == "sources/pannes"
    assert cat.covering(items, "sources/pannes-old/p.jpg") is None


# --- ids ----------------------------------------------------------------------

def test_an_id_is_the_prefix_and_eight_unambiguous_characters():
    for _ in range(200):
        i = cat.new_id("manuel", set())
        assert cat.ID.fullmatch(i) and i.startswith("manuel-")
        assert not set(i.removeprefix("manuel-")) & set("0o1li")


def test_an_id_is_drawn_again_until_it_is_free(monkeypatch):
    draws = iter("aaaaaaaa" + "bbbbbbbb")
    monkeypatch.setattr(cat.secrets, "choice", lambda _: next(draws))
    assert cat.new_id("x", {"x-aaaaaaaa"}) == "x-bbbbbbbb"


@pytest.mark.parametrize("prefix", ["Manuel", "manuel_tc", "-a", "a--b", "é", "",
                                    "a" * 25])
def test_a_malformed_prefix_is_refused(prefix):
    with pytest.raises(cat.ManifestError, match="prefix"):
        cat.new_id(prefix, set())


# --- sync ---------------------------------------------------------------------

def test_sync_gives_every_directory_a_manifest(lib, station):
    cat.sync(lib)
    for d in (lib / "lab", lib / "lab" / "tools", station):
        assert (d / cat.MANIFEST).is_file()
    assert cat.read(lib / "lab").items is None
    assert not (station / "sources" / cat.MANIFEST).exists()


def test_sync_lists_the_default_items_with_what_the_tool_knows(station, lib):
    cat.sync(lib)
    got = items(station)
    assert set(got) == {"document/index.md", "notice.txt", "sources/manuel.pdf",
                        "sources/pannes", "study/NOTES.md", "study/schema.md"}
    assert got["sources/pannes"].kind == "directory" and got["sources/pannes"].files == 2
    assert got["sources/manuel.pdf"].kind == "pdf"
    assert got["notice.txt"].kind == "text"
    # A digest for the user's files only: the agent's change every session.
    assert got["sources/manuel.pdf"].sha256 and got["notice.txt"].sha256
    assert got["study/schema.md"].sha256 is None


def test_sync_names_the_anatomys_standard_files(station, lib):
    cat.sync(lib)
    got = items(station)
    for path in ("document/index.md", "study/NOTES.md"):
        assert got[path].name == cat.STANDARD[path][1]
        assert got[path].id.startswith(cat.STANDARD[path][0] + "-")
    assert got["study/schema.md"].name is None and got["study/schema.md"].id is None


def test_an_empty_directory_needs_no_item(station, lib):
    cat.sync(lib)
    assert "document/assets" not in items(station)        # only a .gitkeep


def test_sync_a_second_time_changes_nothing(station, lib):
    cat.sync(lib)
    before = snapshot(lib)
    report = cat.sync(lib)
    assert snapshot(lib) == before
    assert report[-1].startswith("0 manifests written")


def test_sync_never_touches_a_name_or_a_description(station, lib):
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22", "Station TC22", "Ma station.", "tc22")
    cat.describe(lib, "lab/tools/tc-22/sources/manuel.pdf", "Manuel", "Le manuel.", "manuel")
    put(station, "sources/new.pdf", "nouveau")
    cat.sync(lib)
    m = cat.read(station)
    assert (m.name, m.description) == ("Station TC22", "Ma station.")
    assert items(station)["sources/manuel.pdf"].name == "Manuel"
    assert "sources/new.pdf" in items(station)


def test_sync_never_writes_into_the_users_sources(station, lib):
    before = snapshot(station / doc.SOURCES)
    cat.sync(lib)
    assert snapshot(station / doc.SOURCES) == before


def test_a_new_file_in_a_covered_directory_is_no_new_item(station, lib):
    cat.sync(lib)
    put(station, "sources/pannes/p3.jpg", "jpeg 3")
    cat.sync(lib)
    assert items(station)["sources/pannes"].files == 3
    assert "sources/pannes/p3.jpg" not in items(station)


def test_a_renamed_source_keeps_its_id_name_and_description(station, lib):
    cat.sync(lib)
    first = cat.describe(lib, "lab/tools/tc-22/sources/manuel.pdf", "Manuel", "Le manuel.",
                         "manuel").split()[0]
    (station / "sources/manuel.pdf").rename(station / "sources/TC22 manual.pdf")
    report = cat.sync(lib)
    got = items(station)
    assert "sources/manuel.pdf" not in got
    moved = got["sources/TC22 manual.pdf"]
    assert (moved.id, moved.name, moved.description) == (first, "Manuel", "Le manuel.")
    assert any("followed: lab/tools/tc-22/sources/manuel.pdf → sources/TC22 manual.pdf"
               in line for line in report)


def test_a_renamed_directory_of_sources_is_followed(station, lib):
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22/sources/pannes", "Pannes", "Photos de pannes.", "pannes")
    (station / "sources/pannes").rename(station / "sources/failures")
    cat.sync(lib)
    assert items(station)["sources/failures"].name == "Pannes"


def test_a_source_moved_to_another_entry_is_followed(station, lib):
    other = lib / "lab" / "tools" / "support"
    put(other, "sources/support.jpg", "support")
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22/notice.txt", "Notice", "La notice.", "notice")
    (station / "notice.txt").rename(other / "sources" / "notice.txt")
    cat.sync(lib)
    assert "notice.txt" not in items(station)
    assert items(other)["sources/notice.txt"].name == "Notice"


def test_a_vanished_named_source_is_kept_and_reported(station, lib):
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22/sources/manuel.pdf", "Manuel", "Le manuel.", "manuel")
    (station / "sources/manuel.pdf").unlink()
    report = cat.sync(lib)
    assert "sources/manuel.pdf" in items(station)
    assert "lab/tools/tc-22 — vanished: sources/manuel.pdf" in report


def test_a_vanished_item_never_named_is_dropped(station, lib):
    cat.sync(lib)
    (station / "study/schema.md").unlink()
    cat.sync(lib)
    assert "study/schema.md" not in items(station)


def test_a_described_source_that_changed_is_reported_and_keeps_its_digest(station, lib):
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22/sources/manuel.pdf", "Manuel", "Le manuel.", "manuel")
    described = items(station)["sources/manuel.pdf"].sha256
    put(station, "sources/manuel.pdf", "%PDF manuel, révision 2")
    report = cat.sync(lib)
    assert "lab/tools/tc-22 — changed since described: sources/manuel.pdf" in report
    assert items(station)["sources/manuel.pdf"].sha256 == described
    cat.describe(lib, "lab/tools/tc-22/sources/manuel.pdf", description="Révisé.")
    assert items(station)["sources/manuel.pdf"].sha256 != described


def test_an_undescribed_source_follows_its_content(station, lib):
    cat.sync(lib)
    put(station, "sources/manuel.pdf", "%PDF autre")
    report = cat.sync(lib)
    assert not any("changed" in line for line in report)
    assert items(station)["sources/manuel.pdf"].sha256 == cat.file_digest(
        station / "sources/manuel.pdf")


def test_sync_of_one_entry_writes_it_and_the_topics_above_only(station, lib):
    put(lib, "other/entry/sources/x.pdf")
    cat.sync(lib, ["lab/tools/tc-22"])
    assert (station / cat.MANIFEST).is_file() and (lib / "lab" / cat.MANIFEST).is_file()
    assert not (lib / "other" / cat.MANIFEST).exists()


def test_sync_of_a_path_inside_an_entry_syncs_the_entry(station, lib):
    cat.sync(lib, ["library/lab/tools/tc-22/sources/pannes"])
    assert (station / cat.MANIFEST).is_file()


def test_an_unreadable_manifest_is_left_as_it_is(station, lib):
    put(station, cat.MANIFEST, "items: 3\n")
    report = cat.sync(lib)
    assert (station / cat.MANIFEST).read_text() == "items: 3\n"
    assert any("unreadable manifest" in line for line in report)


# --- describe -----------------------------------------------------------------

def test_a_first_naming_draws_the_id_from_the_prefix(station, lib):
    cat.sync(lib)
    line = cat.describe(lib, "lab", "Laboratoire", "L'équipement de l'atelier.", "labo")
    m = cat.read(lib / "lab")
    assert m.id.startswith("labo-") and line == f"{m.id} — lab"
    assert (m.name, m.description) == ("Laboratoire", "L'équipement de l'atelier.")


@pytest.mark.parametrize("args, what", [
    (("N", "D", None), "prefix"),
    (("N", None, "p"), "both the name and the description"),
    ((None, None, "p"), "nothing to write"),
])
def test_a_first_naming_needs_the_name_the_description_and_the_prefix(station, lib,
                                                                      args, what):
    cat.sync(lib)
    with pytest.raises(cat.ManifestError, match=what):
        cat.describe(lib, "lab", *args)


def test_an_id_never_changes(station, lib):
    cat.sync(lib)
    first = cat.describe(lib, "lab", "Labo", "d", "labo").split()[0]
    again = cat.describe(lib, "lab", "Laboratoire", None, "autre").split()[0]
    assert again == first and cat.read(lib / "lab").name == "Laboratoire"


def test_describe_reaches_a_node_by_its_id(station, lib):
    cat.sync(lib)
    first = cat.describe(lib, "lab/tools/tc-22/study/schema.md", "Schéma", "Relevé.", "schema")
    ident = first.split()[0]
    cat.describe(lib, ident, description="Relevé du schéma.")
    cat.describe(lib, f"id:{ident}", name="Schéma relevé")
    got = items(station)["study/schema.md"]
    assert (got.name, got.description) == ("Schéma relevé", "Relevé du schéma.")


def test_describing_a_file_inside_a_covered_directory_takes_it_out(station, lib):
    cat.sync(lib)
    cat.describe(lib, "lab/tools/tc-22/sources/pannes/p1.jpg", "Panne 1", "La première.", "panne")
    got = items(station)
    assert got["sources/pannes/p1.jpg"].sha256 and got["sources/pannes"]
    assert cat.covering(list(got.values()), "sources/pannes/p1.jpg").name == "Panne 1"
    before = snapshot(lib)
    cat.sync(lib)
    assert snapshot(lib) == before


@pytest.mark.parametrize("target, what", [
    ("lab/tools/tc-22/.work/review/sheet.png", "hidden"),
    ("lab/nowhere", "nothing there"),
    ("id:gone-abcdefgh", "no such id"),
])
def test_describe_refuses_what_it_cannot_describe(station, lib, target, what):
    cat.sync(lib)
    with pytest.raises(cat.ManifestError, match=what):
        cat.describe(lib, target, "N", "D", "p")


def test_a_directory_under_a_topic_is_described_as_a_node(station, lib):
    cat.sync(lib)
    line = cat.describe(lib, "lab/tools", "Outils", "Les outils.", "outils")
    assert line.endswith("— lab/tools")


# --- citations ------------------------------------------------------------------

def test_citations_are_read_from_the_agents_markdown_only(station, lib):
    put(station, "study/discussion/index.md",
        "Voir [le manuel](id:manuel-abcdefgh) et [ici](topics/a.md).\n")
    put(station, "sources/copied.md", "[x](id:ignored-abcdefgh)\n")
    put(station, ".work/x.md", "[x](id:ignored-bcdefghj)\n")
    found = [(p.relative_to(station).as_posix(), n, i) for p, n, i in cat.citations(lib)]
    assert found == [("study/discussion/index.md", 1, "manuel-abcdefgh")]


# --- the command line -----------------------------------------------------------

def test_the_command_line_syncs_and_describes(station, lib, capsys):
    assert cat.main(["sync"]) == 0
    assert "manifest created" in capsys.readouterr().out
    assert cat.main(["describe", "lab", "--name", "Labo", "--description", "d",
                     "--prefix", "labo"]) == 0
    assert capsys.readouterr().out.startswith("labo-")


def test_the_command_line_fails_loudly_on_a_refusal(station, lib, capsys):
    assert cat.main(["describe", "lab", "--name", "Labo"]) == 1
    assert capsys.readouterr().err.startswith("catalogue: ")
