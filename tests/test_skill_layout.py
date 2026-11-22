from __future__ import annotations

from pathlib import Path

from _skill_utils import iter_skills
from check_skill_layout import check_skill


def test_public_skill_layout_and_reachability() -> None:
    errors = [error for skill in iter_skills() for error in check_skill(skill)[0]]
    assert errors == []


def test_unlinked_reference_is_rejected(tmp_path: Path) -> None:
    skill = tmp_path / "example"
    references = skill / "references"
    references.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example.\n---\n# Example\n",
        encoding="utf-8",
    )
    (references / "unused.md").write_text("# Unused\n", encoding="utf-8")
    errors, _ = check_skill(skill)
    assert any("not directly linked" in error for error in errors)


def test_public_skill_entrypoints_stay_below_advisory_limit() -> None:
    oversized = {
        skill.name: len((skill / "SKILL.md").read_text(encoding="utf-8-sig").splitlines())
        for skill in iter_skills()
        if len((skill / "SKILL.md").read_text(encoding="utf-8-sig").splitlines()) > 500
    }
    assert oversized == {}
