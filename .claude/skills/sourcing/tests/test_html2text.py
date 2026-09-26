"""html2text.py: readable text rather than a slab, Discourse's JSON first."""
import gzip
import json

import html2text

THREAD = b"""<html><head><style>p { color: red }</style>
<script>var tracker = "do not keep me";</script></head><body>
<!-- the forum's banner -->
<div class="post">First message<br>second line</div>
<div class="post"><p>Reply one</p><p>Reply &amp; two &lt;b&gt;</p></div>
<table><tr><td>A37</td><td>B188</td></tr></table>
</body></html>"""

DISCOURSE = {
    "title": "The machine won't start",
    "post_stream": {"posts": [
        {"username": "member42", "created_at": "2019-03-02T10:11:12Z",
         "cooked": "<p>Check <b>the fuse</b> first.</p>"},
        {"username": "member7", "created_at": "2019-03-04T08:00:00Z",
         "cooked": "<p>It was the pump &amp; the fuse.</p>"},
    ]},
}


def test_scripts_and_styles_go_before_the_tags(tmp_path, capsys):
    """Stripped after the tags, their content would surface in the text."""
    (tmp_path / "t.html").write_bytes(THREAD)
    assert html2text.main([str(tmp_path / "t.html")]) == 0
    out = capsys.readouterr().out
    assert "tracker" not in out and "color" not in out and "banner" not in out


def test_line_breaks_are_placed_before_stripping(tmp_path, capsys):
    """Otherwise the messages run together into one unreadable slab."""
    (tmp_path / "t.html").write_bytes(THREAD)
    html2text.main([str(tmp_path / "t.html")])
    lines = capsys.readouterr().out.splitlines()
    assert "First message" in lines and "second line" in lines
    assert "Reply one" in lines


def test_entities_are_unescaped_after_stripping(tmp_path, capsys):
    """An escaped `<b>` is text: unescaped first, it would be stripped as a tag."""
    (tmp_path / "t.html").write_bytes(THREAD)
    html2text.main([str(tmp_path / "t.html")])
    assert "Reply & two <b>" in capsys.readouterr().out


def test_a_badly_declared_old_forum_page_does_not_crash(tmp_path, capsys):
    (tmp_path / "old.html").write_bytes("<p>Réparé : ça marche</p>".encode("latin-1"))
    assert html2text.main([str(tmp_path / "old.html")]) == 0
    assert "marche" in capsys.readouterr().out


def test_a_gzipped_piece_is_read_as_it_is_archived(tmp_path, capsys):
    (tmp_path / "t.html.gz").write_bytes(gzip.compress(THREAD))
    assert html2text.main([str(tmp_path / "t.html.gz")]) == 0
    assert "Reply one" in capsys.readouterr().out


def test_a_discourse_url_goes_through_its_json_first(web, capsys):
    """The HTML pages of the same site answered 403; the .json did not."""
    web.add("/t/wont-start/1499", "<p>Forbidden</p>", status=403)
    web.add("/t/wont-start/1499.json", json.dumps(DISCOURSE),
            content_type="application/json")
    assert html2text.main([web.url("/t/wont-start/1499")]) == 0
    out = capsys.readouterr().out
    assert "member42" in out and "2019-03-02" in out and "Check the fuse first." in out
    assert "It was the pump & the fuse." in out


def test_a_discourse_json_file_is_read_as_posts(tmp_path, capsys):
    (tmp_path / "thread.json").write_text(json.dumps(DISCOURSE))
    assert html2text.main([str(tmp_path / "thread.json")]) == 0
    assert "member7" in capsys.readouterr().out


def test_a_plain_url_is_stripped(web, capsys):
    assert html2text.main([web.add("/viewtopic.php", THREAD)]) == 0
    assert "Reply one" in capsys.readouterr().out


def test_the_transcription_carries_its_provenance_header(tmp_path):
    (tmp_path / "t.html").write_bytes(THREAD)
    out = tmp_path / "threads" / "t12345.md"
    assert html2text.main([str(tmp_path / "t.html"), "-o", str(out),
                           "--url", "https://www.forum.example.org/viewtopic.php?t=12345",
                           "--archive", "https://web.archive.org/web/20251115085815/x",
                           "--conditions", "the forum answered HTTP 500 on every page"]) == 0
    text = out.read_text(encoding="utf-8")
    head = text.split("---")[1]
    assert "url: https://www.forum.example.org/viewtopic.php?t=12345" in head
    assert "archive: https://web.archive.org/web/20251115085815/x" in head
    assert "retrieved:" in head
    assert "the forum answered HTTP 500" in head
    assert "Reply one" in text.split("---", 2)[2]


def test_a_page_with_no_text_fails_loudly(tmp_path, capsys):
    (tmp_path / "t.html").write_bytes(b"<html><script>x()</script><div> </div></html>")
    out = tmp_path / "t.md"
    assert html2text.main([str(tmp_path / "t.html"), "-o", str(out)]) == 1
    assert "no text" in capsys.readouterr().err
    assert not out.exists()


def test_a_discourse_thread_with_no_post_fails_loudly(tmp_path, capsys):
    (tmp_path / "thread.json").write_text(json.dumps({"post_stream": {"posts": []}}))
    assert html2text.main([str(tmp_path / "thread.json")]) == 1
    assert "0 post" in capsys.readouterr().err


def test_a_url_answering_an_error_fails_with_its_probe_line(web, capsys):
    assert html2text.main([web.add("/forum", THREAD, status=500)]) == 1
    assert "http=500" in capsys.readouterr().err
