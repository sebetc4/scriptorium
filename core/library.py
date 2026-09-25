"""The user's library, checked: what `make check-library` reports.

`library/` is user content, reorganised at any time. The suite never reads it —
a rename there is not a defect in the code — and this module is where it is
read instead, on request, with every finding naming the document it concerns.

Read-only by construction: each document is converted in memory and nothing is
written — no `.work/`, no `out/`, no EPUB. Building stays `make build` and
`make epub`.

In the core rather than in a skill: it is reached by `make`, outside every
skill, and it checks what both backbones read (docs/architecture.md §2).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from core import catalogue as cat
from core import doc

# The five roles of a document root, docs/architecture.md §11.
ROLES = {doc.DOCUMENT, doc.SOURCES, doc.STUDY, doc.GENERATORS, doc.WORK}
# What the anatomy does not place yet, and a skill already writes at the root:
# `translate` reads a document's glossary there (docs/document.md, *What the
# anatomy does not place yet*). Reporting it would fail every translated document.
TOLERATED = {"glossary.yaml", cat.MANIFEST}
# What a tool computes from `sources/` goes to `study/`. Found in `sources/`, it
# is derived material in the one directory that belongs to the user.
DERIVED = {"extracted.md", "meta.json", "pages"}
# A discussion's journal, `discussion` skill: an index, its topics, and the
# sessions they link to. It exists before `document/` does, so it is found on
# its own rather than through `documents()`.
JOURNAL = "discussion"
# An inline Markdown link's target, up to a title or the closing parenthesis.
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")


@dataclass(frozen=True)
class Defect:
    where: str      # the document, `<topic…>/<slug>`, or a directory above one
    kind: str       # anatomy | derived | generator | layout | load | convert | xhtml | journal
                    # | manifest | id | citation
    what: str

    def __str__(self) -> str:
        return f"{self.where} — {self.kind}: {self.what}"


def documents(library: Path) -> list[Path]:
    """Every document root of the library, in path order."""
    return sorted(p.parent.parent
                  for p in library.rglob(f"{doc.DOCUMENT}/{doc.ENTRY}"))


def layout(library: Path) -> list[Defect]:
    """What sits in the library's tree and belongs to no document's shape."""
    found = []
    for p in sorted(library.rglob("*")):
        if not p.is_dir():
            continue
        where = p.relative_to(library).as_posix()
        if p.name == "out":
            found.append(Defect(where, "layout", "a build output inside the "
                                "library; outputs go to out/ at the repository root"))
        elif p.name == "source":
            found.append(Defect(where, "layout", "“source” in the singular; the "
                                "material a document was made from goes in sources/"))
    return found


def anatomy(d: Path, where: str) -> list[Defect]:
    """The five roles and nothing else, docs/architecture.md §11."""
    found = [Defect(where, "anatomy", f"{p.name} — not one of the five roles "
                    f"({', '.join(sorted(ROLES))})")
             for p in sorted(d.iterdir()) if p.name not in ROLES | TOLERATED]
    sources = d / doc.SOURCES
    found += [Defect(where, "derived", f"{doc.SOURCES}/{name} — computed by a "
                     f"tool, it belongs in {doc.STUDY}/")
              for name in sorted(DERIVED) if (sources / name).exists()]
    found += [Defect(where, "generator", f"{p.relative_to(d).as_posix()} — code "
                     f"that draws an asset lives in {doc.GENERATORS}/")
              for p in sorted(d.rglob("*.py")) if p.parent.name != doc.GENERATORS]
    return found


def journals(library: Path) -> list[Path]:
    """Every `study/` holding a discussion's journal, in either layout, in path order."""
    return sorted({p.parent for p in library.rglob(f"{JOURNAL}*")
                   if p.parent.name == doc.STUDY and p.name in (JOURNAL, f"{JOURNAL}.md")})


def journal(study: Path, where: str) -> list[Defect]:
    """A journal in three layers whose index and topics link only to what exists.

    The sessions are not read: they are never rewritten, so a link in one is
    whatever was true the day it was written — and a topic's name is permanent
    precisely so that it stays true."""
    single, layered = study / f"{JOURNAL}.md", study / JOURNAL
    found = []
    if single.is_file():
        found.append(Defect(where, "journal", f"{doc.STUDY}/{single.name} — a "
                            f"journal in one file; the layout is {doc.STUDY}/{JOURNAL}/"
                            f"index.md, topics/, sessions/ (the discussion skill "
                            f"migrates it)"))
    if not layered.is_dir():
        return found
    index = layered / "index.md"
    if not index.is_file():
        return found + [Defect(where, "journal", f"{doc.STUDY}/{JOURNAL}/ has no index.md")]
    for page in [index, *sorted((layered / "topics").glob("*.md"))]:
        text = page.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if re.match(r"[a-z][a-z0-9+.-]*:|#", target):   # a URL, or an anchor here
                continue
            if not (page.parent / target.split("#", 1)[0]).exists():
                found.append(Defect(where, "journal", f"{page.relative_to(study.parent).as_posix()}"
                                    f" links to {target}, which does not exist"))
    return found


def manifests(library: Path) -> list[Defect]:
    """Every directory described, every id well formed and held once, every item
    on the disk — core/catalogue.py."""
    found = []
    for d, kind in cat.nodes(library):
        where = d.relative_to(library).as_posix()
        try:
            m = cat.read(d)
        except cat.ManifestError as exc:
            found.append(Defect(where, "manifest", f"{cat.MANIFEST} unreadable: {exc}"
                                if (d / cat.MANIFEST).exists() else str(exc)))
            continue
        if kind == "topic" and m.items is not None:
            found.append(Defect(where, "manifest", "a topic's manifest lists items; "
                                "a topic holds only directories"))
        missing = [k for k in ("name", "description") if not getattr(m, k)]
        if missing:
            found.append(Defect(where, "manifest", f"no {' and no '.join(missing)} "
                                f"— describe the {kind}"))
        labels = ([(m.id, "its id")] + [(i.id, i.path) for i in m.items or []]
                  + [(r.id, f"retired {r.path}") for r in m.retired])
        found += [Defect(where, "id", f"{label}: {ident!r} is not an id (prefix, "
                         f"hyphen, {cat.SUFFIX} characters)")
                  for ident, label in labels if ident and not cat.ID.fullmatch(ident)]
        paths = [i.path for i in m.items or []]
        found += [Defect(where, "manifest", f"two items for {p}")
                  for p in sorted({p for p in paths if paths.count(p) > 1})]
        found += [Defect(where, "manifest", f"{p} is gone from the disk — sync "
                         "follows a moved source; otherwise remove the item")
                  for p in dict.fromkeys(paths) if not (d / p).exists()]
    for ident, holders in sorted(cat.ids(library).items()):
        if len(holders) > 1:
            places = [f"{h.relative_to(library).as_posix()}" + (f"/{i.path}" if i else "")
                      for h, i in holders]
            found.append(Defect(holders[0][0].relative_to(library).as_posix(), "id",
                                f"{ident} held {len(holders)} times ({', '.join(places)})"
                                " — a copied directory: say which copy keeps its ids"))
    return found


def citations(library: Path) -> list[Defect]:
    """Every `id:` citation leads to a node, and none sits in `document/`: ids
    serve the agent, never the reader."""
    known = cat.ids(library)
    found = []
    for p, line, ident in cat.citations(library):
        node = cat.node_of(library, p)
        where, inside = node.relative_to(library).as_posix(), p.relative_to(node).as_posix()
        if inside.split("/", 1)[0] == doc.DOCUMENT:
            found.append(Defect(where, "citation", f"{inside}:{line} cites id:{ident} — "
                                "no id goes into document/"))
        elif ident not in known:
            found.append(Defect(where, "citation", f"{inside}:{line} cites id:{ident}, "
                                "which no manifest holds"))
    return found


def todo(library: Path) -> dict[str, int]:
    """What remains to do, reported without failing: files no item covers,
    items not described yet, sources changed since they were described."""
    counts = {"uncovered": 0, "to describe": 0, "changed": 0}
    for d, kind in cat.nodes(library):
        if kind != "entry":
            continue
        try:
            items = cat.read(d).items or []
        except cat.ManifestError:
            continue
        counts["uncovered"] += len(cat.uncovered(d, items))
        counts["to describe"] += sum(not i.described for i in items)
        counts["changed"] += sum(1 for i in items
                                 if i.source and i.described and i.sha256
                                 and (d / i.path).exists()
                                 and cat.digest(d, i.path) != i.sha256)
    return counts


def readable(d: Path, where: str) -> list[Defect]:
    """What the build would refuse: a front matter it cannot load, a body that
    does not convert, an XHTML the EPUB could not package."""
    try:
        fm, body = doc.load_doc(d)
    except (doc.DocError, yaml.YAMLError) as exc:
        return [Defect(where, "load", str(exc))]
    try:
        tokens = doc.token_map(d, {**fm, "theme": "epub"})
        html, _ = doc.convert(body, tokens, d.name, icon_color="currentColor")
    except Exception as exc:  # user content: report it, never crash on it
        return [Defect(where, "convert", f"{type(exc).__name__}: {exc}")]
    try:
        doc.check_xhtml(html, where)
    except doc.DocError as exc:
        return [Defect(where, "xhtml", str(exc).split(" — ", 1)[-1])]
    return []


def check(library: Path | None = None) -> list[Defect]:
    """Every defect of the library, the layout's first, then document by document."""
    library = doc.LIBRARY if library is None else library
    if not library.is_dir():
        return []
    found = layout(library)
    for d in documents(library):
        where = d.relative_to(library).as_posix()
        found += anatomy(d, where) + readable(d, where)
    for study in journals(library):
        found += journal(study, study.parent.relative_to(library).as_posix())
    return found + manifests(library) + citations(library)


def main() -> int:
    library = doc.LIBRARY
    if not library.is_dir():
        print(f"no library at {doc.shown(library)} — nothing to check")
        return 0
    count = len(documents(library))
    defects = check(library)
    for defect in defects:
        print(defect)
    n = len(defects)
    verdict = "no defect" if not n else f"{n} defect{'s' * (n != 1)}"
    print(f"{count} document{'s' * (count != 1)} checked — {verdict}")
    left = todo(library)
    print(f"to do: {left['uncovered']} file{'s' * (left['uncovered'] != 1)} no item covers, "
          f"{left['to describe']} item{'s' * (left['to describe'] != 1)} to describe, "
          f"{left['changed']} source{'s' * (left['changed'] != 1)} changed since described")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
