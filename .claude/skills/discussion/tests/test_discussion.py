"""The skill's promises that a file can hold, checked against the file.

The skill has no script: what it teaches is prose. What can be tested is that
the prose and the journal's three templates agree — a section the skill names
and a template lacks is a slot the agent will not fill — and that the
description keeps the phrase that tells this skill from its neighbours. That
the links of a real journal resolve is `make check-library`'s, tested in
tests/test_library.py.
"""
import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = SKILL_DIR / "SKILL.md"
ASSETS = SKILL_DIR / "assets"
# Each layer of the journal: the heading of its table in the skill, its template.
LAYERS = {
    "`index.md`": "index.md",
    "`topics/<subject>.md`": "topic.md",
    "`sessions/<date>.md`": "session.md",
}


@pytest.fixture(scope="module")
def skill_text():
    """The skill as one line, so an assertion is not defeated by a line wrap."""
    return " ".join(SKILL.read_text(encoding="utf-8").split())


def _section(text: str, heading: str) -> str:
    """The body of a `## heading` section of the skill, up to the next one."""
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, heading
    return match.group(1)


def _layer(heading: str) -> str:
    """The body of the skill's `### heading — from …` subsection, up to the next heading."""
    text = SKILL.read_text(encoding="utf-8")
    match = re.search(rf"^### {re.escape(heading)} — .*?\n(.*?)(?=^##)", text, re.M | re.S)
    assert match, heading
    return match.group(1)


def _headings(template: str) -> list[str]:
    return re.findall(r"^##+ (.+)$", (ASSETS / template).read_text(encoding="utf-8"), re.M)


def _description(skill_md: Path) -> str:
    front = skill_md.read_text(encoding="utf-8").split("---")[1]
    return re.search(r"^description: (.*)$", front, re.M).group(1)


@pytest.mark.parametrize("heading, template", LAYERS.items())
def test_each_template_has_exactly_the_sections_the_skill_names(heading, template):
    named = re.findall(r"^\| \*\*(.+?)\*\* \|", _layer(heading), re.M)
    assert len(named) >= 4, named
    sections = re.findall(r"^## (.+)$", (ASSETS / template).read_text(encoding="utf-8"), re.M)
    assert sections == named, template


def test_the_skill_names_a_template_for_each_layer():
    for heading, template in LAYERS.items():
        assert f"from `assets/{template}`" in SKILL.read_text(encoding="utf-8")
        assert (ASSETS / template).is_file(), template
    assert sorted(p.name for p in ASSETS.iterdir()) == sorted(LAYERS.values())


def test_a_topic_separates_an_agents_account_from_what_is_established():
    claims = _section((ASSETS / "topic.md").read_text(encoding="utf-8"), "Claims")
    assert re.findall(r"^### (.+)$", claims, re.M) == ["An agent's account", "Established"]


def test_the_substance_lives_in_the_topics_and_not_in_the_index():
    """One fact, one place: the index a resume reads carries pointers, not substance."""
    index = _headings("index.md")
    for section in ("Key points", "Claims", "Replaced"):
        assert section not in index, section
    assert "Topics" in index and "Material" in index


def test_the_journal_keeps_the_substance_and_the_rejected_options():
    """A long discussion is resumed from the journal: what it drops, a resume must re-read."""
    topic = " ".join(_layer("`topics/<subject>.md`").split())
    assert "| **Key points** |" in topic
    assert "considered and rejected, with why" in topic
    journal = " ".join(_section(SKILL.read_text(encoding="utf-8"), "The journal").split())
    assert "sized by the document rather than by the conversation" in journal


def test_the_skill_states_what_keeps_the_files_from_drifting(skill_text):
    for rule in ("One fact lives in one place", "never deleted, and never kept beside what replaced it",
                 "A topic's file name is permanent", "`make check-library` checks each link"):
        assert rule in skill_text, rule
    session = " ".join(_layer("`sessions/<date>.md`").split())
    assert "never rewritten once it ends" in session


def test_the_skill_states_its_three_statuses(skill_text):
    for status in ("*Said by the user*", "*An agent's account*", "*Established*"):
        assert status in skill_text, status


def test_the_skill_names_where_the_journal_lives(skill_text):
    assert "library/<topic…>/<slug>/study/discussion/" in skill_text


def test_the_skill_hands_over_to_sourcing_and_to_pdf():
    handing = _section(SKILL.read_text(encoding="utf-8"), "Handing over")
    assert "**To `sourcing`**" in handing
    assert "**To `pdf`**" in handing


def test_the_skill_refuses_what_belongs_to_others():
    refuses = " ".join(_section(SKILL.read_text(encoding="utf-8"), "What this skill refuses").split())
    for refusal in ("Writing `index.md`", "Establishing a fact", "Inferring what the user said",
                    "Keeping a transcript", "Editing `sources/`"):
        assert refusal in refuses, refusal


def test_the_resume_reads_the_journal_and_not_the_transcript(skill_text):
    resuming = " ".join(_section(SKILL.read_text(encoding="utf-8"), "Resuming").split())
    assert "reads `index.md`, and only `index.md`" in resuming
    assert "Never ask again" in resuming
    assert "Load a topic when the discussion returns to it" in resuming
    assert "Look in `sessions/` only for an earlier point" in resuming


def test_the_resume_migrates_a_single_file_journal_only_once_the_user_agrees():
    resuming = " ".join(_section(SKILL.read_text(encoding="utf-8"), "Resuming").split())
    assert "`study/discussion.md`" in resuming
    assert "once the user agrees" in resuming


def test_the_description_carries_a_phrase_no_other_skill_does(repo):
    """docs/architecture.md §5: a skill that fires on a neighbour's job is worse than none."""
    phrases = ("before its document exists", "pasted out of conversations with other agents")
    ours = _description(SKILL)
    for phrase in phrases:
        assert phrase in ours, phrase
    for other in (repo / ".claude" / "skills").glob("*/SKILL.md"):
        if other == SKILL:
            continue
        for phrase in phrases:
            assert phrase not in _description(other), (other.parent.name, phrase)


def test_the_description_names_what_must_not_trigger_it():
    ours = _description(SKILL)
    assert "Not for an ordinary exchange about the repository" in ours
    assert "`sourcing`" in ours and "`pdf`" in ours
