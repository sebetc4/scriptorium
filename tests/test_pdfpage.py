"""core/pdfpage.py: one page rendered, and each page's text layer read.

The fixture PDF is built by WeasyPrint: page 1 carries text, page 2 carries
only an image — which is what a scanned schematic looks like to a reader of
text layers.
"""
import io

import pytest
from PIL import Image
from weasyprint import HTML

from core import pdfpage


@pytest.fixture(scope="module")
def pdf(tmp_path_factory):
    d = tmp_path_factory.mktemp("pdf")
    Image.new("RGB", (300, 200), "gray").save(d / "scan.png")
    html = ("<style>@page{size:A5;margin:10mm}</style>"
            "<p>Power section: F1 CPH6302, IC20 S-8520.</p>"
            "<p style='break-before:page'><img src='scan.png' style='width:100mm'></p>")
    path = d / "manual.pdf"
    HTML(string=html, base_url=str(d) + "/").write_pdf(path)
    return path


def test_text_gives_one_string_per_page(pdf):
    pages = pdfpage.text(pdf)
    assert len(pages) == 2
    assert "CPH6302" in pages[0]


def test_a_page_with_no_text_layer_reads_as_empty(pdf):
    assert pdfpage.text(pdf)[1].strip() == ""


def test_render_page_renders_that_page_alone(pdf):
    first = pdfpage.render_page(pdf, 0, scale=1)
    second = pdfpage.render_page(pdf, 1, scale=1)
    assert first.size == second.size
    assert first.tobytes() != second.tobytes()


def test_render_page_scales(pdf):
    one = pdfpage.render_page(pdf, 0, scale=1)
    six = pdfpage.render_page(pdf, 0, scale=6)
    assert abs(six.width - 6 * one.width) <= 6


def test_render_page_refuses_a_page_that_does_not_exist(pdf):
    with pytest.raises(IndexError):
        pdfpage.render_page(pdf, 2, scale=1)
