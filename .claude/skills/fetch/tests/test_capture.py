"""One URL in, one document out — and every silent failure made loud.

Each capture runs end to end against a local server, into a library that lives
in a temporary directory: nothing touches the network or the real library/.
"""
import gzip
import json
import os

import pytest

import fetch

PARAGRAPH = ("A dough starts to rise past a certain warmth, and a few "
             "degrees beyond it are enough to triple the speed at which the "
             "yeast works through the whole loaf. ")
ARTICLE = f"""<!DOCTYPE html>
<html lang="en"><head><title>Baking bread</title></head>
<body>
<nav><a href="/">Home</a> <a href="/about">About</a></nav>
<article>
<h1>Baking bread</h1>
<p>{PARAGRAPH * 4}</p>
<h2>The yeast</h2>
<p>{PARAGRAPH * 4}</p>
</article>
</body></html>"""
SIGNUP_WALL = ("<!DOCTYPE html><html lang='en'><body><article><h1>Create an "
               f"account</h1><p>{PARAGRAPH * 3}</p></article></body></html>")
PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


@pytest.fixture
def library(tmp_path, monkeypatch):
    """A throwaway library, wired into the script in place of the real one."""
    monkeypatch.setattr(fetch, "ROOT", tmp_path)
    monkeypatch.setattr(fetch, "LIBRARY", tmp_path / "library")
    monkeypatch.setattr(fetch, "IMAGE_PAUSE", 0)
    return tmp_path / "library"


def test_a_page_is_captured_with_its_provenance(web, library):
    url = web.add("/bread", ARTICLE)
    assert fetch.main([url, "watch/bread"]) == 0

    dest = library / "watch" / "bread"
    assert "triple the speed" in (dest / "document" / "index.md").read_text(encoding="utf-8")
    received = gzip.decompress((dest / "sources" / "page.html.gz").read_bytes())
    assert received == ARTICLE.encode("utf-8")
    meta = json.loads((dest / "study" / "meta.json").read_text(encoding="utf-8"))
    assert meta["url"] == url
    assert meta["effective_url"] == url
    assert meta["http_status"] == 200
    assert meta["content_type"] == "text/html; charset=utf-8"
    assert meta["tls_verified"] is True


def test_the_received_page_is_kept_as_received(web, library):
    """Not decoded and re-encoded: a Latin-1 page keeps its own bytes."""
    latin1 = ARTICLE.replace("Baking bread", "Cuisson d’un pain").replace("’", "'").replace(
        "<title>", "<meta charset='iso-8859-1'><title>").replace("pain</h1>", "pain à éviter</h1>")
    body = latin1.encode("iso-8859-1")
    url = web.add("/bread", body, content_type="text/html; charset=iso-8859-1")
    assert fetch.main([url, "watch/bread"]) == 0
    dest = library / "watch" / "bread"
    assert gzip.decompress((dest / "sources" / "page.html.gz").read_bytes()) == body
    assert "à éviter" in (dest / "document" / "index.md").read_text(encoding="utf-8")


def test_the_probe_line_is_printed(web, library, capsys):
    url = web.add("/bread", ARTICLE)
    fetch.main([url, "watch/bread"])
    assert f"http=200 size={len(ARTICLE.encode())} " in capsys.readouterr().out


def test_a_silent_redirect_is_reported_and_recorded(web, library, capsys):
    web.add("/index", ARTICLE)
    url = web.redirect("/bread", "/index")
    assert fetch.main([url, "watch/bread"]) == 0
    assert "redirected" in capsys.readouterr().out
    meta = json.loads((library / "watch" / "bread" / "study" / "meta.json")
                      .read_text(encoding="utf-8"))
    assert meta["effective_url"] == web.url("/index")


def test_a_pdf_url_answering_html_is_refused(web, library, capsys):
    url = web.add("/notice.pdf", SIGNUP_WALL, content_type="application/pdf")
    assert fetch.main([url, "watch/notice"]) == 1
    err = capsys.readouterr().err
    assert "text/html" in err and ".pdf" in err
    assert not (library / "watch" / "notice").exists()


def test_a_real_pdf_is_sent_to_the_import(web, library, capsys):
    url = web.add("/manual", PDF, content_type="application/pdf")
    assert fetch.main([url, "watch/manual"]) == 1
    assert "make import" in capsys.readouterr().err
    assert not (library / "watch" / "manual").exists()


def test_an_http_error_is_refused_with_its_probe_line(web, library, capsys):
    url = web.add("/forum", ARTICLE, status=500)
    assert fetch.main([url, "watch/forum"]) == 1
    assert "http=500" in capsys.readouterr().err
    assert not (library / "watch" / "forum").exists()


def test_an_extraction_with_no_text_writes_nothing(web, library, capsys):
    """Images only: the extraction is not empty, but there is nothing to read."""
    png = web.add("/a.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")
    page = ("<!DOCTYPE html><html lang='en'><body><article>"
            + f"<p><img src='{png}' alt=''></p>" * 3
            + "</article></body></html>")
    url = web.add("/gallery", page)
    assert fetch.main([url, "watch/gallery"]) == 1
    assert "no text" in capsys.readouterr().err
    assert not (library / "watch" / "gallery").exists()


def test_an_unverifiable_certificate_is_captured_and_said(tls_web, library, capsys):
    url = tls_web.add("/bread", ARTICLE)
    assert fetch.main([url, "watch/bread"]) == 0
    assert "certificate" in capsys.readouterr().out
    meta = json.loads((library / "watch" / "bread" / "study" / "meta.json")
                      .read_text(encoding="utf-8"))
    assert meta["tls_verified"] is False


def test_a_host_filtering_user_agents_is_captured(web, library):
    url = web.add("/bread", ARTICLE, browsers_only=True)
    assert fetch.main([url, "watch/bread"]) == 0


def test_an_image_answering_html_is_reported_as_such(web, library):
    wall = web.add("/figure.jpg", SIGNUP_WALL, content_type="image/jpeg")
    page = ARTICLE.replace("<h2>", f"<p><img src='{wall}' alt='Figure'></p><h2>")
    url = web.add("/bread", page)
    assert fetch.main([url, "watch/bread"]) == 0
    meta = json.loads((library / "watch" / "bread" / "study" / "meta.json")
                      .read_text(encoding="utf-8"))
    assert any("text/html" in f for f in meta["image_failures"]), meta["image_failures"]


def test_the_capture_ignores_the_working_directory(web, library, tmp_path):
    """The working directory is reset between tool calls: a relative write
    lands elsewhere, silently. Everything is resolved from LIBRARY."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    url = web.add("/bread", ARTICLE)
    cwd = os.getcwd()
    os.chdir(elsewhere)
    try:
        assert fetch.main([url, "watch/bread"]) == 0
    finally:
        os.chdir(cwd)
    assert (library / "watch" / "bread" / "document" / "index.md").is_file()
    assert list(elsewhere.iterdir()) == []


def test_the_page_language_is_recorded_for_the_translation(web, library):
    """The language is stated once: `translate` reads it here instead of asking."""
    url = web.add("/bread", ARTICLE.replace('<html lang="en">', "<html>"))
    assert fetch.main([url, "watch/bread", "--lang", "fr"]) == 0
    meta = json.loads((library / "watch" / "bread" / "study" / "meta.json").read_text(encoding="utf-8"))
    assert meta["source_language"] == "en"


def test_a_capture_is_put_on_the_map(web, library, capsys):
    """The entry's manifest and its topic's are written, and what is left to
    name is printed for the catalogue skill."""
    assert fetch.main([web.add("/bread", ARTICLE), "watch/bread"]) == 0
    assert (library / "watch" / "manifest.yaml").is_file()
    assert (library / "watch" / "bread" / "manifest.yaml").is_file()
    out = capsys.readouterr().out
    assert "map: watch/bread synced — to name: watch/bread, watch" in out
    assert "to describe: sources/page.html.gz" in out
