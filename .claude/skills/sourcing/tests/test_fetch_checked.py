"""fetch_checked.py: a mirror chain that stops at the first real file."""
import fetch_checked

PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
WALL = b"<!DOCTYPE html><html><body><h1>Create an account to download</h1></body></html>"


def test_the_chain_stops_at_the_first_real_pdf(web, tmp_path, capsys):
    """The Sanyo datasheet took four attempts: 403, HTML in 200, then a mirror."""
    urls = [web.add("/aggregator/cph6302.pdf", WALL, status=403),
            web.add("/mouser/CPH6302.pdf", WALL, content_type="application/pdf"),
            web.add("/obscure-mirror/CPH6302.pdf", PDF, content_type="application/pdf"),
            web.add("/never-asked.pdf", PDF, content_type="application/pdf")]
    out = tmp_path / "cph6302.pdf"
    assert fetch_checked.main([*urls, "-o", str(out)]) == 0
    assert out.read_bytes() == PDF
    printed = capsys.readouterr().out
    assert "http=403" in printed and "text/html" in printed
    assert not any(p == "/never-asked.pdf" for p in web.paths)


def test_the_expected_type_comes_from_the_output_name(web, tmp_path):
    png = b"\x89PNG\r\n\x1a\n" + b"\0" * 64
    url = web.add("/figure", png, content_type="application/octet-stream")
    assert fetch_checked.main([url, "-o", str(tmp_path / "figure.png")]) == 0


def test_an_explicit_type_overrides_the_name(web, tmp_path):
    url = web.add("/doc", PDF, content_type="application/pdf")
    assert fetch_checked.main([url, "--expect", "application/pdf",
                               "-o", str(tmp_path / "doc.bin")]) == 0


def test_an_output_name_that_says_no_type_needs_expect(web, tmp_path, capsys):
    url = web.add("/doc", PDF)
    assert fetch_checked.main([url, "-o", str(tmp_path / "doc.bin")]) == 1
    assert "--expect" in capsys.readouterr().err


def test_when_no_mirror_serves_the_file_nothing_is_written(web, tmp_path, capsys):
    urls = [web.add("/a.pdf", WALL, content_type="application/pdf"),
            web.add("/b.pdf", WALL, status=500)]
    out = tmp_path / "ds.pdf"
    assert fetch_checked.main([*urls, "-o", str(out)]) == 1
    assert "no URL served application/pdf" in capsys.readouterr().err
    assert not out.exists()
    assert list(tmp_path.iterdir()) == []


def test_probe_prints_one_line_per_url_and_writes_nothing(web, tmp_path, capsys):
    urls = [web.add("/forum/", WALL, status=500), web.add("/manual.pdf", PDF)]
    assert fetch_checked.main(["--probe", *urls]) == 0
    lines = [l for l in capsys.readouterr().out.splitlines() if "http=" in l]
    assert len(lines) == 2
    assert "http=500" in lines[0] and "application/pdf" in lines[1]
    assert list(tmp_path.iterdir()) == []


def test_the_output_is_printed_as_an_absolute_path(web, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    url = web.add("/m.pdf", PDF)
    assert fetch_checked.main([url, "-o", "datasheets/m.pdf"]) == 0
    assert str(tmp_path / "datasheets" / "m.pdf") in capsys.readouterr().out
