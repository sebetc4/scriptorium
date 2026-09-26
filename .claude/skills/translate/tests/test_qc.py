"""qc.py: what a translation must keep, checked chunk by chunk."""
import qc
import zones

SOURCE = f"""## Choosing the yeast

With 500 g of flour and a proofing time of 1.5 h, a PanPro loaf needs 145 g of starter.

- Use 1/4 of a {zones.token(1)} sachet.
- Check the oven.

| Part | Value |
{zones.token(2)}
| S1 | 150 g |
"""

GOOD = f"""## Choisir la levure

Avec 500 g de farine et une levée de 1,5 h, un pain PanPro demande 145 g de levain.

- Utiliser 1/4 d'un sachet {zones.token(1)}.
- Vérifier le four.

| Pièce | Valeur |
{zones.token(2)}
| S1 | 150 g |
"""


def check(target, source=SOURCE, **kw):
    kw.setdefault("glossary", {"yeast": "levure"})
    kw.setdefault("keep", ("PanPro",))
    return qc.check_chunk(0, source, target, "en", "fr", **kw)


def messages(findings, level="error"):
    return [f.message for f in findings if f.level == level]


def test_a_faithful_translation_passes():
    assert messages(check(GOOD)) == []


def test_a_decimal_comma_is_the_same_number():
    assert qc.numbers("1.5 h and 1 000 g") == qc.numbers("1,5 h et 1 000 g")


def test_a_lost_number_is_an_error():
    assert any("145" in m for m in messages(check(GOOD.replace("145 g", "cent quarante-cinq g"))))


def test_a_changed_number_is_an_error():
    assert any("150" in m for m in messages(check(GOOD.replace("150 g", "510 g"))))


def test_placeholders_are_not_counted_as_numbers():
    assert qc.numbers(f"{zones.token(12)} and {zones.token(3)}") == qc.numbers("")


def test_a_chunk_returned_unchanged_is_an_error():
    assert any("unchanged" in m for m in messages(check(SOURCE)))


def test_a_glossary_term_not_used_is_an_error():
    bad = GOOD.replace("levure", "yeast")
    assert any("levure" in m for m in messages(check(bad)))


def test_a_term_to_keep_that_was_translated_is_an_error():
    bad = GOOD.replace("PanPro", "Pan Pro")
    assert any("PanPro" in m for m in messages(check(bad)))


def test_a_lost_heading_is_an_error():
    bad = GOOD.replace("## Choisir la levure", "Choisir la levure")
    assert any("heading" in m for m in messages(check(bad)))


def test_a_lost_list_item_is_an_error():
    bad = GOOD.replace("- Vérifier le four.\n", "")
    assert any("list" in m for m in messages(check(bad)))


def test_a_broken_table_row_is_an_error():
    bad = GOOD.replace("| Pièce | Valeur |", "| Pièce Valeur |")
    assert any("table" in m for m in messages(check(bad)))


def test_a_placeholder_moved_off_its_own_line_is_an_error():
    """A fenced block's placeholder inside a sentence would glue code to prose."""
    bad = GOOD.replace(f"| Pièce | Valeur |\n{zones.token(2)}\n", f"| Pièce | Valeur | {zones.token(2)}\n")
    assert any("own line" in m for m in messages(check(bad)))


def test_a_suspicious_length_is_a_warning_not_an_error():
    long_target = GOOD + "\n" + "Une précision ajoutée par le moteur. " * 30
    findings = check(long_target)
    assert messages(findings) == []
    assert any("length" in m for m in messages(findings, "warning"))


def test_the_cross_check_flags_the_chunks_where_two_engines_disagree():
    other = GOOD.replace("145 g", "154 g")
    findings = qc.cross_check({0: SOURCE, 1: SOURCE}, {0: GOOD, 1: GOOD}, {0: other, 1: GOOD},
                              names=("agent", "local"))
    assert [f.chunk for f in findings] == [0]
    assert "agent" in findings[0].message and "local" in findings[0].message


def test_the_cross_check_flags_diverging_lengths():
    shorter = GOOD.split("\n\n")[0] + "\n"
    findings = qc.cross_check({0: SOURCE}, {0: GOOD}, {0: shorter}, names=("a", "b"))
    assert findings and findings[0].chunk == 0
