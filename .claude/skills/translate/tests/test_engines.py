"""engines.py: one interface, the agent engine behind it, the local seam."""
import pytest

import engines
import zones


def request(**over):
    fields = dict(index=2, total=5, source_lang="en", target_lang="fr",
                  text=f"The stone must be hot for {zones.token(7)}.\n",
                  context_before="## Heat", previous_translation="## Chaleur",
                  headings=("Baking", "Heat"), glossary={"yeast": "levure"},
                  keep=("PanPro",))
    fields.update(over)
    return engines.Request(**fields)


def test_the_agent_engine_is_pending_until_its_answer_exists(tmp_path):
    engine = engines.AgentEngine(tmp_path)
    with pytest.raises(engines.Pending) as raised:
        engine.translate(request())
    assert raised.value.request_path.is_file()
    assert raised.value.answer_path == engine.answer_path(2)


def test_the_request_tells_the_agent_everything_a_chunk_cannot_carry(tmp_path):
    engine = engines.AgentEngine(tmp_path)
    with pytest.raises(engines.Pending) as raised:
        engine.translate(request())
    text = raised.value.request_path.read_text(encoding="utf-8")
    for expected in ("en → fr", "3 of 5", "Baking › Heat", "## Heat",
                     "## Chaleur", "yeast → levure", "PanPro",
                     str(engine.answer_path(2)), zones.token(7),
                     "The stone must be hot for"):
        assert expected in text, expected


def test_the_agent_engine_returns_the_answer_it_finds(tmp_path):
    engine = engines.AgentEngine(tmp_path)
    engine.answer_path(2).parent.mkdir(parents=True)
    engine.answer_path(2).write_text("La pierre doit être chaude.\n", encoding="utf-8")
    assert engine.translate(request()) == "La pierre doit être chaude.\n"


def test_the_local_engine_is_a_seam_that_says_where_it_will_come_from(tmp_path):
    with pytest.raises(engines.EngineUnavailable) as raised:
        engines.LocalEngine(tmp_path).translate(request())
    assert "docs/local-translation.md" in str(raised.value)


def test_the_registry_names_both_engines():
    assert set(engines.ENGINES) == {"agent", "local"}
    for name, cls in engines.ENGINES.items():
        assert cls.name == name


def test_every_engine_satisfies_the_interface(tmp_path):
    for cls in engines.ENGINES.values():
        assert isinstance(cls(tmp_path), engines.Engine)


def test_the_folder_of_the_answer_exists_when_the_request_is_written(tmp_path):
    engine = engines.AgentEngine(tmp_path)
    with pytest.raises(engines.Pending) as raised:
        engine.translate(request())
    assert raised.value.answer_path.parent.is_dir()
