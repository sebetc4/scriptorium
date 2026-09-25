"""The corpus reader, against hand-written reviews.

Every fixture here is a review written by hand from `references/format.md`,
which is also the first acceptance criterion of this phase: the format has to
be writable without reading any code. Nothing in this suite reads a real
transcript, so it passes on a fresh clone.
"""
import textwrap

import pytest

import corpus
from corpus import ReviewError

FIXTURES = __import__("pathlib").Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def reviews():
    return corpus.load(FIXTURES)


def write(tmp_path, name, text):
    (tmp_path / name).write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    return tmp_path


GOOD = """
    ---
    review: 1
    date: 2026-09-25
    session: abc
    slice: {from: 2026-09-25T10:00:00Z, to: 2026-09-25T11:00:00Z}
    task: A task.
    skill: epub
    outcome: delivered
    corrections: 0
    measured: {turns: 10}
    findings: []
    ---

    Prose.
"""


# --- reading -----------------------------------------------------------------

def test_load_reads_every_review_oldest_first(reviews):
    assert [r.meta["date"].isoformat() for r in reviews] == [
        "2026-09-17", "2026-09-20", "2026-09-22"]


def test_a_missing_corpus_is_empty_not_an_error(tmp_path):
    assert corpus.load(tmp_path / "nowhere") == []


def test_the_body_is_kept_whole_and_never_parsed(reviews):
    assert reviews[0].body.startswith("The four delegated")


# --- refusing ----------------------------------------------------------------

def test_an_unknown_kind_is_refused_by_file_and_by_value(tmp_path):
    d = write(tmp_path, "bad.md", GOOD.replace(
        "findings: []",
        "findings: [{kind: vibes, severity: low, target: x, fix: y}]"))
    with pytest.raises(ReviewError) as e:
        corpus.load(d)
    assert "bad.md" in str(e.value) and "vibes" in str(e.value)


def test_a_trigger_finding_is_accepted(tmp_path):
    d = write(tmp_path, "trigger.md", GOOD.replace(
        "findings: []",
        "findings: [{kind: trigger, severity: medium, "
        "target: .claude/skills/discussion/SKILL.md, "
        "fix: Say in the description that a question about the repository "
        "is not a discussion.}]"))
    review, = corpus.load(d)
    assert review.findings[0]["kind"] == "trigger"


def test_the_vocabulary_is_closed_with_trigger_in_it():
    assert "trigger" in corpus.KINDS
    assert len(corpus.KINDS) == 9


def test_a_review_of_a_discussion_is_accepted(tmp_path):
    d = write(tmp_path, "d.md", GOOD.replace("skill: epub", "skill: discussion"))
    assert corpus.load(d)[0].skill == "discussion"


def test_a_finding_without_a_fix_is_refused(tmp_path):
    d = write(tmp_path, "bad.md", GOOD.replace(
        "findings: []", "findings: [{kind: waste, severity: high, target: x}]"))
    with pytest.raises(ReviewError, match="fix"):
        corpus.load(d)


def test_a_finding_without_a_target_is_refused(tmp_path):
    d = write(tmp_path, "bad.md", GOOD.replace(
        "findings: []", "findings: [{kind: waste, severity: high, fix: y}]"))
    with pytest.raises(ReviewError, match="target"):
        corpus.load(d)


@pytest.mark.parametrize("field", corpus.REQUIRED)
def test_every_required_field_is_required(tmp_path, field):
    lines = [l for l in textwrap.dedent(GOOD).lstrip().splitlines()
             if not l.startswith(f"{field}:")]
    d = write(tmp_path, "bad.md", "\n".join(lines))
    with pytest.raises(ReviewError, match=field):
        corpus.load(d)


def test_an_unknown_outcome_is_refused(tmp_path):
    d = write(tmp_path, "bad.md", GOOD.replace("outcome: delivered",
                                               "outcome: glorious"))
    with pytest.raises(ReviewError, match="glorious"):
        corpus.load(d)


def test_an_unknown_skill_is_refused(tmp_path):
    """Medians are grouped by skill, so a value outside the list makes a group
    the format does not recognise. `skill` was required but never checked, and
    four reviews of 2026-09-18 came to sit under a skill that was not listed.
    """
    d = write(tmp_path, "bad.md", GOOD.replace("skill: epub", "skill: plumbing"))
    with pytest.raises(ReviewError, match="plumbing"):
        corpus.load(d)


def test_a_review_without_front_matter_is_refused(tmp_path):
    d = write(tmp_path, "bad.md", "Just prose.\n")
    with pytest.raises(ReviewError, match="front matter"):
        corpus.load(d)


# --- measures ----------------------------------------------------------------

def test_a_measure_is_read_by_dotted_path(reviews):
    assert reviews[0].measure("tokens.fresh") == 154333
    assert reviews[0].measure("tools.Bash") == 25


def test_a_measure_across_subagent_runs_is_summed(reviews):
    assert reviews[0].measure("subagents.fresh") == 91911
    assert reviews[0].measure("subagents.cache_read") == 288210


def test_a_derived_measure_reads_as_its_value(reviews):
    assert reviews[0].measure("derived.image_carry") == 625600
    assert reviews[0].measure("derived.image_carry.value") == 625600


def test_an_absent_measure_is_none_never_zero(reviews):
    fetch = reviews[2]
    assert fetch.measure("images") is None
    assert fetch.measure("friction.denials") is None
    assert fetch.measure("subagents.fresh") is None


# --- medians -----------------------------------------------------------------

def test_the_median_is_computed_per_skill(reviews):
    assert corpus.median(reviews, "tokens.fresh", skill="pdf") == 107666.5
    assert corpus.median(reviews, "turns", skill="pdf") == 45


def test_a_single_review_has_no_median(reviews):
    assert corpus.median(reviews, "tokens.fresh", skill="fetch") is None


def test_an_empty_corpus_has_no_median():
    assert corpus.median([], "tokens.fresh") is None


def test_a_measure_missing_from_one_review_is_not_counted_as_zero(reviews):
    # Only the pdf reviews carry `images`; the median must not be dragged
    # towards zero by the review that never recorded one.
    assert corpus.median(reviews, "images") == 6.5


def test_two_format_versions_are_never_mixed(tmp_path):
    for n, version in enumerate((1, 1, 2, 2)):
        write(tmp_path, f"r{n}.md", GOOD.replace(
            "review: 1", f"review: {version}").replace(
            "turns: 10", f"turns: {10 * (n + 1)}"))
    rs = corpus.load(tmp_path)
    assert corpus.median(rs, "turns", version=1) == 15
    assert corpus.median(rs, "turns", version=2) == 35


def test_a_review_can_be_excluded_from_its_own_baseline(reviews):
    assert corpus.median(reviews, "tokens.fresh", skill="pdf",
                         exclude=reviews[0].path) is None
