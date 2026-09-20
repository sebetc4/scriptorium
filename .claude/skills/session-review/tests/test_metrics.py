"""`metrics.py`, against transcripts built line by line in the test.

Nothing here reads a real conversation: the fixtures are written by
`Transcript` below, so this suite passes on a fresh clone, unlike the parts of
the repository's suite that read documents kept outside it.

The first test is the one that matters most. A real transcript writes **one
record per content block of a single assistant message, each repeating the
whole `usage` object**. Summing usage over records inflates every token figure
by the number of blocks the model happened to emit — which is how the review of
2026-09-17 came to record 727,020 cache reads for four delegated passes that
actually read 288,210.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import metrics
from metrics import Slice

T0 = datetime(2026, 9, 18, 10, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[3].parent   # the repository root


def stamp(minutes: float) -> str:
    return (T0 + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def usage(fresh=1000, cached=10000, out=200, thinking=0):
    return {"input_tokens": fresh // 2,
            "cache_creation_input_tokens": fresh - fresh // 2,
            "cache_read_input_tokens": cached,
            "output_tokens": out,
            "output_tokens_details": {"thinking_tokens": thinking}}


class Transcript:
    """A transcript written the way Claude Code writes one."""

    def __init__(self, path: Path):
        self.path = path
        self.lines: list[dict] = []
        self.n = 0

    def assistant(self, at, blocks, use=None, skill=None, error=False):
        """One message, written as one record per content block.

        The repetition is the point: `usage` is identical on each record.
        """
        self.n += 1
        mid = f"msg_{self.n:03d}"
        use = use or usage()
        for block in blocks:
            rec = {"type": "assistant", "timestamp": stamp(at),
                   "requestId": f"req_{self.n:03d}",
                   "uuid": f"u{len(self.lines)}",
                   "message": {"id": mid, "usage": use, "content": [block]}}
            if skill:
                rec["attributionSkill"] = skill
            if error:
                rec["isApiErrorMessage"] = True
            self.lines.append(rec)
        return mid

    def user(self, at, content, result=None):
        rec = {"type": "user", "timestamp": stamp(at),
               "uuid": f"u{len(self.lines)}",
               "message": {"content": content}}
        if result is not None:
            rec["toolUseResult"] = result
        self.lines.append(rec)

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            "".join(json.dumps(r) + "\n" for r in self.lines), encoding="utf-8")
        return self.path


def tool(name, tid="t1", **params):
    return {"type": "tool_use", "id": tid, "name": name, "input": params}


def thinking(text="…"):
    return {"type": "thinking", "thinking": text}


@pytest.fixture
def plain(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [thinking(), tool("Bash", command="make build")],
                use=usage(fresh=1000, cached=10000, out=200, thinking=50),
                skill="pdf")
    t.user(1, [{"type": "tool_result", "tool_use_id": "t1"}])
    t.assistant(2, [{"type": "text", "text": "done"}],
                use=usage(fresh=500, cached=20000, out=100), skill="pdf")
    return t.write()


# --- the deduplication trap --------------------------------------------------

def test_usage_is_counted_once_a_message_not_once_a_record(plain):
    t = metrics.scan(plain, Slice(None, None))
    assert t.turns == 2                  # not 3, though three records exist
    assert t.fresh == 1500               # not 2500
    assert t.cache_read == 30000         # not 40000
    assert t.output == 300
    assert t.thinking == 50


def test_content_blocks_are_not_deduplicated(plain):
    # The blocks of one message really are distinct, unlike its usage.
    t = metrics.scan(plain, Slice(None, None))
    assert t.tools["Bash"] == 1
    assert t.skills["pdf"] == 2


# --- the slice ---------------------------------------------------------------

def test_the_slice_bounds_what_is_counted(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    for i in range(4):
        t.assistant(i * 10, [tool("Bash", tid=f"t{i}", command=f"echo {i}")])
    path = t.write()
    window = Slice(metrics.when(stamp(5)), metrics.when(stamp(25)))
    assert metrics.scan(path, window).turns == 2


def test_two_consecutive_reviews_produce_disjoint_slices(tmp_path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "r.md").write_text(f"""---
review: 1
date: 2026-09-18
session: s
slice: {{from: {stamp(0)}, to: {stamp(20)}}}
task: The first task.
skill: pdf
outcome: delivered
corrections: 0
findings: []
---

Prose.
""", encoding="utf-8")
    window = metrics.resolve_slice("s", reviews, None, None)
    assert window.start == metrics.when(stamp(20))
    assert not window.holds(metrics.when(stamp(19)))
    assert window.holds(metrics.when(stamp(21)))


def test_the_cursor_ignores_reviews_of_another_session(tmp_path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "r.md").write_text(f"""---
review: 1
date: 2026-09-18
session: somebody-else
slice: {{from: {stamp(0)}, to: {stamp(20)}}}
task: Another session's task.
skill: pdf
outcome: delivered
corrections: 0
findings: []
---

Prose.
""", encoding="utf-8")
    assert metrics.resolve_slice("s", reviews, None, None).start is None


# --- the instrument leaves itself out ----------------------------------------

def test_a_review_tooling_turn_is_excluded(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command="make build")])
    t.user(1, [{"type": "tool_result", "tool_use_id": "t0"}])
    t.assistant(2, [tool("Bash", tid="t1",
                         command=".venv/bin/python …/metrics.py --timeline")])
    t.user(3, [{"type": "tool_result", "tool_use_id": "t1"}],
           result={"type": "image", "file": {"base64": "…"}})
    t.assistant(4, [tool("Write", tid="t2", file_path="reviews/2026-09-18.md")])
    path = t.write()

    m = metrics.scan(path, Slice(None, None))
    assert m.turns == 1                  # only the build turn
    assert m.tools["Bash"] == 1
    assert "Write" not in m.tools
    assert m.images == 0                 # the tooling's own image is not carried


# --- friction ----------------------------------------------------------------

def test_an_interruption_is_counted(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", command="sleep 100")])
    t.user(1, [{"type": "text", "text": "[Request interrupted by user]"}])
    m = metrics.scan(t.write(), Slice(None, None))
    assert m.interruptions == 1


def test_an_api_error_is_counted(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [{"type": "text", "text": "API Error"}], error=True)
    assert metrics.scan(t.write(), Slice(None, None)).api_errors == 1


def test_a_shape_this_corpus_never_showed_is_written_as_nothing(plain):
    # No permission denial was ever observed on this project's transcripts, so
    # the counter is omitted rather than printed as a measured zero.
    block = "\n".join(metrics.yaml_block(metrics.scan(plain, Slice(None, None)), []))
    assert "denials" not in block
    assert "interruptions: 0" in block   # this shape *was* confirmed


def test_an_absent_measure_is_absent_from_the_block(plain):
    block = "\n".join(metrics.yaml_block(metrics.scan(plain, Slice(None, None)), []))
    assert "images" not in block
    assert "subagents" not in block


# --- subagents ---------------------------------------------------------------

def test_a_subagent_run_is_read_from_its_own_transcript(tmp_path):
    main = Transcript(tmp_path / "s.jsonl")
    main.assistant(0, [tool("Agent", tid="t0", description="review it")])
    main.write()

    inner = Transcript(tmp_path / "s" / "subagents" / "agent-a1.jsonl")
    inner.assistant(1, [thinking(), tool("Read", file_path="out/x.pdf")],
                    use=usage(fresh=4000, cached=50000))
    inner.assistant(2, [{"type": "text", "text": "two defects"}],
                    use=usage(fresh=1000, cached=60000))
    inner.write()
    (tmp_path / "s" / "subagents" / "agent-a1.meta.json").write_text(
        json.dumps({"agentType": "pdf-reviewer"}), encoding="utf-8")

    runs = metrics.subagent_runs(tmp_path / "s.jsonl", Slice(None, None))
    assert runs == [{"type": "pdf-reviewer", "fresh": 5000,
                     "cache_read": 110000, "seconds": 60}]


def test_a_subagent_outside_the_slice_is_not_counted(tmp_path):
    main = Transcript(tmp_path / "s.jsonl")
    main.assistant(0, [tool("Agent", description="review it")])
    main.write()
    inner = Transcript(tmp_path / "s" / "subagents" / "agent-a1.jsonl")
    inner.assistant(90, [{"type": "text", "text": "later"}])
    inner.write()
    (tmp_path / "s" / "subagents" / "agent-a1.meta.json").write_text(
        json.dumps({"agentType": "pdf-reviewer"}), encoding="utf-8")
    window = Slice(None, metrics.when(stamp(10)))
    assert metrics.subagent_runs(tmp_path / "s.jsonl", window) == []


# --- derived -----------------------------------------------------------------

def test_an_idle_gap_is_left_out_of_the_active_minutes(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    for at in (0, 2, 4, 90, 92):         # a 86-minute gap in the middle
        t.assistant(at, [{"type": "text", "text": "."}])
    m = metrics.scan(t.write(), Slice(None, None))
    active = dict((name, value) for name, value, _ in metrics.derived(m))
    assert active["active_minutes"] == 6


def test_every_derived_measure_states_its_rule(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command="make build")])
    t.assistant(1, [tool("Bash", tid="t1", command="make build")])
    t.assistant(2, [tool("Read", tid="t2", file_path="a.md")])
    t.assistant(3, [tool("Read", tid="t3", file_path="a.md")])
    m = metrics.scan(t.write(), Slice(None, None))
    rows = metrics.derived(m)
    assert all(rule and rule.strip() for _, _, rule in rows)
    got = {name: value for name, value, _ in rows}
    assert got["repeated_bash"] == 1
    assert got["files_read_twice"] == 1
    assert got["build_cycles"] == 2


def test_an_image_is_paid_for_again_on_every_later_call(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Read", tid="t0", file_path="a.png")])
    t.user(1, [{"type": "tool_result", "tool_use_id": "t0"}],
           result={"type": "image", "file": {"base64": "…"}})
    for at in (2, 3, 4):
        t.assistant(at, [{"type": "text", "text": "."}])
    m = metrics.scan(t.write(), Slice(None, None))
    assert m.images == 1
    assert m.image_carry == 3 * metrics.IMAGE_TOKENS


# --- output ------------------------------------------------------------------

def test_no_baseline_yet_is_said_rather_than_shown_as_zero(plain, tmp_path):
    rows = metrics.baselines(metrics.scan(plain, Slice(None, None)), [], [], "pdf")
    assert rows == ["# no baseline yet: fewer than two earlier reviews of this skill"]


def test_a_baseline_flags_a_measure_over_one_and_a_half_times_the_median(tmp_path):
    import corpus
    reviews = corpus.load(Path(__file__).parent / "fixtures")
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [{"type": "text", "text": "."}],
                use=usage(fresh=400000, cached=1000))
    m = metrics.scan(t.write(), Slice(None, None))
    rows = "\n".join(metrics.baselines(m, [], reviews, "pdf"))
    assert "tokens.fresh" in rows and "over 1.5×" in rows


def test_the_whole_output_stays_under_fifty_lines(tmp_path, capsys):
    t = Transcript(tmp_path / "s.jsonl")
    for i in range(40):
        t.assistant(i, [tool(f"Tool{i}", tid=f"t{i}", command=f"echo {i}")])
    path = t.write()
    metrics.main(["--transcript", str(path), "--reviews", str(tmp_path / "none")])
    assert len(capsys.readouterr().out.splitlines()) <= metrics.MAX_LINES + 1


def test_the_timeline_is_truncated(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", command="x", description="y" * 300)])
    rows = metrics.timeline(metrics.scan(t.write(), Slice(None, None)))
    assert len(rows) == 1 and len(rows[0]) <= 60 + 12


# --- the ledger --------------------------------------------------------------

def test_the_ledger_is_numbers_and_the_size_it_was_read_from(plain, capsys):
    metrics.main(["--transcript", str(plain), "--ledger"])
    entry = json.loads(capsys.readouterr().out)
    assert entry["turns"] == 2 and entry["fresh"] == 1500
    assert entry["bytes"] == plain.stat().st_size
    assert set(entry) == {"session", "bytes", "from", "to", "turns", "fresh",
                          "cache_read", "subagents", "tools", "skills"}


def test_the_ledger_ignores_the_review_cursor(tmp_path):
    # A ledger describes a whole transcript, not a task: it is written from
    # outside the session, by a sweep that knows nothing of any slice.
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [{"type": "text", "text": "."}])
    t.assistant(50, [{"type": "text", "text": "."}])
    path = t.write()
    out = subprocess.run([sys.executable, str(ROOT / ".claude/skills/"
                          "session-review/scripts/metrics.py"),
                          "--transcript", str(path), "--ledger"],
                         capture_output=True, text=True, cwd=ROOT)
    assert json.loads(out.stdout)["turns"] == 2


# --- refusing to guess -------------------------------------------------------

def test_without_a_session_it_fails_rather_than_guessing(capsys):
    with pytest.raises(SystemExit):
        metrics.main(["--session", "", "--reviews", "/nowhere"])
    assert "never guesses" in capsys.readouterr().err


# --- running the instrument, versus working on it ----------------------------

def test_a_turn_that_edits_the_instrument_is_the_task(tmp_path):
    """The exclusion is there so a review does not bill a task for the cost of
    reviewing it. Work *on* the review tooling is a task like any other, and
    the first version could not tell the two apart: it matched any mention of a
    path, so the four phases that built this instrument measured a third short.
    """
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Edit", tid="t0",
                         file_path=".claude/skills/session-review/scripts/metrics.py")])
    t.assistant(1, [tool("Bash", tid="t1", command=(
        ".venv/bin/python -m pytest -q .claude/skills/session-review/tests"))])
    t.assistant(2, [tool("Bash", tid="t2", command=(
        "cat .claude/skills/session-review/scripts/corpus.py"))])
    t.assistant(3, [tool("Bash", tid="t3", command=(
        "grep -n 'median' .claude/skills/session-review/scripts/corpus.py"))])
    t.assistant(4, [tool("Read", tid="t4",
                         file_path=".claude/skills/session-review/references/format.md")])
    m = metrics.scan(t.write(), Slice(None, None))
    assert m.turns == 5
    assert m.tools["Bash"] == 3
    assert m.tools["Edit"] == 1


def test_a_turn_that_runs_the_instrument_is_not_the_task(tmp_path):
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command="make build")])
    for i, command in enumerate((
            ".venv/bin/python .claude/skills/session-review/scripts/metrics.py --owed",
            "cd /code/x && .venv/bin/python .claude/skills/session-review/scripts/corpus.py",
            ".venv/bin/python .claude/skills/session-review/scripts/aggregate.py --coverage",
    ), start=1):
        t.assistant(i, [tool("Bash", tid=f"t{i}", command=command)])
    t.assistant(4, [tool("Write", tid="t4", file_path="reviews/2026-09-20-x.md")])
    t.assistant(5, [{"type": "tool_use", "id": "t5", "name": "Skill",
                     "input": {"skill": "session-review"}}])
    m = metrics.scan(t.write(), Slice(None, None))
    assert m.turns == 1                  # only the build
    assert m.tools["Bash"] == 1
    assert "Write" not in m.tools and "Skill" not in m.tools


def test_a_command_quoted_inside_a_heredoc_is_not_a_run(tmp_path):
    """A heredoc body is part of the Bash command string, so writing a test
    that quotes a run of the instrument read as running it. What the shell
    executes is everything outside the bodies — including whatever follows
    one, which is why the body is removed rather than the command truncated.
    """
    t = Transcript(tmp_path / "s.jsonl")
    t.assistant(0, [tool("Bash", tid="t0", command=(
        "cat > .claude/skills/session-review/tests/test_x.py <<'EOF'\n"
        "def test_it():\n"
        "    assert is_tooling(command='.venv/bin/python …/metrics.py')\n"
        "EOF"))])
    t.assistant(1, [tool("Bash", tid="t1", command=(
        "cat > note.md <<'EOF'\nprose\nEOF\n"
        ".venv/bin/python .claude/skills/session-review/scripts/metrics.py"))])
    t.assistant(2, [tool("Bash", tid="t2", command=(
        ".venv/bin/python .claude/skills/session-review/scripts/metrics.py"))])
    m = metrics.scan(t.write(), Slice(None, None))
    assert m.turns == 1                  # only the heredoc that writes a test
    assert m.tools["Bash"] == 1
