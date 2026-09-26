"""Reading the map: `find`, `ls`, `links` and `path`, core/navigate.py.

Read-only commands, so most tests read the shared fixture library. What needs a
library of its own — markers, a large library — builds it in a temporary
directory, through the catalogue.
"""
import shutil

import pytest

from core import catalogue as cat
from core import doc
from core import navigate as nav

GUIDE = "guide-style-6bhjjn7c"          # the fixture's style guide, an entry
COMPONENT = "composant-yqbta74m"         # the fixture's component, which cites it


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
def workshop(lib):
    """A washer with a described manual, a journal that cites it, and a
    coffee pack described in French with its accents."""
    washer = lib / "home" / "washer"
    put(washer, "sources/manuel.pdf", "%PDF")
    put(washer, "sources/pannes/p1.jpg", "jpeg")
    coffee = lib / "home" / "cafe"
    put(coffee, "sources/fiche.md", "# Fiche\n\nArabica, torréfaction légère, café en grains.\n")
    works = lib / "travaux"
    put(works, "study/NOTES.md", "# Notes\n")
    cat.sync(lib)
    cat.describe(lib, "home", "Maison", "Ce qui concerne la maison.", "maison")
    cat.describe(lib, "home/washer", "Lave-linge", "Mon lave-linge, à hublot.", "lave-linge")
    cat.describe(lib, "home/washer/sources/manuel.pdf", "Manuel du lave-linge",
                 "Réglages, entretien, codes d'erreur.", "manuel")
    cat.describe(lib, "home/cafe", "Paquet de café", "« Café » en grains, torréfaction légère.", "cafe")
    cat.describe(lib, "travaux", "Travaux", "Le chantier de la maison.", "travaux")
    manual = ident_of(lib, "home/washer/sources/manuel.pdf")
    put(works, "study/discussion/index.md",
        f"# Travaux\n\nLa panne se diagnostique comme le dit [le manuel](id:{manual}).\n")
    cat.sync(lib)
    return lib


def ident_of(lib, target):
    """The id of a node or an item, reached by its path."""
    node, item = nav.Atlas(lib).resolve(target)
    return (item or node).id


# --- folding and bounding -------------------------------------------------------

def test_folding_drops_case_accents_and_curly_apostrophes():
    assert nav.fold("« Été » à l’ombre") == "« ete » a l'ombre"


def test_an_answer_is_bounded_and_says_how_many_more():
    lines = [f"line {n}" for n in range(25)]
    out = nav.bounded(lines, 20, "narrow it")
    assert len(out) == 20
    assert out[-1] == "… 6 more — narrow it, or --limit 25"
    assert nav.bounded(lines, 0) == lines
    assert nav.bounded(lines[:20], 20) == lines[:20]


# --- find ---------------------------------------------------------------------

def test_find_cafe_finds_a_description_that_writes_cafe_with_its_accent(workshop):
    out = nav.find(workshop, "cafe")
    assert len(out) == 1
    kind, ident, *rest = out[0].split("  ")
    assert (kind, rest) == ("entry", ["Paquet de café", "home/cafe"])
    assert ident.startswith("cafe-")


def test_find_needs_every_word(workshop):
    assert len(nav.find(workshop, "manuel reglages")) == 1
    assert nav.find(workshop, "manuel cafe") == ["nothing matches “manuel cafe”"]


def test_find_reports_an_item_with_its_kind_and_path(workshop):
    (line,) = nav.find(workshop, "codes d'erreur")
    assert line.startswith("pdf  manuel-")
    assert line.endswith("  Manuel du lave-linge  home/washer/sources/manuel.pdf")


def test_find_in_a_topic_or_an_entry_only(workshop):
    assert len(nav.find(workshop, "travaux")) == 1
    assert nav.find(workshop, "travaux", within="home")[0].startswith("nothing matches")
    assert len(nav.find(workshop, "hublot", within=ident_of(workshop, "home"))) == 1


def test_find_never_lists_what_is_not_named(workshop):
    # `sources/pannes` is an item, described by nobody yet.
    assert nav.find(workshop, "pannes")[0].startswith("nothing matches")


def test_find_text_searches_the_content_of_text_items(workshop):
    out = nav.find(workshop, "arabica", text=True)
    assert len(out) == 1
    assert "sources/fiche.md" in out[0] and out[0].endswith(
        "3: Arabica, torréfaction légère, café en grains.")


def test_find_text_searches_the_text_files_of_a_directory_item(workshop):
    (line,) = nav.find(workshop, "panne se diagnostique", text=True)
    assert line.startswith("discussion-") and "Discussion journal" in line
    assert "index.md:3: La panne se diagnostique" in line


def test_find_text_reads_no_file_the_manifest_does_not_know(workshop):
    put(workshop / "travaux", "study/new.md", "Arabica again")   # not synced
    assert len(nav.find(workshop, "arabica", text=True)) == 1


def test_find_on_the_fixture_library(fixture_library):
    assert nav.find(fixture_library, "guide style") == [
        f"entry  {GUIDE}  Guide de style  exemples/guide-de-style"]


# --- ls -------------------------------------------------------------------------

def test_ls_of_the_root_lists_the_top_topics_with_their_counts(fixture_library):
    assert nav.ls(fixture_library) == [
        "exemples/  Exemples  exemples-p4a7j3s8  topic, 1 entry",
        "sample/  Échantillons  echantillons-ynbpytwa  topic, 1 entry"]


def test_ls_of_a_topic_lists_its_entries_and_l_adds_the_descriptions(fixture_library):
    (line,) = nav.ls(fixture_library, "sample", level=1)
    assert line.startswith(f"component/  Composant d'essai  {COMPONENT}  entry, 4 items — ")
    assert line.endswith("le journal de sa discussion.")


def test_ls_of_an_entry_lists_its_items(fixture_library):
    out = nav.ls(fixture_library, COMPONENT)
    assert [line.split("  ")[0] for line in out] == [
        "document/assets", "document/cover.md", "document/index.md", "study/discussion"]


def test_ls_ll_adds_the_kind_size_and_date(fixture_library):
    line = nav.ls(fixture_library, "sample/component", level=2)[-1]
    assert " directory, 4 files  " in line and " KB  20" in line


def test_ls_of_an_item_shows_it_and_what_a_directory_holds(fixture_library):
    out = nav.ls(fixture_library, "sample/component/study/discussion")
    assert out[0].startswith("study/discussion  Journal de discussion  discussion-")
    assert any(line.startswith("  topics/brochage.md  20") for line in out)


def test_ls_of_a_directory_item_marks_the_files_that_have_an_item_of_their_own(workshop):
    """A file that arrived in a described directory has no item of its own:
    after a sync, the directory is `to review`, and its listing says which."""
    washer = workshop / "home" / "washer"
    cat.describe(workshop, "home/washer/sources/pannes", "Pannes", "Les pannes du lave-linge.",
                 "pannes")
    cat.describe(workshop, "home/washer/sources/pannes/p1.jpg", "Panne K", "La panne couteau.",
                 "panne-k")
    put(washer, "sources/pannes/p2.jpg", "jpeg 2")
    cat.sync(workshop, ["home/washer"])
    out = nav.ls(workshop, "home/washer/sources/pannes")
    assert out[0].endswith("[to review]")
    p1 = next(line for line in out if line.startswith("  p1.jpg  "))
    p2 = next(line for line in out if line.startswith("  p2.jpg  "))
    assert p1.endswith(f"  → {ident_of(workshop, 'home/washer/sources/pannes/p1.jpg')}")
    assert "→" not in p2


def test_ls_marks_what_is_to_describe_new_to_review_and_gone(workshop):
    washer = workshop / "home" / "washer"
    put(washer, "sources/new.pdf", "new")                      # not synced: new
    put(washer, "sources/manuel.pdf", "%PDF revised")          # described: to review
    out = nav.ls(workshop, "home/washer")
    assert any(line.startswith("sources/manuel.pdf") and line.endswith("[to review]")
               for line in out)
    assert any(line.startswith("sources/pannes") and "[to describe]" in line for line in out)
    assert "sources/new.pdf  (new, no item covers it)" in out
    (washer / "sources/manuel.pdf").unlink()
    assert any(line.endswith("[gone]") for line in nav.ls(workshop, "home/washer"))


def test_ls_of_a_topic_adds_up_the_markers_below(workshop):
    put(workshop / "home" / "washer", "sources/new.pdf", "new")
    line = next(l for l in nav.ls(workshop, "home") if l.startswith("washer/"))
    assert line.endswith("entry, 2 items  [1 to describe, 1 new]")


def test_ls_of_a_library_without_manifests_still_answers(lib):
    put(lib, "topic/slug/sources/a.pdf")
    assert nav.ls(lib) == ["topic/  (to describe)  -  topic, 1 entry  [2 to describe, 1 new]"]


# --- links --------------------------------------------------------------------------

def test_links_of_an_entry_lists_what_it_cites_and_what_cites_it(fixture_library):
    assert nav.links(fixture_library, "sample/component") == [
        "cites:",
        f" exemples/guide-de-style  Guide de style  {GUIDE}",
        f"  (the entry)  {GUIDE} ← study/discussion/topics/brochage.md:17",
        "cited by: nothing"]
    assert nav.links(fixture_library, GUIDE) == [
        "cites: nothing",
        "cited by:",
        f" sample/component  Composant d'essai  {COMPONENT}",
        "  (the entry) ← study/discussion/topics/brochage.md:17"]


def test_links_of_an_item_counts_the_citations_of_that_item(workshop):
    manual = ident_of(workshop, "home/washer/sources/manuel.pdf")
    out = nav.links(workshop, manual)
    assert out[1:] == ["cited by:", f" travaux  Travaux  {ident_of(workshop, 'travaux')}",
                       "  Manuel du lave-linge ← study/discussion/index.md:3"]
    assert nav.links(workshop, "home/washer")[1:] == out[1:]    # the entry holds it


def test_links_reports_a_citation_that_leads_nowhere(workshop):
    put(workshop / "travaux", "study/discussion/topics/t.md", "[x](id:gone-abcdefgh)\n")
    out = nav.links(workshop, "travaux")
    assert "  gone-abcdefgh (no such id) ← study/discussion/topics/t.md:1" in out


# --- path -----------------------------------------------------------------------------

def test_path_resolves_an_id_from_the_repository_root(fixture_library):
    assert nav.path(fixture_library, GUIDE).endswith("library/exemples/guide-de-style")
    assert nav.path(fixture_library, f"id:{GUIDE}") == nav.path(fixture_library, GUIDE)


def test_path_refuses_an_unknown_id(fixture_library):
    with pytest.raises(cat.ManifestError, match="no such id"):
        nav.path(fixture_library, "gone-abcdefgh")


# --- the entry point ------------------------------------------------------------------

def test_the_command_line_answers_each_command(fixture_library, capsys):
    for argv, expected in ((["find", "guide"], GUIDE), (["ls"], "exemples/"),
                           (["links", COMPONENT], "cites:"),
                           (["path", GUIDE], "guide-de-style")):
        assert cat.main(argv) == 0, argv
        assert expected in capsys.readouterr().out, argv


def test_the_entry_point_is_declared(repo):
    assert 'catalogue = "core.catalogue:main"' in (repo / "pyproject.toml").read_text()


# --- the size of an answer depends on the question, never on the library ---------------

def grown(tmp_path, entries=500):
    """The fixture library, and `entries` more entries nobody asks about."""
    lib = tmp_path / "grown"
    shutil.copytree(cat.Path(doc.ROOT / "tests" / "fixtures" / "library"), lib)
    taken = set(cat.ids(lib))
    topic = lib / "generated"
    topic.mkdir()

    def named(prefix, name, description, items=None):
        ident = cat.new_id(prefix, taken)
        taken.add(ident)
        return cat.Manifest(ident, name, description, items)

    cat.write(topic, named("genere", "Généré", "Des entrées de remplissage."))
    for n in range(entries):
        e = topic / f"e{n:03}"
        put(e, "sources/scan.pdf", f"scan {n}")
        put(e, "study/notes.md", f"Remplissage numéro {n}.\n")
        items = [cat.Item("sources/scan.pdf", "pdf", **_named(f"Scan {n}", taken)),
                 cat.Item("study/notes.md", "text", **_named(f"Notes {n}", taken))]
        cat.write(e, named("entree", f"Entrée {n}", f"Remplissage numéro {n}.", items))
    return lib


def _named(name, taken):
    ident = cat.new_id("item", taken)
    taken.add(ident)
    return {"id": ident, "name": name, "description": f"{name}, sans intérêt."}


QUERIES = [
    ("find", lambda lib: nav.find(lib, "guide style")),
    ("find --in", lambda lib: nav.find(lib, "journal", within="sample")),
    ("find --text", lambda lib: nav.find(lib, "meplat", text=True)),
    ("ls topic", lambda lib: nav.ls(lib, "sample", level=1)),
    ("ls entry", lambda lib: nav.ls(lib, "sample/component", level=2)),
    ("links", lambda lib: nav.links(lib, COMPONENT)),
    ("path", lambda lib: [nav.path(lib, GUIDE)]),
]


@pytest.fixture(scope="module")
def large(tmp_path_factory):
    return grown(tmp_path_factory.mktemp("large"))


@pytest.mark.parametrize("name, ask", QUERIES, ids=[q[0] for q in QUERIES])
def test_an_answer_is_as_long_on_500_entries_as_on_the_fixture(fixture_library, large,
                                                                name, ask):
    small = ask(fixture_library)
    assert len(ask(large)) == len(small)


def test_a_question_that_matches_everything_is_still_bounded(large):
    out = nav.find(large, "remplissage")
    assert len(out) == nav.LIMIT and out[-1].startswith("… ")
    assert len(nav.ls(large, "generated")) == nav.LIMIT
    assert len(nav.find(large, "remplissage", text=True)) == nav.LIMIT


# --- peek ---------------------------------------------------------------------------

def a_pdf(path, pages):
    """A PDF with a text layer on each page given as text, none on a page given as None."""
    import pymupdf
    pdf = pymupdf.open()
    for text in pages:
        page = pdf.new_page()
        if text:
            page.insert_text((72, 72), text)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(path)
    return path


def test_peek_reads_the_text_layer_of_a_pdfs_first_pages(lib):
    a_pdf(lib / "home" / "four" / "sources" / "manuel.pdf",
          ["Four FX-60\nManuel", None, "Codes d'erreur"])
    out = nav.peek(lib, "home/four/sources/manuel.pdf")
    assert out[0].startswith("pdf, 3 pages, ")
    assert out[1:] == ["— p.1 —", "Four FX-60", "Manuel",
                       "— p.2: no text layer — read it as an image —"]
    assert nav.peek(lib, "home/four/sources/manuel.pdf", pages="3")[1:] == [
        "— p.3 —", "Codes d'erreur"]


def test_peek_gives_an_images_size_without_showing_it(lib):
    from PIL import Image
    p = lib / "home" / "four" / "sources" / "photo.png"
    p.parent.mkdir(parents=True)
    Image.new("RGB", (40, 30)).save(p)
    out = nav.peek(lib, "home/four/sources/photo.png")
    assert out[0].startswith("image, 40×30 px, ")
    assert out[1] == "read it to see what it shows"


def test_peek_reads_a_text_and_lists_a_directory_by_path_or_id(workshop):
    assert nav.peek(workshop, "home/cafe/sources/fiche.md")[1:] == [
        "# Fiche", "", "Arabica, torréfaction légère, café en grains."]
    out = nav.peek(workshop, "home/washer/sources/pannes")
    assert out[0].startswith("directory, 1 file, ") and out[1].startswith("  p1.jpg  image  ")
    manual = ident_of(workshop, "home/washer/sources/manuel.pdf")     # "%PDF": no real PDF
    (line,) = nav.peek(workshop, manual)
    assert line.startswith("pdf, 4 B, not readable: ")


def test_peek_is_bounded(lib):
    put(lib, "t/e/sources/long.md", "\n".join(f"ligne {n}" for n in range(50)))
    out = nav.peek(lib, "t/e/sources/long.md")
    assert len(out) == nav.LIMIT and out[-1].startswith("… ")


# --- retired ids ------------------------------------------------------------------------

def test_a_removed_id_still_answers_path_and_links(workshop):
    manual = ident_of(workshop, "home/washer/sources/manuel.pdf")
    cat.remove(workshop, [manual], used=True)
    assert nav.path(workshop, manual).startswith("removed on ")
    assert nav.path(workshop, manual).endswith("home/washer/sources/manuel.pdf")
    out = nav.links(workshop, "travaux")
    assert any(f"Manuel du lave-linge  {manual} (removed " in line for line in out)
    assert nav.links(workshop, "home/washer")[-1].startswith("  Manuel du lave-linge ← ")


def test_a_merged_id_leads_to_the_item_it_was_merged_into(workshop):
    cat.describe(workshop, "home/washer/sources/pannes", "Pannes", "Photos de pannes.", "pannes")
    photo = cat.describe(workshop, "home/washer/sources/pannes/p1.jpg", "Panne", "Une panne.",
                         "panne").split()[0]
    cat.merge(workshop, [photo])
    assert nav.path(workshop, photo).endswith("home/washer/sources/pannes")
    with pytest.raises(cat.ManifestError, match="retired"):
        nav.ls(workshop, photo)
