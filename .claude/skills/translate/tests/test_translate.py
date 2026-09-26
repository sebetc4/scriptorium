"""translate.py end to end: prepare, run an engine, apply, cross-check."""
import json
import re

import pytest

import engines
import translate
from core import doc
import zones

DOC = """---
title: Baking bread        # the cover's title
subtitle: Sizing the yeast
preset: report
lang: fr
theme: light
---

## The yeast

With 500 g of flour and a proofing time of 1.5 h, the dough takes 7 g of yeast.

```python
yeast = (500 / 1000) * 14
```

!!! warning "Check the oven"
    The stone must be hot :circle-alert.alert:.

## Baking

- Put the salt away from the yeast.
- Bake 35 min at 240 °C in the PanPro.
"""

WORDS = {"Baking bread": "Faire du pain", "Sizing the yeast": "Doser la levure",
         "The yeast": "La levure",
         "With 500 g of flour and a proofing time of 1.5 h, the dough takes 7 g of yeast.":
         "Avec 500 g de farine et une levée de 1,5 h, la pâte prend 7 g de levure.",
         '"Check the oven"': '"Vérifier le four"',
         "The stone must be hot": "La pierre doit être chaude", "Baking": "Cuisson",
         "Put the salt away from the yeast.": "Placer le sel loin de la levure.",
         "Bake 35 min at 240 °C in the PanPro.": "Cuire 35 min à 240 °C dans le PanPro."}


def fake_translate(text):
    for en, fr in sorted(WORDS.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(en, fr)
    return text


class DictionaryEngine:
    """A stand-in for a local model: answers at once, through the interface."""
    name = "dictionary"
    seen = []

    def __init__(self, workspace):
        self.workspace = workspace

    def translate(self, request):
        DictionaryEngine.seen.append(request)
        return fake_translate(request.text)


@pytest.fixture
def library(tmp_path, monkeypatch):
    lib = tmp_path / "library"
    d = lib / "watch" / "bread"
    (d / doc.STUDY).mkdir(parents=True)
    (doc.doc_dir(d)).mkdir(parents=True)
    (doc.doc_dir(d) / doc.ENTRY).write_text(DOC, encoding="utf-8")
    (d / doc.STUDY / "meta.json").write_text(json.dumps({"source_language": "en"}))
    monkeypatch.setattr(translate, "LIBRARY", lib)
    monkeypatch.setitem(engines.ENGINES, "dictionary", DictionaryEngine)
    DictionaryEngine.seen = []
    return d


def workspace(d):
    return d / doc.STUDY / translate.WORKSPACE


def answer_all_as_agent(d, transform=fake_translate):
    """Do what the agent does: read each request, write each answer."""
    for _ in range(50):
        if translate.main(["run", "watch/bread"]) == 0:
            return
        requests = sorted((workspace(d) / "requests").glob("*.md"))
        text = requests[-1].read_text(encoding="utf-8")
        answer = re.search(r"Write the translation to:\n\n    (\S+)", text).group(1)
        source = text.split("<<<<<<<< BEGIN\n", 1)[1].rsplit(">>>>>>>> END", 1)[0]
        with open(answer, "w", encoding="utf-8") as f:
            f.write(transform(source))
    raise AssertionError("the agent loop did not finish")


def test_the_target_is_lang_and_the_source_comes_from_the_import(library, capsys):
    assert translate.main(["prepare", "watch/bread"]) == 0
    job = json.loads((workspace(library) / "job.json").read_text())
    assert (job["source_lang"], job["target_lang"]) == ("en", "fr")
    assert "en → fr" in capsys.readouterr().out


def test_a_document_already_in_its_target_language_is_refused(library, capsys):
    (library / doc.STUDY / "meta.json").write_text(json.dumps({"source_language": "fr"}))
    assert translate.main(["prepare", "watch/bread"]) == 1
    assert "set lang:" in capsys.readouterr().err


def test_a_document_without_an_explicit_lang_is_refused(library, capsys):
    (doc.doc_dir(library) / doc.ENTRY).write_text(DOC.replace("lang: fr\n", ""), encoding="utf-8")
    assert translate.main(["prepare", "watch/bread"]) == 1
    assert "lang:" in capsys.readouterr().err


def test_a_captured_page_gives_its_language_through_its_metadata(library):
    (library / doc.STUDY / "meta.json").write_text(json.dumps({"metadata": {"language": "en-GB"}}))
    assert translate.main(["prepare", "watch/bread"]) == 0
    assert json.loads((workspace(library) / "job.json").read_text())["source_lang"] == "en"


def test_the_agent_engine_goes_through_requests_and_answers(library):
    translate.main(["prepare", "watch/bread", "--budget", "120"])
    assert translate.main(["run", "watch/bread"]) == 1         # pending: a request to read
    assert (workspace(library) / "requests" / "000.md").is_file()
    answer_all_as_agent(library)
    assert translate.main(["apply", "watch/bread"]) == 0
    out = (doc.doc_dir(library) / doc.ENTRY).read_text(encoding="utf-8")
    assert "## La levure" in out and "## Cuisson" in out
    assert "yeast = (500 / 1000) * 14" in out                      # the code block, intact
    assert '!!! warning "Vérifier le four"' in out           # the admonition type, intact
    assert ":circle-alert.alert:" in out                        # the icon, intact


def test_apply_rewrites_the_front_matter_strings_only(library):
    translate.main(["prepare", "watch/bread"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    assert translate.main(["apply", "watch/bread", "--engine", "dictionary"]) == 0
    front = (doc.doc_dir(library) / doc.ENTRY).read_text(encoding="utf-8").split("---")[1]
    assert "title: Faire du pain        # the cover's title" in front
    assert "subtitle: Doser la levure" in front
    for line in ("preset: report", "lang: fr", "theme: light", "translated_from: en"):
        assert line in front


def test_a_run_through_a_model_like_engine_carries_context_between_chunks(library):
    translate.main(["prepare", "watch/bread", "--budget", "120"])
    assert translate.main(["run", "watch/bread", "--engine", "dictionary"]) == 0
    body_requests = [r for r in DictionaryEngine.seen if r.index > 0]
    assert len(body_requests) > 2
    later = body_requests[-1]
    assert later.context_before and later.previous_translation
    assert later.headings == ("Baking",)


def test_an_answer_that_drops_a_placeholder_is_refused_at_run(library, capsys):
    translate.main(["prepare", "watch/bread"])
    translate.main(["run", "watch/bread"])
    request = (workspace(library) / "requests" / "000.md").read_text(encoding="utf-8")
    answer = re.search(r"Write the translation to:\n\n    (\S+)", request).group(1)
    source = request.split("<<<<<<<< BEGIN\n", 1)[1].rsplit(">>>>>>>> END", 1)[0]
    with open(answer, "w", encoding="utf-8") as f:
        f.write(zones.TOKEN_RE.sub("", fake_translate(source), count=1))
    assert translate.main(["run", "watch/bread"]) == 1
    assert "missing placeholder" in capsys.readouterr().err


def test_a_qc_error_blocks_apply_and_leaves_the_document_untouched(library, capsys):
    translate.main(["prepare", "watch/bread"])
    answer_all_as_agent(library, transform=lambda t: fake_translate(t).replace("240 °C", "420 °C"))
    assert translate.main(["apply", "watch/bread"]) == 1
    assert "240" in capsys.readouterr().err
    assert (doc.doc_dir(library) / doc.ENTRY).read_text(encoding="utf-8") == DOC


def test_apply_refuses_a_document_changed_since_prepare(library, capsys):
    translate.main(["prepare", "watch/bread"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    (doc.doc_dir(library) / doc.ENTRY).write_text(DOC + "\nA late edit.\n", encoding="utf-8")
    assert translate.main(["apply", "watch/bread", "--engine", "dictionary"]) == 1
    assert "changed since" in capsys.readouterr().err


def test_a_translated_document_is_not_prepared_twice(library, capsys):
    translate.main(["prepare", "watch/bread"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    translate.main(["apply", "watch/bread", "--engine", "dictionary"])
    assert translate.main(["prepare", "watch/bread"]) == 1
    assert "translated_from" in capsys.readouterr().err


def test_the_glossary_of_the_document_reaches_the_engine_and_the_checks(library, capsys):
    (library / "glossary.yaml").write_text("terms:\n  yeast: levure\nkeep:\n  - PanPro\n")
    translate.main(["prepare", "watch/bread"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    assert any(r.glossary == {"yeast": "levure"} for r in DictionaryEngine.seen)
    assert translate.main(["apply", "watch/bread", "--engine", "dictionary"]) == 0


def test_the_local_engine_says_it_is_not_there_yet(library, capsys):
    translate.main(["prepare", "watch/bread"])
    assert translate.main(["run", "watch/bread", "--engine", "local"]) == 1
    assert "docs/local-translation.md" in capsys.readouterr().err


def test_cross_check_names_the_chunk_two_engines_disagree_on(library, capsys):
    translate.main(["prepare", "watch/bread", "--budget", "120"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    answer_all_as_agent(library, transform=lambda t: fake_translate(t).replace("7 g", "9 g"))
    capsys.readouterr()
    assert translate.main(["cross-check", "watch/bread", "--engines", "agent", "dictionary"]) == 0
    out = capsys.readouterr().out
    assert "disagree on numbers" in out
    assert out.count("disagree") == 1


def test_preparing_again_keeps_only_the_answers_whose_chunk_did_not_change(library, capsys):
    translate.main(["prepare", "watch/bread", "--budget", "120"])
    translate.main(["run", "watch/bread", "--engine", "dictionary"])
    answers = workspace(library) / "responses" / "dictionary"
    before = sorted(p.name for p in answers.iterdir())
    assert translate.main(["prepare", "watch/bread", "--budget", "120"]) == 0
    assert sorted(p.name for p in answers.iterdir()) == before       # nothing changed: all kept
    assert translate.main(["prepare", "watch/bread", "--budget", "4000"]) == 0
    kept = sorted(p.name for p in answers.iterdir())
    assert kept == ["000.md"]                                        # only the front matter's chunk is the same
    assert "discarded" in capsys.readouterr().out
