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

import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from core import doc

# The five roles of a document root, docs/architecture.md §11.
ROLES = {doc.DOCUMENT, doc.SOURCES, doc.STUDY, doc.GENERATORS, doc.WORK}
# What a tool computes from `sources/` goes to `study/`. Found in `sources/`, it
# is derived material in the one directory that belongs to the user.
DERIVED = {"extracted.md", "meta.json", "pages"}


@dataclass(frozen=True)
class Defect:
    where: str      # the document, `<topic…>/<slug>`, or a directory above one
    kind: str       # anatomy | derived | generator | layout | load | convert | xhtml
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
             for p in sorted(d.iterdir()) if p.name not in ROLES]
    sources = d / doc.SOURCES
    found += [Defect(where, "derived", f"{doc.SOURCES}/{name} — computed by a "
                     f"tool, it belongs in {doc.STUDY}/")
              for name in sorted(DERIVED) if (sources / name).exists()]
    found += [Defect(where, "generator", f"{p.relative_to(d).as_posix()} — code "
                     f"that draws an asset lives in {doc.GENERATORS}/")
              for p in sorted(d.rglob("*.py")) if p.parent.name != doc.GENERATORS]
    return found


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
    return found


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
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
