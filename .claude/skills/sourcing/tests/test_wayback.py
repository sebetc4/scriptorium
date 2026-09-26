"""wayback.py: what is archived, in batch, and the print view preferred."""
import urllib.parse

import pytest

import wayback

T12345 = "https://www.forum.example.org/phpBB3/viewtopic.php?t=12345"
PRINT_PAGE = "<html><body><h1>Service manual</h1>" + "<p>message</p>" * 12 + "</body></html>"
FULL_PAGE = PRINT_PAGE + "<div>" + "navigation " * 800 + "</div>"


class Archive:
    """A CDX index and its snapshots: {original URL: [timestamps]}."""

    def __init__(self, web, captures, bodies=None):
        self.captures, self.bodies = captures, bodies or {}
        web.handle("/cdx", self.cdx)
        web.handle("/web/", self.snapshot)

    def cdx(self, path):
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
        pattern = q["url"][0]
        exact = not pattern.endswith("*")
        lines = []
        for original, stamps in sorted(self.captures.items()):
            bare = original.split("://", 1)[1].removeprefix("www.")
            wanted = pattern.split("://", 1)[-1].removeprefix("www.").rstrip("*")
            if (bare == wanted) if exact else bare.startswith(wanted):
                lines += [f"{ts} {original} 200" for ts in stamps]
        return 200, "text/plain", "\n".join(lines) + ("\n" if lines else "")

    def snapshot(self, path):
        ts, original = path[len("/web/"):].split("/", 1)
        body = self.bodies.get((ts.removesuffix("id_"), original))
        if body is None:
            return 404, "text/html", "<!DOCTYPE html><title>Not archived</title>"
        return 200, "text/html; charset=utf-8", body


@pytest.fixture
def archive_of(web, monkeypatch):
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    monkeypatch.setattr(wayback, "ARCHIVE", web.url("/web"))
    return lambda captures, bodies=None: Archive(web, captures, bodies)


def test_list_gives_one_archive_url_per_capture(archive_of, capsys):
    archive_of({T12345: ["20251115085815"], T12345 + "&view=print": ["20251115085815"]})
    assert wayback.main(["list", "forum.example.org/phpBB3/viewtopic.php?t=12345*"]) == 0
    out = capsys.readouterr().out
    assert "/web/20251115085815/" + T12345 in out
    assert "view=print" in out


def test_list_with_no_capture_fails_loudly(archive_of, capsys):
    archive_of({})
    assert wayback.main(["list", "forum.example.org/phpBB3/viewtopic.php?p=345678"]) == 1
    assert "no capture" in capsys.readouterr().err


def test_check_reports_each_url_of_a_batch(archive_of, capsys):
    """Two topics out of twelve had no capture: known in five seconds."""
    archive_of({T12345: ["20251115085815", "20240101000000"]})
    missing = "https://www.forum.example.org/phpBB3/viewtopic.php?p=345678"
    assert wayback.main(["check", T12345, missing]) == 0
    out = capsys.readouterr().out.splitlines()
    assert any("2 capture(s)" in l and "t=12345" in l for l in out)
    assert any("no capture" in l and "p=345678" in l for l in out)


def test_check_where_nothing_is_archived_fails_loudly(archive_of, capsys):
    archive_of({})
    assert wayback.main(["check", T12345]) == 1


def test_get_prefers_the_print_view_of_a_phpbb_thread(archive_of, tmp_path, capsys):
    """16 kB of clean text against 91 kB, the whole thread on one page."""
    archive_of({T12345: ["20250827175934"], T12345 + "&view=print": ["20251115085815"]},
               {("20250827175934", T12345): FULL_PAGE,
                ("20251115085815", T12345 + "&view=print"): PRINT_PAGE})
    assert wayback.main(["get", T12345, "--dir", str(tmp_path)]) == 0
    files = list(tmp_path.iterdir())
    assert len(files) == 1 and "print" in files[0].name
    assert files[0].read_text() == PRINT_PAGE


def test_get_both_keeps_the_full_view_for_its_image_links(archive_of, tmp_path):
    """The print view loses the attachment links: a picture thread needs both."""
    archive_of({T12345: ["20250827175934"], T12345 + "&view=print": ["20251115085815"]},
               {("20250827175934", T12345): FULL_PAGE,
                ("20251115085815", T12345 + "&view=print"): PRINT_PAGE})
    assert wayback.main(["get", T12345, "--both", "--dir", str(tmp_path)]) == 0
    assert len(list(tmp_path.iterdir())) == 2


def test_get_takes_the_latest_capture(archive_of, tmp_path):
    page = "https://example.org/documents/"
    archive_of({page: ["20190101000000", "20240101000000"]},
               {("20190101000000", page): "<p>old</p>" * 20,
                ("20240101000000", page): "<p>new</p>" * 20})
    assert wayback.main(["get", page, "--dir", str(tmp_path)]) == 0
    assert "new" in next(tmp_path.iterdir()).read_text()


def test_a_batch_of_identical_sizes_is_flagged_as_error_pages(archive_of, tmp_path, capsys):
    """start=15/30/45 of an archived thread: 4,684 bytes each, one error page."""
    error = "<html><body>" + "x" * 4600 + "</body></html>"
    urls = [f"https://site.example/viewtopic.php?t=23456&start={n}" for n in (15, 30, 45)]
    archive_of({u: ["20251123171429"] for u in urls},
               {("20251123171429", u): error for u in urls})
    assert wayback.main(["get", *urls, "--dir", str(tmp_path)]) == 1
    assert "identical size" in capsys.readouterr().err


def test_get_with_no_capture_writes_nothing_and_fails(archive_of, tmp_path, capsys):
    archive_of({})
    assert wayback.main(["get", T12345, "--dir", str(tmp_path)]) == 1
    assert "no capture" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_a_busy_cdx_index_is_retried(web, monkeypatch, capsys):
    """Live, the index answered 503 on the second request of a batch."""
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    monkeypatch.setattr(wayback, "RETRY_WAITS", (0, 0))
    answers = iter([(503, "text/html", "<p>Service unavailable</p>"),
                    (200, "text/plain", f"20251115085815 {T12345} 200\n")])
    web.handle("/cdx", lambda path: next(answers))
    assert wayback.main(["check", T12345]) == 0
    assert "1 capture(s)" in capsys.readouterr().out


def test_one_url_the_index_keeps_refusing_does_not_sink_the_batch(web, monkeypatch, capsys):
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    monkeypatch.setattr(wayback, "RETRY_WAITS", (0, 0))

    def cdx(path):
        if "p%3D345678" in path:
            return 503, "text/html", "<p>Service unavailable</p>"
        return 200, "text/plain", f"20251115085815 {T12345} 200\n"
    web.handle("/cdx", cdx)
    missing = "https://www.forum.example.org/phpBB3/viewtopic.php?p=345678"
    assert wayback.main(["check", missing, T12345]) == 1
    captured = capsys.readouterr()
    assert "1 capture(s)" in captured.out          # the batch went on
    assert "p=345678" in captured.err and "503" in captured.err


def test_get_asks_for_the_page_as_served_without_the_archive_toolbar(web, archive_of, tmp_path):
    """`<timestamp>id_/` is the original bytes; without it the Wayback Machine
    injects its toolbar, which then opens every transcription."""
    archive_of({T12345 + "&view=print": ["20251115085815"]},
               {("20251115085815", T12345 + "&view=print"): PRINT_PAGE})
    assert wayback.main(["get", T12345, "--dir", str(tmp_path)]) == 0
    assert any(p.startswith("/web/20251115085815id_/") for p in web.paths)
