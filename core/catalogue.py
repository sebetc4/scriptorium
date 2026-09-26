"""The library's catalogue: a manifest in every directory, and ids to cite by.

Every directory of `library/` except the root describes itself in a
`manifest.yaml`. A directory is one of two kinds, read from what it holds and
never declared: a **topic** holds only directories; an **entry** holds one of
the five roles, or a file. Inside an entry, **items** describe its files, and
an entry's items cover it once: the item that covers a file is the one with
the longest path leading to it.

The agent writes a node's name, its description and the prefix of its id,
through `describe`. The tool writes everything else — paths, kinds, file
counts, digests — through `sync`, and names the anatomy's standard files
itself. A manifest is written by this module only: the PreToolUse guard
refuses an edit by hand.

What an agent cites, it cites by id, in a Markdown link of its own files:
`[Notice du lave-linge](id:notice-a8f2c3d9)`. An id never changes and is never
reused, so a session written today still points at the same thing tomorrow.

In the core rather than in a skill: `make` and several skills read the map
(docs/architecture.md §2). Keeping it — naming, describing, cleaning up — is
the intent, and belongs to a skill.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import secrets
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from core import doc

MANIFEST = "manifest.yaml"
HEADER = ("# Written by the catalogue, core/catalogue.py: change it through\n"
          "# `sync` and `describe`, never by hand.\n")
# The five roles of a document root, docs/architecture.md §11. `.work/` is one
# of them, and never listed: a command remakes it.
ROLES = {doc.DOCUMENT, doc.SOURCES, doc.STUDY, doc.GENERATORS, doc.WORK}
# The agent's roles. Whatever else an entry holds is what the user gave it, and
# gets a digest: a source never changes, so a new digest means something.
AGENT = {doc.DOCUMENT, doc.STUDY, doc.GENERATORS}

# An id: the prefix the agent gives, a hyphen, and a suffix the tool draws from
# an alphabet without the characters that read alike (0 o, 1 l i).
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"
SUFFIX = 8
PREFIX_MAX = 24
PREFIX = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ID = re.compile(rf"[a-z0-9]+(?:-[a-z0-9]+)*-[{ALPHABET}]{{{SUFFIX}}}")
# An `id:` citation: an inline Markdown link whose target is an id.
CITATION = re.compile(r"\]\(\s*<?id:([^)\s>]*)")

KINDS = {
    "pdf": {".pdf"},
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic", ".bmp",
              ".tif", ".tiff"},
    "text": {".md", ".txt", ".yaml", ".yml", ".json", ".csv", ".html", ".htm",
             ".css", ".xml", ".py", ".ino", ".c", ".h", ".cpp"},
    "video": {".mp4", ".mov", ".webm", ".mkv"},
    "audio": {".mp3", ".wav", ".ogg", ".flac", ".m4a"},
}

# The anatomy's standard files, named by the tool rather than the agent: their
# role says what they are. Keyed by the library's language, then by path inside
# the entry → prefix, name, description. A library says its language in
# `.catalogue.yaml` at its root (`language()`); English when it says nothing.
SETTINGS = ".catalogue.yaml"
STANDARD = {
    "en": {
        "document/index.md": (
            "document", "Document text",
            "The document's Markdown text and its front matter: what the build reads."),
        "document/cover.md": (
            "cover", "Document cover",
            "The Markdown of the document's cover."),
        "document/theme.css": (
            "theme", "The document's own style",
            "This document's departures from the shared art direction."),
        "document/assets": (
            "illustrations", "Document illustrations",
            "The images and the diagrams the document's text inserts."),
        "study/extracted.md": (
            "extraction", "Text extracted from the sources",
            "The raw extraction of an import or a capture, never edited: the "
            "reference the document is checked against."),
        "study/meta.json": (
            "provenance", "Provenance of the extraction",
            "Where the source came from, when and how it was acquired, and its digest."),
        "study/NOTES.md": (
            "investigation", "Investigation journal",
            "The journal of an investigation: questions, leads, pieces consulted, conclusions."),
        "study/discussion": (
            "discussion", "Discussion journal",
            "The journal of the discussion with the user: index, topics and sessions."),
        "study/translate": (
            "translation", "Translation workspace",
            "A translation in progress or already applied: segments, engine answers, review."),
        "glossary.yaml": (
            "glossary", "Translation glossary",
            "The terms and the translation chosen for each, which the translation respects."),
    },
    "fr": {
        "document/index.md": (
            "document", "Texte du document",
            "Le texte Markdown du document et sa front matter : ce que la construction lit."),
        "document/cover.md": (
            "couverture", "Couverture du document",
            "Le Markdown propre à la couverture du document."),
        "document/theme.css": (
            "theme", "Style propre au document",
            "Les écarts de ce document à la direction artistique commune."),
        "document/assets": (
            "illustrations", "Illustrations du document",
            "Les images et les schémas que le texte du document insère."),
        "study/extracted.md": (
            "extraction", "Texte extrait des sources",
            "L'extraction brute d'un import ou d'une capture, jamais retouchée : la "
            "référence contre laquelle le document est vérifié."),
        "study/meta.json": (
            "provenance", "Provenance de l'extraction",
            "D'où vient la source, quand et comment elle a été acquise, et son empreinte."),
        "study/NOTES.md": (
            "enquete", "Journal d'enquête",
            "Le journal d'une investigation : questions, pistes, pièces consultées, conclusions."),
        "study/discussion": (
            "discussion", "Journal de discussion",
            "Le journal de la discussion avec l'utilisateur : index, sujets et séances."),
        "study/translate": (
            "traduction", "Espace de traduction",
            "Une traduction en cours ou déjà appliquée : segments, réponses du moteur, relecture."),
        "glossary.yaml": (
            "glossaire", "Glossaire de traduction",
            "Les termes et la traduction retenue pour chacun, que la traduction respecte."),
    },
}

# libyaml's loader when PyYAML was built with it: every command of the map
# reads every manifest, and the pure-Python loader is most of their cost.
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

NODE_KEYS = ("id", "name", "description")
ITEM_KEYS = ("path", "original", "id", "name", "description", "kind", "files", "sha256")
RETIRED_KEYS = ("id", "name", "path", "date", "into")

# The most lines an answer prints, unless asked for more (core/navigate.py).
LIMIT = 20


class ManifestError(Exception):
    """A manifest the catalogue cannot read, or a request it refuses."""


@dataclass
class Item:
    path: str
    kind: str
    id: str | None = None
    name: str | None = None
    description: str | None = None
    files: int | None = None
    sha256: str | None = None
    original: str | None = None         # the file's name before `rename`

    @property
    def described(self) -> bool:
        return bool(self.name and self.description)

    @property
    def source(self) -> bool:
        return is_source(self.path)


@dataclass
class Retired:
    """An id whose item left the manifest — removed, or merged `into` the item
    above it. Kept so that a citation never leads nowhere, and the id is never
    drawn again: a session citing it is never rewritten."""
    id: str
    path: str
    date: str
    name: str | None = None
    into: str | None = None


@dataclass
class Manifest:
    id: str | None = None
    name: str | None = None
    description: str | None = None
    items: list[Item] | None = None     # None for a topic, which never lists anything
    retired: list[Retired] = field(default_factory=list)

    @property
    def described(self) -> bool:
        return bool(self.name and self.description)


# --- the tree ---------------------------------------------------------------

def visible(p: Path) -> bool:
    """Neither hidden (`.gitkeep`, `.work/`) nor the manifest itself."""
    return not p.name.startswith(".") and p.name != MANIFEST


def is_entry(d: Path) -> bool:
    """An entry holds one of the five roles, or a file; a topic holds only directories."""
    return any(p.name in ROLES or (p.is_file() and visible(p)) for p in d.iterdir())


def holds_files(d: Path) -> bool:
    """Whether a visible file lies anywhere under `d`: an empty directory, or one
    holding only hidden files, has nothing to describe and is no node."""
    return any(True for _ in visible_files(d))


def visible_files(d: Path):
    for p in d.rglob("*"):
        if p.is_file() and all(visible(Path(part)) for part in p.relative_to(d).parts):
            yield p


def nodes(library: Path, under: Path | None = None) -> list[tuple[Path, str]]:
    """Every topic and entry at or below `under` (the whole library by default),
    as `(directory, "topic" | "entry")`, in path order. An entry's inside is
    items, never nodes."""
    found = []

    def walk(d: Path) -> None:
        if d != library and not holds_files(d):
            return
        if is_entry(d):
            found.append((d, "entry"))
            return
        if d != library:
            found.append((d, "topic"))
        for child in sorted(d.iterdir()):
            if child.is_dir() and visible(child):
                walk(child)

    walk(library if under is None else under)
    return found


def where(library: Path, d: Path) -> str:
    return d.relative_to(library).as_posix()


def files_under(root: Path, rel: str = "") -> list[str]:
    """Every visible file at or under `root/rel`, as paths inside `root`.
    `.work/` and anything hidden are left out, at every depth."""
    start = root / rel if rel else root
    if start.is_file():
        return [rel] if visible(start) else []
    return sorted(p.relative_to(root).as_posix() for p in visible_files(start))


def default_paths(entry: Path) -> list[str]:
    """One item per direct child of each role, and one per other child of the
    entry's root — a file, or a directory that is none of the roles."""
    out = []
    for p in sorted(entry.iterdir()):
        if not visible(p):
            continue
        if p.is_dir() and p.name in ROLES:
            out += [c.relative_to(entry).as_posix()
                    for c in sorted(p.iterdir()) if visible(c)]
        else:
            out.append(p.name)
    return out


def is_source(path: str) -> bool:
    """Whether an item's path is the user's: anything outside the agent's roles."""
    return path.split("/", 1)[0] not in AGENT


def kind_of(p: Path) -> str:
    if p.is_dir():
        return "directory"
    ext = p.suffix.lower()
    return next((k for k, exts in KINDS.items() if ext in exts), "file")


def covering(items: list[Item], path: str) -> Item | None:
    """The item that covers `path`: the one with the longest path leading to it."""
    best = None
    for item in items:
        if path == item.path or path.startswith(item.path + "/"):
            if best is None or len(item.path) > len(best.path):
                best = item
    return best


def uncovered(entry: Path, items: list[Item]) -> list[str]:
    """The entry's files no item covers."""
    return [f for f in files_under(entry) if covering(items, f) is None]


# --- digests ------------------------------------------------------------------

def file_digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest(entry: Path, path: str, cache: dict[Path, str] | None = None) -> str:
    """A file's SHA-256; for a directory, the SHA-256 of its files' paths and
    digests, so that renaming the directory keeps it and changing a file inside
    does not."""
    cache = {} if cache is None else cache
    full = entry / path

    def one(p: Path) -> str:
        if p not in cache:
            cache[p] = file_digest(p)
        return cache[p]

    if full.is_file():
        return one(full)
    h = hashlib.sha256()
    for f in files_under(full):
        h.update(f"{f}\0{one(full / f)}\n".encode())
    return h.hexdigest()


# --- reading and writing ----------------------------------------------------

def _text(value, what: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ManifestError(f"{what} is not text")
    return value.strip() or None


def parse(text: str) -> Manifest:
    """A manifest from its YAML; ManifestError when its shape is wrong."""
    try:
        data = yaml.load(text, Loader=LOADER)
    except yaml.YAMLError as exc:
        raise ManifestError(f"not YAML: {str(exc).splitlines()[0]}") from None
    data = {} if data is None else data
    if not isinstance(data, dict):
        raise ManifestError("not a mapping")
    unknown = set(data) - {*NODE_KEYS, "items", "retired"}
    if unknown:
        raise ManifestError(f"unknown key {', '.join(sorted(map(str, unknown)))}")
    m = Manifest(**{k: _text(data.get(k), k) for k in NODE_KEYS})
    if "items" in data:
        raw = data["items"] or []
        if not isinstance(raw, list):
            raise ManifestError("items is not a list")
        m.items = []
        for n, it in enumerate(raw, 1):
            if not isinstance(it, dict):
                raise ManifestError(f"item {n} is not a mapping")
            unknown = set(it) - set(ITEM_KEYS)
            if unknown:
                raise ManifestError(f"item {n}: unknown key "
                                    f"{', '.join(sorted(map(str, unknown)))}")
            for key in ("path", "kind"):
                if not isinstance(it.get(key), str) or not it[key].strip():
                    raise ManifestError(f"item {n} has no {key}")
            files = it.get("files")
            if files is not None and (not isinstance(files, int) or isinstance(files, bool)):
                raise ManifestError(f"item {n}: files is not a count")
            m.items.append(Item(path=it["path"].strip().strip("/"),
                                kind=it["kind"].strip(), files=files,
                                **{k: _text(it.get(k), f"item {n}: {k}")
                                   for k in ("id", "name", "description", "sha256",
                                             "original")}))
    raw = data.get("retired") or []
    if not isinstance(raw, list):
        raise ManifestError("retired is not a list")
    for n, r in enumerate(raw, 1):
        if not isinstance(r, dict):
            raise ManifestError(f"retired {n} is not a mapping")
        unknown = set(r) - set(RETIRED_KEYS)
        if unknown:
            raise ManifestError(f"retired {n}: unknown key {', '.join(sorted(map(str, unknown)))}")
        if isinstance(r.get("date"), datetime.date):      # YAML reads a bare date as one
            r = {**r, "date": r["date"].isoformat()}
        fields = {k: _text(r.get(k), f"retired {n}: {k}") for k in RETIRED_KEYS}
        for key in ("id", "path", "date"):
            if not fields[key]:
                raise ManifestError(f"retired {n} has no {key}")
        m.retired.append(Retired(**fields))
    return m


def read(d: Path) -> Manifest:
    """The manifest of directory `d`; ManifestError if it is missing or unreadable."""
    p = d / MANIFEST
    if not p.is_file():
        raise ManifestError(f"no {MANIFEST} — run sync")
    return parse(p.read_text(encoding="utf-8"))


class _Dumper(yaml.SafeDumper):
    """Double quotes where YAML needs quotes: prose is full of apostrophes,
    which single quotes would double."""


def _str(dumper, value: str):
    style = '"' if ("'" in value or ": " in value or " #" in value
                    or value[:1] in "!&*-?:,[]{}#|>@`\"%") else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _str)


def dump(m: Manifest) -> str:
    data: dict = {k: getattr(m, k) for k in NODE_KEYS if getattr(m, k)}
    if m.items is not None:
        data["items"] = [{k: getattr(i, k) for k in ITEM_KEYS if getattr(i, k) is not None}
                         for i in sorted(m.items, key=lambda i: i.path)]
    if m.retired:
        data["retired"] = [{k: getattr(r, k) for k in RETIRED_KEYS if getattr(r, k) is not None}
                           for r in m.retired]
    body = yaml.dump(data, Dumper=_Dumper, allow_unicode=True, sort_keys=False,
                     width=1000) if data else ""
    return HEADER + body


def write(d: Path, m: Manifest) -> bool:
    """Write `d`'s manifest if its content changed; whether it did."""
    p, text = d / MANIFEST, dump(m)
    if p.is_file() and p.read_text(encoding="utf-8") == text:
        return False
    p.write_text(text, encoding="utf-8")
    return True


# --- ids --------------------------------------------------------------------

def ids(library: Path) -> dict[str, list[tuple[Path, Item | Retired | None]]]:
    """Every id of the library → where it is: the node's directory, and the item
    — or the retired id's record — when it is one. Unreadable manifests are
    skipped; the check reports them."""
    found: dict[str, list[tuple[Path, Item | Retired | None]]] = {}
    for d, _ in nodes(library):
        try:
            m = read(d)
        except ManifestError:
            continue
        if m.id:
            found.setdefault(m.id, []).append((d, None))
        for item in [*(m.items or []), *m.retired]:
            if item.id:
                found.setdefault(item.id, []).append((d, item))
    return found


def new_id(prefix: str, taken) -> str:
    """`prefix-xxxxxxxx`, with a suffix drawn until the id is not in `taken`."""
    if not PREFIX.fullmatch(prefix) or len(prefix) > PREFIX_MAX:
        raise ManifestError(f"prefix {prefix!r}: lowercase ASCII words joined by "
                            f"hyphens, at most {PREFIX_MAX} characters")
    while True:
        candidate = f"{prefix}-{''.join(secrets.choice(ALPHABET) for _ in range(SUFFIX))}"
        if candidate not in taken:
            return candidate


def citations(library: Path) -> list[tuple[Path, int, str]]:
    """Every `id:` citation of the library's Markdown, as `(file, line, id)`.
    `sources/` is the user's and `.work/` is remade: neither is read."""
    found = []
    for p in sorted(library.rglob("*.md")):
        parts = p.relative_to(library).parts
        if doc.SOURCES in parts or any(part.startswith(".") for part in parts):
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            found += [(p, n, target) for target in CITATION.findall(line)]
    return found


# --- sync ---------------------------------------------------------------------

def language(library: Path) -> str:
    """The language a library's names and descriptions are written in, as its
    `.catalogue.yaml` says (`language: fr`): the standard files are named in
    it. English when the library says nothing, or names a language the tool
    has no standard names for — the agent renames those through `describe`."""
    p = library / SETTINGS
    if not p.is_file():
        return "en"
    try:
        data = yaml.load(p.read_text(encoding="utf-8"), Loader=LOADER)
    except yaml.YAMLError as exc:
        raise ManifestError(f"{SETTINGS} unreadable: {exc}") from None
    lang = data.get("language") if isinstance(data, dict) else None
    return lang if lang in STANDARD else "en"


def _standard(item: Item, taken: set[str], names: dict) -> None:
    """Name an unnamed item that is one of the anatomy's standard files."""
    if item.name or item.path not in names:
        return
    prefix, item.name, item.description = names[item.path]
    if not item.id:
        item.id = new_id(prefix, taken)
        taken.add(item.id)


def _new_item(entry: Path, path: str, cache: dict) -> Item:
    full = entry / path
    return Item(path=path, kind=kind_of(full),
                files=len(files_under(entry, path)) if full.is_dir() else None,
                sha256=digest(entry, path, cache) if is_source(path) else None)


def _scope(library: Path, targets: list[str] | None) -> list[tuple[Path, str]]:
    """The nodes a sync covers: the whole library, or each target, everything
    below it, and the topics above it."""
    if not targets:
        return nodes(library)
    seen: dict[Path, str] = {}
    for t in targets:
        # An id, as every other command takes one: the node that holds it. A
        # path inside an entry is an item, not a node: sync the entry.
        if t.strip().startswith("id:") or (ID.fullmatch(t.strip()) and not under(library, t).exists()):
            d = resolve(library, t)[0]
        else:
            d = node_of(library, _inside(library, t))
        for up in reversed(d.relative_to(library).parents[:-1]):
            seen.setdefault(library / up, "topic")
        for n, k in nodes(library, d):
            seen[n] = k
    return sorted(seen.items())


def sync(library: Path, targets: list[str] | None = None) -> list[str]:
    """Bring the manifests in step with the disk; one line per thing done or
    found. Creates the missing manifests, adds an item for each file no item
    covers, follows a moved source by its digest, and reports a source gone or
    changed since it was described. A second run changes nothing, and no run
    touches a name or a description the agent wrote."""
    report: list[str] = []
    taken = set(ids(library))
    names = STANDARD[language(library)]
    cache: dict[Path, str] = {}
    scope = _scope(library, targets)
    manifests: dict[Path, Manifest] = {}

    for d, kind in scope:
        w = where(library, d)
        if (d / MANIFEST).is_file():
            try:
                manifests[d] = read(d)
            except ManifestError as exc:
                report.append(f"{w} — unreadable manifest, left as it is: {exc}")
                continue
        else:
            manifests[d] = Manifest()
            report.append(f"{w} — manifest created")
        m = manifests[d]
        if kind == "entry" and m.items is None:
            m.items = []

    entries = [d for d, k in scope if k == "entry" and d in manifests]

    # Follow what moved: an item whose path is gone, matched by its digest
    # against the sources of the scope that no item names exactly — the same
    # entry first, then anywhere else in the scope when there is one match.
    vanished = [(d, i) for d in entries for i in manifests[d].items
                if not (d / i.path).exists()]
    if any(i.sha256 for _, i in vanished):
        named = {(d, i.path) for d in entries for i in manifests[d].items}
        pool: dict[tuple[Path, str], None] = {}
        for d in entries:
            for f in files_under(d):
                if is_source(f):
                    for p in [f, *(p.as_posix() for p in Path(f).parents if p != Path("."))]:
                        if (d, p) not in named:
                            pool[(d, p)] = None
        candidates: dict[str, list[tuple[Path, str]]] = {}
        for d, p in pool:
            candidates.setdefault(digest(d, p, cache), []).append((d, p))
        claimed: set[tuple[Path, str]] = set()
        for d, item in vanished:
            if not item.sha256:
                continue
            found = [c for c in candidates.get(item.sha256, [])
                     if c not in claimed and kind_of(c[0] / c[1]) == item.kind]
            here = [c for c in found if c[0] == d]
            match = here[0] if len(here) == 1 else found[0] if len(found) == 1 else None
            if match is None:
                continue
            claimed.add(match)
            to, path = match
            old = f"{where(library, d)}/{item.path}"
            manifests[d].items.remove(item)
            item.path = path
            manifests[to].items.append(item)
            report.append(f"{where(library, to)} — followed: {old} → {path}")

    for d in entries:
        m, w = manifests[d], where(library, d)
        for item in list(m.items):
            full = d / item.path
            if not full.exists():
                if item.id:
                    report.append(f"{w} — vanished: {item.path}")
                else:           # never named, so never cited: nothing to keep
                    m.items.remove(item)
                    report.append(f"{w} — dropped, never named: {item.path}")
                continue
            item.kind = kind_of(full)
            item.files = len(files_under(d, item.path)) if full.is_dir() else None
            if not item.source:
                item.sha256 = None
                continue
            now = digest(d, item.path, cache)
            if not item.described or not item.sha256:
                item.sha256 = now
            elif item.sha256 != now:
                report.append(f"{w} — changed since described: {item.path}")
        for path in default_paths(d):
            known = {i.path for i in m.items}
            if path in known:
                continue
            if any(covering(m.items, f) is None for f in files_under(d, path)):
                m.items.append(_new_item(d, path, cache))
                report.append(f"{w} — new item: {path}")
        for item in m.items:
            _standard(item, taken, names)

    written = sum(write(d, m) for d, m in manifests.items())
    to_name = sum(not m.described for m in manifests.values())
    to_describe = sum(not i.described for m in manifests.values() for i in m.items or [])
    report.append(f"{written} manifest{'s' * (written != 1)} written — "
                  f"{to_name} to name, {to_describe} item{'s' * (to_describe != 1)} to describe")
    return report


def mapped(library: Path, entry: Path) -> list[str]:
    """What a command that creates an entry — `make new`, `import`, `fetch` —
    prints about the map: the entry synced, the manifests of the topics above
    it created, and what is left to name there, which the catalogue skill
    turns into names. Never fails the command: the entry exists, and a map
    left behind is what `make check-library` reports."""
    w = where(library, entry)
    try:
        sync(library, [w])
        unnamed = [where(library, d) for d in [entry, *entry.parents]
                   if library in d.parents and not read(d).described]
        items = [i.path for i in read(entry).items or [] if not i.described]
    except ManifestError as exc:
        return [f"  ! map: {w} not synced — {exc}"]
    lines = [f"  map: {w} synced — to name: {', '.join(unnamed) or 'nothing'}"]
    if items:
        lines.append(f"       to describe: {', '.join(items)}")
    if unnamed or items:
        lines.append(f"       by the catalogue skill: .venv/bin/catalogue ls {w} -l")
    return lines


# --- describe -----------------------------------------------------------------

def resolve(library: Path, target: str) -> tuple[Path, Item | None, str]:
    """A target — an id, or a path under the library — as `(node directory,
    item or None, path inside the entry)`. A path inside an entry that no item
    names comes back with `None` and the path, for `describe` to create."""
    target = target.strip()
    inside = under(library, target)
    if target.startswith("id:") or (ID.fullmatch(target) and not inside.exists()):
        found = ids(library).get(target.removeprefix("id:"), [])
        if len(found) != 1:
            raise ManifestError(f"{target}: {'no such id' if not found else 'id held twice'}")
        d, item = found[0]
        if isinstance(item, Retired):
            raise ManifestError(f"{target}: retired on {item.date}, "
                                + (f"merged into {item.into}" if item.into
                                   else f"{item.path} removed"))
        return d, item, item.path if item else ""
    if not inside.exists():
        return _vanished(library, target, inside)
    full = _inside(library, target)
    d = node_of(library, full)
    if d == full:
        return d, None, ""
    path = full.relative_to(d).as_posix()
    return d, None, path


def _vanished(library: Path, target: str, full: Path) -> tuple[Path, None, str]:
    """A path gone from the disk that an item still names: `remove` retires it."""
    here = next(p for p in full.parents if p.exists())
    if here != library and library in here.parents:
        d = node_of(library, here)
        if d.is_dir() and is_entry(d):
            path = full.relative_to(d).as_posix()
            try:
                if any(i.path == path for i in read(d).items or []):
                    return d, None, path
            except ManifestError:
                pass
    raise ManifestError(f"{target}: nothing there in the library")


def under(library: Path, target: str) -> Path:
    """A path given on the command line — relative to the library, or starting
    with `library/` — joined to the library. A `..` is refused rather than
    followed: `remove` and `rename` act on what this returns."""
    rel = target.strip().removeprefix("library/").strip("/")
    if ".." in Path(rel).parts:
        raise ManifestError(f"{target}: a path inside the library, without `..`")
    return library / rel


def _inside(library: Path, target: str) -> Path:
    """`under`, and existing, strictly inside the library."""
    full = under(library, target)
    if not full.exists() or full == library or library not in full.parents:
        raise ManifestError(f"{target}: nothing there in the library")
    return full


def node_of(library: Path, full: Path) -> Path:
    """The node a path belongs to: the directory itself when it is a topic or an
    entry, otherwise the entry that holds it."""
    for up in [*reversed(full.relative_to(library).parents[:-1]), full.relative_to(library)]:
        d = library / up
        if d.is_dir() and is_entry(d):
            return d
    return full


def describe(library: Path, target: str, name: str | None = None,
             description: str | None = None, prefix: str | None = None) -> str:
    """Set the name and description of a topic, an entry or an item, drawing its
    id from `prefix` the first time it is named. A path inside an entry that no
    item names becomes an item of its own, taken out of the one that covered it."""
    name, description = (v.strip() if v else None for v in (name, description))
    if not (name or description):
        raise ManifestError("nothing to write: give a name, a description, or both")
    d, item, path = resolve(library, target)
    m = read(d)
    if path:
        m.items = [] if m.items is None else m.items      # an entry not synced yet
        item = next((i for i in m.items if i.path == path), None)
        if item is None:
            if not visible(Path(path)) or any(p.startswith(".") for p in path.split("/")):
                raise ManifestError(f"{path}: hidden, never listed")
            item = _new_item(d, path, {})
            m.items.append(item)
        node = item
    else:
        node = m
    if not node.id and not (name and description):
        raise ManifestError("a first naming gives both the name and the description")
    if not node.id:
        if not prefix:
            raise ManifestError("a first naming gives the id's prefix as well")
        node.id = new_id(prefix, set(ids(library)))
    if name:
        node.name = name
    if description:
        node.description = description
    if isinstance(node, Item) and node.source:
        node.sha256 = digest(d, node.path)       # described as it is now
    write(d, m)
    shown = f"{where(library, d)}/{path}" if path else where(library, d)
    return f"{node.id} — {shown}"


# --- cleaning up: unused, remove, merge, rename, move ---------------------------
# Each acts on the user's word only, and only on what its command line names:
# the `catalogue` skill proposes, the user confirms, the command does that.

def bounded(lines: list[str], limit: int = LIMIT, narrow: str = "") -> list[str]:
    """At most `limit` lines: past it, the last one says how many more there are."""
    if limit <= 0 or len(lines) <= limit:
        return lines
    more = len(lines) - (limit - 1)
    hint = f" — {narrow}" if narrow else ""
    return lines[:limit - 1] + [f"… {more} more{hint}, or --limit {len(lines)}"]


def today() -> str:
    return datetime.date.today().isoformat()


def derived(entry: Path) -> set[str]:
    """The files of an entry a tool derived something from, and would derive
    from again: a capture's `sources/page.html.gz`; an import's PDF, found by
    the digest its provenance records and as `make rederive` finds it, the
    first PDF of `sources/`."""
    meta_path = entry / doc.STUDY / "meta.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    except (ValueError, UnicodeDecodeError):
        return set()
    sources, found = entry / doc.SOURCES, set()
    if "sha256_html" in meta and (sources / "page.html.gz").is_file():
        found.add(f"{doc.SOURCES}/page.html.gz")
    if "pages_total" in meta:
        pdfs = sorted(sources.glob("*.pdf"))
        if pdfs:
            found.add(pdfs[0].relative_to(entry).as_posix())
        want = meta.get("sha256")
        found |= {f for f in files_under(entry) if want and is_source(f)
                  and f.lower().endswith(".pdf") and file_digest(entry / f) == want}
    return found


def cited(library: Path) -> set[str]:
    """Every id a citation points at — and, for a retired id merged into
    another, the id it was merged into."""
    into = {r.id: r.into for holders in ids(library).values()
            for _, r in holders if isinstance(r, Retired) and r.into}
    found = set()
    for _, _, ident in citations(library):
        while ident and ident not in found:
            found.add(ident)
            ident = into.get(ident)
    return found


def in_use(entry: Path, items: list[Item], cited_ids: set[str]) -> dict[str, str]:
    """The items of an entry still in use → why: cited, derived from by a tool,
    or holding an item that is."""
    direct = {i.path: "cited" for i in items if i.id and i.id in cited_ids}
    for f in derived(entry):
        holder = covering(items, f)
        if holder:
            direct.setdefault(holder.path, "a tool derives from it")
    used = dict(direct)
    for i in items:
        if i.path not in used and any(p.startswith(i.path + "/") for p in direct):
            used[i.path] = "holds an item in use"
    return used


def _entry(library: Path, target: str, command: str) -> Path:
    d, item, path = resolve(library, target)
    if item is not None or path or not is_entry(d):
        raise ManifestError(f"{target}: {command} takes an entry")
    return d


def unused(library: Path, target: str, limit: int = LIMIT) -> list[str]:
    """The sources of an entry no citation of the library points at and no tool
    derives from, each with its reason: the list the user confirms before
    `remove`."""
    d = _entry(library, target, "unused")
    items = read(d).items or []
    sources = sorted((i for i in items if i.source), key=lambda i: i.path)
    used = in_use(d, items, cited(library))
    has_document = (d / doc.DOCUMENT / doc.ENTRY).is_file()
    lines = []
    for i in sources:
        if i.path in used:
            continue
        if not (d / i.path).exists():
            why = "gone from the disk; remove retires it"
        elif not i.id:
            why = "never named, so never cited"
        else:
            why = "cited by nothing" + ("; the entry's document may rest on it"
                                        if has_document else "")
        lines.append(f"{i.path}  {i.name or '(to describe)'}  {i.id or '-'} — {why}")
    head = (f"{len(lines)} of {len(sources)} source{'s' * (len(sources) != 1)} of "
            f"{where(library, d)} neither cited nor derived from")
    return bounded([head + (":" if lines else "")] + lines, limit)


def _named_items(library: Path, targets: list[str], command: str) -> dict[Path, list[str]]:
    """The items each target names exactly — by id, or by its own path — grouped
    by entry. A target that names no item is refused: nothing is inferred."""
    if not targets:
        raise ManifestError(f"{command} takes the items to act on, each by its path or id")
    found: dict[Path, list[str]] = {}
    for t in targets:
        d, item, path = resolve(library, t)
        known = {i.path for i in (read(d).items or [])} if path else set()
        if not path or path not in known:
            raise ManifestError(f"{t}: not an item — {command} acts on items only, "
                                "each named by its path or its id")
        if path not in found.setdefault(d, []):
            found[d].append(path)
    return found


def remove(library: Path, targets: list[str], used: bool = False) -> list[str]:
    """Delete the files of the items named and their lines in the manifest,
    together; each removed id is retired, never erased. Refuses an item of
    `document/`, a directory holding an item not named as well, and — unless
    `used` — an item still cited or derived from."""
    plan = _named_items(library, targets, "remove")
    cited_ids = cited(library)
    for d, paths in plan.items():
        items = read(d).items or []
        busy = in_use(d, items, cited_ids)
        for p in paths:
            if p.split("/", 1)[0] == doc.DOCUMENT:
                raise ManifestError(f"{where(library, d)}/{p}: document/ is the "
                                    "deliverable, remove never touches it")
            below = [i.path for i in items if i.path.startswith(p + "/") and i.path not in paths]
            if below:
                raise ManifestError(f"{where(library, d)}/{p} holds items not named: "
                                    f"{', '.join(below)} — name them too, or remove less")
            if p in busy and not used:
                raise ManifestError(f"{where(library, d)}/{p} is in use ({busy[p]}) — "
                                    "--used removes it anyway, on the user's word")
    lines = []
    for d, paths in plan.items():
        m = read(d)
        for p in sorted(paths, key=lambda p: -p.count("/")):     # the deepest first
            item = next(i for i in m.items if i.path == p)
            full = d / p
            if full.is_dir():
                shutil.rmtree(full)
            elif full.exists():
                full.unlink()
            m.items.remove(item)
            if item.id:
                m.retired.append(Retired(item.id, item.path, today(), item.name))
            lines.append(f"{where(library, d)}/{p} — removed"
                         + (f", {item.id} retired" if item.id else ""))
        write(d, m)
    return lines


def merge(library: Path, targets: list[str]) -> list[str]:
    """Fold each item named back into the item above it, leaving its file where
    it is: the inverse of describing a file inside a directory. Its id is
    retired into the item above, so a citation still leads somewhere."""
    plan = _named_items(library, targets, "merge")
    lines = []
    for d, paths in plan.items():
        m = read(d)
        keep = [i for i in m.items if i.path not in paths]
        moves = []
        for p in paths:
            if not (d / p).exists():
                raise ManifestError(f"{where(library, d)}/{p} is gone from the disk: "
                                    "remove retires it")
            above = covering(keep, p)
            if above is None or not above.id:
                raise ManifestError(f"{where(library, d)}/{p}: no named item above it "
                                    "to merge into — describe the directory first")
            moves.append((p, above))
        for p, above in moves:
            item = next(i for i in m.items if i.path == p)
            m.items.remove(item)
            if item.id:
                m.retired.append(Retired(item.id, item.path, today(), item.name, above.id))
            lines.append(f"{where(library, d)}/{p} — merged into {above.path} ({above.id})")
        write(d, m)
    return lines


def rename(library: Path, target: str, new_name: str) -> list[str]:
    """Rename one source file and its item together, keeping the file's
    original name in the manifest. A file inside a directory item gets an item
    of its own, as `describe` would give it."""
    d, _, path = resolve(library, target)
    full = d / path if path else d
    w = f"{where(library, d)}/{path}"
    if not path or not full.is_file():
        raise ManifestError(f"{target}: rename takes one file of an entry")
    if not is_source(path) or any(part.startswith(".") for part in path.split("/")):
        raise ManifestError(f"{w}: only a source is renamed through the catalogue")
    new = new_name.strip()
    if not new or "/" in new or "\\" in new or new.startswith("."):
        raise ManifestError(f"{new_name!r}: a file name, not a path")
    if Path(new).suffix.lower() != full.suffix.lower():
        raise ManifestError(f"{new}: the file keeps its extension, {full.suffix or 'none'}")
    dest = full.parent / new
    if dest.exists():
        raise ManifestError(f"{dest.relative_to(d).as_posix()} already exists")
    if path in derived(d):
        raise ManifestError(f"{w}: a tool derives from it and finds it by name — "
                            "renaming would break `make rederive`")
    m = read(d)
    m.items = [] if m.items is None else m.items
    item = next((i for i in m.items if i.path == path), None)
    # A rename is not a change of content: the directory items above stay
    # current, if they were.
    above = [i for i in m.items if path.startswith(i.path + "/") and i.sha256]
    before = {i.path: digest(d, i.path) for i in above}
    full.rename(dest)
    new_path = dest.relative_to(d).as_posix()
    if item is None:
        item = _new_item(d, new_path, {})
        m.items.append(item)
    else:
        item.path = new_path
    item.original = item.original or full.name
    if item.original == new:
        item.original = None
    for i in above:
        if i.sha256 == before[i.path]:
            i.sha256 = digest(d, i.path)
    write(d, m)
    kept = f" — original name kept: {item.original}" if item.original else ""
    return [f"{w} → {new}{kept}"]


def move(library: Path, target: str, dest: str) -> list[str]:
    """Move one item — a file or a directory — to another path of its entry,
    its id, name and description going with it. `sync` follows a moved source
    by its digest; this follows any item, across roles too: an investigation's
    pieces taken out of `sources/` into `study/`, notes the user gave put back
    into `sources/`. The items inside a moved directory go with it, and the
    directories it leaves empty are removed. A source keeps the digest it was
    described against; an agent's file carries none."""
    d, _, path = resolve(library, target)
    w = where(library, d)
    m = read(d)
    item = next((i for i in m.items or [] if path and i.path == path), None)
    if item is None:
        raise ManifestError(f"{target}: not an item — move acts on items only, each "
                            "named by its path or its id")
    full = d / path
    if not full.exists():
        raise ManifestError(f"{w}/{path} is gone from the disk: sync follows a moved "
                            "source, remove retires the rest")
    new = dest.strip().strip("/")
    parts = Path(new).parts
    if (not new or Path(new).is_absolute() or ".." in parts
            or any(p.startswith(".") for p in parts) or parts[-1] == MANIFEST):
        raise ManifestError(f"{dest!r}: a path inside the entry, neither hidden nor "
                            "with `..`")
    if new == path or new.startswith(path + "/"):
        raise ManifestError(f"{w}/{new} is inside the item it would move")
    to = d / new
    if to.exists():
        raise ManifestError(f"{w}/{new} already exists")
    taken = [p for p in derived(d) if p == path or p.startswith(path + "/")]
    if taken:
        raise ManifestError(f"{w}/{taken[0]}: a tool derives from it and finds it by "
                            "name — moving it would break `make rederive`")
    moving = [i for i in m.items if i.path == path or i.path.startswith(path + "/")]
    to.parent.mkdir(parents=True, exist_ok=True)
    full.rename(to)
    lines = []
    for i in sorted(moving, key=lambda i: i.path):
        old, i.path = i.path, new + i.path[len(path):]
        i.kind = kind_of(d / i.path)
        i.files = len(files_under(d, i.path)) if (d / i.path).is_dir() else None
        if not is_source(i.path):
            i.sha256 = None
        elif not is_source(old) or not i.sha256:
            i.sha256 = digest(d, i.path)
        lines.append(f"{w}/{old} → {i.path}" + (f" — {i.id} kept" if i.id else ""))
    write(d, m)
    left = full.parent
    while left != d and not any(left.iterdir()):
        left.rmdir()
        lines.append(f"{w}/{left.relative_to(d).as_posix()} — left empty, removed")
        left = left.parent
    return lines


def parser() -> argparse.ArgumentParser:
    """The entry point's command line: every command of the map, read or kept."""
    ap = argparse.ArgumentParser(prog="catalogue",
                                 description="The library's map: keep it, and read it.")
    ap.add_argument("--library", type=Path, metavar="DIR",
                    help="another library than the repository's, for a trial on a copy")
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sync", help="bring the manifests in step with the disk")
    s.add_argument("targets", nargs="*", metavar="topic/slug",
                   help="what to sync, with everything below it; the whole library by default")
    d = sub.add_parser("describe", help="name and describe a topic, an entry or an item")
    d.add_argument("target", help="an id, or a path under the library")
    d.add_argument("--name")
    d.add_argument("--description")
    d.add_argument("--prefix", help="the id's prefix, at the first naming")
    limit = argparse.ArgumentParser(add_help=False)
    limit.add_argument("--limit", type=int, default=20,
                       help="the most lines an answer prints (default 20; 0 for all)")
    f = sub.add_parser("find", parents=[limit], help="what the library holds about a query")
    f.add_argument("query", nargs="+")
    f.add_argument("--in", dest="within", metavar="TOPIC_OR_ENTRY",
                   help="search below this topic or entry only (a path or an id)")
    f.add_argument("--text", action="store_true",
                   help="search the content of the text items, not their descriptions")
    ls = sub.add_parser("ls", parents=[limit], help="a topic's nodes, or an entry's items")
    ls.add_argument("target", nargs="?", help="a path or an id; the library's root by default")
    ls.add_argument("-l", dest="level", action="count", default=0,
                    help="-l adds the descriptions, -ll the kind, size and date")
    k = sub.add_parser("links", parents=[limit], help="what an entry or item cites, and what cites it")
    k.add_argument("target", help="a path or an id")
    p = sub.add_parser("path", help="where an id is")
    p.add_argument("id")
    pk = sub.add_parser("peek", parents=[limit],
                        help="a first look at a file: a PDF's text, an image's size, a text's lines")
    pk.add_argument("target", help="a path or an id")
    pk.add_argument("--pages", help="for a PDF, the pages to read, as 3 or 2-5 (default 1-2)")
    u = sub.add_parser("unused", parents=[limit],
                       help="the sources of an entry nothing cites and no tool derives from")
    u.add_argument("target", help="an entry, by its path or id")
    r = sub.add_parser("remove", help="delete the items named, files and lines together")
    r.add_argument("targets", nargs="+", metavar="item")
    r.add_argument("--used", action="store_true",
                   help="remove an item still cited or derived from — on the user's word")
    mg = sub.add_parser("merge", help="fold items back into the item above them")
    mg.add_argument("targets", nargs="+", metavar="item")
    rn = sub.add_parser("rename", help="rename a source file and its item together")
    rn.add_argument("target", help="the file, by its path or its item's id")
    rn.add_argument("new_name", metavar="new-name", help="a file name, with the same extension")
    mv = sub.add_parser("move", help="move an item's file or directory within its entry, "
                                     "keeping its id")
    mv.add_argument("target", help="the item, by its path or its id")
    mv.add_argument("dest", metavar="new-path", help="its new path, inside the entry: study/raw")
    return ap


def commands() -> set[str]:
    """The names of the entry point's commands."""
    sub = next(a for a in parser()._actions if isinstance(a, argparse._SubParsersAction))
    return set(sub.choices)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    library = args.library.resolve() if args.library else doc.LIBRARY
    try:
        if not library.is_dir():
            raise ManifestError(f"no library at {doc.shown(library)}")
        from core import navigate          # it reads this module: imported late
        if args.command == "sync":
            lines = sync(library, args.targets)
        elif args.command == "describe":
            lines = [describe(library, args.target, args.name, args.description, args.prefix)]
        elif args.command == "find":
            lines = navigate.find(library, " ".join(args.query), args.within, args.text,
                                  args.limit)
        elif args.command == "ls":
            lines = navigate.ls(library, args.target, args.level, args.limit)
        elif args.command == "links":
            lines = navigate.links(library, args.target, args.limit)
        elif args.command == "path":
            lines = [navigate.path(library, args.id)]
        elif args.command == "peek":
            lines = navigate.peek(library, args.target, args.pages, args.limit)
        elif args.command == "unused":
            lines = unused(library, args.target, args.limit)
        elif args.command == "remove":
            lines = remove(library, args.targets, args.used)
        elif args.command == "merge":
            lines = merge(library, args.targets)
        elif args.command == "move":
            lines = move(library, args.target, args.dest)
        else:
            lines = rename(library, args.target, args.new_name)
    except ManifestError as exc:
        print(f"catalogue: {exc}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
