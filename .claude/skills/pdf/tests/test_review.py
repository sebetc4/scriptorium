"""review.py: what can be checked of a built PDF without looking at it, and the
sheets that make looking at it cheap.

Every fixture is a real PDF made by WeasyPrint from a few lines of HTML, each
carrying one defect the review loop has met in this library — a check is only
trusted once it has been seen to catch its own.
"""
from pathlib import Path

import pytest
from PIL import Image
from weasyprint import HTML

import review

# The geometry of the library's documents, reduced to what the checks rely on:
# running header and page number in the margins, text set on the page margins.
PAGE_CSS = """
@page {
  size: A4; margin: 24mm 20mm 20mm;
  @top-left { content: "Doc title"; font-size: 7.5pt; }
  @bottom-right { content: counter(page) " / " counter(pages); font-size: 7.5pt; }
}
@page :first { @top-left { content: none; } @bottom-right { content: none; } }
body { margin: 0; font-size: 10.5pt; text-align: justify; }
h2 { font-size: 16pt; }
"""
PROSE = "<p>" + "Un paragraphe de texte courant, justifié sur la largeur du bloc. " * 12 + "</p>"


def make_pdf(tmp_path: Path, body: str, css: str = "", name: str = "doc.pdf") -> Path:
    pdf = tmp_path / name
    html = f"<html><head><style>{PAGE_CSS}{css}</style></head><body>{body}</body></html>"
    HTML(string=html).write_pdf(pdf)
    return pdf


def kinds(findings) -> list[tuple[int, str]]:
    return [(f.page, f.kind) for f in findings]


def cover_and_body(body: str) -> str:
    return "<h1>Cover</h1><div style='break-before: page'></div>" + body


# --------------------------------------------------------------------------
# The checks
# --------------------------------------------------------------------------
def test_a_clean_document_raises_nothing(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        '<p><a href="#one">One <span class="n"></span></a></p>'
        f'<h2 id="one" style="break-before: page">One</h2>{PROSE}{PROSE}'),
        css="a::after { content: ' ' target-counter(attr(href url), page); }")
    assert review.checks(pdf) == []


def test_a_toc_number_that_reads_zero_is_reported(tmp_path):
    # The flex container is the real cause met in theme/page.css: WeasyPrint
    # resolves target-counter() to 0 inside it.
    pdf = make_pdf(tmp_path, cover_and_body(
        f'<nav><a href="#one">One</a></nav><h2 id="one" style="break-before: page">One</h2>{PROSE}'),
        css="nav a { display: flex; justify-content: space-between; padding: 0.42em 0; }"
            "nav a::after { content: target-counter(attr(href url), page); }")
    assert kinds(review.checks(pdf)) == [(2, "toc")]


def test_a_toc_number_pointing_at_another_page_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f'<p><a href="#one">One 9</a></p><h2 id="one" style="break-before: page">One</h2>{PROSE}'))
    [finding] = review.checks(pdf)
    assert (finding.page, finding.kind) == (2, "toc")
    assert "9" in finding.detail and "3" in finding.detail


def test_a_link_that_ends_without_a_number_is_not_a_toc_entry(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f'<p>See <a href="#one">the section</a>.</p><h2 id="one" style="break-before: page">One</h2>{PROSE}'))
    assert review.checks(pdf) == []


def test_a_page_with_nothing_but_its_header_and_number_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<div style='break-before: page'></div><div style='break-before: page'></div>{PROSE}"))
    assert kinds(review.checks(pdf)) == [(3, "blank")]


def test_text_past_the_right_margin_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        PROSE + "<p style='white-space: nowrap; text-align: left'>"
        + "débordement " * 14 + "</p>" + PROSE))
    assert kinds(review.checks(pdf)) == [(2, "overflow")]


def test_the_spaces_ending_a_justified_line_are_not_an_overflow(tmp_path):
    # A trailing space's box reaches past the margin in a justified line.
    pdf = make_pdf(tmp_path, cover_and_body(PROSE * 3))
    assert review.checks(pdf) == []


def test_a_heading_left_at_the_bottom_of_a_page_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Intro.</p><div style='height: 230mm'></div><h2>Stranded</h2>{PROSE}"),
        css="h2 { break-after: auto; margin: 0; }")
    assert kinds(review.checks(pdf)) == [(2, "orphan-heading")]


def test_a_heading_followed_by_a_captioned_figure_is_not_stranded(tmp_path):
    # Met in the library: a heading, a photograph under it, and its caption set
    # small near the foot of the page — a caption is not a running footer.
    photo = tmp_path / "photo.png"
    Image.new("RGB", (400, 300), "steelblue").save(photo)
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<h2>Heading</h2><figure style='margin: 0'>"
        f"<img src='{photo.as_uri()}' style='width: 100%; height: 178mm'>"
        "<figcaption style='font-size: 7.5pt'>Figure 1 — A photograph</figcaption></figure>"
        f"<div style='break-before: page'>{PROSE}</div>"))
    assert review.checks(pdf) == []


def test_a_heading_followed_by_an_image_alone_is_not_stranded(tmp_path):
    photo = tmp_path / "photo.png"
    Image.new("RGB", (400, 300), "steelblue").save(photo)
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<h2>Heading</h2><p style='margin: 0'>"
        f"<img src='{photo.as_uri()}' style='width: 100%; height: 150mm'></p>"
        f"<div style='break-before: page'>{PROSE}</div>"))
    assert review.checks(pdf) == []


def test_a_page_missing_its_number_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<div style='page: bare; break-before: page'>{PROSE}</div>"
        f"<div style='break-before: page'>{PROSE}</div>"),
        css="@page bare { @bottom-right { content: none; } }")
    assert kinds(review.checks(pdf)) == [(3, "page-number")]


def test_an_icon_name_left_in_the_text_is_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(f"<p>Statut :circle-check.accent: conforme</p>{PROSE}"))
    assert kinds(review.checks(pdf)) == [(2, "icon")]


def test_an_icon_name_written_as_code_is_not_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Une icône s'écrit <code>:nom:</code> dans le texte.</p>{PROSE}"),
        css="code { font-family: monospace; }")
    assert review.checks(pdf) == []


# --------------------------------------------------------------------------
# The sheets and the zoom
# --------------------------------------------------------------------------
def pages(n: int) -> str:
    return "".join(f"<h2 style='break-before: page'>Page {i}</h2>{PROSE}" for i in range(n))


def test_sheets_hold_four_pages_each_under_the_pixel_budget(tmp_path):
    pdf = make_pdf(tmp_path, pages(5))
    sheets = review.sheets(pdf, tmp_path / "review")
    assert [p.name for p in sheets] == ["sheet-01.png", "sheet-02.png"]
    for sheet in sheets:
        with Image.open(sheet) as image:
            assert image.width * image.height <= review.MAX_PIXELS
    with Image.open(sheets[0]) as first:
        # two columns of A4 pages, each drawn well above thumbnail size
        assert first.height > first.width > 800


def test_sheets_of_landscape_pages_are_laid_out_wide(tmp_path):
    pdf = make_pdf(tmp_path, pages(4), css="@page { size: 254mm 190mm; }")
    [sheet] = review.sheets(pdf, tmp_path / "review")
    with Image.open(sheet) as image:
        assert image.width > image.height
        assert image.width * image.height <= review.MAX_PIXELS


def test_a_new_run_removes_the_sheets_of_the_last(tmp_path):
    dest = tmp_path / "review"
    review.sheets(make_pdf(tmp_path, pages(9), name="long.pdf"), dest)
    review.sheets(make_pdf(tmp_path, pages(3), name="short.pdf"), dest)
    assert sorted(p.name for p in dest.glob("sheet-*.png")) == ["sheet-01.png"]


def test_zoom_renders_each_asked_page_alone_under_the_budget(tmp_path):
    pdf = make_pdf(tmp_path, pages(3))
    zoomed = review.zoom(pdf, [2, 3], tmp_path / "review")
    assert [p.name for p in zoomed] == ["page-02.png", "page-03.png"]
    with Image.open(zoomed[0]) as image:
        assert image.width * image.height <= review.MAX_PIXELS
        assert image.width > 850


def test_zoom_refuses_a_page_the_document_does_not_have(tmp_path):
    pdf = make_pdf(tmp_path, pages(2))
    with pytest.raises(IndexError):
        review.zoom(pdf, [1, 7], tmp_path / "review")
    # refused as a whole, before any page is rendered
    assert not list((tmp_path / "review").glob("page-*.png"))


# --------------------------------------------------------------------------
# Which PDFs a document has, and whether they are current
# --------------------------------------------------------------------------
def test_a_light_document_has_one_variant(tmp_path):
    (tmp_path / "guide.pdf").write_bytes(b"%PDF")
    assert review.variants(tmp_path, "guide", "light") == [("light", tmp_path / "guide.pdf")]


def test_a_document_in_both_themes_has_two_variants(tmp_path):
    for name in ("guide.pdf", "guide-dark.pdf"):
        (tmp_path / name).write_bytes(b"%PDF")
    assert review.variants(tmp_path, "guide", "both") == [
        ("light", tmp_path / "guide.pdf"), ("dark", tmp_path / "guide-dark.pdf")]


def test_a_dark_only_document_names_its_single_pdf_dark(tmp_path):
    (tmp_path / "guide.pdf").write_bytes(b"%PDF")
    assert review.variants(tmp_path, "guide", "dark") == [("dark", tmp_path / "guide.pdf")]


def test_a_pdf_older_than_any_source_file_is_stale(tmp_path):
    import os
    doc = tmp_path / "doc"
    (doc / "assets").mkdir(parents=True)
    (doc / "index.md").write_text("x")
    (doc / "assets" / "figure.svg").write_text("x")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    os.utime(pdf, (1_000, 1_000))
    os.utime(doc / "index.md", (500, 500))
    os.utime(doc / "assets" / "figure.svg", (2_000, 2_000))
    assert review.stale(pdf, doc)
    os.utime(doc / "assets" / "figure.svg", (500, 500))
    assert not review.stale(pdf, doc)


def test_the_sources_of_an_import_do_not_make_a_pdf_stale(tmp_path):
    import os
    doc = tmp_path / "doc"
    (doc / "sources").mkdir(parents=True)
    (doc / "index.md").write_text("x")
    (doc / "sources" / "meta.json").write_text("x")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    os.utime(pdf, (1_000, 1_000))
    os.utime(doc / "index.md", (500, 500))
    os.utime(doc / "sources" / "meta.json", (2_000, 2_000))
    assert not review.stale(pdf, doc)
