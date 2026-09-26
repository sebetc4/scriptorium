"""zones.py: what an engine must never translate is taken out before it sees it."""
import pytest

import zones

BODY = """## Baking the bread

Status :circle-check.accent: compliant, and :unknownword: stays as written.

```python
yeast = (flour / 1000) * rate   # never translated
```

Use `Y = (F / 1000) * R` for the yeast[^1].

!!! warning "Check the oven"
    The stone must be hot.

![A loaf](assets/loaf.svg "Figure 1 — The crust must be golden"){: .diagram }

See <https://example.org/bread> or https://example.org/recipe.pdf.

<div class="keep" markdown="1">
Kept together.
</div>

<!-- a note for the author -->

| Part | Value |
|---|---|
| Salt | 10 g |

[^1]: A 7 g sachet is enough.
"""


def protected(text):
    return zones.protect(text)


def test_a_round_trip_restores_the_text_byte_for_byte():
    masked, table = protected(BODY)
    assert zones.restore(masked, table) == BODY


@pytest.mark.parametrize("fragment", [
    "yeast = (flour / 1000) * rate   # never translated",      # a code block
    "`Y = (F / 1000) * R`",                               # a code span
    ":circle-check.accent:",                              # an icon, with its role
    ":unknownword:",                                      # an unknown name: not "fixed"
    "!!! warning",                                        # an admonition type
    "](assets/loaf.svg",                                   # an image target
    "{: .diagram }",                                      # an attribute list
    "<https://example.org/bread>",
    "https://example.org/recipe.pdf",
    '<div class="keep" markdown="1">',
    "<!-- a note for the author -->",
    "|---|---|",                                          # a table's separator row
    "[^1]",
])
def test_the_engine_never_sees_a_protected_zone(fragment):
    masked, _ = protected(BODY)
    assert fragment not in masked


@pytest.mark.parametrize("text", [
    "Baking the bread", "compliant, and", "Check the oven",
    "The stone must be hot.", "Figure 1 — The crust must be golden",
    "Kept together.", "A 7 g sachet is enough.", "A loaf",
])
def test_the_prose_around_them_is_left_to_translate(text):
    masked, _ = protected(BODY)
    assert text in masked


def test_each_zone_becomes_one_placeholder():
    masked, table = protected("Run `make build` then `make epub`.")
    assert masked == f"Run {zones.token(1)} then {zones.token(2)}."
    assert table == {zones.token(1): "`make build`", zones.token(2): "`make epub`"}


def test_placeholders_can_be_numbered_from_an_offset():
    """Chunks share one table for the document: numbering must not restart."""
    _, first = zones.protect("`a`")
    masked, second = zones.protect("`b`", start=len(first) + 1)
    assert masked == zones.token(2)


def test_a_text_already_holding_the_placeholder_mark_is_refused():
    with pytest.raises(zones.ZoneError):
        zones.protect(f"a text quoting {zones.token(3)} literally")


def test_restore_refuses_a_missing_placeholder():
    masked, table = protected("Run `make build` now.")
    with pytest.raises(zones.ZoneError, match="missing"):
        zones.restore(masked.replace(zones.token(1), ""), table)


def test_restore_refuses_a_duplicated_placeholder():
    masked, table = protected("Run `make build` now.")
    with pytest.raises(zones.ZoneError, match="more than once"):
        zones.restore(masked + " " + zones.token(1), table)


def test_restore_refuses_an_invented_placeholder():
    masked, table = protected("Run `make build` now.")
    with pytest.raises(zones.ZoneError, match="unknown"):
        zones.restore(masked + " " + zones.token(9), table)


FRONT = """---
title: Le pain              # the cover's title
subtitle: "Doser, et ne pas le brûler"
eyebrow: Fiche technique
author: Jean Dupont
date: 2026-09-10
preset: report
lang: en
theme: light          # light | dark | both
meta: {Client: Acme, Version: "1.0"}
---
"""


def test_the_front_matter_offers_only_its_displayed_strings():
    strings = zones.front_matter_strings(FRONT)
    assert strings == {"title": "Le pain",
                       "subtitle": "Doser, et ne pas le brûler",
                       "eyebrow": "Fiche technique"}


def test_translated_strings_go_back_without_touching_keys_or_comments():
    out = zones.set_front_matter_strings(FRONT, {
        "title": "Bread", "subtitle": "Dosing it: and not burning it",
        "eyebrow": "Recipe card"})
    assert "title: Bread              # the cover's title" in out
    assert 'subtitle: "Dosing it: and not burning it"' in out
    assert "eyebrow: Recipe card" in out
    for line in ("author: Jean Dupont", "preset: report", "lang: en",
                 "theme: light          # light | dark | both",
                 'meta: {Client: Acme, Version: "1.0"}'):
        assert line in out


def test_a_translated_value_is_quoted_when_yaml_needs_it():
    import yaml
    out = zones.set_front_matter_strings(FRONT, {"title": "Bread: # a guide"})
    assert yaml.safe_load(out.split("---")[1])["title"] == "Bread: # a guide"
