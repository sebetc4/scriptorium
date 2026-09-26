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
        css="h2 { break-after: auto; margin: 0; font-family: sans-serif; } body { font-family: serif; }")
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


def test_a_large_formula_at_the_foot_of_a_page_is_not_a_heading(tmp_path):
    # Seen on a document, p.8: a displayed formula, set larger than the text but in its family.
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Intro.</p><div style='height: 216mm'></div>"
        f"<p style='font-size: 14pt; margin: 0'>P = (V − V) × I = R × I</p>"
        f"<p style='margin: 0'>Une seule phrase.</p>{PROSE}"),
        css="h2 { font-family: sans-serif; } body { font-family: serif; } p { orphans: 1; widows: 1; }")
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
        f"<p>Une icône s’écrit <code>:nom:</code> dans le texte.</p>{PROSE}"),
        css="code { font-family: monospace; }")
    assert review.checks(pdf) == []


# --- What the first sheet-based reviews found, read from the text layer -------
def test_a_heading_followed_by_a_single_line_at_the_foot_of_a_full_page_is_reported(tmp_path):
    # Seen on a document, p.5: the heading and one sentence, the section's content on the next page.
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Intro.</p><div style='height: 216mm'></div><h2>Stranded</h2>"
        f"<p style='margin: 0'>Une seule phrase.</p>{PROSE}"),
        css="h2 { break-after: auto; margin: 0; font-family: sans-serif; } body { font-family: serif; } "
            "p { orphans: 1; widows: 1; }")
    assert kinds(review.checks(pdf)) == [(2, "orphan-heading")]


def test_a_page_holding_a_few_lines_among_full_pages_is_reported(tmp_path):
    # Seen on a document, p.10: the end of a list, then the next chapter opens on a new page.
    photo = tmp_path / "photo.png"
    Image.new("RGB", (400, 300), "steelblue").save(photo)
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p style='margin: 0'><img src='{photo.as_uri()}' style='width: 100%; height: 248mm'></p>"
        "<p>Deux lignes seulement.</p>"
        f"<div style='break-before: page'>{PROSE * 5}</div><div style='break-before: page'>{PROSE * 5}</div>"))
    found = kinds(review.checks(pdf))
    assert (3, "near-blank") in found
    assert [k for k in found if k[1] == "near-blank"] == [(3, "near-blank")]


def test_a_table_of_contents_page_is_not_near_blank(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        '<p><a href="#a">A <span></span></a></p><p><a href="#b">B <span></span></a></p>'
        f'<h2 id="a" style="break-before: page">A</h2>{PROSE * 5}'
        f'<h2 id="b" style="break-before: page">B</h2>{PROSE * 5}<div style="break-before: page">{PROSE * 5}</div>'),
        css="a::after { content: ' ' target-counter(attr(href url), page); }")
    assert "near-blank" not in {f.kind for f in review.checks(pdf)}


def test_a_glyph_set_in_a_font_outside_the_art_direction_is_reported(tmp_path):
    # Seen on a document: "→" and "≥" missing from the brand fonts, set in the fallback.
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Par heure <span style='font-family: Cantarell'>→</span> cinq mois.</p>{PROSE}"),
        css="body { font-family: 'Noto Serif'; }")
    [finding] = review.checks(pdf, fonts={"Noto Serif", "Noto Sans"})
    assert (finding.page, finding.kind) == (2, "font")
    assert "Cantarell" in finding.detail and "→" in finding.detail


def test_fonts_are_not_checked_without_the_art_direction(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"<p>Par heure <span style='font-family: Cantarell'>→</span> cinq mois.</p>{PROSE}"),
        css="body { font-family: 'Noto Serif'; }")
    assert review.checks(pdf) == []


def test_a_url_cut_by_hyphenation_is_reported(tmp_path):
    # Seen on a document, p.31: "jeanmarc-/dupont.example.org" — the printed address is wrong.
    pdf = make_pdf(tmp_path, cover_and_body(
        "<p style='width: 45mm; text-align: left'>Voir https://jeanmarc&shy;dupont.example.org/notes</p>"
        + PROSE))
    assert kinds(review.checks(pdf)) == [(2, "url-hyphen")]


def test_two_letters_carried_by_hyphenation_are_reported(tmp_path):
    # Seen on a document, p.20: "réquisition-/né".
    pdf = make_pdf(tmp_path, cover_and_body(
        "<p style='width: 18mm; text-align: left'>réquisition&shy;né</p>" + PROSE))
    assert kinds(review.checks(pdf)) == [(2, "short-hyphen")]


def test_two_letters_left_before_a_hyphenation_are_not_reported(tmp_path):
    # French typesetting forbids carrying two letters over, not leaving two
    # before the break: "in-/connue" is correct.
    pdf = make_pdf(tmp_path, cover_and_body(
        "<p style='width: 14mm; text-align: left'>in&shy;connue</p>" + PROSE))
    assert review.checks(pdf) == []


def test_a_word_joined_by_a_slash_is_not_an_address(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        "<p style='width: 40mm; text-align: left'>page principale/inter&shy;face</p>" + PROSE))
    assert "url-hyphen" not in {f.kind for f in review.checks(pdf)}

def test_a_hyphenated_table_cell_continues_in_its_own_column(tmp_path):
    # Seen on a document, p.12: "Réfé-" in one cell, "Ce" opening the next column's line.
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<table style='width: 70mm'><tr>"
        "<td style='width: 13mm; line-height: 4; vertical-align: top'>Réfé&shy;rence</td>"
        "<td style='padding-top: 10mm; vertical-align: top'>Ce que tu ranges</td>"
        f"</tr></table>{PROSE}"))
    assert "short-hyphen" not in {f.kind for f in review.checks(pdf)}

def test_a_justified_line_stretched_far_wider_than_the_page_is_reported(tmp_path):
    # Seen on a document, p.31: the line before a long unbreakable address spreads across the width.
    pdf = make_pdf(tmp_path, cover_and_body(
        PROSE + "<p>Analyse de Dupont en anglais avec <span style='white-space: nowrap'>"
        "https://docs.example.org/guides/lavage/quick_start_k450_en.html</span> et la suite du texte "
        "qui continue sur la ligne suivante pour que la ligne étirée ne soit pas la dernière.</p>" + PROSE))
    assert kinds(review.checks(pdf)) == [(2, "loose-line")]


def test_the_columns_of_a_table_are_not_a_loose_line(tmp_path):
    rows = "".join(f"<tr><td>Modèle {i}</td><td>620–645</td><td>Blanc, inox</td><td>2,0 kW</td>"
                   f"<td>1,8–2,2 V</td></tr>" for i in range(8))
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<table style='width: 100%; font-size: 8.4pt'>{rows}</table>{PROSE}"))
    assert review.checks(pdf) == []


def test_the_labels_of_a_code_block_are_not_a_loose_line(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<pre style='font-family: monospace'>"
        "│ A1 │                                   ← voir la note 1\n"
        "│ A2 │                                   ← voir la note 2\n"
        "│ A3 │                                   ← voir la note 3</pre>{PROSE}"))
    assert review.checks(pdf) == []

def test_inline_code_between_words_does_not_make_a_line_loose(tmp_path):
    # Seen on a document, p.7: "chercher les termes très précis `A`, `B`, `C`, et" — the
    # code is left out of the spacing, not the space it takes.
    codes = ", ".join(f"<code>{c}</code>" for c in ("XR-3315", "K4", "B24", "P2", "XR6302", "reset button"))
    pdf = make_pdf(tmp_path, cover_and_body(
        f"{PROSE}<p>Termes précis {codes} et quelques autres "
        f"encore, dans les fils du forum comme dans les notices des appareils.</p>{PROSE}"),
        css="code { font-family: monospace; font-size: 0.86em; padding: 0 0.2em; }")
    assert "loose-line" not in {f.kind for f in review.checks(pdf)}

def test_a_straight_apostrophe_in_the_text_is_reported(tmp_path):
    # Seen on a document, p.1: the subtitle "ce qu'on achète", untouched by the Markdown's typography.
    pdf = make_pdf(tmp_path, cover_and_body(f"<p>Ce qu'on achète.</p>{PROSE}"))
    assert kinds(review.checks(pdf)) == [(2, "apostrophe")]


def test_a_straight_apostrophe_in_code_is_not_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(f"<p><code>print('x')</code></p>{PROSE}"),
                   css="code { font-family: monospace; }")
    assert review.checks(pdf) == []


def test_text_set_below_a_readable_size_is_reported(tmp_path):
    # Seen on a document, p.22: diagram values at 4 pt.
    pdf = make_pdf(tmp_path, cover_and_body(f"{PROSE}<p style='font-size: 4pt'>30+j10 Ω</p>{PROSE}"))
    assert kinds(review.checks(pdf)) == [(2, "tiny-text")]


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
    inside = doc / "document"
    (inside / "assets").mkdir(parents=True)
    (inside / "index.md").write_text("x")
    (inside / "assets" / "figure.svg").write_text("x")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    os.utime(pdf, (1_000, 1_000))
    os.utime(inside / "index.md", (500, 500))
    os.utime(inside / "assets" / "figure.svg", (2_000, 2_000))
    assert review.stale(pdf, doc)
    os.utime(inside / "assets" / "figure.svg", (500, 500))
    assert not review.stale(pdf, doc)


def test_the_sources_of_an_import_do_not_make_a_pdf_stale(tmp_path):
    import os
    doc = tmp_path / "doc"
    (doc / "sources").mkdir(parents=True)
    (doc / "document").mkdir(parents=True)
    (doc / "document" / "index.md").write_text("x")
    (doc / "sources" / "meta.json").write_text("x")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    os.utime(pdf, (1_000, 1_000))
    os.utime(doc / "document" / "index.md", (500, 500))
    os.utime(doc / "sources" / "meta.json", (2_000, 2_000))
    assert not review.stale(pdf, doc)


def test_the_art_direction_fonts_are_the_first_family_of_each_role():
    tokens = {"font-serif": "'Noto Serif', 'Liberation Serif', Georgia, serif",
              "font-sans": "'Noto Sans', Cantarell, system-ui, sans-serif",
              "font-mono": "'JetBrains Mono', ui-monospace, monospace",
              "font-body": "var(--font-serif)"}
    assert review.art_direction_fonts(tokens) == {"Noto Serif", "Noto Sans", "JetBrains Mono"}


# --------------------------------------------------------------------------
# A targeted pass: the pages that were given, and the checks over all of them
# --------------------------------------------------------------------------
GUIDE = "exemples/guide-de-style"


@pytest.fixture(scope="module")
def guide_pdf(on_fixtures):
    """The fixture guide, built once: a review refuses a PDF it cannot find."""
    import build
    with on_fixtures() as library:
        return build.build(library / GUIDE)


def targeted(doc, capsys, zoom=None):
    review.main([doc, "--variant", "light"] + (["--zoom"] + zoom if zoom else []))
    return capsys.readouterr().out


def test_a_targeted_pass_renders_only_the_pages_it_was_given(guide_pdf,
                                                             fixture_library,
                                                             capsys):
    out = targeted(GUIDE, capsys, zoom=["1", "3"])
    rendered = [line.rsplit("/", 1)[-1] for line in out.splitlines()
                if "page-" in line]
    assert rendered == ["page-01.png", "page-03.png"]
    assert "sheet:" not in out


def test_a_targeted_pass_still_checks_the_whole_document(guide_pdf,
                                                         fixture_library, capsys):
    # A fix on one page reflows the ones after it, so the checks cover the
    # document even when the look does not: here a finding on a page the pass
    # was never given.
    out = targeted(GUIDE, capsys, zoom=["1"])
    assert "checks:" in out
    reported = {line.split("—")[0].strip() for line in out.splitlines()
                if line.startswith("  p.")}
    assert reported - {"p.1"}, out


def test_a_pass_given_no_pages_reads_every_sheet(guide_pdf, fixture_library,
                                                 capsys):
    out = targeted(GUIDE, capsys)
    assert "sheet:" in out and "checks:" in out
    assert "page-" not in out


# --------------------------------------------------------------------------
# Text printed on top of text — what a hand-placed figure label does
# --------------------------------------------------------------------------
COLLISION = """
<svg viewBox="0 0 200 100" width="160mm" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="50" font-size="9">XR2000</text>
  <text x="22" y="52" font-size="9">VCC</text>
</svg>
"""
APART = """
<svg viewBox="0 0 200 100" width="160mm" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="30" font-size="9">XR2000</text>
  <text x="120" y="80" font-size="9">VCC</text>
</svg>
"""


def test_two_labels_on_top_of_each_other_are_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(COLLISION))
    found = [f for f in review.checks(pdf) if f.kind == "overlapping-text"]
    assert len(found) == 1, [str(f) for f in review.checks(pdf)]
    assert "XR2000" in str(found[0]) and "VCC" in str(found[0])


def test_two_labels_apart_are_not_reported(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(APART))
    assert not [f for f in review.checks(pdf) if f.kind == "overlapping-text"]


def test_running_prose_never_reads_as_a_collision(tmp_path):
    # Consecutive spans of one line touch, and a justified paragraph has many.
    # A check that cried wolf here would cost more than the defect it names.
    pdf = make_pdf(tmp_path, cover_and_body(PROSE * 3))
    assert not [f for f in review.checks(pdf) if f.kind == "overlapping-text"]


# --------------------------------------------------------------------------
# A figure's own labels are checked like any other text
# --------------------------------------------------------------------------
# An SVG is inlined into the page, so its text lands in the PDF's text layer.
# The printed size is therefore *measured* rather than computed from the
# viewBox and the placed width, and a glyph the art direction has not got is
# named by the same check that names one in a paragraph. These two pin that,
# because the roadmap that asked for them was written from a session that ran
# before `review.py` had any of these checks.
TINY_LABEL = """
<svg viewBox="0 0 400 100" width="160mm" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="50" font-size="4">R21 10 kΩ</text>
</svg>
"""
GLYPH_LABEL = """
<svg viewBox="0 0 400 100" width="160mm" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="50" font-size="20" font-family="Inter">≈ 3 mA</text>
</svg>
"""


def test_a_label_printed_too_small_is_named_by_tiny_text(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(TINY_LABEL))
    found = [f for f in review.checks(pdf) if f.kind == "tiny-text"]
    assert found and "R21" in str(found[0]), [str(f) for f in review.checks(pdf)]


def test_a_label_in_a_glyph_the_fonts_have_not_got_is_named_by_font(tmp_path):
    pdf = make_pdf(tmp_path, cover_and_body(GLYPH_LABEL))
    found = [f for f in review.checks(pdf, fonts={"Inter"}) if f.kind == "font"]
    assert any("≈" in str(f) for f in found), [str(f) for f in found]
