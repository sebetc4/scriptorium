"""pdf_find.py and pdf_render.py: locate a term, then read the page as an image."""
import pytest
from PIL import Image
from weasyprint import HTML

import pdf_find
import pdf_render


@pytest.fixture(scope="module")
def manuals(tmp_path_factory):
    """Two manuals. The second one's page 2 is a scan: an image, no text layer."""
    d = tmp_path_factory.mktemp("manuals")
    Image.new("RGB", (400, 300), "gray").save(d / "scan.png")
    HTML(string="<p>Parts list</p><p style='break-before:page'>A1 XR 6302 filter pump</p>"
         ).write_pdf(d / "manual-a.pdf")
    HTML(string="<p>Q12 XR6302</p><p style='break-before:page'><img src='scan.png'></p>",
         base_url=str(d) + "/").write_pdf(d / "manual-b.pdf")
    return d


def test_find_names_the_pages_carrying_the_term_in_each_manual(manuals, capsys):
    assert pdf_find.main(["XR6302", str(manuals / "manual-a.pdf"),
                          str(manuals / "manual-b.pdf")]) == 0
    out = capsys.readouterr().out
    assert "manual-a.pdf" in out and "page(s) 2" in out
    assert "manual-b.pdf" in out and "page(s) 1" in out


def test_find_ignores_case_and_spacing_inside_the_term(manuals, capsys):
    """The manuals wrote both XR6302 and XR 6302."""
    assert pdf_find.main(["xr6302", str(manuals / "manual-a.pdf")]) == 0


def test_find_reports_the_pages_with_no_text_layer(manuals, capsys):
    pdf_find.main(["XR6302", str(manuals / "manual-b.pdf")])
    out = capsys.readouterr().out
    assert "no text layer" in out and "2" in out.split("no text layer")[1]


def test_find_accepts_a_folder_of_pdfs(manuals, capsys):
    assert pdf_find.main(["XR6302", str(manuals)]) == 0
    out = capsys.readouterr().out
    assert "manual-a.pdf" in out and "manual-b.pdf" in out


def test_a_term_found_nowhere_fails_loudly_and_points_at_the_scans(manuals, capsys):
    assert pdf_find.main(["K-8520", str(manuals / "manual-b.pdf")]) == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
    assert "no text layer" in captured.out       # where it may still be


def test_find_without_any_pdf_fails_loudly(tmp_path, capsys):
    assert pdf_find.main(["XR6302", str(tmp_path)]) == 1
    assert "no PDF" in capsys.readouterr().err


def test_render_writes_the_page_at_its_scale(manuals, tmp_path):
    out = tmp_path / "p2.png"
    assert pdf_render.main([str(manuals / "manual-a.pdf"), "2", "--scale", "3", "-o", str(out)]) == 0
    one = pdf_render.pdfpage.render_page(manuals / "manual-a.pdf", 1, scale=1)
    assert abs(Image.open(out).width - 3 * one.width) <= 3


def test_render_then_crop_in_one_step(manuals, tmp_path):
    out = tmp_path / "detail.png"
    assert pdf_render.main([str(manuals / "manual-a.pdf"), "2", "--scale", "2",
                            "--region", "0,0,0.5,0.25", "-o", str(out)]) == 0
    one = pdf_render.pdfpage.render_page(manuals / "manual-a.pdf", 1, scale=2)
    assert abs(Image.open(out).width - one.width / 2) <= 2


def test_render_refuses_a_page_that_does_not_exist(manuals, tmp_path, capsys):
    assert pdf_render.main([str(manuals / "manual-a.pdf"), "9", "-o", str(tmp_path / "x.png")]) == 1
    assert "has 2" in capsys.readouterr().err


def test_render_refuses_what_is_not_a_pdf(tmp_path, capsys):
    fake = tmp_path / "notice.pdf"
    fake.write_bytes(b"<!DOCTYPE html><title>Create an account</title>")
    assert pdf_render.main([str(fake), "1", "-o", str(tmp_path / "x.png")]) == 1
    assert "text/html" in capsys.readouterr().err
