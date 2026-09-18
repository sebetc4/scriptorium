"""The sweep, the ledger it writes, and the coverage it makes possible.

A ledger is written from outside the session it describes, one session late,
because `SessionEnd` does not fire for a session that crashed or was killed —
the sessions whose cost is most worth knowing. Everything awkward about the
sweep follows from that, and is tested here.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

import corpus
import metrics
from test_metrics import Transcript, stamp, tool, usage

ROOT = Path(__file__).resolve().parents[3].parent
HOOK = ROOT / ".claude" / "hooks" / "session-ledger.sh"


@pytest.fixture
def project(tmp_path):
    """A projects directory holding one project's transcripts."""
    folder = tmp_path / "projects" / metrics.project_slug()
    folder.mkdir(parents=True)
    return folder


def session(folder, name, turns=5, **kw):
    t = Transcript(folder / f"{name}.jsonl")
    for i in range(turns):
        t.assistant(i, [{"type": "text", "text": "."}], use=usage(**kw))
    return t.write()


# --- the sweep ---------------------------------------------------------------

def test_a_session_that_crashed_is_found_by_the_next_one(project, tmp_path):
    # Nothing marks the crashed session as finished: the sweep does not ask.
    session(project, "crashed")
    written = metrics.sweep(tmp_path / "projects", tmp_path / "ledger",
                            live="the-session-running-the-hook")
    assert written == ["crashed"]
    assert (tmp_path / "ledger" / "crashed.json").exists()


def test_the_live_session_writes_no_ledger_for_itself(project, tmp_path):
    session(project, "live")
    ledger = tmp_path / "ledger"
    assert metrics.sweep(tmp_path / "projects", ledger, live="live") == []
    assert not (ledger / "live.json").exists()


def test_the_next_session_writes_the_complete_one(project, tmp_path):
    path = session(project, "live", turns=3)
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger, live="live")

    # The session goes on, then ends. The next session sweeps it whole.
    t = Transcript(path)
    for i in range(9):
        t.assistant(i, [{"type": "text", "text": "."}])
    t.write()
    assert metrics.sweep(tmp_path / "projects", ledger, live="another") == ["live"]
    assert json.loads((ledger / "live.json").read_text())["turns"] == 9


def test_a_session_of_fewer_than_three_turns_leaves_no_entry(project, tmp_path):
    session(project, "stub", turns=2)
    assert metrics.sweep(tmp_path / "projects", tmp_path / "ledger") == []


def test_a_transcript_that_has_not_grown_is_not_swept_again(project, tmp_path):
    session(project, "s")
    ledger = tmp_path / "ledger"
    assert metrics.sweep(tmp_path / "projects", ledger) == ["s"]
    assert metrics.sweep(tmp_path / "projects", ledger) == []


def test_a_transcript_that_grew_is_swept_again(project, tmp_path):
    path = session(project, "s")
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "assistant", "timestamp": stamp(99),
                             "message": {"id": "extra", "usage": {},
                                         "content": [{"type": "text",
                                                      "text": "."}]}}) + "\n")
    assert metrics.sweep(tmp_path / "projects", ledger) == ["s"]


def test_a_damaged_entry_is_swept_again_rather_than_trusted(project, tmp_path):
    session(project, "s")
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    (ledger / "s.json").write_text("{ truncated", encoding="utf-8")
    assert metrics.sweep(tmp_path / "projects", ledger) == ["s"]


# --- the sweep's bounds ------------------------------------------------------

def test_the_sweep_takes_the_top_level_transcripts_and_nothing_else(project,
                                                                    tmp_path):
    session(project, "s")
    for hidden in ("memory", "s/subagents"):
        folder = project / hidden
        folder.mkdir(parents=True, exist_ok=True)
        session(folder, "agent-a1")
    assert metrics.sweep(tmp_path / "projects", tmp_path / "ledger") == ["s"]


def test_the_ledger_holds_numbers_and_no_prose(project, tmp_path):
    t = Transcript(project / "s.jsonl")
    for i in range(4):
        t.assistant(i, [tool("Bash", tid=f"t{i}",
                             command=f"echo {i}",
                             description="a secret the ledger must not keep")])
        t.user(i + 0.5, [{"type": "text", "text": "do not record this either"}])
    t.write()
    metrics.sweep(tmp_path / "projects", tmp_path / "ledger")
    written = (tmp_path / "ledger" / "s.json").read_text(encoding="utf-8")
    assert "secret" not in written and "do not record" not in written
    assert "echo 0" not in written          # not even the commands
    assert json.loads(written)["tools"] == {"Bash": 4}


# --- the hook ----------------------------------------------------------------

def test_the_hook_does_nothing_and_says_nothing_without_a_venv(tmp_path):
    out = subprocess.run(["bash", str(HOOK)], capture_output=True, text=True,
                         env={**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert out.returncode == 0
    assert out.stdout == "" and out.stderr == ""


def test_the_hook_is_wired_into_the_settings():
    settings = json.loads((ROOT / ".claude" / "settings.json")
                          .read_text(encoding="utf-8"))
    commands = [h["command"] for entry in settings["hooks"]["SessionStart"]
                for h in entry["hooks"]]
    assert any("session-ledger.sh" in c for c in commands)


# --- coverage ----------------------------------------------------------------

def review(directory, name, session_id, start, end):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(f"""---
review: 1
date: 2026-09-18
session: {session_id}
slice: {{from: {start}, to: {end}}}
task: A task.
skill: pdf
outcome: delivered
corrections: 0
findings: []
---

Prose.
""", encoding="utf-8")


def test_coverage_names_an_uncovered_slice_by_time(project, tmp_path):
    session(project, "s", turns=10)
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    # The first half of the session was reviewed, the rest was not.
    review(tmp_path / "reviews", "r.md", "s", stamp(0), stamp(4))

    row, = corpus.coverage(corpus.load(tmp_path / "reviews"), ledger)
    assert row["session"] == "s" and row["reviews"] == 1
    (start, end), = row["uncovered"]
    assert start == metrics.when(stamp(4)) and end == metrics.when(stamp(9))
    # By time, never by content: nothing of what was done in the gap is named.
    assert set(row) == {"session", "reviews", "turns", "uncovered"}


def test_a_fully_reviewed_session_has_nothing_uncovered(project, tmp_path):
    session(project, "s", turns=10)
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    review(tmp_path / "reviews", "r.md", "s", stamp(0), stamp(9))
    row, = corpus.coverage(corpus.load(tmp_path / "reviews"), ledger)
    assert row["uncovered"] == []


def test_a_session_nobody_reviewed_is_uncovered_end_to_end(project, tmp_path):
    session(project, "s", turns=10)
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    row, = corpus.coverage([], ledger)
    assert row["reviews"] == 0
    assert row["uncovered"] == [(metrics.when(stamp(0)), metrics.when(stamp(9)))]


def test_a_review_of_another_session_covers_nothing_here(project, tmp_path):
    session(project, "s", turns=10)
    ledger = tmp_path / "ledger"
    metrics.sweep(tmp_path / "projects", ledger)
    review(tmp_path / "reviews", "r.md", "elsewhere", stamp(0), stamp(9))
    row, = corpus.coverage(corpus.load(tmp_path / "reviews"), ledger)
    assert row["reviews"] == 0 and len(row["uncovered"]) == 1
