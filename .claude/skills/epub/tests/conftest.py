"""Puts this skill's own scripts on the import path.

pytest puts the *test* file's directory on sys.path, never the directory of the
code under test. Each skill therefore carries this file rather than one root
conftest inserting all five `scripts/` directories: kept local, two skills'
flat module names cannot collide.

The shared core needs nothing here — it is an installed package.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
