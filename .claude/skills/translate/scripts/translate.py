#!/usr/bin/env python3
"""Translate a document of the library in place, through an engine.

    translate.py prepare <topic>/<slug> [--from en] [--budget 6000]
    translate.py run     <topic>/<slug> [--engine agent]
    translate.py apply   <topic>/<slug> [--engine agent] [--force]
    translate.py cross-check <topic>/<slug> --engines agent local

**prepare** reads `index.md`, protects what must not be translated (zones.py),
cuts the body into chunks that carry their context (chunking.py), and writes
the job into a workspace under `out/translate/<topic>/<slug>/`. The target
language is the front matter's `lang:`, stated when the document was imported
or captured. The source language comes from `sources/meta.json` — recorded by
the import and the capture — or `--from`, or is detected. It is never asked.

**run** hands the chunks to an engine in order, each with the context before it
and the engine's own previous output, and validates every answer: a placeholder
lost, doubled or invented stops the run. The `agent` engine answers through
files — `run` writes the request, the agent writes the answer, `run` again
moves on — so it goes through exactly the same checks as a model would.

**apply** checks every chunk (qc.py). An error blocks: nothing is written.
Otherwise the translation replaces the body, the displayed front-matter strings
are translated in their own lines, and `translated_from:` is added, so the
document is never prepared a second time by mistake. `apply` refuses an
`index.md` edited since `prepare`.

**cross-check** compares two engines' translations and names the chunks where
they disagree.

The workspace is a build artefact: `make clean` removes it, and a translation
not yet applied is lost with it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

from core import doc

import chunking
import engines
import qc
import zones

LIBRARY = doc.LIBRARY
WORKSPACES = doc.OUT / "translate"
FRONT_RE = re.compile(r"\A---[ \t]*\n.*?\n---[ \t]*\n", re.S)
FRONT_LINE_RE = re.compile(r"^(⟦\d+⟧)[ \t]?(.*)$")


class TranslateError(Exception):
    pass


# --------------------------------------------------------------------------
# The document and its job
# --------------------------------------------------------------------------
def document(path: str) -> Path:
    d = LIBRARY / path
    if not (doc.doc_dir(d) / doc.ENTRY).is_file():
        raise TranslateError(f"{path}: no index.md under library/")
    return d


def workspace(d: Path) -> Path:
    return WORKSPACES / d.relative_to(LIBRARY)


def split_front(text: str) -> tuple[str, str]:
    m = FRONT_RE.match(text)
    return (m.group(0), text[m.end():]) if m else ("", text)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lang_code(value) -> str:
    return str(value or "").split("-")[0].split("_")[0].lower()


def source_language(d: Path, body: str, given: str | None) -> tuple[str, str]:
    """The source language, and where it came from."""
    if given:
        return lang_code(given), "--from"
    meta_path = d / "sources" / "meta.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for value, origin in ((meta.get("source_language"), "sources/meta.json"),
                              ((meta.get("metadata") or {}).get("language"),
                               "sources/meta.json, the page's metadata")):
            if lang_code(value):
                return lang_code(value), origin
    try:
        import py3langid
        return lang_code(py3langid.classify(zones.TOKEN_RE.sub("", body)[:5000])[0]), "detected"
    except Exception:
        raise TranslateError("the source language is recorded nowhere and could not be "
                             "detected: pass --from")


def glossary(d: Path) -> tuple[dict[str, str], list[str]]:
    path = d / "glossary.yaml"
    if not path.is_file():
        return {}, []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    terms, keep = data.get("terms") or {}, data.get("keep") or []
    if not isinstance(terms, dict) or not isinstance(keep, list):
        raise TranslateError(f"{path}: expected `terms:` as a mapping and `keep:` as a list")
    return {str(k): str(v) for k, v in terms.items()}, [str(k) for k in keep]


def load_job(d: Path) -> dict:
    path = workspace(d) / "job.json"
    if not path.is_file():
        raise TranslateError(f"no translation prepared for {d.relative_to(LIBRARY)}: run prepare first")
    return json.loads(path.read_text(encoding="utf-8"))


def response_path(d: Path, engine: str, index: int) -> Path:
    return workspace(d) / "responses" / engine / f"{index:03d}.md"


def chunk_table(job: dict, chunk: dict) -> dict[str, str]:
    return {m.group(0): job["table"][m.group(0)] for m in zones.TOKEN_RE.finditer(chunk["text"])}


# --------------------------------------------------------------------------
# prepare
# --------------------------------------------------------------------------
def prepare(args) -> int:
    d = document(args.doc)
    text = (doc.doc_dir(d) / doc.ENTRY).read_text(encoding="utf-8")
    front, body = split_front(text)
    meta = yaml.safe_load(front.strip().strip("-")) if front else {}
    meta = meta or {}
    if meta.get("translated_from") and not args.force:
        raise TranslateError(f"index.md says translated_from: {meta['translated_from']} — "
                             "it has been translated already (--force to do it again)")
    target = lang_code(meta.get("lang"))
    if not target:
        raise TranslateError("index.md has no lang: in its front matter — it states the "
                             "target language, and nothing here assumes one")
    source, origin = source_language(d, body, args.from_)
    if source == target:
        raise TranslateError(f"the source is already in {target} ({origin}): to translate it, "
                             "set lang: to the target language first")

    masked, table = zones.protect(body)
    terms, keep = glossary(d)
    chunks = [{"kind": "body", "text": c.text, "context_before": c.context_before,
               "headings": c.headings, "oversized": c.oversized}
              for c in chunking.split(masked, budget=args.budget)]
    strings = zones.front_matter_strings(front)
    if strings:
        keys, lines = {}, []
        for key, value in strings.items():
            t = zones.token(len(table) + len(keys) + 1)
            keys[t] = key
            lines.append(f"{t} {value}")
        chunks.insert(0, {"kind": "front", "text": "\n".join(lines) + "\n",
                          "context_before": "", "headings": [], "oversized": False, "keys": keys})
    for i, c in enumerate(chunks):
        c["index"] = i

    ws = workspace(d)
    job = {"doc": args.doc, "source_lang": source, "target_lang": target,
           "index_sha256": digest(text), "budget": args.budget,
           "glossary": {"terms": terms, "keep": keep}, "table": table,
           "front": front, "chunks": chunks}
    previous = ws / "job.json"
    if previous.is_file():
        # An answer is only worth keeping for the very chunk it answered: the
        # same text under the same placeholders. Anything else is discarded.
        old = json.loads(previous.read_text(encoding="utf-8"))
        old_texts = {c["index"]: c["text"] for c in old["chunks"]}
        stale = [c["index"] for c in chunks if old_texts.get(c["index"]) != c["text"]]
        stale += [i for i in old_texts if i >= len(chunks)]
        discarded = 0
        for index in stale:
            for path in [ws / "requests" / f"{index:03d}.md",
                         *(ws / "responses").glob(f"*/{index:03d}.md")]:
                if path.is_file():
                    discarded += path.parent.name != "requests"
                    path.unlink()
        if discarded:
            print(f"  · {discarded} answer(s) to changed chunks discarded")
    ws.mkdir(parents=True, exist_ok=True)
    previous.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ws / "original.md").write_text(text, encoding="utf-8")

    oversized = sum(c["oversized"] for c in chunks)
    print(f"  ✓ {ws}\n    {source} → {target} (source language: {origin}), "
          f"{len(chunks)} chunk(s), {len(table)} protected zone(s)"
          + (f", {oversized} block(s) larger than the budget" if oversized else ""))
    print(f"    next: translate.py run {args.doc}")
    return 0


# --------------------------------------------------------------------------
# run
# --------------------------------------------------------------------------
def terms_in(text: str, terms: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in terms.items()
            if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", text, re.I)}


def validate(job: dict, chunk: dict, answer: str) -> str:
    """The answer with its zones restored; raises ZoneError when one is wrong."""
    if chunk["kind"] == "front":
        return json.dumps(front_strings(chunk, answer), ensure_ascii=False)
    return zones.restore(answer, chunk_table(job, chunk))


def front_strings(chunk: dict, answer: str) -> dict[str, str]:
    found = {}
    for line in answer.splitlines():
        if m := FRONT_LINE_RE.match(line.strip()):
            if m.group(1) in found:
                raise zones.ZoneError(f"placeholder present more than once {m.group(1)}")
            found[m.group(1)] = m.group(2).strip()
    missing = [t for t in chunk["keys"] if t not in found]
    unknown = [t for t in found if t not in chunk["keys"]]
    if missing or unknown:
        raise zones.ZoneError("; ".join(filter(None, [
            missing and f"missing placeholder(s) {', '.join(missing)}",
            unknown and f"unknown placeholder(s) {', '.join(unknown)}"])))
    return {chunk["keys"][t]: v for t, v in found.items()}


def request_for(job: dict, chunk: dict, previous: str) -> engines.Request:
    return engines.Request(
        index=chunk["index"], total=len(job["chunks"]),
        source_lang=job["source_lang"], target_lang=job["target_lang"],
        text=chunk["text"], context_before=chunk["context_before"],
        previous_translation=previous, headings=tuple(chunk["headings"]),
        glossary=terms_in(chunk["text"], job["glossary"]["terms"]) or None,
        keep=tuple(k for k in job["glossary"]["keep"] if k in chunk["text"]))


def run_engine(args) -> int:
    d = document(args.doc)
    job = load_job(d)
    if args.engine not in engines.ENGINES:
        raise TranslateError(f"unknown engine “{args.engine}” "
                             f"(available: {', '.join(sorted(engines.ENGINES))})")
    engine = engines.ENGINES[args.engine](workspace(d))
    previous = ""
    for chunk in job["chunks"]:
        path = response_path(d, args.engine, chunk["index"])
        if path.is_file():
            answer = path.read_text(encoding="utf-8")
        else:
            try:
                answer = engine.translate(request_for(job, chunk, previous))
            except engines.Pending as pending:
                print(f"  · chunk {chunk['index'] + 1} of {len(job['chunks'])} is waiting\n"
                      f"    read  {pending.request_path}\n"
                      f"    write {pending.answer_path}\n"
                      f"    then: translate.py run {args.doc}")
                return 1
            except engines.EngineUnavailable as exc:
                raise TranslateError(f"engine {args.engine}: {exc}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(answer, encoding="utf-8")
        try:
            validate(job, chunk, answer)
        except zones.ZoneError as exc:
            raise TranslateError(f"chunk {chunk['index'] + 1}: {exc}\n    fix {path}, "
                                 f"then: translate.py run {args.doc}")
        if chunk["kind"] == "body":
            previous = chunking.context_of(chunking.blocks(answer), chunking.DEFAULT_CONTEXT)
    print(f"  ✓ {len(job['chunks'])} chunk(s) translated by {args.engine}\n"
          f"    next: translate.py apply {args.doc}"
          + ("" if args.engine == "agent" else f" --engine {args.engine}"))
    return 0


# --------------------------------------------------------------------------
# apply, cross-check
# --------------------------------------------------------------------------
def same_edges(source: str, target: str) -> str:
    """The target with the source's leading and trailing blank lines."""
    lead = source[:len(source) - len(source.lstrip("\n"))]
    trail = source[len(source.rstrip("\n")):]
    return lead + target.strip("\n") + trail


def answers(d: Path, job: dict, engine: str) -> dict[int, str]:
    found, pending = {}, []
    for chunk in job["chunks"]:
        path = response_path(d, engine, chunk["index"])
        if not path.is_file():
            pending.append(chunk["index"] + 1)
            continue
        found[chunk["index"]] = same_edges(chunk["text"], path.read_text(encoding="utf-8"))
    if pending:
        raise TranslateError(f"engine {engine}: {len(pending)} chunk(s) without an answer "
                             f"({', '.join(map(str, pending[:10]))}…): "
                             f"translate.py run {job['doc']} --engine {engine}")
    return found


def apply(args) -> int:
    d = document(args.doc)
    job = load_job(d)
    current = (doc.doc_dir(d) / doc.ENTRY).read_text(encoding="utf-8")
    if digest(current) != job["index_sha256"]:
        raise TranslateError("index.md has changed since prepare — prepare again, "
                             "the answers of unchanged chunks are not reused across a change")
    translated = answers(d, job, args.engine)

    findings, strings, body = [], {}, []
    for chunk in job["chunks"]:
        answer = translated[chunk["index"]]
        try:
            restored = validate(job, chunk, answer)
        except zones.ZoneError as exc:
            raise TranslateError(f"chunk {chunk['index'] + 1}: {exc}")
        findings += qc.check_chunk(chunk["index"], chunk["text"], answer,
                                   job["source_lang"], job["target_lang"],
                                   glossary=terms_in(chunk["text"], job["glossary"]["terms"]),
                                   keep=tuple(job["glossary"]["keep"]))
        if chunk["kind"] == "front":
            strings = json.loads(restored)
        else:
            body.append(restored)

    errors = [f for f in findings if f.level == "error"]
    for f in findings:
        where = response_path(d, args.engine, f.chunk)
        line = f"  {'✗' if f.level == 'error' else '!'} chunk {f.chunk + 1}: {f.message}  ({where})"
        print(line, file=sys.stderr if f.level == "error" else sys.stdout)
    if errors and not args.force:
        raise TranslateError(f"{len(errors)} error(s): nothing written. Fix the answers, "
                             "or pass --force after reading every one")

    front = zones.set_front_matter_strings(job["front"], strings) if job["front"] else ""
    if front and "translated_from:" not in front:
        front = re.sub(r"\n---[ \t]*\n\Z", f"\ntranslated_from: {job['source_lang']}\n---\n", front)
    (doc.doc_dir(d) / doc.ENTRY).write_text(front + "".join(body),
                                            encoding="utf-8")
    print(f"  ✓ {d / 'index.md'}  {job['source_lang']} → {job['target_lang']}, "
          f"{len(job['chunks'])} chunk(s), {len(findings) - len(errors)} warning(s)\n"
          f"    the untranslated version stays in {workspace(d) / 'original.md'}\n"
          f"    next: make build DOC={job['doc']}, and review it")
    return 0


def cross_check(args) -> int:
    d = document(args.doc)
    job = load_job(d)
    a_name, b_name = args.engines
    a, b = answers(d, job, a_name), answers(d, job, b_name)
    sources = {c["index"]: c["text"] for c in job["chunks"]}
    findings = qc.cross_check(sources, a, b, names=(a_name, b_name))
    for f in findings:
        print(f"  ! chunk {f.chunk + 1}: {f.message}")
    if not findings:
        print(f"  ✓ {a_name} and {b_name} agree on every chunk's numbers, structure and length")
    return 0


# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Translate a document of the library in place.")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("doc", help="topic/slug under library/")
    p.add_argument("--from", dest="from_", metavar="LANG", help="the source language, if not recorded")
    p.add_argument("--budget", type=int, default=chunking.DEFAULT_BUDGET, help="characters per chunk")
    p.add_argument("--force", action="store_true", help="prepare a document already translated")
    p = sub.add_parser("run")
    p.add_argument("doc")
    p.add_argument("--engine", default="agent")
    p = sub.add_parser("apply")
    p.add_argument("doc")
    p.add_argument("--engine", default="agent")
    p.add_argument("--force", action="store_true", help="write despite errors — after reading them")
    p = sub.add_parser("cross-check")
    p.add_argument("doc")
    p.add_argument("--engines", nargs=2, required=True, metavar="ENGINE")
    args = ap.parse_args(argv)
    handler = {"prepare": prepare, "run": run_engine, "apply": apply,
               "cross-check": cross_check}[args.command]
    try:
        return handler(args)
    except (TranslateError, zones.ZoneError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
