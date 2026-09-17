"""The repository layout: sources under library/, outputs under out/."""


def test_the_sources_are_under_library(repo):
    assert (repo / "library").is_dir()
    assert not (repo / "pdfs").exists()


def test_no_out_inside_the_documents(repo):
    assert list((repo / "library").rglob("out")) == []


def test_the_source_material_directory_is_plural(repo):
    assert list((repo / "library").rglob("source")) == []
    assert (repo / "library" / "electronique" / "components" / "led"
            / "sources" / "source.md").is_file()
