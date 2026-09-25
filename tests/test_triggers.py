"""Every skill's description against the trigger check of docs/architecture.md §5.

A description is all a session reads before deciding to load a skill, and a
skill that fires on a neighbour's job is worse than no skill. So each
description carries a phrase no other description carries, names at least
one neighbour it must not be confused with, and says what is not its job.

`DISCRIMINATORS` is the table these tests hold. A skill added under
`.claude/skills/` fails the first test until it has a row — which is how a new
skill inherits the check. The `discussion` skill's own test stays: this one
generalises it.
"""
import re

import pytest

DISCRIMINATORS = {
    # `epub` says "the paginated PDF" in its negative clause, so the phrase
    # is the longer one. A phrase only counts where it is said positively.
    "pdf": ("paginated PDF document", "shared art direction"),
    "epub": ("reflowable EPUB", "e-reader"),
    "fetch": ("known by its URL",),
    "sourcing": ("established and cross-checked",),
    "discussion": ("before its document exists",
                   "pasted out of conversations with other agents"),
    "translate": ("already in this library, in place",),
    "session-review": ("once it is finished",),
}

# The neighbours each description must name, from the overlaps met in real
# sessions (suite-and-review, phase 2): `discussion`'s opening request also
# reads as "create a document"; a PDF behind a URL loads `fetch`, which then
# refuses it; a review of a task is not a review of a PDF.
NEIGHBOURS = {
    "pdf": {"epub", "sourcing", "translate", "fetch", "discussion"},
    "epub": {"pdf"},
    "fetch": {"sourcing", "translate", "pdf"},
    "sourcing": {"fetch", "pdf"},
    "discussion": {"sourcing", "pdf"},
    "translate": {"pdf", "fetch"},
    "session-review": {"pdf"},
}


def descriptions(repo) -> dict[str, str]:
    found = {}
    for skill_md in sorted((repo / ".claude" / "skills").glob("*/SKILL.md")):
        # Read as a line, the way Claude Code reads it: several descriptions
        # hold a `: ` and are not valid YAML.
        front = skill_md.read_text(encoding="utf-8").split("---")[1]
        found[skill_md.parent.name] = re.search(
            r"^description: (.*)$", front, re.M).group(1)
    return found


def test_every_skill_has_a_row(repo):
    assert set(descriptions(repo)) == set(DISCRIMINATORS) == set(NEIGHBOURS)


@pytest.mark.parametrize("skill", sorted(DISCRIMINATORS))
def test_the_description_carries_a_phrase_no_other_does(repo, skill):
    every = descriptions(repo)
    for phrase in DISCRIMINATORS[skill]:
        assert phrase in every[skill], phrase
        for other, text in every.items():
            if other != skill:
                assert phrase not in text, (other, phrase)


@pytest.mark.parametrize("skill", sorted(DISCRIMINATORS))
def test_the_description_names_a_neighbour_and_what_is_not_its_job(repo, skill):
    every = descriptions(repo)
    named = set(re.findall(r"`([a-z-]+)`", every[skill])) & set(every)
    assert NEIGHBOURS[skill] <= named, NEIGHBOURS[skill] - named
    assert re.search(r"\b(Not for|not|never)\b", every[skill]), skill


def test_the_trigger_table_has_a_row_for_every_skill(repo):
    text = (repo / "docs" / "architecture.md").read_text(encoding="utf-8")
    table = text.split("### The trigger check", 1)[1].split("\n\n", 3)[2]
    rows = set(re.findall(r"^\| `([a-z-]+)` \|", table, re.M))
    assert rows == set(DISCRIMINATORS)
