"""Past 5 columns, a table becomes a sequence of blocks."""
from core import doc

import epub

NARROW = ("<table><thead><tr><th>A</th><th>B</th></tr></thead>"
          "<tbody><tr><td>1</td><td>2</td></tr></tbody></table>")

WIDE = ("<table><thead><tr>"
         + "".join(f"<th>C{i}</th>" for i in range(9))
         + "</tr></thead><tbody><tr>"
         + "".join(f"<td>v{i}</td>" for i in range(9))
         + "</tr></tbody></table>")


def test_a_narrow_table_is_left_intact():
    assert epub.transpose_wide_tables(NARROW) == NARROW


def test_a_five_column_table_is_left_intact():
    five = ("<table><thead><tr>"
            + "".join(f"<th>C{i}</th>" for i in range(5))
            + "</tr></thead><tbody><tr>"
            + "".join(f"<td>v{i}</td>" for i in range(5))
            + "</tr></tbody></table>")
    assert epub.transpose_wide_tables(five) == five


def test_a_wide_table_becomes_blocks():
    out = epub.transpose_wide_tables(WIDE)
    assert "<table>" not in out
    assert 'class="row-block"' in out


def test_the_first_cell_titles_the_block():
    out = epub.transpose_wide_tables(WIDE)
    assert '<p class="row-title">v0</p>' in out


def test_the_other_cells_become_pairs():
    out = epub.transpose_wide_tables(WIDE)
    assert "<dt>C1</dt><dd>v1</dd>" in out
    assert "<dt>C8</dt><dd>v8</dd>" in out
    assert "C0" not in out.split("<dl>")[1]   # the key's header is not repeated


def test_one_row_per_block():
    two = WIDE.replace("</tbody>",
                         "<tr>" + "".join(f"<td>w{i}</td>" for i in range(9))
                         + "</tr></tbody>")
    out = epub.transpose_wide_tables(two)
    assert out.count('class="row-block"') == 2


def test_the_result_stays_well_formed():
    epub.check_xhtml(epub.transpose_wide_tables(WIDE), "test")


def test_an_empty_cell_keeps_its_label():
    """A label that disappears takes the question away with it."""
    wide = ("<table><thead><tr>"
             + "".join(f"<th>C{i}</th>" for i in range(7))
             + "</tr></thead><tbody><tr><td>key</td><td>v1</td><td></td>"
             + "".join(f"<td>v{i}</td>" for i in range(3, 7))
             + "</tr></tbody></table>")
    out = epub.transpose_wide_tables(wide)
    assert "<dt>C2</dt><dd></dd>" in out
    assert out.count("<dt>") == 6      # every column except the key


def test_a_row_shorter_than_the_header_loses_nothing():
    """zip would truncate in silence; the fill keeps every label."""
    wide = ("<table><thead><tr>"
             + "".join(f"<th>C{i}</th>" for i in range(7))
             + "</tr></thead><tbody><tr>"
             + "".join(f"<td>v{i}</td>" for i in range(4))
             + "</tr></tbody></table>")
    out = epub.transpose_wide_tables(wide)
    assert out.count("<dt>") == 6          # the six labels besides the key
    assert "<dt>C6</dt><dd></dd>" in out   # the last one survives, with no value
    epub.check_xhtml(out, "test")


def test_a_cell_with_markup_passes_through_intact():
    wide = ("<table><thead><tr>"
             + "".join(f"<th>C{i}</th>" for i in range(7))
             + "</tr></thead><tbody><tr><td>key</td>"
             + "<td><strong>bold</strong></td>"
             + "".join(f"<td>v{i}</td>" for i in range(2, 7))
             + "</tr></tbody></table>")
    out = epub.transpose_wide_tables(wide)
    assert "<dd><strong>bold</strong></dd>" in out
    epub.check_xhtml(out, "test")


def test_a_table_without_a_thead_transposes_too():
    """The first row makes the header, whatever its container."""
    wide = ("<table><tr>"
             + "".join(f"<th>C{i}</th>" for i in range(7))
             + "</tr><tr>"
             + "".join(f"<td>v{i}</td>" for i in range(7))
             + "</tr></table>")
    out = epub.transpose_wide_tables(wide)
    assert '<p class="row-title">v0</p>' in out
    assert "<dt>C1</dt><dd>v1</dd>" in out


def test_only_esp32_is_transposed_in_the_library(repo):
    """Checking spec §6.2's survey: a single irreducible table."""
    touched = []
    for d in doc.find_docs([]):
        fm, body = doc.load_doc(d)
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
        if epub.transpose_wide_tables(html) != html:
            touched.append(d.name)
    assert touched == ["esp32"], touched
