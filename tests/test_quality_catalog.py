from __future__ import annotations

from _skill_utils import publication_names
from apply_skill_quality import catalog_errors
from skill_quality import QUALITY


def test_catalog_covers_public_allowlist() -> None:
    names = publication_names()
    assert names is not None
    assert len(names) == 39
    assert set(names) == set(QUALITY)
    assert catalog_errors() == []


def test_ui_metadata_is_unique_and_specific() -> None:
    display_names = [quality.display_name for quality in QUALITY.values()]
    assert len(display_names) == len(set(display_names))
    for name, quality in QUALITY.items():
        assert 25 <= len(quality.short_description) <= 64
        assert f"${name}" in quality.default_prompt
        assert "complete the current authorized task" not in quality.default_prompt
        assert not quality.display_name.startswith("Ctf ")


def test_high_risk_skills_include_authorization_language() -> None:
    for name, quality in QUALITY.items():
        if quality.risk in {"offensive", "high"}:
            text = " ".join((quality.description, quality.default_prompt)).casefold()
            assert any(word in text for word in ("authorized", "ctf")), name
