"""A document holds the five roles and nothing else — docs/architecture.md §11.

A convention with no enforcement holds until the next script is written, and
this repository has twice proved it: `sources/` became a miscellany one script
at a time, and a figure generator sat in it for weeks because nothing could say
it should not.

These tests read `library/`, which is user content kept outside the repository:
on a fresh clone there is nothing to check and they skip, like the rest of the
suite that reads real documents.
"""
import json
import subprocess

import pytest

from core import doc

ROLES = {doc.DOCUMENT, doc.SOURCES, doc.STUDY, doc.GENERATORS, doc.WORK}

# One document keeps an investigation's pieces at its root rather than in
# `sources/`: `electronique/repair/electribe-2/sources` is a `sourcing` session's
# own material promoted to a document, so its root *is* the investigation. The
# anatomy has no place for that shape, and reshaping it would mean rearranging
# user content that nobody asked to have rearranged. Named here so that it is a
# recorded fact rather than a hole in the rule — delete the entry the day the
# document is reshaped, and this test will say whether anything still needs it.
INVESTIGATION_AT_ROOT = {
    "electronique/repair/electribe-2/sources": {"datasheets", "images", "raw",
                                                "threads"},
}


def documents():
    if not doc.LIBRARY.is_dir():
        return []
    return sorted(p.parent.parent
                  for p in doc.LIBRARY.rglob(f"{doc.DOCUMENT}/{doc.ENTRY}"))


def test_the_checks_skip_when_the_library_is_absent(monkeypatch, tmp_path):
    """A fresh clone has no `library/`: there is nothing to check, not a failure."""
    monkeypatch.setattr(doc, "LIBRARY", tmp_path / "nowhere")
    assert documents() == []


@pytest.fixture
def docs():
    found = documents()
    if not found:
        pytest.skip("no document in library/ — user content, outside a clone")
    return found


def test_a_document_root_holds_only_the_five_roles(docs):
    stray = []
    for d in docs:
        rel = str(d.relative_to(doc.LIBRARY))
        allowed = ROLES | INVESTIGATION_AT_ROOT.get(rel, set())
        stray += [f"{rel}: {p.name}" for p in sorted(d.iterdir())
                  if p.name not in allowed]
    assert not stray, "not placed by the anatomy — " + ", ".join(stray)


def test_the_build_reads_document_and_the_entry_is_there(docs):
    for d in docs:
        assert (doc.doc_dir(d) / doc.ENTRY).is_file(), d


def test_no_derived_file_sits_in_the_users_sources(docs):
    # What a tool computes goes to study/; sources/ holds what was received.
    derived = {"extracted.md", "meta.json", "pages"}
    found = [f"{d.relative_to(doc.LIBRARY)}: {name}"
             for d in docs if (d / doc.SOURCES).is_dir()
             for name in derived if (d / doc.SOURCES / name).exists()]
    assert not found, "derived, and in the user's directory — " + ", ".join(found)


def test_no_generator_sits_outside_generators(docs):
    found = [f"{d.relative_to(doc.LIBRARY)}: {p.relative_to(d)}"
             for d in docs
             for p in d.rglob("*.py")
             if p.parent.name != doc.GENERATORS]
    assert not found, "code that draws an asset lives in generators/ — " \
        + ", ".join(found)


# --- the guard -------------------------------------------------------------

def probe(repo, path):
    """What the PreToolUse guard answers for one write."""
    out = subprocess.run(["bash", str(repo / ".claude/hooks/protect-paths.sh")],
                         input=json.dumps({"tool_input": {"file_path": str(path)}}),
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent",
                              "CLAUDE_PROJECT_DIR": str(repo)})
    return out.returncode


def test_the_guard_refuses_a_write_into_the_users_sources(repo, docs):
    assert probe(repo, docs[0] / doc.SOURCES / "invented.md") == 2


def test_the_guard_refuses_a_write_into_the_disposable_directory(repo, docs):
    assert probe(repo, docs[0] / doc.WORK / "review" / "sheet-01.png") == 2


def test_the_guard_allows_what_belongs_to_the_agent(repo, docs):
    for role in (doc.DOCUMENT, doc.STUDY, doc.GENERATORS):
        assert probe(repo, docs[0] / role / "a-file.md") == 0, role


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
        assert probe(repo, root / "raw" / "page.html") == 2, journal
