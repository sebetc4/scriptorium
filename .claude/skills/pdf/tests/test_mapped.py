"""`make new` and `make import` leave the entry they create on the map: its
manifest and those of the topics above it written, and what is left to name
printed. Each runs into a library in a temporary directory."""
import shutil
import sys
from pathlib import Path

import pymupdf
import pytest

import ingest
import new
from core import catalogue as cat

REPO = Path(__file__).resolve().parents[4]


@pytest.fixture
def library(tmp_path, monkeypatch):
    for module in (new, ingest):
        monkeypatch.setattr(module, "ROOT", tmp_path)
        monkeypatch.setattr(module, "LIBRARY", tmp_path / "library")
    return tmp_path / "library"


def test_new_maps_the_entry_it_creates(library, tmp_path, monkeypatch, capsys):
    (tmp_path / "brand").mkdir()          # new.py reads brand/tokens.yaml
    shutil.copy(REPO / "brand" / "tokens.yaml", tmp_path / "brand")
    monkeypatch.setattr(sys, "argv", ["new.py", "watch/station"])
    assert new.main() == 0
    for d in (library / "watch", library / "watch" / "station"):
        assert (d / cat.MANIFEST).is_file()
    assert "map: watch/station synced — to name: watch/station, watch" in capsys.readouterr().out


def test_import_maps_the_entry_it_creates(library, tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "manuel.pdf"
    with pymupdf.open() as d:
        d.new_page().insert_text((72, 72), "Lave-linge K-450 — notice")
        d.save(pdf)
    monkeypatch.setattr(sys, "argv", ["ingest.py", str(pdf), "watch/washer",
                                      "--lang", "fr", "--no-page-images"])
    assert ingest.main() == 0
    assert (library / "watch" / "washer" / cat.MANIFEST).is_file()
    out = capsys.readouterr().out
    assert "map: watch/washer synced" in out and "to describe: sources/manuel.pdf" in out
