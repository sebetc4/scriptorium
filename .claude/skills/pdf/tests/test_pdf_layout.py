"""The skill's three scripts read from library/; the build writes under out/pdf/.

Split from the repository's tests/test_layout.py when the modules moved into
this skill: the paths are still the repository's, but the modules that hold
them are this skill's.
"""
import build
import ingest
import new


def test_the_three_scripts_point_at_library(repo):
    for module in (build, new, ingest):
        assert module.LIBRARY == repo / "library", module.__name__
        assert module.ROOT == repo, module.__name__


def test_new_reads_the_templates_from_the_skill_assets(repo):
    assert new.TEMPLATES == repo / ".claude" / "skills" / "pdf" / "assets" / "templates"
    assert sorted(p.name for p in new.TEMPLATES.iterdir()) == ["letter", "onepager", "report", "slides"]


def test_build_writes_under_out_pdf(repo):
    assert build.OUT == repo / "out"
    d = repo / "library" / "exemples" / "guide-de-style"
    assert build.out_dir(d) == repo / "out" / "pdf" / "exemples" / "guide-de-style"
