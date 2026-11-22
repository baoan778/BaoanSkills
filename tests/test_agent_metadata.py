from __future__ import annotations

from generate_agent_metadata import merge_agent_data, validate_agent_data
from skill_quality import QUALITY


def test_quality_metadata_is_valid_and_specific() -> None:
    quality = QUALITY["ctf-web"]
    payload = {
        "interface": {
            "display_name": quality.display_name,
            "short_description": quality.short_description,
            "default_prompt": quality.default_prompt,
        },
        "policy": {"allow_implicit_invocation": True},
    }
    assert validate_agent_data(payload, quality) == []


def test_generic_prompt_and_display_case_are_rejected() -> None:
    quality = QUALITY["ctf-web"]
    payload = {
        "interface": {
            "display_name": "Ctf Web",
            "short_description": quality.short_description,
            "default_prompt": "Use $ctf-web to complete the current authorized task.",
        }
    }
    errors = validate_agent_data(payload, quality)
    assert any("display_name" in error for error in errors)
    assert any("default_prompt" in error for error in errors)


def test_merge_preserves_extension_fields() -> None:
    quality = QUALITY["burpsuite-project-parser"]
    payload = {
        "interface": {"display_name": "Old", "short_description": "Old description.", "default_prompt": "Old"},
        "policy": {"allow_implicit_invocation": False, "other": "kept"},
        "dependencies": ["semgrep"],
        "user-invocable": True,
    }
    merged, errors = merge_agent_data(payload, quality)
    assert errors == []
    assert merged["policy"] == payload["policy"]
    assert merged["dependencies"] == ["semgrep"]
    assert merged["user-invocable"] is True
    assert merged["interface"]["display_name"] == "Burp Suite Project Parser"
