"""Flattening: no var() may survive inside an EPUB."""
from core import doc

import epub


def test_epub_is_not_a_preset():
    assert "epub" not in doc.PRESETS


def test_drop_at_rule_removes_the_block_and_its_margin_boxes():
    css = '@page { size: A4; @top-center { content: "x" } } body { color: red }'
    assert epub.drop_at_rule(css, "@page").strip() == "body { color: red }"


def test_drop_at_rule_leaves_the_rest_intact():
    css = "body { color: red }"
    assert epub.drop_at_rule(css, "@page") == css


def test_flatten_resolves_the_variables():
    out = epub.flatten_css("a { color: var(--accent) }", {"accent": "#36654C"})
    assert "#36654C" in out
    assert "var(" not in out


def test_flatten_removes_the_variable_declarations():
    out = epub.flatten_css(":root { --x: 1px; color: red }", {})
    assert "--x" not in out
    assert "color: red" in out


def test_flatten_removes_the_paginated_rules():
    out = epub.flatten_css("@page { margin: 2cm } p { margin: 0 }", {})
    assert "@page" not in out


def test_the_epub_stylesheet_flattens_entirely(repo):
    d = repo / "library" / "exemples" / "guide-de-style"
    fm, _ = doc.load_doc(d)
    tokens = doc.token_map(d, {**fm, "theme": "epub"})
    css = epub.epub_css(d, tokens)
    assert "var(" not in css
    assert "@page" not in css
    assert "#36654C" in css
    assert "html {" in css
    assert "body {" in css
    assert css.count("/*") == css.count("*/") == 0


def test_the_body_has_neither_colour_nor_background(repo):
    """Spec §3.2: the text takes the reader's settings."""
    src = (repo / "theme" / "epub.css").read_text(encoding="utf-8")
    body = doc.block(src, "body")
    assert "color:" not in body
    assert "background" not in body


def test_the_epub_stylesheet_embeds_no_font(repo):
    """Spec §3.4: the reader applies the font it was given."""
    src = (repo / "theme" / "epub.css").read_text(encoding="utf-8")
    assert "@font-face" not in src
    assert "var(--font-" not in src


def test_prose_inside_a_comment_does_not_trigger_the_flattening():
    """A comment that TALKS about @page or var() must destroy nothing."""
    css = ("/* Replaces the @page and resolves the var(--x) of the sheets. */\n"
           "html { font-size: 100% }\n"
           "body { line-height: 1.5 }\n")
    out = epub.flatten_css(css, {"x": "#000000"})
    assert "html {" in out
    assert "body {" in out
    assert "currentColor" not in out


def test_the_comments_do_not_go_into_the_archive():
    out = epub.flatten_css("/* author note */ p { margin: 0 }", {})
    assert "author note" not in out
    assert "margin: 0" in out
