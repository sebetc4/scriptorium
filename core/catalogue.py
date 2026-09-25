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
`[Manuel de la TC22](id:manuel-a8f2c3d9)`. An id never changes and is never
reused, so a session written today still points at the same thing tomorrow.

In the core rather than in a skill: `make` and several skills read the map
(docs/architecture.md §2). Keeping it — naming, describing, cleaning up — is
the intent, and belongs to a skill.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import secrets
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
# role says what they are. Keyed by path inside the entry → prefix, name,
# description. In French, the language of the library.
STANDARD = {
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
}

# libyaml's loader when PyYAML was built with it: every command of the map
# reads every manifest, and the pure-Python loader is most of their cost.
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

NODE_KEYS = ("id", "name", "description")
ITEM_KEYS = ("path", "id", "name", "description", "kind", "files", "sha256")


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

    @property
    def described(self) -> bool:
        return bool(self.name and self.description)

    @property
    def source(self) -> bool:
        return is_source(self.path)


@dataclass
class Manifest:
    id: str | None = None
    name: str | None = None
    description: str | None = None
    items: list[Item] | None = None     # None for a topic, which never lists anything

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
    unknown = set(data) - {*NODE_KEYS, "items"}
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
                                   for k in ("id", "name", "description", "sha256")}))
    return m


def read(d: Path) -> Manifest:
    """The manifest of directory `d`; ManifestError if it is missing or unreadable."""
    p = d / MANIFEST
    if not p.is_file():
        raise ManifestError(f"no {MANIFEST} — run sync")
    return parse(p.read_text(encoding="utf-8"))


class _Dumper(yaml.SafeDumper):
    """Double quotes where YAML needs quotes: French text is full of apostrophes,
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

def ids(library: Path) -> dict[str, list[tuple[Path, Item | None]]]:
    """Every id of the library → where it is: the node's directory, and the item
    when it is one. Unreadable manifests are skipped; the check reports them."""
    found: dict[str, list[tuple[Path, Item | None]]] = {}
    for d, _ in nodes(library):
        try:
            m = read(d)
        except ManifestError:
            continue
        if m.id:
            found.setdefault(m.id, []).append((d, None))
        for item in m.items or []:
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

def _standard(item: Item, taken: set[str]) -> None:
    """Name an unnamed item that is one of the anatomy's standard files."""
    if item.name or item.path not in STANDARD:
        return
    prefix, item.name, item.description = STANDARD[item.path]
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
        # A path inside an entry is an item, not a node: sync the entry.
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
            _standard(item, taken)

    written = sum(write(d, m) for d, m in manifests.items())
    to_name = sum(not m.described for m in manifests.values())
    to_describe = sum(not i.described for m in manifests.values() for i in m.items or [])
    report.append(f"{written} manifest{'s' * (written != 1)} written — "
                  f"{to_name} to name, {to_describe} item{'s' * (to_describe != 1)} to describe")
    return report


# --- describe -----------------------------------------------------------------

def resolve(library: Path, target: str) -> tuple[Path, Item | None, str]:
    """A target — an id, or a path under the library — as `(node directory,
    item or None, path inside the entry)`. A path inside an entry that no item
    names comes back with `None` and the path, for `describe` to create."""
    target = target.strip()
    inside = library / target.removeprefix("library/").strip("/")
    if target.startswith("id:") or (ID.fullmatch(target) and not inside.exists()):
        found = ids(library).get(target.removeprefix("id:"), [])
        if len(found) != 1:
            raise ManifestError(f"{target}: {'no such id' if not found else 'id held twice'}")
        d, item = found[0]
        return d, item, item.path if item else ""
    full = _inside(library, target)
    d = node_of(library, full)
    if d == full:
        return d, None, ""
    path = full.relative_to(d).as_posix()
    return d, None, path


def _inside(library: Path, target: str) -> Path:
    """A path given on the command line — relative to the library, or starting
    with `library/` — as an existing path strictly inside it."""
    full = library / target.strip().removeprefix("library/").strip("/")
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="catalogue",
                                 description="The library's map: keep it, and read it.")
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
    args = ap.parse_args(argv)
    library = doc.LIBRARY
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
        else:
            lines = [navigate.path(library, args.id)]
    except ManifestError as exc:
        print(f"catalogue: {exc}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
