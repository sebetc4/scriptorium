#!/usr/bin/env python3
"""Archive images as evidence: capped recompression and a manifest.

    archive_images.py raw/ --dest images [--full detail.jpg]
    archive_images.py --plan plan.json --dest images

For every image, the manifest records the SHA-256 of the **original** — taken
before recompression — its origin, its caption, and its original and stored
dimensions. Two days later nobody remembers where an image came from; the
manifest was consulted constantly while writing the notes, and the digest
proves the piece was not altered.

Recompression caps the long side at 2600 px, quality 88, progressive: 36 MB
became 21 MB on the investigation with no loss of small print. The
two or three decisive pieces keep their full size (`--full`).

A plan is the editorial half, written by hand: which source becomes which file,
from where, with which caption. It is JSON, and its `source` paths are relative
to the plan file:

    {"diagram-redrawn.jpg": {"source": "raw/Ab3dE5f.jpeg",
                             "origin": "https://imgur.com/a/Xy7Kq2",
                             "caption": "The diagram, redrawn by a forum member",
                             "max_side": 0}}

`max_side: 0` keeps the full size. Without a plan, every image of the folder is
archived under its own name, with an empty origin and caption to fill in.

A second run into the same destination updates the manifest's entries by file
name; it does not discard the others.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from _sourcing import ToolError, absolute, run

MAX_SIDE = 2600
QUALITY = 88
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}


def entries_from_folder(folder: Path, full: set[str]) -> list[dict]:
    if not folder.is_dir():
        raise ToolError(f"{folder}: not a folder")
    return [{"file": f.name, "source": f, "origin": "", "caption": "",
             "max_side": 0 if f.name in full else MAX_SIDE}
            for f in sorted(folder.iterdir()) if f.suffix.lower() in IMAGE_SUFFIXES]


def entries_from_plan(plan: Path) -> list[dict]:
    try:
        data = json.loads(plan.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ToolError(f"{plan}: unreadable plan — {exc}")
    return [{"file": name, "source": (plan.parent / e["source"]).resolve(),
             "origin": e.get("origin", ""), "caption": e.get("caption", ""),
             "max_side": e.get("max_side", MAX_SIDE)}
            for name, e in sorted(data.items())]


def archive(entry: dict, dest: Path) -> dict:
    src: Path = entry["source"]
    original = src.read_bytes()
    with Image.open(src) as im:
        im.load()
        size = im.size
        cap = entry["max_side"]
        if cap and max(size) > cap:
            im.thumbnail((cap, cap), Image.LANCZOS)
        target = dest / entry["file"]
        if target.suffix.lower() == ".png":
            im.save(target, optimize=True)
        else:
            im.convert("RGB").save(target, quality=QUALITY, optimize=True, progressive=True)
        stored = im.size
    return {"file": entry["file"], "origin": entry["origin"], "caption": entry["caption"],
            "original_size": list(size), "stored_size": list(stored),
            "sha256_original": hashlib.sha256(original).hexdigest(),
            "bytes": target.stat().st_size}


def tool(argv: list[str] | None) -> None:
    ap = argparse.ArgumentParser(description="Archive images with a provenance manifest.")
    ap.add_argument("folder", nargs="?", help="a folder of images (or use --plan)")
    ap.add_argument("--plan", help="a JSON plan: destination name → source, origin, caption")
    ap.add_argument("--dest", required=True)
    ap.add_argument("--full", action="append", default=[], metavar="NAME",
                    help="keep this file at full size (repeatable)")
    args = ap.parse_args(argv)

    if bool(args.folder) == bool(args.plan):
        raise ToolError("give either a folder or --plan")
    dest = absolute(args.dest)
    entries = (entries_from_plan(absolute(args.plan)) if args.plan
               else entries_from_folder(absolute(args.folder), set(args.full)))
    if not entries:
        raise ToolError("no image to archive")

    dest.mkdir(parents=True, exist_ok=True)
    manifest_path = dest / "manifest.json"
    manifest = ({e["file"]: e for e in json.loads(manifest_path.read_text(encoding="utf-8"))}
                if manifest_path.exists() else {})
    problems = []
    for entry in entries:
        if not entry["source"].is_file():
            problems.append(f"{entry['source']}: missing")
            continue
        try:
            record = archive(entry, dest)
        except (UnidentifiedImageError, OSError):
            problems.append(f"{entry['source']}: not a readable image — an error page?")
            continue
        manifest[record["file"]] = record
        print(f"  ✓ {dest / record['file']}  {record['original_size'][0]}×{record['original_size'][1]}"
              f" → {record['stored_size'][0]}×{record['stored_size'][1]}, {record['bytes'] // 1024} kB")

    manifest_path.write_text(json.dumps(sorted(manifest.values(), key=lambda e: e["file"]),
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓ {manifest_path}  ({len(manifest)} entries)")
    if problems:
        raise ToolError(f"{len(problems)} image(s) not archived:\n    " + "\n    ".join(problems))


def main(argv: list[str] | None = None) -> int:
    return run(tool, argv)


if __name__ == "__main__":
    sys.exit(main())
