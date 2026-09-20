#!/usr/bin/env python3
"""One task's slice of a transcript, turned into the `measured:` block.

This script counts and never judges. It names no cause, calls no number bad,
and writes no prose. Everything it prints is either read from the transcript or
derived from what was read by a rule printed beside it.

Three properties of the transcript govern the whole file, and each was verified
against this project's own sessions rather than taken from documentation:

- **One assistant message is written as one record per content block, and every
  one of those records repeats the same `usage`.** Summing usage over assistant
  records therefore counts one API call two or three times. Usage is
  deduplicated by `message.id`; content blocks are not, because they really are
  distinct.
- **A subagent has its own transcript**, in `<session>/subagents/agent-<id>.jsonl`
  beside a `.meta.json` carrying its `agentType`. Delegated cost is the largest
  item of a review session and the one most often guessed; here it is read.
- **A record shape this corpus could never confirm is not counted.** A measure
  that is absent from the output means “this transcript does not record it”. A
  zero means “counted, found none”. The distinction is the format's, it is
  load-bearing for every median computed afterwards, and it is why `denials`
  below is emitted only when something was actually found.

Usage:

    metrics.py                     # this session, since its last review
    metrics.py --from <ISO> --to <ISO>
    metrics.py --timeline          # what happened, one truncated line a step
    metrics.py --ledger            # session-level JSON, for the ledger hook
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import corpus  # noqa: E402  (same directory, not an installed package)
from core.doc import ROOT  # noqa: E402

PROJECTS = Path.home() / ".claude" / "projects"
LEDGER = corpus.REVIEWS / ".ledger"

# A session shorter than this leaves nothing worth a ledger entry: a start that
# was abandoned, a question answered in one turn.
MIN_TURNS = 3

# Derived measures and their rules. The rule travels with the number because a
# derived measure is an opinion with a number attached, and the rule is what
# makes it arguable.
IDLE_MINUTES = 5
IMAGE_TOKENS = 1600          # what a page image costs, from pdf/scripts/review.py
MAX_LINES = 50               # the session that runs this pays for every line

# A turn that *ran* the review tooling, or wrote into the corpus, is not part of
# the task being reviewed. Without this the instrument measures itself.
#
# Running is the act, not the subject: a command that executes one of these
# scripts, the skill being invoked, a write into `reviews/`. Reading, editing or
# testing those same files is work **on** the instrument, and work on the
# instrument is a task like any other. The first rule matched any mention of a
# path, so it could not tell the two apart — and the four phases that built this
# script measured 106 API calls of 147 and 43 Bash calls of 125, always short,
# always in the flattering direction.
#
# What the rule still cannot tell apart, knowingly: a direct run of one of these
# scripts to *test* it. `-m pytest` is excluded by form, a manual smoke run is
# not. A slice is bounded by the previous review's `to`, so a review lands at the
# start of the *next* task's slice — which is what this rule protects. The
# alternative considered was to switch the exclusion off in a slice that holds no
# write under `reviews/`, and it would have recovered the seven such runs in the
# 2026-09-18 reference window. It is not in: it would still under-count a slice
# that builds the instrument *and* reviews with it — the very case that produced
# this bug — and the only sessions it mis-measures at all are the ones working on
# `session-review` itself. Reopen it once the corpus holds reviews of sessions
# that genuinely re-read something; until then a review of such a session says so
# in prose.
TOOLING_SCRIPTS = ("metrics.py", "corpus.py", "aggregate.py")
# A python interpreter, its flags, then a path ending in one of those scripts.
# `-m pytest <path>` does not match: the token after the flags is `pytest`.
RUNS_TOOLING = re.compile(
    r"(?:^|[|&;]|\s)(?:\S*\bpython[\d.]*|\S*/\w+\.py)\s+(?:-\S+\s+)*"
    r"\S*(?:" + "|".join(t.replace(".", r"\.") for t in TOOLING_SCRIPTS) + r")\b")
# `<<EOF`, `<< "EOF"`, `<<-EOF` — the word that opens a heredoc, but not the
# `<<<` of a here-string, whose body is a single word on the same line.
HEREDOC = re.compile(r"""(?<!<)<<-?\s*(['"]?)(\w+)\1(?!<)""")


def runnable(command: str) -> str:
    """The command as the shell runs it, with every heredoc body removed.

    A heredoc body is part of the Bash command string, so writing a test file
    with `cat > … <<'EOF'` whose body quotes a run of this script reads as
    running it. Only the bodies are dropped, never the tail: a real command
    after a heredoc still counts, and dropping it would under-count in the
    flattering direction the comment above warns about.
    """
    kept, pending = [], []
    for line in command.split("\n"):
        if pending:
            if line.strip() == pending[0]:
                pending.pop(0)
            continue
        kept.append(line)
        pending.extend(m.group(2) for m in HEREDOC.finditer(line))
    return "\n".join(kept)


def die(message: str) -> None:
    print(f"metrics: {message}", file=sys.stderr)
    raise SystemExit(2)


def project_slug(root: Path = ROOT) -> str:
    """`/code/claude/scriptorium` → `-code-claude-scriptorium`."""
    return str(root.resolve()).replace("/", "-")


def transcript_of(session: str, projects: Path = PROJECTS) -> Path:
    path = projects / project_slug() / f"{session}.jsonl"
    if not path.exists():
        die(f"no transcript for session {session} under {path.parent}")
    return path


def when(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def records(path: Path):
    """Every record of a transcript, in order, malformed lines skipped.

    A transcript flushes live, about two seconds behind: the last line can be
    half-written when this runs, which is a truncated line and not a corrupt
    session.
    """
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


# --- the slice ---------------------------------------------------------------

@dataclass(frozen=True)
class Slice:
    start: datetime | None
    end: datetime | None

    def holds(self, ts: datetime | None) -> bool:
        if ts is None:
            return False
        if self.start and ts < self.start:
            return False
        if self.end and ts > self.end:
            return False
        return True


def resolve_slice(session: str, reviews_dir: Path, start: str | None,
                  end: str | None) -> Slice:
    """One task, one review: a review starts where the previous one stopped.

    Nothing is inferred from the shape of the conversation — no heuristic on
    which user message opens a new task. The default is a cursor, and the
    override is explicit.
    """
    if start:
        first = when(start) or die(f"--from is not a timestamp: {start}")
    else:
        first = None
        try:
            for review in corpus.load(reviews_dir):
                if review.meta.get("session") != session:
                    continue
                stop = when(str(review.meta["slice"]["to"]))
                if stop and (first is None or stop > first):
                    first = stop
        except corpus.ReviewError as e:
            die(f"the corpus is unreadable, so the cursor cannot be read: {e}")
    return Slice(first, when(end) if end else None)


# --- counting ----------------------------------------------------------------

@dataclass
class Tally:
    fresh: int = 0
    cache_read: int = 0
    output: int = 0
    thinking: int = 0
    turns: int = 0
    context_peak: int = 0
    tools: Counter = field(default_factory=Counter)
    skills: Counter = field(default_factory=Counter)
    images: int = 0
    files_written: int = 0
    interruptions: int = 0
    api_errors: int = 0
    denials: int = 0
    bash: Counter = field(default_factory=Counter)
    reads: Counter = field(default_factory=Counter)
    builds: int = 0
    reviews: int = 0
    image_carry: int = 0
    stamps: list = field(default_factory=list)
    timeline: list = field(default_factory=list)


def is_tooling(block: dict) -> bool:
    """Whether this tool call ran the review tooling rather than the task."""
    name, params = block.get("name"), block.get("input") or {}
    if name == "Bash":
        return bool(RUNS_TOOLING.search(runnable(str(params.get("command", "")))))
    if name == "Skill":
        return str(params.get("skill", "")).endswith("session-review")
    if name in ("Write", "Edit", "NotebookEdit"):
        path = str(params.get("file_path") or params.get("notebook_path") or "")
        return path.startswith("reviews/") or "/reviews/" in path
    return False


def tooling_messages(path: Path, window: Slice) -> set[str]:
    """The ids of the messages that ran the review tooling.

    A first pass, because one message is written as one record per content
    block: its tool call and its thinking sit in different records, and
    skipping record by record would drop the call while still counting the
    turn. What is excluded is a turn, not a line of the file.
    """
    found = set()
    for rec in records(path):
        if rec.get("type") != "assistant" or not window.holds(when(rec.get("timestamp"))):
            continue
        message = rec.get("message") or {}
        content = message.get("content")
        blocks = content if isinstance(content, list) else []
        if any(b.get("type") == "tool_use" and is_tooling(b) for b in blocks):
            found.add(message.get("id") or rec.get("requestId") or rec.get("uuid"))
    return found


def scan(path: Path, window: Slice) -> Tally:
    t = Tally()
    seen: set[str] = set()          # message ids whose usage is already counted
    skip: set[str] = set()          # tool_use ids belonging to the tooling
    tooling = tooling_messages(path, window)
    image_at: list[int] = []        # the API call each image arrived on

    for rec in records(path):
        ts = when(rec.get("timestamp"))
        if not window.holds(ts):
            continue
        kind = rec.get("type")
        message = rec.get("message") or {}
        content = message.get("content")
        blocks = content if isinstance(content, list) else []

        if kind == "assistant":
            if rec.get("isApiErrorMessage"):
                t.api_errors += 1
            tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
            mid = message.get("id") or rec.get("requestId") or rec.get("uuid")
            if mid in tooling:
                skip.update(b.get("id", "") for b in tool_uses)
                continue

            usage = message.get("usage") or {}
            if mid not in seen:
                seen.add(mid)
                t.turns += 1
                t.stamps.append(ts)
                fresh = (usage.get("input_tokens") or 0) \
                    + (usage.get("cache_creation_input_tokens") or 0)
                cached = usage.get("cache_read_input_tokens") or 0
                t.fresh += fresh
                t.cache_read += cached
                t.output += usage.get("output_tokens") or 0
                t.thinking += (usage.get("output_tokens_details")
                               or {}).get("thinking_tokens") or 0
                t.context_peak = max(t.context_peak, fresh + cached)
                if skill := rec.get("attributionSkill"):
                    t.skills[skill] += 1

            for b in tool_uses:
                name = b.get("name", "?")
                t.tools[name] += 1
                params = b.get("input") or {}
                if name == "Bash":
                    command = " ".join(str(params.get("command", "")).split())
                    t.bash[command] += 1
                    if "make build" in command:
                        t.builds += 1
                    if "make review" in command:
                        t.reviews += 1
                elif name == "Read":
                    t.reads[str(params.get("file_path", ""))] += 1
                elif name in ("Write", "Edit", "NotebookEdit"):
                    t.files_written += 1
                if arg := params.get("description") or params.get("prompt"):
                    t.timeline.append((ts, f"{name}: {arg}"))
                else:
                    t.timeline.append((ts, name))

        elif kind == "user":
            texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
            if isinstance(content, str):
                texts.append(content)
            if any("Request interrupted" in x for x in texts):
                t.interruptions += 1
            # The permission-denial shape was never observed on this project's
            # transcripts. Its counter is therefore emitted only when something
            # matched: a zero here would claim a measurement nobody has made.
            if any("user doesn't want to take this action" in x
                   or "tool use was rejected" in x for x in texts):
                t.denials += 1
            if any(b.get("tool_use_id") in skip for b in blocks):
                continue
            result = rec.get("toolUseResult")
            found = sum(1 for b in blocks if b.get("type") == "image")
            if isinstance(result, dict) and result.get("type") == "image":
                found = max(found, 1)
            if found:
                t.images += found
                image_at.extend([t.turns] * found)

    # An image is paid for again on every later API call it stays in context.
    t.image_carry = sum(IMAGE_TOKENS * max(t.turns - at, 0) for at in image_at)
    return t


# --- subagents ---------------------------------------------------------------

def subagent_runs(path: Path, window: Slice) -> list[dict]:
    """One entry per run, never aggregated: a review prices a single pass."""
    runs = []
    folder = path.with_suffix("") / "subagents"
    if not folder.is_dir():
        return runs
    for meta_path in sorted(folder.glob("agent-*.meta.json")):
        transcript = meta_path.with_name(meta_path.name.replace(".meta.json",
                                                               ".jsonl"))
        if not transcript.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        inner = scan(transcript, Slice(None, None))
        stamps = [s for s in inner.stamps if s]
        if not stamps or not window.holds(stamps[0]):
            continue
        run = {"type": meta.get("agentType", "?"),
               "fresh": inner.fresh, "cache_read": inner.cache_read}
        if len(stamps) > 1:
            run["seconds"] = round((max(stamps) - min(stamps)).total_seconds())
        runs.append(run)
    return runs


# --- output ------------------------------------------------------------------

def yaml_block(t: Tally, runs: list[dict]) -> list[str]:
    out = ["measured:", "  tokens:",
           f"    fresh: {t.fresh}", f"    cache_read: {t.cache_read}",
           f"    output: {t.output}"]
    if t.thinking:
        out.append(f"    thinking: {t.thinking}")
    if runs:
        out.append("  subagents:")
        for r in runs:
            fields = ", ".join(f"{k}: {v}" for k, v in r.items())
            out.append(f"    - {{{fields}}}")
    out.append(f"  turns: {t.turns}")
    if t.tools:
        pairs = ", ".join(f"{k}: {v}" for k, v in t.tools.most_common())
        out.append(f"  tools: {{{pairs}}}")
    if t.images:
        out.append(f"  images: {t.images}")
    if t.files_written:
        out.append(f"  files_written: {t.files_written}")
    if t.skills:
        pairs = ", ".join(f"{k}: {v}" for k, v in t.skills.most_common())
        out.append(f"  skills: {{{pairs}}}")
    friction = [f"interruptions: {t.interruptions}",
                f"api_errors: {t.api_errors}"]
    if t.denials:
        friction.append(f"denials: {t.denials}")
    out.append(f"  friction: {{{', '.join(friction)}}}")

    out.append("  derived:")
    for name, value, rule in derived(t):
        out.append(f"    {name}:")
        out.append(f"      value: {value}")
        out.append(f"      rule: {rule}")
    return out


def derived(t: Tally) -> list[tuple[str, int, str]]:
    stamps = sorted(s for s in t.stamps if s)
    active = 0.0
    for a, b in zip(stamps, stamps[1:]):
        gap = (b - a).total_seconds()
        if gap <= IDLE_MINUTES * 60:
            active += gap
    rows = [
        ("active_minutes", round(active / 60),
         f"wall clock minus every gap over {IDLE_MINUTES} min"),
        ("context_peak", t.context_peak,
         "largest input of one API call, fresh and cached"),
    ]
    if t.images:
        rows.append(("image_carry", t.image_carry,
                     f"{IMAGE_TOKENS} tokens an image times the API calls it "
                     "stayed in context"))
    if t.builds:
        rows.append(("build_cycles", t.builds, "Bash commands running make build"))
    if t.reviews:
        rows.append(("review_cycles", t.reviews,
                     "Bash commands running make review"))
    repeated = sum(n - 1 for n in t.bash.values() if n > 1)
    if repeated:
        rows.append(("repeated_bash", repeated,
                     "identical Bash commands run more than once"))
    twice = sum(1 for n in t.reads.values() if n > 1)
    if twice:
        rows.append(("files_read_twice", twice,
                     "files read again in the same slice"))
    return rows


def baselines(t: Tally, runs: list[dict], reviews: list, skill: str | None,
              own: Path | None = None) -> list[str]:
    """Each measure beside the median of previous reviews of the same skill.

    Printed apart from the block rather than inside it: a median is computed
    from the corpus at the moment a review is written and is never stored in
    one, or a review ends up compared against a baseline it wrote itself.
    """
    mine = {
        "tokens.fresh": t.fresh,
        "tokens.cache_read": t.cache_read,
        "subagents.fresh": sum(r["fresh"] for r in runs) or None,
        "turns": t.turns,
        "images": t.images or None,
        "derived.context_peak": t.context_peak,
    }
    rows = []
    for measure, value in mine.items():
        if value is None:
            continue
        median = corpus.median(reviews, measure, skill=skill, exclude=own)
        if median is None:
            continue
        ratio = value / median if median else 0
        flag = "  ← over 1.5×" if ratio > 1.5 else ""
        rows.append(f"  {measure:<22} {value:>9}  median {median:>9,.0f}"
                    f"  ×{ratio:.2f}{flag}")
    if not rows:
        return ["# no baseline yet: fewer than two earlier reviews of this skill"]
    return ["# this slice against the median of earlier reviews"] + rows


def owed(t: Tally, runs: list[dict], reviews: list, skill: str | None) -> list[str]:
    """The obligations this slice triggers, printed so they cannot be forgotten.

    The skill never asks a session what went wrong — a session grading itself
    gives itself a good mark. It sets duties that the measurements trigger, and
    this is where the triggering happens, in arithmetic rather than in good
    faith.
    """
    rows = []
    costs = {"the main context": t.fresh,
             "cache reads": t.cache_read,
             "the delegated runs": sum(r["fresh"] for r in runs),
             "images carried": t.image_carry,
             "output written": t.output}
    ranked = [name for name, value in
              sorted(costs.items(), key=lambda kv: -kv[1]) if value]

    # With no baseline, the obligation on medians cannot fire. The review does
    # not therefore owe less: it owes the wider account instead, because an
    # obligation that cannot fire is not a lenient obligation, it is an absent
    # one.
    has_baseline = any(
        corpus.median(reviews, m, skill=skill) is not None
        for m in ("tokens.fresh", "turns"))
    top = 3 if has_baseline else 5
    rows.append(f"- explain the {top} largest costs: "
                + ", ".join(ranked[:top])
                + ("" if has_baseline else "  (no baseline yet: three becomes five)"))

    for measure, value in (("tokens.fresh", t.fresh),
                           ("subagents.fresh", sum(r["fresh"] for r in runs)),
                           ("turns", t.turns), ("images", t.images),
                           ("derived.context_peak", t.context_peak)):
        median = corpus.median(reviews, measure, skill=skill)
        if median and value > 1.5 * median:
            rows.append(f"- explain {measure}: {value} against a median of "
                        f"{median:,.0f} (×{value / median:.2f})")

    counters = {"repeated_bash": sum(n - 1 for n in t.bash.values() if n > 1),
                "files_read_twice": sum(1 for n in t.reads.values() if n > 1),
                "interruptions": t.interruptions, "api_errors": t.api_errors,
                "denials": t.denials}
    for name, value in counters.items():
        if value:
            rows.append(f"- a finding or a justification for {name}: {value}")

    rows.append("- a finding or a reason for each correction the user made "
                "(only the session can count these)")
    return rows


def timeline(t: Tally, width: int = 60) -> list[str]:
    rows = []
    for ts, what in t.timeline:
        stamp = ts.astimezone().strftime("%H:%M") if ts else "--:--"
        text = " ".join(str(what).split())
        rows.append(f"  {stamp}  {text[:width]}")
    return rows


def ledger(session: str, t: Tally, runs: list[dict], path: Path) -> str:
    """Session-level numbers, for the hook of Phase 3. No prose, ever.

    Keyed by transcript and carrying the size it was computed from, which is
    what lets a later sweep decide whether the session has grown since.
    """
    stamps = sorted(s for s in t.stamps if s)
    return json.dumps({
        "session": session,
        "bytes": path.stat().st_size,
        "from": stamps[0].isoformat() if stamps else None,
        "to": stamps[-1].isoformat() if stamps else None,
        "turns": t.turns,
        "fresh": t.fresh,
        "cache_read": t.cache_read,
        "subagents": [{"type": r["type"], "fresh": r["fresh"]} for r in runs],
        "tools": dict(t.tools),
        "skills": dict(t.skills),
    }, sort_keys=True)


def needs_sweep(transcript: Path, ledger_dir: Path) -> bool:
    """True when this transcript has no ledger entry, or has grown since.

    A ledger is always written from outside the session it describes, one
    session late, so an entry can be written while the session it describes is
    still running. Keying the entry by transcript and recording the size it was
    computed from is what makes that decidable: the same session is swept again
    when it has grown, and measured whole.
    """
    entry = ledger_dir / f"{transcript.stem}.json"
    try:
        return json.loads(entry.read_text(encoding="utf-8"))["bytes"] \
            != transcript.stat().st_size
    except (OSError, json.JSONDecodeError, KeyError):
        return True


def sweep(projects: Path = PROJECTS, ledger_dir: Path = LEDGER,
          live: str | None = None) -> list[str]:
    """Write a ledger entry for every transcript of this project that owes one.

    Reviews are written on purpose, and a purpose is selective. The ledger is
    written by nobody's decision, which is what stops the corpus from becoming
    a record of the tasks that went well.

    `glob` here is deliberately not `rglob`: the sweep takes the top-level
    transcripts and nothing else — never `memory/`, never a session's
    `subagents/` directory, which `metrics.scan` reaches through its own
    session and would otherwise count twice.
    """
    folder = projects / project_slug()
    if not folder.is_dir():
        return []
    written = []
    for transcript in sorted(folder.glob("*.jsonl")):
        # The live session's transcript is a few lines old at SessionStart.
        # A ledger written now would freeze it at nearly nothing while looking
        # complete; the next session finds it grown and sweeps it whole.
        if live and transcript.stem == live:
            continue
        if not needs_sweep(transcript, ledger_dir):
            continue
        tally = scan(transcript, Slice(None, None))
        if tally.turns < MIN_TURNS:
            continue
        runs = subagent_runs(transcript, Slice(None, None))
        ledger_dir.mkdir(parents=True, exist_ok=True)
        (ledger_dir / f"{transcript.stem}.json").write_text(
            ledger(transcript.stem, tally, runs, transcript) + "\n",
            encoding="utf-8")
        written.append(transcript.stem)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One task's slice, counted.")
    ap.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID"))
    ap.add_argument("--transcript", type=Path, help="a transcript, read as is")
    ap.add_argument("--reviews", type=Path, default=corpus.REVIEWS)
    ap.add_argument("--from", dest="start", help="ISO timestamp (default: the "
                    "end of this session's last review)")
    ap.add_argument("--to", dest="end", help="ISO timestamp (default: now)")
    ap.add_argument("--skill", help="the skill whose median to compare against")
    ap.add_argument("--owed", action="store_true",
                    help="the obligations these measures trigger")
    ap.add_argument("--timeline", action="store_true",
                    help="what happened, one truncated line a step")
    ap.add_argument("--ledger", action="store_true",
                    help="session-level JSON, whole transcript, no prose")
    ap.add_argument("--sweep", action="store_true",
                    help="write a ledger entry for every transcript that owes "
                         "one, silently (the SessionStart hook)")
    ap.add_argument("--ledger-dir", type=Path, default=LEDGER)
    ap.add_argument("--projects", type=Path, default=PROJECTS)
    args = ap.parse_args(argv)

    if args.sweep:
        sweep(args.projects, args.ledger_dir, args.session)
        return 0

    if args.transcript:
        path, session = args.transcript, args.transcript.stem
    elif args.session:
        path, session = transcript_of(args.session), args.session
    else:
        die("no session: CLAUDE_CODE_SESSION_ID is unset and --session was not "
            "given. This script never guesses a transcript by modification "
            "time — two conversations run side by side.")

    window = (Slice(None, None) if args.ledger
              else resolve_slice(session, args.reviews, args.start, args.end))
    tally = scan(path, window)
    runs = subagent_runs(path, window)

    if args.ledger:
        print(ledger(session, tally, runs, path))
        return 0

    lines = yaml_block(tally, runs)
    try:
        reviews = corpus.load(args.reviews)
    except corpus.ReviewError as e:
        print(f"metrics: corpus not read ({e})", file=sys.stderr)
        reviews = []
    lines += [""] + baselines(tally, runs, reviews, args.skill)
    if args.owed:
        lines += ["", "# owed by the review, from the measures above"]
        lines += owed(tally, runs, reviews, args.skill)
    if args.timeline:
        lines += ["", "# timeline"] + timeline(tally)
    elif len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES] + [f"# … {len(lines) - MAX_LINES} more line(s)"]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
