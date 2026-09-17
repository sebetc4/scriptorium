"""crop.py: read a detail, and settle a contradiction between two photos."""
from PIL import Image

import crop


def board(path, size=(2000, 1000), colour="green"):
    im = Image.new("RGB", size, "white")
    im.paste(colour, (0, 0, size[0] // 2, size[1] // 2))
    im.save(path)
    return path


def test_a_region_is_cut_and_enlarged(tmp_path):
    src, out = board(tmp_path / "pcb.jpg"), tmp_path / "detail.png"
    assert crop.main([str(src), "--region", "0,0,0.5,0.5", "--width", "1500", "-o", str(out)]) == 0
    im = Image.open(out)
    assert im.size == (1500, 750)


def test_without_a_width_the_crop_keeps_its_pixels(tmp_path):
    src, out = board(tmp_path / "pcb.jpg"), tmp_path / "detail.png"
    assert crop.main([str(src), "--region", "0.5,0.5,1,1", "-o", str(out)]) == 0
    assert Image.open(out).size == (1000, 500)


def test_compare_lays_the_same_region_of_two_photos_side_by_side(tmp_path):
    """Two photos by two people, cropped alike and normalised to one size."""
    a = board(tmp_path / "a.jpg", (2000, 1000), "green")
    b = board(tmp_path / "b.png", (800, 400), "red")
    out = tmp_path / "cmp.png"
    assert crop.main([str(a), "--compare", str(b), "--region", "0,0,0.5,0.5",
                      "--width", "600", "-o", str(out)]) == 0
    im = Image.open(out)
    assert im.size == (2 * 600 + crop.GAP, 300)
    assert im.getpixel((300, 150))[1] > 100            # left: green
    assert im.getpixel((600 + crop.GAP + 300, 150))[0] > 200   # right: red


def test_compare_needs_a_width_to_normalise(tmp_path, capsys):
    a, b = board(tmp_path / "a.jpg"), board(tmp_path / "b.jpg", (800, 400))
    assert crop.main([str(a), "--compare", str(b), "--region", "0,0,0.5,0.5",
                      "-o", str(tmp_path / "c.png")]) == 1
    assert "--width" in capsys.readouterr().err


def test_a_region_in_pixels_is_refused(tmp_path, capsys):
    src = board(tmp_path / "pcb.jpg")
    assert crop.main([str(src), "--region", "100,50,900,600", "-o", str(tmp_path / "d.png")]) == 1
    assert "not pixels" in capsys.readouterr().err
    assert not (tmp_path / "d.png").exists()


def test_a_region_holding_no_pixel_fails_loudly(tmp_path, capsys):
    src = board(tmp_path / "tiny.png", (20, 10))
    assert crop.main([str(src), "--region", "0,0,0.01,0.01", "-o", str(tmp_path / "d.png")]) == 1
    assert "no pixel" in capsys.readouterr().err


def test_an_unreadable_image_fails_loudly(tmp_path, capsys):
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"<!DOCTYPE html><title>Sign in</title>")
    assert crop.main([str(src), "--region", "0,0,1,1", "-o", str(tmp_path / "d.png")]) == 1
    assert "not a readable image" in capsys.readouterr().err
