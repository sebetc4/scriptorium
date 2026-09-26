"""The skill's promises that a file can hold, checked against the files.

The skill has no script: its commands live in the core (`core/catalogue.py`,
`core/navigate.py`), tested in tests/test_catalogue.py and
tests/test_navigate.py. What is tested here is that the prose agrees with the
code — every command the skill, its rules and its agent name exists, and every
command that exists is in the skill's table — and that the skill states its
refusals and its user's-word rules where a reader looks for them.
"""
import re
from pathlib import Path

import pytest

from core import catalogue

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = SKILL_DIR / "SKILL.md"
RULES = SKILL_DIR / "references" / "describing.md"
AGENT = SKILL_DIR.parent.parent / "agents" / "catalogue-describer.md"
# A command as the prose writes it: the entry point, an optional --library.
INVOKED = re.compile(r"\.venv/bin/catalogue (?:--library \S+ )?([a-z]+)")


def text(p: Path) -> str:
    """A file as one line, so an assertion is not defeated by a line wrap."""
    return " ".join(p.read_text(encoding="utf-8").split())


def section(p: Path, heading: str) -> str:
    match = re.search(rf"^##+ {re.escape(heading)}\n(.*?)(?=^## |\Z)",
                      p.read_text(encoding="utf-8"), re.M | re.S)
    assert match, heading
    return " ".join(match.group(1).split())


@pytest.fixture(scope="module")
def commands() -> set[str]:
    """The commands the entry point actually has."""
    found = catalogue.commands()
    assert {"sync", "describe", "unused", "remove", "merge", "rename", "peek"} <= found
    return found


def test_the_skill_documents_every_command_and_only_those(commands):
    table = section(SKILL, "The commands")
    documented = set(re.findall(r"\| `([a-z]+)\b", table))
    assert documented == commands


@pytest.mark.parametrize("path", [SKILL, RULES, AGENT], ids=lambda p: p.name)
def test_every_command_the_prose_runs_exists(path, commands):
    used = set(INVOKED.findall(path.read_text(encoding="utf-8")))
    assert used, path.name
    assert used <= commands, used - commands
    inline = set(re.findall(r"`([a-z]+) <", path.read_text(encoding="utf-8")))
    assert inline <= commands | {"make"}, inline - commands


def test_the_skill_states_its_refusals():
    refuses = section(SKILL, "What this skill refuses")
    for refusal in ("Changing a source's content", "Writing an id by hand",
                    "An id in `document/`", "Describing a file from its name",
                    "Removing, renaming or moving without the user's word"):
        assert refusal in refuses, refusal


def test_cleaning_up_and_renaming_wait_for_the_user():
    cleaning = section(SKILL, "Cleaning up, on the user's word")
    assert "Only when the user asks" in cleaning
    assert "`remove` exactly the items confirmed" in cleaning
    renaming = section(SKILL, "Renaming, on the user's word")
    assert "only those the user accepts" in renaming
    assert "The original name stays in the manifest" in renaming
    moving = section(SKILL, "Moving, on the user's word")
    assert "done on the user's word" in moving
    assert "The id, the name and the description go with the file" in moving


def test_the_skill_says_when_to_turn_to_the_user():
    asking = section(SKILL, "When to turn to the user")
    for case in ("A new source whose nature is unclear", "A vanished source",
                 "Something hard to identify", "A name to find"):
        assert case in asking, case


def test_the_skill_teaches_splitting_and_merging():
    items = section(SKILL, "Splitting and merging items")
    assert "**Split**" in items and "**Merge**" in items
    assert "`merge <item>…`" in items


def test_one_rulebook_serves_the_skill_and_its_agent():
    for path in (SKILL, AGENT):
        assert "references/describing.md" in text(path), path.name
    rules = text(RULES)
    for heading in ("Look before you write", "The name", "The description", "The id"):
        assert f"## {heading}" in RULES.read_text(encoding="utf-8"), heading
    assert "Never from the file's name alone" in rules


def test_the_agent_describes_and_never_acts_on_files():
    front = AGENT.read_text(encoding="utf-8").split("---")[1]
    assert re.search(r"^tools: Read, Bash$", front, re.M)
    never = section(AGENT, "Never")
    for act in ("Rename, remove, merge, move or sync", "Edit a file", "Guess"):
        assert act in never, act
    assert "Questions for the user:" in text(AGENT)
    assert "Rename proposals:" in text(AGENT)
