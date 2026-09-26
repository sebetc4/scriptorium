"""Reading the library's map: `find`, `ls`, `links` and `path`.

Four read-only commands over the manifests `core/catalogue.py` keeps. Nothing is
loaded when a session opens: a question costs the lines of its answer, and no
answer is longer than `LIMIT` lines however large the library grows — it says
how many more there are and how to narrow the question instead.

A brick rather than an intent (docs/architecture.md §2): the `catalogue` skill,
the `discussion` skill and `make` all read the map, and none of them owns it.
"""
from __future__ import annotations

import datetime
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from core import catalogue as cat
from core import doc

LIMIT = cat.LIMIT
bounded = cat.bounded


# --- the map, read once per command -----------------------------------------

@dataclass
class Node:
    dir: Path
    kind: str                       # topic | entry
    m: cat.Manifest | None          # None when missing or unreadable

    @property
    def id(self) -> str | None:
        return self.m.id if self.m else None

    @property
    def name(self) -> str | None:
        return self.m.name if self.m else None

    @property
    def items(self) -> list[cat.Item]:
        return (self.m.items or []) if self.m else []


class Atlas:
    """Every node of the library and every id, from the manifests as they are."""

    def __init__(self, library: Path):
        self.library = library
        self.nodes: dict[Path, Node] = {}
        self.ids: dict[str, tuple[Node, cat.Item | None]] = {}
        self.retired: dict[str, tuple[Node, cat.Retired]] = {}
        for d, kind in cat.nodes(library):
            try:
                m = cat.read(d)
            except cat.ManifestError:
                m = None
            node = self.nodes[d] = Node(d, kind, m)
            if node.id:
                self.ids.setdefault(node.id, (node, None))
            for item in node.items:
                if item.id:
                    self.ids.setdefault(item.id, (node, item))
            for r in (m.retired if m else []):
                self.retired.setdefault(r.id, (node, r))

    def where(self, node: Node, item: cat.Item | None = None) -> str:
        w = node.dir.relative_to(self.library).as_posix()
        return f"{w}/{item.path}" if item else w

    def resolve(self, target: str) -> tuple[Node | None, cat.Item | None]:
        """An id, or a path under the library, as `(node, item)`. The root of
        the library is `(None, None)`; a path inside an entry that no item
        names is its entry and the item that covers it."""
        target = (target or "").strip()
        full = cat.under(self.library, target)
        ident = cat.as_id(self.library, target)
        if ident is not None:
            if ident in self.retired:
                raise cat.ManifestError(f"{target}: retired — path {ident} says where it went")
            if ident not in self.ids:
                raise cat.ManifestError(f"{target}: no such id")
            return self.ids[ident]
        if full == self.library:
            return None, None
        if not full.exists() or self.library not in full.parents:
            raise cat.ManifestError(f"{target}: nothing there in the library")
        d = cat.node_of(self.library, full)
        if d not in self.nodes:
            raise cat.ManifestError(f"{target}: holds no file, so no node")
        node = self.nodes[d]
        if d == full:
            return node, None
        path = full.relative_to(d).as_posix()
        item = cat.covering(node.items, path)
        if item is None:
            raise cat.ManifestError(f"{target}: no item covers it — sync the entry")
        return node, item

    def children(self, d: Path | None) -> list[Node]:
        """The nodes directly below a topic, or below the library's root."""
        parent = self.library if d is None else d
        return [n for p, n in self.nodes.items() if p.parent == parent]

    def below(self, d: Path | None) -> list[Node]:
        """Every node at or below `d`; the whole library for the root."""
        if d is None:
            return list(self.nodes.values())
        return [n for p, n in self.nodes.items() if p == d or d in p.parents]


# --- output -------------------------------------------------------------------

def fold(text: str) -> str:
    """Lower case, accents stripped, apostrophes made one: `« Étain »` finds `etain`."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return plain.replace("’", "'")


def label(name: str | None) -> str:
    return name or "(to describe)"


# --- find ---------------------------------------------------------------------

def find(library: Path, query: str, within: str | None = None, text: bool = False,
         limit: int = LIMIT) -> list[str]:
    """What the library holds about `query`: every word of it found, accents and
    case folded, in a name or a description — or, with `text`, on one line of a
    text item's content. One line per result, in path order."""
    words = fold(query).split()
    if not words:
        raise cat.ManifestError("find needs at least one word")
    atlas = Atlas(library)
    top, item = atlas.resolve(within) if within else (None, None)
    if item is not None:
        raise cat.ManifestError(f"{within}: --in takes a topic or an entry")
    scope = atlas.below(top.dir if top else None)

    def hit(*fields: str | None) -> bool:
        folded = fold(" ".join(f for f in fields if f))
        return all(w in folded for w in words)

    lines = []
    for node in sorted(scope, key=lambda n: n.dir):
        if text:
            lines += _grep(atlas, node, hit)
            continue
        if node.id and hit(node.name, node.m.description):
            lines.append(f"{node.kind}  {node.id}  {node.name}  {atlas.where(node)}")
        for it in sorted(node.items, key=lambda i: i.path):
            if it.id and hit(it.name, it.description):
                lines.append(f"{it.kind}  {it.id}  {it.name}  {atlas.where(node, it)}")
    if not lines:
        return [f"nothing matches “{query}”" + (f" in {within}" if within else "")]
    return bounded(lines, limit, "add a word, or --in <topic or entry>")


def _grep(atlas: Atlas, node: Node, hit) -> list[str]:
    """The lines of an entry's text items where every word of the query is."""
    out = []
    for it in sorted(node.items, key=lambda i: i.path):
        full = node.dir / it.path
        if it.kind == "text":
            files = [(full, "")]
        elif it.kind == "directory":
            files = [(full / f, f) for f in cat.files_under(full)
                     if cat.kind_of(full / f) == "text"]
        else:
            continue
        for f, inside in files:
            if not f.is_file():
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for n, line in enumerate(content.splitlines(), 1):
                if hit(line):
                    where = f"{inside}:{n}" if inside else f"{n}"
                    ref = it.id or atlas.where(node, it)
                    out.append(f"{ref}  {label(it.name)}  {where}: {line.strip()[:160]}")
    return out


# --- ls -------------------------------------------------------------------------

def _markers(node: Node) -> dict[str, int]:
    """What is left to do in one node: to describe, new on disk, to review."""
    counts = {"to describe": 0, "new": 0, "to review": 0, "gone": 0}
    if node.m is None:          # never synced: the node, and every file in it
        counts["to describe"] += 1
        if node.kind == "entry":
            counts["new"] += len(cat.uncovered(node.dir, []))
        return counts
    counts["to describe"] += not node.m.described
    if node.kind != "entry":
        return counts
    counts["new"] += len(cat.uncovered(node.dir, node.items))
    for it in node.items:
        full = node.dir / it.path
        if not full.exists():
            counts["gone"] += 1
            continue
        counts["to describe"] += not it.described
        if it.source and it.described and it.sha256 and cat.digest(node.dir, it.path) != it.sha256:
            counts["to review"] += 1
    return counts


def _shown(counts: dict[str, int]) -> str:
    parts = [f"{n} {k}" for k, n in counts.items() if n]
    return f"  [{', '.join(parts)}]" if parts else ""


def _item_marker(node: Node, it: cat.Item) -> str:
    full = node.dir / it.path
    if not full.exists():
        return "  [gone]"
    if not it.described:
        return "  [to describe]"
    if it.source and it.sha256 and cat.digest(node.dir, it.path) != it.sha256:
        return "  [to review]"
    return ""


def _size(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in cat.visible_files(p))


def _date(p: Path) -> str:
    stamps = [p.stat().st_mtime] + ([f.stat().st_mtime for f in cat.visible_files(p)]
                                    if p.is_dir() else [])
    return datetime.date.fromtimestamp(max(stamps)).isoformat()


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def ls(library: Path, target: str | None = None, level: int = 0,
       limit: int = LIMIT) -> list[str]:
    """A topic's topics and entries, with their counts; an entry's items. `level`
    1 adds the descriptions, 2 the kind, size and date as well. Markers say what
    is to describe, new on disk, to review, or gone."""
    atlas = Atlas(library)
    node, item = atlas.resolve(target) if target else (None, None)
    if item is not None:
        return bounded(_ls_item(atlas, node, item, level), limit, "ls -l for less")
    if node is not None and node.kind == "entry":
        return bounded(_ls_entry(atlas, node, level), limit, "ls <item> for one of them")
    children = sorted(atlas.children(node.dir if node else None), key=lambda n: n.dir)
    if not children:
        return ["nothing here"]
    # Only the lines shown are computed: a topic of 500 entries costs 19 of them.
    shown = children if limit <= 0 or len(children) <= limit else children[:limit - 1]
    lines = []
    for child in shown:
        below = atlas.below(child.dir)
        if child.kind == "topic":
            entries = sum(n.kind == "entry" for n in below)
            size = f"{entries} entr{'y' if entries == 1 else 'ies'}"
        else:
            size = f"{len(child.items)} item{'s' * (len(child.items) != 1)}"
        todo: dict[str, int] = {}
        for n in below:
            for k, v in _markers(n).items():
                todo[k] = todo.get(k, 0) + v
        line = (f"{child.dir.name}/  {label(child.name)}  {child.id or '-'}  "
                f"{child.kind}, {size}{_shown(todo)}")
        if level >= 2:
            line += f"  {_human(_size(child.dir))}  {_date(child.dir)}"
        if level >= 1 and child.m and child.m.description:
            line += f" — {child.m.description}"
        lines.append(line)
    if len(shown) < len(children):
        more = len(children) - len(shown)
        lines.append(f"… {more} more — find inside it with --in, or --limit {len(children)}")
    return lines


def _ls_entry(atlas: Atlas, node: Node, level: int) -> list[str]:
    lines = []
    for it in sorted(node.items, key=lambda i: i.path):
        line = f"{it.path}  {label(it.name)}  {it.id or '-'}{_item_marker(node, it)}"
        full = node.dir / it.path
        if level >= 2 and full.exists():
            files = f", {it.files} files" if it.files is not None else ""
            line += f"  {it.kind}{files}  {_human(_size(full))}  {_date(full)}"
        if level >= 1 and it.description:
            line += f" — {it.description}"
        lines.append(line)
    lines += [f"{f}  (new, no item covers it)" for f in cat.uncovered(node.dir, node.items)]
    return lines or ["no item yet — sync the entry"]


def _ls_item(atlas: Atlas, node: Node, item: cat.Item, level: int) -> list[str]:
    """One item: its line, its description, its entry, and a directory's files,
    each with its date and, when an item of its own covers it, that item's id.
    A file without one is covered by the directory alone: a directory marked
    `to review` is told apart from the file that arrived in it that way."""
    line = f"{item.path}  {label(item.name)}  {item.id or '-'}{_item_marker(node, item)}"
    lines = [line, f"in {atlas.where(node)}  {label(node.name)}  {node.id or '-'}"]
    if item.description:
        lines.insert(1, item.description)
    full = node.dir / item.path
    if full.is_dir():
        for f in cat.files_under(full):
            own = cat.covering(node.items, f"{item.path}/{f}")
            mark = f"  → {own.id or own.path}" if own is not item else ""
            lines.append(f"  {f}  {_date(full / f)}{mark}")
    return lines


# --- links ------------------------------------------------------------------------

def links(library: Path, target: str, limit: int = LIMIT) -> list[str]:
    """What an entry or an item cites, and what cites it, from the `id:`
    citations alone, grouped by entry, each with the file that cites it."""
    atlas = Atlas(library)
    node, item = atlas.resolve(target)
    if node is None:
        raise cat.ManifestError("links takes an entry or an item, not the library")
    retired = node.m.retired if node.m else []
    own = ({item.id, *(r.id for r in retired if r.into == item.id)} if item
           else {node.id, *(i.id for i in node.items), *(r.id for r in retired)})
    own.discard(None)
    here = node.dir / item.path if item else node.dir

    cites: dict[Path, list[str]] = {}
    cited: dict[Path, list[str]] = {}
    for f, line, ident in cat.citations(library):
        inside = f == here or here in f.parents
        if inside and ident not in own:
            got = atlas.ids.get(ident)
            if got is None and ident in atlas.retired:
                n, r = atlas.retired[ident]
                fate = f"merged into {r.into}" if r.into else "removed"
                cites.setdefault(n.dir, []).append(
                    f"  {r.name or r.path}  {ident} ({fate} {r.date}) "
                    f"← {f.relative_to(node.dir).as_posix()}:{line}")
                continue
            if got is None:
                cites.setdefault(Path("?"), []).append(
                    f"  {ident} (no such id) ← {f.relative_to(node.dir).as_posix()}:{line}")
                continue
            n, it = got
            what = f"{it.name}  {ident}" if it else f"(the entry)  {ident}"
            cites.setdefault(n.dir, []).append(
                f"  {what} ← {f.relative_to(node.dir).as_posix()}:{line}")
        elif not inside and ident in own:
            by = atlas.nodes.get(cat.node_of(library, f))
            n_dir = by.dir if by else f.parent
            held = atlas.ids.get(ident) or atlas.retired.get(ident)
            target_name = (held[1].name or held[1].path) if held and held[1] else "(the entry)"
            cited.setdefault(n_dir, []).append(
                f"  {target_name} ← {f.relative_to(n_dir).as_posix()}:{line}")

    def group(title: str, found: dict[Path, list[str]]) -> list[str]:
        out = [f"{title}: nothing" if not found else f"{title}:"]
        for d in sorted(found):
            n = atlas.nodes.get(d)
            head = (f" {atlas.where(n)}  {label(n.name)}  {n.id or '-'}" if n
                    else " (unknown ids)")
            out += [head, *found[d]]
        return out

    return bounded(group("cites", cites) + group("cited by", cited), limit,
                   "links <item> for one file")


# --- path ---------------------------------------------------------------------------

def path(library: Path, ident: str) -> str:
    """Where an id is, from the repository's root."""
    atlas = Atlas(library)
    bare = ident.strip().removeprefix("id:")
    bare = cat.canonical(bare) or bare
    seen = set()
    while bare in atlas.retired and bare not in seen:      # merged: follow it
        seen.add(bare)
        node, r = atlas.retired[bare]
        if not r.into:
            was = doc.shown(node.dir / r.path).as_posix()
            return f"removed on {r.date} — it was {was}"
        bare = r.into
    if bare not in atlas.ids:
        raise cat.ManifestError(f"{ident}: no such id")
    node, item = atlas.ids[bare]
    full = node.dir / item.path if item else node.dir
    return doc.shown(full).as_posix()


# --- peek -------------------------------------------------------------------------

def _pages(spec: str | None, total: int) -> list[int]:
    """`3` or `2-5` as zero-based page indexes within the document; 1-2 by default."""
    first, _, last = (spec or "1-2").partition("-")
    try:
        a, b = int(first), int(last or first)
    except ValueError:
        raise cat.ManifestError(f"--pages {spec}: a page, or a range such as 2-5") from None
    return [p - 1 for p in range(max(a, 1), min(b, total) + 1)]


def peek(library: Path, target: str, pages: str | None = None,
         limit: int = LIMIT) -> list[str]:
    """A first look at a file, cheap enough to take before any image: a PDF's
    page count and the text layer of its first pages, an image's size and the
    date and camera it records, a text's first lines, a directory's files."""
    atlas = Atlas(library)
    ident = cat.as_id(library, target)
    if ident is not None:
        if ident not in atlas.ids:
            raise cat.ManifestError(f"{target}: no such id")
        node, item = atlas.ids[ident]
        full = node.dir / item.path if item else node.dir
    else:
        full = cat._inside(library, target)
    size = _human(_size(full))
    kind = cat.kind_of(full)
    if kind == "directory":
        files = cat.files_under(full)
        lines = [f"directory, {len(files)} file{'s' * (len(files) != 1)}, {size}"]
        lines += [f"  {f}  {cat.kind_of(full / f)}  {_human(_size(full / f))}" for f in files]
        return bounded(lines, limit, "peek one file of it")
    if kind == "pdf":
        from core import pdfpage               # pypdfium2, loaded only when needed
        try:
            text = pdfpage.text(full)
        except Exception as exc:               # a damaged file is a finding, not a crash
            return [f"pdf, {size}, not readable: {str(exc).splitlines()[0]}"]
        lines = [f"pdf, {len(text)} page{'s' * (len(text) != 1)}, {size}"]
        for i in _pages(pages, len(text)):
            body = [l.strip() for l in text[i].splitlines() if l.strip()]
            if not body:
                lines.append(f"— p.{i + 1}: no text layer — read it as an image —")
                continue
            lines.append(f"— p.{i + 1} —")
            lines += [l[:200] for l in body]
        return bounded(lines, limit, "--pages to read further")
    if kind == "image":
        return [_image(full, size), "read it to see what it shows"]
    if kind == "text":
        try:
            body = full.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            return [f"file, {size}, not UTF-8 text"]
        lines = [f"text, {len(body)} line{'s' * (len(body) != 1)}, {size}"]
        return bounded(lines + [l[:200] for l in body], limit, "read the file for the rest")
    return [f"{kind}, {size}"]


def _image(p: Path, size: str) -> str:
    """An image's size, and the date and camera its EXIF records, when it can be read."""
    from PIL import Image, UnidentifiedImageError
    try:
        with Image.open(p) as im:
            exif = im.getexif()
            shot = exif.get(306) or exif.get_ifd(0x8769).get(36867)   # DateTime(Original)
            camera = " ".join(str(exif.get(k, "")).strip() for k in (271, 272)).strip()
            facts = [f"image, {im.width}×{im.height} px, {size}"]
    except (UnidentifiedImageError, OSError):
        return f"image, {size}, not readable by PIL (an SVG, or damaged)"
    if shot:
        facts.append(f"taken {str(shot).strip()}")
    if camera:
        facts.append(camera)
    return ", ".join(facts)
