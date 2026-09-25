"""The EPUB mapping: equalised luminance, tinted backgrounds removed."""
from core import doc
from core.doc import contrast, grey_level

FLOOR = 6.5


def epub_tokens(repo):
    css = (repo / "brand" / "tokens.css").read_text(encoding="utf-8")
    src = doc.block(css, '[data-theme="epub"]')
    assert src, "the [data-theme=\"epub\"] block is missing from tokens.css"
    return dict(doc.DECL_RE.findall(src))


def test_the_epub_values_are_the_ones_in_the_spec(repo):
    t = {k: v.strip() for k, v in epub_tokens(repo).items()}
    assert t["accent"] == "#36654C"
    assert t["alert"] == "#953C05"
    assert t["danger"] == "#A52911"
    assert t["link"] == "#045468"


def test_the_tinted_backgrounds_are_removed(repo):
    t = {k: v.strip() for k, v in epub_tokens(repo).items()}
    for role in ("accent-tint", "alert-tint", "danger-tint"):
        assert t[role] == "transparent"


def test_the_signalling_roles_have_equal_strength_in_grey(repo):
    """The point of spec §3: three marks of identical strength in monochrome."""
    t = {k: v.strip() for k, v in epub_tokens(repo).items()}
    values = [grey_level(t[r]) for r in ("accent", "alert", "danger")]
    assert max(values) - min(values) <= 8, f"unequal strengths: {values}"


def test_every_role_clears_the_contrast_floor(repo):
    t = {k: v.strip() for k, v in epub_tokens(repo).items()}
    paper = t["paper"]
    for role in ("accent", "alert", "danger", "link", "ink"):
        c = contrast(t[role], paper)
        assert c >= FLOOR, f"{role}: contrast {c:.2f} < {FLOOR}"


def test_token_map_reads_the_epub_block(fixture_tree):
    d = fixture_tree / "library" / "exemples" / "guide-de-style"
    fm, _ = doc.load_doc(d)
    t = doc.token_map(d, {**fm, "theme": "epub"})
    assert t["accent"] == "#36654C"
    assert t["alert-tint"] == "transparent"
