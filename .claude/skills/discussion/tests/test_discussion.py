"""The skill's promises that a file can hold, checked against the file.

The skill has no script: what it teaches is prose. What can be tested is that
the prose and the journal template agree — a section the skill names and the
template lacks is a slot the agent will not fill — and that the description
keeps the phrase that tells this skill from its neighbours.
"""
import re
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = SKILL_DIR / "SKILL.md"
TEMPLATE = SKILL_DIR / "assets" / "journal.md"


@pytest.fixture(scope="module")
def skill_text():
    """The skill as one line, so an assertion is not defeated by a line wrap."""
    return " ".join(SKILL.read_text(encoding="utf-8").split())


def _section(text: str, heading: str) -> str:
    """The body of a `## heading` section of the skill, up to the next one."""
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, heading
    return match.group(1)


def _description(skill_md: Path) -> str:
    front = skill_md.read_text(encoding="utf-8").split("---")[1]
    return re.search(r"^description: (.*)$", front, re.M).group(1)


def test_the_template_has_every_section_the_skill_names():
    table = _section(SKILL.read_text(encoding="utf-8"), "The journal")
    named = re.findall(r"^\| \*\*(.+?)\*\* \|", table, re.M)
    assert len(named) >= 8, named
    headings = re.findall(r"^##+ (.+)$", TEMPLATE.read_text(encoding="utf-8"), re.M)
    for name in named:
        assert name in headings, name


def test_the_template_separates_an_agents_account_from_what_is_established():
    claims = _section(TEMPLATE.read_text(encoding="utf-8"), "Claims")
    assert re.findall(r"^### (.+)$", claims, re.M) == ["An agent's account", "Established"]


def test_the_journal_keeps_the_substance_and_the_rejected_options():
    """A long discussion is resumed from the journal: what it drops, a resume must re-read."""
    table = " ".join(_section(SKILL.read_text(encoding="utf-8"), "The journal").split())
    assert "| **Key points** |" in table
    assert "considered and rejected, with why" in table
    assert "sized by the document rather than by the conversation" in table


def test_the_skill_states_its_three_statuses(skill_text):
    for status in ("*Said by the user*", "*An agent's account*", "*Established*"):
        assert status in skill_text, status


def test_the_skill_names_where_the_journal_lives(skill_text):
    assert "library/<topic…>/<slug>/study/discussion.md" in skill_text


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
    assert "reads the journal, and only the journal" in resuming
    assert "Never ask again" in resuming


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
