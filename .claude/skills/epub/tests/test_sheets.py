"""The review bears on what does not reflow, not on screens."""
from PIL import Image

import preview


def test_the_reference_screen_is_a_six_inch_one():
    assert (preview.SCREEN_W, preview.SCREEN_H) == (1072, 1448)


def test_render_screens_writes_at_least_one_image(tmp_path):
    pages = preview.render_screens("<p>hello</p>", "p{font-size:20px}",
                                   tmp_path, "trial")
    assert pages
    for p in pages:
        assert p.is_file()
        im = Image.open(p)
        assert im.width == preview.SCREEN_W


def test_long_content_gives_several_screens(tmp_path):
    body = "".join(f"<p>line {i} — some text to fill the page.</p>"
                   for i in range(200))
    pages = preview.render_screens(body, "p{font-size:28px}", tmp_path, "long")
    assert len(pages) > 1


def test_the_contact_sheet_keeps_only_the_non_reflowing(fixture_library):
    d = fixture_library / "sample" / "component"
    pages = preview.contact_sheet(d)
    assert pages
    assert all(p.is_relative_to(d / ".work") for p in pages)


def test_the_sheet_carries_every_object_that_does_not_reflow(fixture_library):
    # The component holds four diagrams, a seven-column table the EPUB folds
    # into one block per row (three rows), and one code block: 4 + 3 + 1.
    d = fixture_library / "sample" / "component"
    assert preview.non_reflowing_count(d) == 8


def test_the_style_proof_renders_the_whole_guide(fixture_library):
    d = fixture_library / "exemples" / "guide-de-style"
    pages = preview.style_screens(d)
    assert 1 <= len(pages) <= 8


def test_a_sheet_really_renders_its_images(tmp_path):
    """Without base_url, WeasyPrint looks for the images in the wrong place and
    the sheet comes out blank — without raising anything."""
    import epub
    from core import doc
    square = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
              '<rect width="200" height="100" fill="var(--accent)" /></svg>')
    (tmp_path / "trial.png").write_bytes(
        epub.rasterize_svg(doc.subst_vars(square, {"accent": "#36654C"}), 400))
    pages = preview.render_screens(
        '<img src="trial.png" style="width:400px"/>', "", tmp_path, "img")
    assert pages
    im = Image.open(pages[0]).convert("L")
    shades = len(im.getcolors(maxcolors=100000) or [])
    # The square is a single flat area with no antialiasing (edges landing on
    # the pixel grid at every step), so a correct sheet carries exactly two
    # shades — the white ground and the square — never three or more. The
    # threshold separating the mute sheet (1 shade measured, before the fix)
    # from the sheet that really shows the image (2 shades measured, after) is
    # therefore 1, not 3.
    assert shades > 1, f"sheet nearly empty: {shades} shades"
