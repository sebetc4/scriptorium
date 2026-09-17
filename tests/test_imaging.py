"""core/imaging.py: the fractional crop and the contact sheet.

Both are bricks: the sourcing tools call them, and nothing else in the
repository may hold a second copy.
"""
import pytest
from PIL import Image

from core import imaging


def quadrants(w=400, h=200):
    """Four flat colours, one per quadrant, so a crop can be read back."""
    im = Image.new("RGB", (w, h), "white")
    for (x, y), colour in {(0, 0): "red", (1, 0): "green",
                           (0, 1): "blue", (1, 1): "black"}.items():
        im.paste(colour, (x * w // 2, y * h // 2, (x + 1) * w // 2, (y + 1) * h // 2))
    return im


def test_a_crop_is_aimed_in_fractions_not_pixels():
    out = imaging.crop(quadrants(), (0.5, 0.0, 1.0, 0.5))
    assert out.size == (200, 100)
    assert out.getpixel((100, 50)) == (0, 128, 0)


def test_the_same_fractions_aim_the_same_place_at_any_size():
    small = imaging.crop(quadrants(400, 200), (0.0, 0.5, 0.5, 1.0))
    large = imaging.crop(quadrants(4000, 2000), (0.0, 0.5, 0.5, 1.0))
    assert small.getpixel((10, 10)) == large.getpixel((100, 100)) == (0, 0, 255)


def test_a_crop_enlarges_to_a_width_keeping_the_proportions():
    out = imaging.crop(quadrants(), (0.0, 0.0, 0.5, 0.5), width=1000)
    assert out.size == (1000, 500)


@pytest.mark.parametrize("region", [
    (0.5, 0.0, 0.5, 1.0),       # zero width
    (0.6, 0.0, 0.4, 1.0),       # reversed
    (0.0, 0.0, 1.2, 1.0),       # outside the image
    (-0.1, 0.0, 1.0, 1.0),
])
def test_an_empty_or_impossible_region_raises(region):
    with pytest.raises(ValueError):
        imaging.crop(quadrants(), region)


def test_a_region_too_small_to_hold_a_pixel_raises():
    with pytest.raises(ValueError):
        imaging.crop(quadrants(40, 20), (0.0, 0.0, 0.001, 0.001))


def test_a_contact_sheet_lays_out_every_thumbnail_in_a_grid():
    items = [(f"img-{i}.jpg", quadrants()) for i in range(6)]
    sheet = imaging.contact_sheet(items, columns=4, cell=(300, 200))
    assert sheet.size == (1200, 400)


def test_a_contact_sheet_writes_each_label_on_its_thumbnail():
    """Without the label, the interesting image is seen without knowing which."""
    blank = Image.new("RGB", (400, 200), "white")
    labelled = imaging.contact_sheet([("a-long-filename.jpg", blank)],
                                     columns=1, cell=(400, 240))
    unlabelled = imaging.contact_sheet([("", blank)], columns=1, cell=(400, 240))
    band = (0, 0, 400, imaging.LABEL_HEIGHT)
    assert labelled.crop(band).getcolors() != unlabelled.crop(band).getcolors()


def test_a_contact_sheet_keeps_a_thumbnail_inside_its_cell():
    tall = Image.new("RGB", (100, 3000), "red")
    sheet = imaging.contact_sheet([("tall", tall), ("next", quadrants())],
                                  columns=2, cell=(300, 200))
    # the second cell starts at x=300: nothing red may reach it
    assert all(sheet.getpixel((x, 150)) != (255, 0, 0) for x in range(300, 600))


def test_a_contact_sheet_of_nothing_raises():
    with pytest.raises(ValueError):
        imaging.contact_sheet([], columns=4, cell=(300, 200))
