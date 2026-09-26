"""core/net.py: retrieval that fails out loud.

Each test is one of the silent failures a real investigation hit, made
reproducible on a local server.
"""
import socket

import pytest

from core import net

PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n"
HTML = b"<!DOCTYPE html><html lang='en'><body><p>Sign up to download</p></body></html>"
PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 32


def test_a_filtering_host_answers_the_browser_user_agent(web):
    url = web.add("/filtered", "<p>ok</p>", browsers_only=True)
    assert net.get(url).status == 200


def test_the_effective_url_reveals_a_silent_redirect(web):
    web.add("/brands", "<p>an index of brands</p>")
    url = web.redirect("/parts", "/brands")
    response = net.get(url)
    assert response.status == 200
    assert response.effective_url == web.url("/brands")


def test_the_probe_line_says_status_size_type_and_effective_url(web):
    url = web.add("/page", "<p>ok</p>")
    line = net.get(url).line()
    assert line == (f"http=200 size=9 type=text/html; charset=utf-8 "
                    f"eff={url}")


def test_an_http_error_is_answered_rather_than_raised(web):
    url = web.add("/forum", "<h1>Internal error</h1>", status=500)
    response = net.get(url)
    assert response.status == 500
    assert response.body == b"<h1>Internal error</h1>"


@pytest.mark.parametrize("body, mime", [
    (PDF, "application/pdf"),
    (HTML, "text/html"),
    (b"  \n<html><body>x</body></html>", "text/html"),
    (b"\xef\xbb\xbf<!DOCTYPE html><html></html>", "text/html"),
    (b"<!-- generated -->\n<!DOCTYPE html><html></html>", "text/html"),
    (PNG, "image/png"),
    (b"\xff\xd8\xff\xe0" + b"\0" * 16, "image/jpeg"),
    (b"GIF89a" + b"\0" * 16, "image/gif"),
    (b"RIFF\0\0\0\0WEBPVP8 ", "image/webp"),
    (b"<?xml version='1.0'?><svg xmlns='http://www.w3.org/2000/svg'/>", "image/svg+xml"),
    (b"\x00\x01\x02\x03", "application/octet-stream"),
])
def test_sniff_reads_the_bytes_not_the_name(body, mime):
    assert net.sniff(body) == mime


def test_a_pdf_url_answering_html_is_the_sniffed_type(web):
    """HTTP 200, a `.pdf` name, a PDF content type — and a signup wall."""
    url = web.add("/notice.pdf", HTML, content_type="application/pdf")
    response = net.get(url)
    assert response.status == 200
    assert response.mime == "text/html"


def test_an_unverifiable_certificate_falls_back_and_says_so(tls_web):
    url = tls_web.add("/forum", "<p>still here</p>")
    response = net.get(url)
    assert response.status == 200
    assert response.tls_verified is False
    assert "tls=unverified" in response.line()


def test_a_verified_connection_says_nothing_about_tls(web):
    url = web.add("/page", "<p>ok</p>")
    response = net.get(url)
    assert response.tls_verified is True
    assert "tls=" not in response.line()


def test_an_unreachable_host_raises(web):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with pytest.raises(net.NetError):
        net.get(f"http://127.0.0.1:{port}/", timeout=2)


def test_a_body_past_the_limit_raises(web):
    url = web.add("/big", b"x" * 2000, content_type="application/octet-stream")
    with pytest.raises(net.NetError, match="too large"):
        net.get(url, max_bytes=1000)
