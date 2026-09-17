"""The documentation follows the code — otherwise it lies."""
import re


def test_the_readme_documents_the_epub_command(repo):
    src = (repo / "README.md").read_text(encoding="utf-8")
    assert "make epub" in src


def test_claude_md_and_readme_point_at_every_skill(repo):
    skills = [p.parent.name for p in (repo / ".claude" / "skills").glob("*/SKILL.md")]
    assert skills
    for doc in ("CLAUDE.md", "README.md"):
        src = (repo / doc).read_text(encoding="utf-8")
        for name in skills:
            assert f"`{name}`" in src, f"{doc}: {name}"


def test_claude_md_maps_the_core(repo):
    src = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    modules = [p.stem for p in (repo / "core").glob("*.py") if p.stem != "__init__"]
    assert modules
    for module in modules:
        assert f"`{module}`" in src, module


def test_claude_md_carries_the_roadmap_contract(repo):
    src = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    contract = src.split("## Roadmaps", 1)[1]
    assert re.search(r"^Root\s*: docs/roadmap/", contract, re.M)
    assert re.search(r"^Checks\s*: make test", contract, re.M)


def test_no_document_mentions_the_old_layout(repo):
    for name in ("README.md", "CLAUDE.md", ".claude/skills/pdf/SKILL.md"):
        src = (repo / name).read_text(encoding="utf-8")
        assert not re.search(r"\bpdfs/|\blib/|(?<![\w/])templates/", src), name


def test_every_makefile_target_is_in_the_help(repo):
    src = (repo / "Makefile").read_text(encoding="utf-8")
    help_text = src.split("help:")[1].split("\n\n")[0]
    targets = set(re.findall(r"^([a-z-]+):", src, re.M)) - {"help", "check"}
    for t in targets:
        assert f"make {t}" in help_text, f"target {t} missing from `make help`"
