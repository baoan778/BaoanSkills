#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from _skill_utils import iter_skills
from skill_quality import QUALITY, SkillQuality

INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")


def expected_interface(quality: SkillQuality) -> dict[str, str]:
    return {
        "display_name": quality.display_name,
        "short_description": quality.short_description,
        "default_prompt": quality.default_prompt,
    }


def validate_agent_data(data: object, quality: SkillQuality) -> list[str]:
    """Validate only the fields owned by the quality catalog plus structure."""
    if not isinstance(data, dict):
        return ["root must be a mapping"]
    errors: list[str] = []
    interface = data.get("interface")
    if not isinstance(interface, dict):
        errors.append("interface must be a mapping")
        interface = {}
    expected = expected_interface(quality)
    for key, value in expected.items():
        actual = interface.get(key)
        if not isinstance(actual, str) or not actual.strip():
            errors.append(f"interface.{key} is required")
        elif actual != value:
            errors.append(f"interface.{key} does not match the reviewed quality catalog")
    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        errors.append("interface.short_description must be 25-64 characters")
    if "allowed-tools" in data:
        errors.append("allowed-tools belongs in SKILL.md, not agents/openai.yaml")
    policy = data.get("policy")
    if policy is not None:
        if not isinstance(policy, dict):
            errors.append("policy must be a mapping when present")
        elif "allow_implicit_invocation" in policy and not isinstance(
            policy["allow_implicit_invocation"], bool
        ):
            errors.append("policy.allow_implicit_invocation must be a boolean")
    if "user-invocable" in data and not isinstance(data["user-invocable"], bool):
        errors.append("user-invocable must be a boolean when present")
    dependencies = data.get("dependencies")
    if dependencies is not None and not isinstance(dependencies, (dict, list)):
        errors.append("dependencies must be a mapping or list when present")
    return errors


def merge_agent_data(data: object, quality: SkillQuality) -> tuple[dict, list[str]]:
    """Update catalog-owned interface fields while preserving extension fields."""
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return {}, ["root must be a mapping"]
    errors: list[str] = []
    existing_interface = data.get("interface")
    if existing_interface is not None and not isinstance(existing_interface, dict):
        return {}, ["interface must be a mapping"]
    interface = dict(existing_interface or {})
    interface.update(expected_interface(quality))

    ordered: dict = {"interface": interface}
    for key, value in data.items():
        if key != "interface":
            ordered[key] = value
    if "policy" not in ordered:
        ordered["policy"] = {"allow_implicit_invocation": True}
    errors.extend(validate_agent_data(ordered, quality))
    return ordered, errors


def render_agent(data: dict) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def load_agent(path: Path) -> tuple[object | None, str | None]:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8-sig")), None
    except yaml.YAMLError as exc:
        return None, f"invalid YAML: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize skill UI metadata with the quality catalog.")
    parser.add_argument("--write", action="store_true", help="create or update agents/openai.yaml")
    parser.add_argument("--check", action="store_true", help="verify agents/openai.yaml matches the catalog")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --write or --check")

    skills = iter_skills()
    failures: list[str] = []
    updated = 0
    created = 0

    for skill_dir in skills:
        quality = QUALITY.get(skill_dir.name)
        if quality is None:
            failures.append(f"{skill_dir.name}: no reviewed quality catalog entry")
            continue
        target = skill_dir / "agents" / "openai.yaml"
        if not target.is_file():
            if args.check:
                failures.append(f"{skill_dir.name}: agents/openai.yaml is missing")
                continue
            data, error = None, None
        else:
            data, error = load_agent(target)
            if error:
                failures.append(f"{skill_dir.name}: {error}")
                continue

        if args.write:
            merged, errors = merge_agent_data(data, quality)
            failures.extend(f"{skill_dir.name}: {item}" for item in errors)
            if errors:
                continue
            rendered = render_agent(merged)
            current = target.read_text(encoding="utf-8-sig") if target.is_file() else None
            if current != rendered:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(rendered, encoding="utf-8", newline="\n")
                if current is None:
                    created += 1
                else:
                    updated += 1
        else:
            errors = validate_agent_data(data, quality)
            failures.extend(f"{skill_dir.name}: {item}" for item in errors)

    for failure in failures:
        print(f"FAIL {failure}")
    if args.write:
        print(f"agent metadata synchronized; created: {created}; updated: {updated}; failures: {len(failures)}")
    else:
        print(f"checked {len(skills)} agent metadata files; failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
