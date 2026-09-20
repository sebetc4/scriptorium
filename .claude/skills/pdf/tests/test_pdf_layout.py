"""The skill's three scripts read from library/; the build writes under out/pdf/.

Split from the repository's tests/test_layout.py when the modules moved into
this skill: the paths are still the repository's, but the modules that hold
them are this skill's.
"""
import build
import ingest
import new
from core import doc


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


# --------------------------------------------------------------------------
# An SVG the build declines to inline goes blind to every text-layer check
# --------------------------------------------------------------------------
def declined(tmp_path, capsys, svg: str, name: str = "figure.svg",
             src: str | None = None):
    import build
    inside = doc.doc_dir(tmp_path) / "assets"
    inside.mkdir(parents=True)
    (inside / name).write_text(svg, encoding="utf-8")
    html = f'<p><img alt="x" src="{src or f"assets/{name}"}" /></p>'
    out = build.inline_svgs(html, tmp_path, {})
    return out, capsys.readouterr().err


def test_an_svg_over_the_limit_is_reported_rather_than_silently_linked(
        tmp_path, capsys):
    import build
    big = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
           + "<!--" + "x" * (build.SVG_MAX + 1) + "-->" + "</svg>")
    out, err = declined(tmp_path, capsys, big)
    assert "<img" in out                      # left as a picture
    assert "not inlined" in err and "kB" in err
    assert "escapes every check" in err


def test_an_svg_outside_the_document_is_reported(tmp_path, capsys):
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / "elsewhere" / "figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>',
        encoding="utf-8")
    out, err = declined(tmp_path, capsys, "<svg/>", src="../elsewhere/figure.svg")
    assert "not inlined" in err and "document/" in err


def test_an_svg_that_inlines_says_nothing(tmp_path, capsys):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
           '<rect width="10" height="10"/></svg>')
    out, err = declined(tmp_path, capsys, svg)
    assert "<svg" in out and "<img" not in out
    assert err == ""
