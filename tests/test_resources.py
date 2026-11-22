from __future__ import annotations

from pathlib import Path

from check_resources import (
    bare_markdown_tokens,
    missing_bare_markdown_references,
)


def make_skill(root: Path, name: str) -> Path:
    skill = root / "skills" / name
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    return skill


def test_bare_markdown_tokens_only_follow_reference_cues() -> None:
    assert bare_markdown_tokens("For commands, see quick-reference.md.") == ["quick-reference.md"]
    assert bare_markdown_tokens("Write the result as writeup.md.") == []
    assert bare_markdown_tokens("See [guide](references/guide.md).") == []
    assert bare_markdown_tokens("See `SKILL.md` for the contract.") == []


def test_bare_markdown_reference_must_exist(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "example")
    skill_file = skill / "SKILL.md"

    assert missing_bare_markdown_references(
        skill_file,
        skill,
        "For commands, see quick-reference.md.",
        tmp_path,
    ) == ["quick-reference.md"]

    (skill / "references" / "quick-reference.md").write_text("# Quick reference\n", encoding="utf-8")
    assert missing_bare_markdown_references(
        skill_file,
        skill,
        "For commands, see quick-reference.md.",
        tmp_path,
    ) == []


def test_bare_markdown_reference_can_resolve_cross_skill(tmp_path: Path) -> None:
    source = make_skill(tmp_path, "source")
    target = make_skill(tmp_path, "target")
    target_file = target / "references" / "shared.md"
    target_file.write_text("# Shared\n", encoding="utf-8")

    assert missing_bare_markdown_references(
        source / "SKILL.md",
        source,
        "See shared.md in target.",
        tmp_path,
    ) == []
