"""imgur_album.py: the whole album through the API, at full resolution."""
import json

import pytest

import imgur_album

JPEG = b"\xff\xd8\xff\xe0" + b"\0" * 200


@pytest.fixture
def imgur(web, monkeypatch):
    """A local stand-in for api.imgur.com and i.imgur.com."""
    monkeypatch.setattr(imgur_album, "API", web.url("/post/v1/albums"))
    monkeypatch.setattr(imgur_album, "IMAGES", web.url("/i"))
    return web


def album(web, ident, media, status=200):
    body = json.dumps({"id": ident, "title": "Fixing the machine", "media": media})
    web.handle(f"/post/v1/albums/{ident}", lambda path: (status, "application/json", body))


MEDIA = [{"id": "VjoMIRY", "ext": "jpeg", "width": 5312, "height": 2988},
         {"id": "t13vxMA", "ext": "jpeg", "width": 4000, "height": 3000}]


def test_the_album_lists_every_image_with_its_size(imgur, capsys):
    album(imgur, "Ab3Cd", MEDIA)
    assert imgur_album.main(["Ab3Cd"]) == 0
    out = capsys.readouterr().out
    assert "VjoMIRY" in out and "5312×2988" in out and "t13vxMA" in out
    assert "client_id=" in imgur.paths[0] and "include=media" in imgur.paths[0]


def test_an_album_url_is_accepted_as_well_as_its_id(imgur):
    album(imgur, "Ab3Cd", MEDIA)
    assert imgur_album.main(["https://imgur.com/a/Ab3Cd"]) == 0


def test_download_fetches_the_originals(imgur, tmp_path):
    album(imgur, "Ab3Cd", MEDIA)
    for m in MEDIA:
        imgur.add(f"/i/{m['id']}.jpeg", JPEG + m["id"].encode(), content_type="image/jpeg")
    dest = tmp_path / "album"
    assert imgur_album.main(["Ab3Cd", "--download", str(dest)]) == 0
    assert sorted(p.name for p in dest.iterdir()) == ["VjoMIRY.jpeg", "t13vxMA.jpeg"]


def test_a_download_that_is_not_an_image_is_refused_and_named(imgur, tmp_path, capsys):
    album(imgur, "Ab3Cd", MEDIA)
    imgur.add("/i/VjoMIRY.jpeg", JPEG, content_type="image/jpeg")
    imgur.add("/i/t13vxMA.jpeg", "<!DOCTYPE html><title>removed</title>", content_type="image/jpeg")
    assert imgur_album.main(["Ab3Cd", "--download", str(tmp_path / "d")]) == 1
    assert "t13vxMA" in capsys.readouterr().err
    assert not (tmp_path / "d" / "t13vxMA.jpeg").exists()


def test_a_refused_client_id_gets_a_clear_message(imgur, capsys):
    album(imgur, "Ab3Cd", [], status=403)
    assert imgur_album.main(["Ab3Cd"]) == 1
    err = capsys.readouterr().err
    assert "client_id" in err and "403" in err


def test_an_album_with_no_media_fails_loudly(imgur, capsys):
    album(imgur, "empty", [])
    assert imgur_album.main(["empty"]) == 1
    assert "no image" in capsys.readouterr().err


@pytest.mark.parametrize("url, original", [
    ("https://i.imgur.com/VjoMIRYh.jpg", "https://i.imgur.com/VjoMIRY.jpg"),
    ("https://i.imgur.com/VjoMIRYm.png", "https://i.imgur.com/VjoMIRY.png"),
    ("https://i.imgur.com/VjoMIRY.jpg", "https://i.imgur.com/VjoMIRY.jpg"),
    ("https://i.imgur.com/abcdh.jpg", "https://i.imgur.com/abcdh.jpg"),   # a 5-char id ending in h
])
def test_the_thumbnail_suffix_is_removed_only_from_an_eight_char_name(url, original):
    """<id>h.jpg is a 40 kB thumbnail; <id>.jpg is the 3 MB original."""
    assert imgur_album.unthumb(url) == original


def test_scan_lists_a_page_s_imgur_images_as_originals_with_context(tmp_path, capsys):
    page = tmp_path / "t23456-full.html"
    page.write_text("<p>Close-up of the AM1802B next to the SD reader</p>"
                    "<img src='https://i.imgur.com/t13vxMAh.jpg'>"
                    "<p>and the other side</p><img src='https://i.imgur.com/AZEavNe.jpg'>")
    assert imgur_album.main(["--scan", str(page)]) == 0
    out = capsys.readouterr().out
    assert "https://i.imgur.com/t13vxMA.jpg" in out
    assert "t13vxMAh" not in out
    assert "AM1802B" in out


def test_scan_of_a_page_without_imgur_links_fails_loudly(tmp_path, capsys):
    page = tmp_path / "p.html"
    page.write_text("<p>no pictures here</p>")
    assert imgur_album.main(["--scan", str(page)]) == 1
    assert "no Imgur image" in capsys.readouterr().err
