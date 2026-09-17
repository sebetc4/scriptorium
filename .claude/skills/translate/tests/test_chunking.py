"""chunking.py: slices that carry their context, and never cut a block."""
import chunking


def long_document(sections=30):
    parts = []
    for s in range(1, sections + 1):
        parts.append(f"## Section {s}\n\n" + "\n\n".join(
            f"Paragraph {s}.{p}: the forward voltage stays near 2 V while the "
            f"current rises, which is why a resistor sets the current."
            for p in range(1, 5)))
        if s % 5 == 0:
            parts.append("```\n" + "\n".join(f"line {i}" for i in range(60)) + "\n```")
    return "\n\n".join(parts) + "\n"


def test_the_chunks_join_back_into_the_body_byte_for_byte():
    body = long_document()
    chunks = chunking.split(body, budget=1500)
    assert "".join(c.text for c in chunks) == body


def test_a_document_longer_than_the_budget_is_split():
    chunks = chunking.split(long_document(), budget=1500)
    assert len(chunks) > 5
    assert all(len(c.text) <= 1500 or c.oversized for c in chunks)


def test_a_short_document_is_one_chunk():
    assert len(chunking.split("## One\n\nA paragraph.\n", budget=1500)) == 1


def test_a_code_block_with_blank_lines_is_never_cut():
    body = "Intro.\n\n```\na\n\n\nb\n```\n\nOutro.\n"
    for budget in (5, 10, 20):
        chunks = chunking.split(body, budget=budget)
        assert not any(c.text.count("```") == 1 for c in chunks)


def test_an_admonition_stays_with_its_indented_body():
    body = "Intro.\n\n!!! warning \"Polarity\"\n    The long leg.\n\n    Still inside.\n\nOutro.\n"
    chunks = chunking.split(body, budget=10)
    holder = next(c for c in chunks if "!!!" in c.text)
    assert "Still inside." in holder.text


def test_a_block_larger_than_the_budget_is_kept_whole_and_flagged():
    body = "Short.\n\n" + "word " * 400 + "\n"
    chunks = chunking.split(body, budget=200)
    big = next(c for c in chunks if "word" in c.text)
    assert big.oversized and big.text.count("word") == 400


def test_a_chunk_prefers_to_start_at_a_heading():
    chunks = chunking.split(long_document(), budget=1500)
    starts = [c.text.lstrip("\n").startswith("#") for c in chunks[1:]]
    assert sum(starts) >= len(starts) * 0.8


def test_each_chunk_carries_the_paragraphs_before_it():
    """A chunk sent alone loses what its first sentence refers to."""
    chunks = chunking.split(long_document(), budget=1500)
    second = chunks[1]
    assert second.context_before
    assert second.context_before in "".join(c.text for c in chunks[:1])
    assert chunks[0].context_before == ""


def test_the_context_is_whole_paragraphs_within_its_size():
    chunks = chunking.split(long_document(), budget=1500, context=300)
    for c in chunks[1:]:
        assert len(c.context_before) <= 300 or "\n\n" not in c.context_before
        assert not c.context_before.startswith(" ")


def test_each_chunk_knows_the_headings_it_sits_under():
    body = "# Part A\n\n## Sub 1\n\n" + "x " * 300 + "\n\n## Sub 2\n\n" + "y " * 300 + "\n"
    chunks = chunking.split(body, budget=700)
    last = chunks[-1]
    assert last.headings == ["Part A", "Sub 2"]


def test_a_chunk_never_ends_on_a_heading_cut_from_its_section():
    """Met on a real document: the heading went in one chunk, its paragraph in the next."""
    body = "## Features\n\n" + "short item.\n\n" * 40 + "## Principle\n\n" + "long " * 220 + "\n"
    chunks = chunking.split(body, budget=1500)
    assert "".join(c.text for c in chunks) == body
    for c in chunks[:-1]:
        last = [b for b in chunking.blocks(c.text) if b.strip()][-1]
        assert not last.lstrip().startswith("#"), c.text[-60:]
    assert any(c.text.startswith("## Principle") for c in chunks)
