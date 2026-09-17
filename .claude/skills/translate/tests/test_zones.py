"""zones.py: what an engine must never translate is taken out before it sees it."""
import pytest

import zones

BODY = """## Wiring the LED

Status :circle-check.accent: compliant, and :unknownword: stays as written.

```python
current = (vcc - vf) / r   # never translated
```

Use `R = (Vcc - Vf) / I` for the resistor[^1].

!!! warning "Check the polarity"
    The long leg is the anode.

![A LED](assets/led.svg "Figure 1 — The anode is the long leg"){: .diagram }

See <https://example.org/led> or https://example.org/datasheet.pdf.

<div class="keep" markdown="1">
Kept together.
</div>

<!-- a note for the author -->

| Part | Value |
|---|---|
| R1 | 220 Ω |

[^1]: A 1/4 W resistor is enough.
"""


def protected(text):
    return zones.protect(text)


def test_a_round_trip_restores_the_text_byte_for_byte():
    masked, table = protected(BODY)
    assert zones.restore(masked, table) == BODY


@pytest.mark.parametrize("fragment", [
    "current = (vcc - vf) / r   # never translated",      # a code block
    "`R = (Vcc - Vf) / I`",                               # a code span
    ":circle-check.accent:",                              # an icon, with its role
    ":unknownword:",                                      # an unknown name: not "fixed"
    "!!! warning",                                        # an admonition type
    "](assets/led.svg",                                   # an image target
    "{: .diagram }",                                      # an attribute list
    "<https://example.org/led>",
    "https://example.org/datasheet.pdf",
    '<div class="keep" markdown="1">',
    "<!-- a note for the author -->",
    "|---|---|",                                          # a table's separator row
    "[^1]",
])
def test_the_engine_never_sees_a_protected_zone(fragment):
    masked, _ = protected(BODY)
    assert fragment not in masked


@pytest.mark.parametrize("text", [
    "Wiring the LED", "compliant, and", "Check the polarity",
    "The long leg is the anode.", "Figure 1 — The anode is the long leg",
    "Kept together.", "A 1/4 W resistor is enough.", "A LED",
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
title: Les LED              # the cover's title
subtitle: "Dimensionner, et ne pas les griller"
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
    assert strings == {"title": "Les LED",
                       "subtitle": "Dimensionner, et ne pas les griller",
                       "eyebrow": "Fiche technique"}


def test_translated_strings_go_back_without_touching_keys_or_comments():
    out = zones.set_front_matter_strings(FRONT, {
        "title": "LEDs", "subtitle": "Sizing them: and not burning them",
        "eyebrow": "Datasheet"})
    assert "title: LEDs              # the cover's title" in out
    assert 'subtitle: "Sizing them: and not burning them"' in out
    assert "eyebrow: Datasheet" in out
    for line in ("author: Jean Dupont", "preset: report", "lang: en",
                 "theme: light          # light | dark | both",
                 'meta: {Client: Acme, Version: "1.0"}'):
        assert line in out


def test_a_translated_value_is_quoted_when_yaml_needs_it():
    import yaml
    out = zones.set_front_matter_strings(FRONT, {"title": "LEDs: # a guide"})
    assert yaml.safe_load(out.split("---")[1])["title"] == "LEDs: # a guide"
