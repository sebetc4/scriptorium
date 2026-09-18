"""The six obligations, and the round trip from a transcript to a valid review.

Four of the six are arithmetic — `metrics.owed()` fires them from the measures,
so they are tested by firing them. The other two are rules about writing, which
no script can check on prose; what is tested there is that the skill states them
and that `corpus.py` enforces the one that can be enforced.
"""
from pathlib import Path

import pytest

import corpus
import metrics
from metrics import Slice
from test_metrics import Transcript, T0, stamp, tool, usage

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="module")
def skill_text():
    """The skill as one line, so an assertion is not defeated by a line wrap."""
    return " ".join(SKILL.read_text(encoding="utf-8").split())


@pytest.fixture
def plain(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [{"type": "text", "text": "."}])
    return t.write()


@pytest.fixture(scope="module")
def reviews():
    return corpus.load(FIXTURES)


def slice_of(tmp_path, **kw):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [{"type": "text", "text": "."}], use=usage(**kw))
    return metrics.scan(t.write(), Slice(None, None))


# --- 1. the three largest costs ----------------------------------------------

def test_the_largest_costs_are_named(tmp_path, reviews):
    m = slice_of(tmp_path, fresh=9000, cached=5000, out=100)
    first = metrics.owed(m, [], reviews, "pdf")[0]
    assert "explain the 3 largest costs" in first
    assert "the main context" in first


def test_with_no_baseline_three_becomes_five(tmp_path):
    m = slice_of(tmp_path, fresh=9000, cached=5000, out=100)
    first = metrics.owed(m, [], [], "pdf")[0]
    assert "explain the 5 largest costs" in first
    assert "no baseline yet" in first


# --- 2. one and a half times the median --------------------------------------

def test_a_measure_past_one_and_a_half_times_the_median_is_owed(tmp_path, reviews):
    # The pdf median of tokens.fresh over the fixtures is 107,666.5.
    m = slice_of(tmp_path, fresh=400000, cached=1000)
    rows = "\n".join(metrics.owed(m, [], reviews, "pdf"))
    assert "explain tokens.fresh" in rows


def test_a_measure_under_the_threshold_is_not_owed(tmp_path, reviews):
    m = slice_of(tmp_path, fresh=150000, cached=1000)   # ×1.39
    rows = "\n".join(metrics.owed(m, [], reviews, "pdf"))
    assert "explain tokens.fresh" not in rows


def test_the_threshold_obligation_cannot_fire_without_a_baseline(tmp_path):
    m = slice_of(tmp_path, fresh=400000, cached=1000)
    rows = "\n".join(metrics.owed(m, [], [], "pdf"))
    assert "explain tokens.fresh" not in rows
    assert "three becomes five" in rows           # the wider duty took its place


# --- 3. the waste and friction counters --------------------------------------

def test_a_non_zero_counter_owes_a_finding(tmp_path, reviews):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command="ls")])
    t.assistant(1, [tool("Bash", tid="t1", command="ls")])
    t.assistant(2, [tool("Read", tid="t2", file_path="a.md")])
    t.assistant(3, [tool("Read", tid="t3", file_path="a.md")])
    t.user(4, [{"type": "text", "text": "[Request interrupted by user]"}])
    m = metrics.scan(t.write(), Slice(None, None))
    rows = "\n".join(metrics.owed(m, [], reviews, "pdf"))
    assert "justification for repeated_bash: 1" in rows
    assert "justification for files_read_twice: 1" in rows
    assert "justification for interruptions: 1" in rows


def test_a_zero_counter_owes_nothing(tmp_path, reviews):
    m = slice_of(tmp_path)
    rows = "\n".join(metrics.owed(m, [], reviews, "pdf"))
    assert "repeated_bash" not in rows
    assert "interruptions" not in rows


# --- 4. the user's corrections -----------------------------------------------

def test_every_correction_is_owed_and_only_the_session_can_count_them(tmp_path,
                                                                     reviews):
    rows = metrics.owed(slice_of(tmp_path), [], reviews, "pdf")
    assert any("correction the user made" in r and "only the session" in r
               for r in rows)


# --- 5 and 6. the two rules no measurement can trigger -----------------------

def test_a_finding_without_a_target_and_a_fix_is_refused(tmp_path, skill_text):
    assert "No finding without a `target:` and a `fix:`" in skill_text
    (tmp_path / "r.md").write_text(f"""---
review: 1
date: 2026-09-18
session: s
slice: {{from: {stamp(0)}, to: {stamp(1)}}}
task: A task.
skill: pdf
outcome: delivered
corrections: 0
findings: [{{kind: waste, severity: high, note: it was slow}}]
---

Prose.
""", encoding="utf-8")
    with pytest.raises(corpus.ReviewError, match="target"):
        corpus.load(tmp_path)


def test_the_skill_forbids_a_section_for_what_went_well(skill_text):
    assert "No section for what went well" in skill_text
    assert "There is no other section" in skill_text


# --- the budget --------------------------------------------------------------

def test_the_skill_states_its_budget_and_what_it_covers(skill_text):
    assert "Eight thousand tokens, everything included" in skill_text
    assert "the tooling's own output included" in skill_text
    assert "cannot be met by moving cost out of the prose and into a command" \
        in skill_text


def test_the_timeline_is_named_optional_and_is_off_by_default(skill_text, plain,
                                                              capsys):
    assert "`--timeline` is optional" in skill_text
    metrics.main(["--transcript", str(plain), "--owed",
                  "--reviews", str(plain.parent / "none")])
    assert "# timeline" not in capsys.readouterr().out


def test_the_whole_output_with_the_obligations_stays_under_fifty_lines(
        tmp_path, capsys):
    t = Transcript(tmp_path / "s.jsonl")
    for i in range(30):
        t.assistant(i, [tool("Bash", tid=f"t{i}", command="ls")])
        t.user(i + 0.5, [{"type": "text", "text": "[Request interrupted by user]"}])
    path = t.write()
    metrics.main(["--transcript", str(path), "--owed",
                  "--reviews", str(FIXTURES), "--skill", "pdf"])
    assert len(capsys.readouterr().out.splitlines()) <= metrics.MAX_LINES + 1


# --- the description ---------------------------------------------------------

def test_the_description_says_what_the_skill_never_does(skill_text):
    description = skill_text.split("description: ")[1].split(" --- ")[0]
    # The description is the only thing that stops this skill loading during
    # ordinary work, so it states the negative, as `sourcing` does.
    assert "not part of doing the work" in description
    for never in ("builds nothing", "fixes nothing", "never runs while"):
        assert never in description


# --- the round trip ----------------------------------------------------------

def test_a_review_written_from_the_tooling_satisfies_the_corpus(tmp_path,
                                                                capsys):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command="make build")],
                use=usage(fresh=3000, cached=40000), skill="pdf")
    t.user(1, [{"type": "tool_result", "tool_use_id": "t0"}])
    t.assistant(2, [{"type": "text", "text": "built"}],
                use=usage(fresh=900, cached=52000), skill="pdf")
    path = t.write()

    metrics.main(["--transcript", str(path), "--reviews", str(tmp_path / "none")])
    block = capsys.readouterr().out.split("\n\n")[0]

    corpus_dir = tmp_path / "reviews"
    corpus_dir.mkdir()
    (corpus_dir / "2026-09-18-s-a-task.md").write_text(f"""---
review: {corpus.VERSION}
date: 2026-09-18
session: s
slice: {{from: {stamp(0)}, to: {stamp(2)}}}
task: Build the document and check it.
skill: pdf
outcome: delivered
corrections: 0
{block}
findings:
  - kind: waste
    severity: low
    target: .claude/skills/pdf/SKILL.md
    fix: Say that a rebuild after a caption change needs no second review pass.
---

The build is the whole cost of this task.
""", encoding="utf-8")

    review, = corpus.load(corpus_dir)
    assert review.measure("tokens.fresh") == 3900
    assert review.measure("tools.Bash") == 1
    assert review.measure("derived.build_cycles") == 1
