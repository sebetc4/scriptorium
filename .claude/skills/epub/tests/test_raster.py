"""The diagrams become PNGs, through WeasyPrint's SVG engine."""
import re

import pytest

from core import doc

import epub

SQUARE = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
         '<rect width="200" height="100" fill="var(--accent)" /></svg>')


def test_svg_size_reads_the_viewbox():
    assert epub.svg_size(SQUARE) == (200.0, 100.0)


def test_svg_size_falls_back_to_width_height():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="150"></svg>'
    assert epub.svg_size(svg) == (300.0, 150.0)


def test_an_svg_without_dimensions_raises():
    with pytest.raises(doc.DocError):
        epub.svg_size('<svg xmlns="http://www.w3.org/2000/svg"></svg>')


def test_rasterize_yields_a_png_at_the_requested_width():
    from PIL import Image
    import io
    png = epub.rasterize_svg(doc.subst_vars(SQUARE, {"accent": "#36654C"}), 400)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    im = Image.open(io.BytesIO(png))
    assert abs(im.width - 400) <= 2
    assert abs(im.height - 200) <= 2


def test_rasterize_applies_the_resolved_colour():
    from PIL import Image
    import io
    png = epub.rasterize_svg(doc.subst_vars(SQUARE, {"accent": "#36654C"}), 100)
    im = Image.open(io.BytesIO(png)).convert("RGB")
    assert im.getpixel((50, 25)) == (0x36, 0x65, 0x4C)


def test_collect_images_rasterises_and_rewrites_the_src(repo, tmp_path):
    d = tmp_path
    inside = doc.doc_dir(d)
    (inside / "assets").mkdir(parents=True)
    (inside / "assets" / "x.svg").write_text(SQUARE, encoding="utf-8")
    html = '<p><img alt="x" src="assets/x.svg" /></p>'
    out, assets = epub.collect_images(html, d, {"accent": "#36654C"}, 200)
    # The exact name (stem + digest) is not contractual; only its shape is
    # — see test_collect_images_does_not_collide_across_directories.
    m = re.search(r'src="\.\./images/(x-[0-9a-f]{8}\.png)"', out)
    assert m, out
    name = m.group(1)
    assert name in assets
    assert assets[name][:8] == b"\x89PNG\r\n\x1a\n"


def test_collect_images_leaves_the_external_urls(tmp_path):
    html = '<img src="https://example.org/x.png" />'
    out, assets = epub.collect_images(html, tmp_path, {}, 200)
    assert out == html
    assert assets == {}


def test_collect_images_does_not_collide_across_directories(tmp_path):
    """The case reproduced in review: two paths a plain '-' would conflate."""
    d = tmp_path
    inside = doc.doc_dir(d)
    (inside / "assets-a").mkdir(parents=True)
    (inside / "assets-a" / "x.svg").write_text(SQUARE, encoding="utf-8")
    (inside / "assets").mkdir()
    (inside / "assets" / "a-x.svg").write_text(SQUARE, encoding="utf-8")
    html = ('<img src="assets-a/x.svg" />'
            '<img src="assets/a-x.svg" />')
    out, assets = epub.collect_images(html, d, {"accent": "#36654C"}, 200)
    assert len(assets) == 2, assets.keys()


def test_the_repositorys_twelve_diagrams_rasterise(repo):
    """The test that counts: the real SVG, at production width.

    The width is checked only for the images whose source is an SVG: the
    repository also embeds already-bitmap screenshots (lc100a-m328) that
    collect_images copies over as they are, without rasterising them, and that
    sometimes share the .png extension on output — conflating them with the
    diagrams would fail the test on an image that never went through
    WeasyPrint, as observed in review.
    """
    import hashlib
    from PIL import Image
    import io as _io

    IMG_SRC_RE = re.compile(r'<img\b[^>]*?src="([^"]+)"')
    seen = 0
    for d in doc.find_docs([]):
        fm, body = doc.load_doc(d)
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
        srcs_svg = [s for s in IMG_SRC_RE.findall(html) if s.lower().endswith(".svg")]
        _, assets = epub.collect_images(html, d, tokens)
        for src in srcs_svg:
            f = (d / src).resolve()
            rel = str(f.relative_to(d.resolve()))
            digest = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]
            name = f"{f.stem}-{digest}.png"
            assert name in assets, f"{d.name}: {name} missing from {sorted(assets)}"
            data = assets[name]
            assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{d.name} / {name}: not a PNG"
            im = Image.open(_io.BytesIO(data))
            assert abs(im.width - epub.RASTER_WIDTH) <= 2, f"{name}: {im.width}"
            seen += 1
    assert seen >= 12, f"{seen} diagrams seen, at least 12 expected"


def test_an_internal_elements_viewbox_does_not_win():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="150">'
           '<symbol id="i" viewBox="0 0 24 24"></symbol></svg>')
    assert epub.svg_size(svg) == (300.0, 150.0)


def test_stroke_width_is_not_taken_for_width():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" stroke-width="2" '
           'width="300" height="150"></svg>')
    assert epub.svg_size(svg) == (300.0, 150.0)
