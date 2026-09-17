"""forum_index.py: title → topic id, rebuilt from archived listings.

phpBB message permalinks (`p=`) are almost never archived; topic pages (`t=`)
almost always are. With the forum dead, the only way from a title to its `t=`
is the forum's own listings, as the Wayback Machine kept them.
"""
import urllib.parse

import pytest

import forum_index
import wayback

LISTING = "korgforums.com/forum/phpBB3/viewforum.php?f=48"


def phpbb_listing(topics):
    rows = "".join(f'<a href="./viewtopic.php?t={t}&amp;sid=0123abcd" class="topictitle">{title}</a>'
                   for t, title in topics)
    return f"<html><body><ul>{rows}</ul>{'<p>forum chrome</p>' * 40}</body></html>"


@pytest.fixture
def forum(web, monkeypatch):
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    monkeypatch.setattr(wayback, "ARCHIVE", web.url("/web"))
    captures = {
        "http://www.korgforums.com/forum/phpBB3/viewforum.php?f=48": ("20150101000000",
            phpbb_listing([(94641, "Guts of a Virgin"), (105619, "Electribe 2/Sampler service manual")])),
        "http://www.korgforums.com/forum/phpBB3/viewforum.php?f=48&start=50": ("20160101000000",
            phpbb_listing([(94641, "Guts of a Virgin"), (117977, "E2 won&#39;t power on")])),
        # another sub-forum sharing the prefix — f=480 must not be taken for f=48
        "http://www.korgforums.com/forum/phpBB3/viewforum.php?f=480": ("20150101000000",
            phpbb_listing([(1, "Unrelated")])),
    }

    def cdx(path):
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
        prefix = q["url"][0].rstrip("*")
        lines = [f"{ts} {u} 200" for u, (ts, _) in sorted(captures.items())
                 if u.split("://")[1].removeprefix("www.").startswith(prefix)]
        return 200, "text/plain", "\n".join(lines) + "\n"

    def snapshot(path):
        ts, original = path[len("/web/"):].split("/", 1)
        ts = ts.removesuffix("id_")
        for u, (stamp, body) in captures.items():
            if (stamp, u) == (ts, original):
                return 200, "text/html", body
        return 404, "text/html", "<!DOCTYPE html><title>404</title>"

    web.handle("/cdx", cdx)
    web.handle("/web/", snapshot)
    return captures


def test_the_index_maps_every_title_to_its_topic_id(forum, tmp_path, capsys):
    out = tmp_path / "topics.tsv"
    assert forum_index.main([LISTING, "-o", str(out)]) == 0
    rows = dict(line.split("\t") for line in out.read_text().splitlines())
    assert rows == {"94641": "Guts of a Virgin",
                    "105619": "Electribe 2/Sampler service manual",
                    "117977": "E2 won't power on"}


def test_a_neighbouring_forum_id_is_not_taken_for_the_one_asked(forum, tmp_path):
    out = tmp_path / "topics.tsv"
    forum_index.main([LISTING, "-o", str(out)])
    assert "Unrelated" not in out.read_text()


def test_grep_prints_only_the_matching_titles(forum, capsys):
    assert forum_index.main([LISTING, "--grep", "guts"]) == 0
    out = capsys.readouterr().out
    assert "94641\tGuts of a Virgin" in out
    assert "105619" not in out


def test_a_grep_matching_nothing_fails_loudly(forum, capsys):
    assert forum_index.main([LISTING, "--grep", "microkorg"]) == 1
    assert "no title matches" in capsys.readouterr().err


def test_the_listings_can_be_kept_as_pieces(forum, tmp_path):
    pieces = tmp_path / "raw" / "f48"
    assert forum_index.main([LISTING, "--dir", str(pieces)]) == 0
    assert len(list(pieces.iterdir())) == 2


def test_listings_where_no_topic_is_recognised_fail_loudly(web, monkeypatch, capsys):
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    monkeypatch.setattr(wayback, "ARCHIVE", web.url("/web"))
    web.handle("/cdx", lambda p: (200, "text/plain",
               "20150101000000 http://forum.example/viewforum.php?f=2 200\n"))
    web.handle("/web/", lambda p: (200, "text/html", "<html><body>Board offline</body></html>"))
    assert forum_index.main(["forum.example/viewforum.php?f=2"]) == 1
    assert "no topic" in capsys.readouterr().err


def test_a_forum_with_no_archived_listing_fails_loudly(web, monkeypatch, capsys):
    monkeypatch.setattr(wayback, "CDX", web.url("/cdx"))
    web.handle("/cdx", lambda p: (200, "text/plain", ""))
    assert forum_index.main(["forum.example/viewforum.php?f=2"]) == 1
    assert "no capture" in capsys.readouterr().err
