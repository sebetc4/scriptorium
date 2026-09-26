"""archive_images.py: provenance at collection time, never afterwards."""
import hashlib
import json

from PIL import Image

import archive_images


def photos(folder, sizes):
    folder.mkdir(parents=True, exist_ok=True)
    for name, size in sizes.items():
        im = Image.effect_noise(size, 60).convert("RGB")
        if name.endswith(".png"):
            im.save(folder / name)
        else:
            im.save(folder / name, quality=98)
    return folder


def manifest(dest):
    return {e["file"]: e for e in json.loads((dest / "manifest.json").read_text())}


def test_images_are_recompressed_under_a_long_side_cap(tmp_path):
    src = photos(tmp_path / "raw", {"board.jpg": (5312, 2988)})
    dest = tmp_path / "images"
    assert archive_images.main([str(src), "--dest", str(dest)]) == 0
    stored = Image.open(dest / "board.jpg")
    assert max(stored.size) == archive_images.MAX_SIDE
    entry = manifest(dest)["board.jpg"]
    assert entry["original_size"] == [5312, 2988]
    assert entry["stored_size"] == list(stored.size)


def test_the_manifest_carries_the_original_digest(tmp_path):
    """The digest proves the piece was not altered: taken before recompression."""
    src = photos(tmp_path / "raw", {"board.jpg": (1200, 800)})
    dest = tmp_path / "images"
    archive_images.main([str(src), "--dest", str(dest)])
    entry = manifest(dest)["board.jpg"]
    assert entry["sha256_original"] == hashlib.sha256((src / "board.jpg").read_bytes()).hexdigest()
    assert entry["bytes"] == (dest / "board.jpg").stat().st_size


def test_a_decisive_piece_keeps_its_full_size(tmp_path):
    src = photos(tmp_path / "raw", {"detail.jpg": (4200, 2400), "other.jpg": (4200, 2400)})
    dest = tmp_path / "images"
    archive_images.main([str(src), "--dest", str(dest), "--full", "detail.jpg"])
    assert Image.open(dest / "detail.jpg").size == (4200, 2400)
    assert max(Image.open(dest / "other.jpg").size) == archive_images.MAX_SIDE


def test_a_png_stays_a_png(tmp_path):
    src = photos(tmp_path / "raw", {"diagram.png": (600, 400)})
    dest = tmp_path / "images"
    archive_images.main([str(src), "--dest", str(dest)])
    assert Image.open(dest / "diagram.png").format == "PNG"


def test_a_plan_names_places_and_captions_each_piece(tmp_path):
    src = photos(tmp_path / "raw", {"Ab3dE5f.jpeg": (900, 600)})
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"diagram-redrawn.jpg": {
        "source": "raw/Ab3dE5f.jpeg", "origin": "https://imgur.com/a/Xy7Kq",
        "caption": "The diagram, redrawn by hand by a forum member"}}))
    dest = tmp_path / "images"
    assert archive_images.main(["--plan", str(plan), "--dest", str(dest)]) == 0
    entry = manifest(dest)["diagram-redrawn.jpg"]
    assert entry["origin"] == "https://imgur.com/a/Xy7Kq"
    assert entry["caption"].startswith("The diagram")


def test_a_second_run_updates_the_manifest_instead_of_losing_it(tmp_path):
    dest = tmp_path / "images"
    archive_images.main([str(photos(tmp_path / "a", {"one.jpg": (300, 200)})), "--dest", str(dest)])
    archive_images.main([str(photos(tmp_path / "b", {"two.jpg": (300, 200)})), "--dest", str(dest)])
    assert set(manifest(dest)) == {"one.jpg", "two.jpg"}


def test_a_missing_plan_source_fails_loudly(tmp_path, capsys):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"x.jpg": {"source": "raw/gone.jpg", "origin": "", "caption": ""}}))
    assert archive_images.main(["--plan", str(plan), "--dest", str(tmp_path / "images")]) == 1
    assert "gone.jpg" in capsys.readouterr().err


def test_an_unreadable_image_is_named_and_the_run_fails(tmp_path, capsys):
    src = photos(tmp_path / "raw", {"good.jpg": (300, 200)})
    (src / "wall.jpg").write_bytes(b"<!DOCTYPE html><title>Sign in</title>")
    dest = tmp_path / "images"
    assert archive_images.main([str(src), "--dest", str(dest)]) == 1
    assert "wall.jpg" in capsys.readouterr().err
    assert "good.jpg" in manifest(dest)          # the rest is still archived


def test_a_folder_with_no_image_fails_loudly(tmp_path, capsys):
    (tmp_path / "raw").mkdir()
    assert archive_images.main([str(tmp_path / "raw"), "--dest", str(tmp_path / "images")]) == 1
    assert "no image" in capsys.readouterr().err
