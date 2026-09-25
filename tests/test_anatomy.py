"""The guard that keeps a document's anatomy — docs/architecture.md §11.

A convention with no enforcement holds until the next script is written, and
this repository has twice proved it: `sources/` became a miscellany one script
at a time, and a figure generator sat in it for weeks because nothing could say
it should not.

The anatomy itself — five roles at a document's root, nothing derived in the
user's `sources/`, code in `generators/` — is a property of the user's library,
and `make check-library` reports it (core/library.py, tests/test_library.py).
What is tested here is the guard: the PreToolUse hook that refuses an edit by
hand where the anatomy forbids one. It decides on the shape of a path alone, so
it is probed under a project root that exists only for the probe, never on the
user's library.
"""
import json
import subprocess

import pytest

from core import doc


def probe(repo, root, path):
    """What the PreToolUse guard answers for one write, in the project `root`."""
    out = subprocess.run(["bash", str(repo / ".claude/hooks/protect-paths.sh")],
                         input=json.dumps({"tool_input": {"file_path": str(path)}}),
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent",
                              "CLAUDE_PROJECT_DIR": str(root)})
    return out.returncode


@pytest.fixture
def document(tmp_path):
    """A document root under a project's `library/` — a path, no files."""
    return tmp_path / "library" / "topic" / "slug"


def test_the_guard_refuses_a_write_into_the_users_sources(repo, tmp_path, document):
    assert probe(repo, tmp_path, document / doc.SOURCES / "invented.md") == 2


def test_the_guard_refuses_a_write_into_the_disposable_directory(repo, tmp_path,
                                                                 document):
    assert probe(repo, tmp_path, document / doc.WORK / "review" / "sheet-01.png") == 2


def test_the_guard_allows_what_belongs_to_the_agent(repo, tmp_path, document):
    for role in (doc.DOCUMENT, doc.STUDY, doc.GENERATORS):
        assert probe(repo, tmp_path, document / role / "a-file.md") == 0, role


def test_the_guard_still_finds_an_investigation_after_the_journal_moved(repo,
                                                                        tmp_path):
    # `NOTES.md` moved to `study/` when the anatomy landed, and the guard looked
    # for it beside `raw/`: the pieces of every investigation stopped being
    # protected, in silence. Both shapes are recognised now.
    for journal in (doc.STUDY + "/NOTES.md", "NOTES.md"):
        root = tmp_path / journal.replace("/", "-") / "library" / "t" / "enquete"
        (root / "raw").mkdir(parents=True)
        (root / journal).parent.mkdir(parents=True, exist_ok=True)
        (root / journal).write_text("journal", encoding="utf-8")
        assert probe(repo, repo, root / "raw" / "page.html") == 2, journal
