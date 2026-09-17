#!/usr/bin/env python3
"""Install or update the Lucide icon set in brand/icons/.

    python brand/icons.py            # install the pinned version
    python brand/icons.py 1.41.0     # switch version and reinstall

Only the `icons/` directory of the `lucide-static` npm package is extracted: the
full package weighs 49 MB (fonts, sprite, JS bindings) for 969 kB of useful SVG.
"""
from __future__ import annotations

import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "brand" / "icons"
VERSION_FILE = DEST / "VERSION"
PINNED = "1.40.0"
URL = "https://registry.npmjs.org/lucide-static/-/lucide-static-{v}.tgz"
LICENSE = """Lucide — https://lucide.dev
Licence ISC. Copyright (c) for portions of Lucide are held by Cole Bemis
2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are
held by Lucide Contributors 2022.

These files are extracted from the `lucide-static` npm package and must not be
edited: regenerate them with `make icons`.
"""


def main() -> int:
    version = sys.argv[1] if len(sys.argv) > 1 else PINNED
    url = URL.format(v=version)
    print(f"lucide-static {version}")

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "lucide.tgz"
        try:
            with urllib.request.urlopen(url, timeout=120) as r, archive.open("wb") as f:
                shutil.copyfileobj(r, f)
        except Exception as exc:
            print(f"error: download failed — {exc}", file=sys.stderr)
            return 1

        staging = Path(tmp) / "out"
        with tarfile.open(archive) as tar:
            members = [m for m in tar.getmembers()
                       if m.isfile()
                       and m.name.startswith("package/icons/")
                       and m.name.endswith(".svg")
                       and "/" not in m.name[len("package/icons/"):]]
            if not members:
                print("error: no icon in the archive", file=sys.stderr)
                return 1
            tar.extractall(staging, members=members, filter="data")

        src = staging / "package" / "icons"
        if DEST.exists():
            shutil.rmtree(DEST)
        shutil.move(src, DEST)

    VERSION_FILE.write_text(f"{version}\n", encoding="utf-8")
    (DEST / "LICENSE").write_text(LICENSE, encoding="utf-8")
    n = len(list(DEST.glob("*.svg")))
    size = sum(f.stat().st_size for f in DEST.glob("*.svg")) / 1024
    print(f"  ✓ {n} icons in brand/icons/ ({size:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
