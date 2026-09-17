"""The two invariants every sourcing tool holds, in one place."""
import pytest

import _sourcing


def test_a_tool_error_becomes_a_message_and_exit_status_1(capsys):
    def main(argv):
        raise _sourcing.ToolError("0 messages found")
    assert _sourcing.run(main, []) == 1
    assert capsys.readouterr().err == "error: 0 messages found\n"


def test_a_successful_tool_returns_0():
    assert _sourcing.run(lambda argv: None, []) == 0


def test_a_relative_path_is_made_absolute_at_once(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = _sourcing.absolute("out/sheet.png")
    assert p.is_absolute()
    assert p == tmp_path / "out" / "sheet.png"


def test_a_region_is_parsed_from_four_fractions():
    assert _sourcing.region("0.05,0.15,0.62,0.85") == (0.05, 0.15, 0.62, 0.85)


@pytest.mark.parametrize("text", ["0.1,0.2,0.3", "a,b,c,d", "10,20,300,400", "0.5,0,0.4,1"])
def test_a_bad_region_is_refused_with_its_reason(text):
    with pytest.raises(_sourcing.ToolError):
        _sourcing.region(text)


def test_identical_sizes_across_a_batch_are_reported(tmp_path):
    """Three files of rigorously identical size were three error pages."""
    for name in ("p15.html", "p30.html", "p45.html"):
        (tmp_path / name).write_bytes(b"x" * 4684)
    (tmp_path / "p1.html").write_bytes(b"x" * 16000)
    groups = _sourcing.same_size(sorted(tmp_path.iterdir()))
    assert [sorted(p.name for p in g) for g in groups] == [["p15.html", "p30.html", "p45.html"]]


def test_two_files_of_the_same_size_are_not_a_suspicion(tmp_path):
    for name in ("a", "b"):
        (tmp_path / name).write_bytes(b"x" * 10)
    assert _sourcing.same_size(sorted(tmp_path.iterdir())) == []
