"""The reports, on a corpus built for the purpose.

What is tested here is what only a corpus can say: a baseline per skill, a
finding that keeps coming back, a finding nobody ever carried, and a
before-and-after around the date something was done about one.
"""
from datetime import date
from pathlib import Path

import pytest

import aggregate
import corpus


def review(directory, name, *, day, skill, measured="", findings="[]"):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(f"""---
review: 1
date: {day}
session: s-{name}
slice: {{from: {day}T10:00:00Z, to: {day}T11:00:00Z}}
task: A task.
skill: {skill}
outcome: delivered
corrections: 0
measured:
{measured or "  turns: 10"}
findings: {findings}
---

Prose.
""", encoding="utf-8")
    return directory


def finding(kind, target, severity="high", carried=None):
    row = (f"{{kind: {kind}, severity: {severity}, target: {target}, "
           f"fix: do the thing")
    return row + (f", carried: {carried}}}" if carried else "}")


# --- baselines ---------------------------------------------------------------

def test_a_baseline_is_the_median_per_skill(tmp_path):
    for n, fresh in enumerate((100, 300, 200)):
        review(tmp_path, f"a{n}.md", day="2026-09-18", skill="pdf",
               measured=f"  tokens: {{fresh: {fresh}}}\n  turns: 10")
    row = [r for r in aggregate.baselines(corpus.load(tmp_path))
           if r.startswith("pdf")][0]
    assert "200" in row and "300" not in row


def test_a_measure_no_review_carries_is_a_dash_not_a_zero(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf")
    row = [r for r in aggregate.baselines(corpus.load(tmp_path))
           if r.startswith("pdf")][0]
    assert "0" not in row.replace("10", "")   # the turns column, nothing else
    assert "—" in row


def test_each_skill_has_its_own_baseline(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf")
    review(tmp_path, "b.md", day="2026-09-18", skill="epub")
    rows = aggregate.baselines(corpus.load(tmp_path))
    assert any(r.startswith("pdf") for r in rows)
    assert any(r.startswith("epub") for r in rows)


# --- findings ----------------------------------------------------------------

def test_findings_are_ranked_by_recurrence_before_severity(tmp_path):
    # A low finding seen three times outranks a high finding seen once: that is
    # the whole reason a corpus is kept.
    for n in range(3):
        review(tmp_path, f"a{n}.md", day="2026-09-18", skill="pdf",
               findings=f"[{finding('waste', 'a.md', severity='low')}]")
    review(tmp_path, "b.md", day="2026-09-18", skill="pdf",
           findings=f"[{finding('skill-gap', 'b.md')}]")
    rows = aggregate.findings(corpus.load(tmp_path))
    assert rows[0].startswith("  3×") and "a.md" in rows[0]
    assert "b.md" in rows[2]


def test_the_same_kind_on_another_target_is_another_finding(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf",
           findings=f"[{finding('waste', 'a.md')}, {finding('waste', 'b.md')}]")
    rows = [r for r in aggregate.findings(corpus.load(tmp_path)) if "×" in r]
    assert len(rows) == 2


def test_a_carried_finding_says_so(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf",
           findings=f"[{finding('waste', 'a.md', carried='docs/x.md')}]")
    assert "(carried)" in aggregate.findings(corpus.load(tmp_path))[0]


# --- never carried -----------------------------------------------------------

def test_a_high_finding_never_carried_is_listed_once_with_its_count(tmp_path):
    for n in range(4):
        review(tmp_path, f"a{n}.md", day=f"2026-09-1{n + 5}", skill="pdf",
               findings=f"[{finding('waste', 'a.md')}]")
    rows = aggregate.never_carried(corpus.load(tmp_path))
    assert rows == ["4×  waste          a.md  (first seen 2026-09-15)"]


def test_a_carried_finding_is_not_in_the_backlog(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf",
           findings=f"[{finding('waste', 'a.md', carried='docs/x.md')}]")
    assert aggregate.never_carried(corpus.load(tmp_path)) == []


def test_only_high_findings_are_in_the_backlog(tmp_path):
    review(tmp_path, "a.md", day="2026-09-18", skill="pdf",
           findings=f"[{finding('waste', 'a.md', severity='medium')}]")
    assert aggregate.never_carried(corpus.load(tmp_path)) == []


# --- before and after --------------------------------------------------------

def test_before_and_after_compares_the_medians_around_a_date(tmp_path):
    for day, fresh in (("2026-09-10", 1000), ("2026-09-11", 1000),
                       ("2026-09-20", 500), ("2026-09-21", 500)):
        review(tmp_path, f"a{day}.md", day=day, skill="pdf",
               measured=f"  tokens: {{fresh: {fresh}}}\n  turns: 10")
    row, = aggregate.around(corpus.load(tmp_path), date(2026, 9, 15))
    assert "2 → 2" in row and "fresh ×0.50" in row


def test_a_skill_with_reviews_on_one_side_only_is_left_out(tmp_path):
    review(tmp_path, "a.md", day="2026-09-10", skill="pdf")
    rows = aggregate.around(corpus.load(tmp_path), date(2026, 9, 15))
    assert rows == ["no skill has reviews on both sides of 2026-09-15"]


# --- coverage ----------------------------------------------------------------

def test_a_gap_of_under_thirty_seconds_is_not_a_gap(tmp_path):
    # A review's bounds are written to the second and the ledger's to the
    # microsecond: an exactly reviewed session must not look uncovered.
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / "s.json").write_text(
        '{"session": "s-a.md", "turns": 10, "bytes": 1,'
        ' "from": "2026-09-18T10:00:00.000001Z",'
        ' "to": "2026-09-18T11:00:00.342000Z"}', encoding="utf-8")
    review(tmp_path / "reviews", "a.md", day="2026-09-18", skill="pdf")
    row, = corpus.coverage(corpus.load(tmp_path / "reviews"), ledger)
    assert row["uncovered"] == []


def test_coverage_says_how_many_sessions_are_fully_reviewed(tmp_path):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    (ledger / "s.json").write_text(
        '{"session": "nobody", "turns": 10, "bytes": 1,'
        ' "from": "2026-09-18T10:00:00Z", "to": "2026-09-18T12:00:00Z"}',
        encoding="utf-8")
    rows = aggregate.coverage([], ledger)
    assert "0/1 session(s) fully reviewed" in rows[-1]
    assert "10:00–12:00" in rows[0]


# --- the whole thing ---------------------------------------------------------

def test_an_empty_corpus_says_so_rather_than_printing_a_table(tmp_path, capsys):
    aggregate.main(["--dir", str(tmp_path), "--ledger-dir", str(tmp_path)])
    assert capsys.readouterr().out.strip() == "no review yet"


def test_a_malformed_review_stops_the_report_and_names_the_file(tmp_path,
                                                               capsys):
    (tmp_path / "bad.md").write_text("no front matter\n", encoding="utf-8")
    assert aggregate.main(["--dir", str(tmp_path)]) == 1
    assert "bad.md" in capsys.readouterr().err
