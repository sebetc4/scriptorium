#!/usr/bin/env python3
"""Create a document directory from a template.

    python .claude/skills/pdf/scripts/new.py finance/report-q3 --preset report --title "Report Q3"

The path is relative to library/; its depth is free, the intermediate
directories serve as topics and are created as needed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

# From the core, not from this file's parents: it lives inside a skill.
from core.doc import DOCUMENT, ENTRY, LIBRARY, ROOT, doc_dir

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def slugify(s: str) -> str:
    s = s.lower().strip()
    for a, b in (("à", "a"), ("â", "a"), ("é", "e"), ("è", "e"), ("ê", "e"),
                 ("ë", "e"), ("î", "i"), ("ï", "i"), ("ô", "o"), ("ö", "o"),
                 ("û", "u"), ("ü", "u"), ("ù", "u"), ("ç", "c")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "document"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a new document.")
    ap.add_argument("path", help="path under library/, e.g. finance/report-q3")
    ap.add_argument("--preset", default="report",
                    choices=sorted(p.name for p in TEMPLATES.iterdir() if p.is_dir()))
    ap.add_argument("--title", help="title (default: derived from the directory name)")
    args = ap.parse_args()

    parts = [slugify(p) for p in Path(args.path).parts if p not in (".", "..")]
    for p in parts:
        if not SLUG_RE.match(p):
            print(f"error: invalid path segment “{p}”", file=sys.stderr)
            return 1
    dest = LIBRARY.joinpath(*parts)
    if (doc_dir(dest) / ENTRY).exists():
        print(f"error: the document already exists — {dest.relative_to(ROOT)}",
              file=sys.stderr)
        return 1

    tokens = yaml.safe_load((ROOT / "brand" / "tokens.yaml").read_text(encoding="utf-8"))
    title = args.title or parts[-1].replace("-", " ").capitalize()
    values = {
        "{{TITLE}}": title,
        "{{DATE}}": dt.date.today().isoformat(),
        "{{AUTHOR}}": "First Last",
    }

    # Only `document/` is created. The four roles beside it — sources/,
    # study/, generators/, .work/ — appear when something has to go in them:
    # an empty directory made in advance teaches nothing and invites the wrong
    # file (docs/architecture.md §11).
    inside = doc_dir(dest)
    (inside / "assets").mkdir(parents=True, exist_ok=True)
    (inside / "assets" / ".gitkeep").touch()

    src = (TEMPLATES / args.preset / "index.md").read_text(encoding="utf-8")
    for k, v in values.items():
        src = src.replace(k, v)
    (inside / ENTRY).write_text(src, encoding="utf-8")

    rel = dest.relative_to(ROOT)
    print(f"✓ {rel}/{DOCUMENT}/{ENTRY}  (preset: {args.preset})")
    print(f"  edit the content, then: make build DOC={'/'.join(parts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
