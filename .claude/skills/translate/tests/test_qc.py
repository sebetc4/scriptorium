"""qc.py: what a translation must keep, checked chunk by chunk."""
import qc
import zones

SOURCE = f"""## Choosing the resistor

With a 5 V supply and a forward voltage of 2.1 V, a 20 mA LED needs 145 Ω.

- Use a 1/4 W {zones.token(1)} resistor.
- Check the anode.

| Part | Value |
{zones.token(2)}
| R1 | 150 Ω |
"""

GOOD = f"""## Choisir la résistance

Avec une alimentation de 5 V et une tension directe de 2,1 V, une LED de 20 mA demande 145 Ω.

- Utiliser une résistance {zones.token(1)} de 1/4 W.
- Vérifier l'anode.

| Pièce | Valeur |
{zones.token(2)}
| R1 | 150 Ω |
"""


def check(target, source=SOURCE, **kw):
    kw.setdefault("glossary", {"resistor": "résistance"})
    kw.setdefault("keep", ("LED",))
    return qc.check_chunk(0, source, target, "en", "fr", **kw)


def messages(findings, level="error"):
    return [f.message for f in findings if f.level == level]


def test_a_faithful_translation_passes():
    assert messages(check(GOOD)) == []


def test_a_decimal_comma_is_the_same_number():
    assert qc.numbers("2.1 V and 1 000 Ω") == qc.numbers("2,1 V et 1 000 Ω")


def test_a_lost_number_is_an_error():
    assert any("145" in m for m in messages(check(GOOD.replace("145 Ω", "cent quarante-cinq Ω"))))


def test_a_changed_number_is_an_error():
    assert any("150" in m for m in messages(check(GOOD.replace("150 Ω", "510 Ω"))))


def test_placeholders_are_not_counted_as_numbers():
    assert qc.numbers(f"{zones.token(12)} and {zones.token(3)}") == qc.numbers("")


def test_a_chunk_returned_unchanged_is_an_error():
    assert any("unchanged" in m for m in messages(check(SOURCE)))


def test_a_glossary_term_not_used_is_an_error():
    bad = GOOD.replace("résistance", "resistor")
    assert any("résistance" in m for m in messages(check(bad)))


def test_a_term_to_keep_that_was_translated_is_an_error():
    bad = GOOD.replace("LED", "DEL")
    assert any("LED" in m for m in messages(check(bad)))


def test_a_lost_heading_is_an_error():
    bad = GOOD.replace("## Choisir la résistance", "Choisir la résistance")
    assert any("heading" in m for m in messages(check(bad)))


def test_a_lost_list_item_is_an_error():
    bad = GOOD.replace("- Vérifier l'anode.\n", "")
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
    other = GOOD.replace("145 Ω", "154 Ω")
    findings = qc.cross_check({0: SOURCE, 1: SOURCE}, {0: GOOD, 1: GOOD}, {0: other, 1: GOOD},
                              names=("agent", "local"))
    assert [f.chunk for f in findings] == [0]
    assert "agent" in findings[0].message and "local" in findings[0].message


def test_the_cross_check_flags_diverging_lengths():
    shorter = GOOD.split("\n\n")[0] + "\n"
    findings = qc.cross_check({0: SOURCE}, {0: GOOD}, {0: shorter}, names=("a", "b"))
    assert findings and findings[0].chunk == 0
