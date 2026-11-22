#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from _skill_utils import (
    ALLOWED_FRONTMATTER_KEYS,
    NAME_RE,
    iter_skills,
    load_skill,
    metadata_of,
    normalized_license,
    repo_root,
)


def validate_one(skill_dir: Path, *, strict: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        doc = load_skill(skill_dir)
    except Exception as exc:  # noqa: BLE001 - report all malformed skills
        return [str(exc)]

    fm = doc.frontmatter
    unexpected = set(fm) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(f"unexpected frontmatter keys: {', '.join(sorted(unexpected))}")

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name must be a non-empty string")
    else:
        name = name.strip()
        if not NAME_RE.fullmatch(name):
            errors.append("name must use lowercase letters, digits, and hyphens only")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append("name cannot start/end with a hyphen or contain consecutive hyphens")
        if len(name) > 64:
            errors.append("name exceeds 64 characters")
        if name != skill_dir.name:
            errors.append(f"name '{name}' does not match directory '{skill_dir.name}'")

    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a non-empty string")
    else:
        description = description.strip()
        if len(description) > 1024:
            errors.append("description exceeds 1024 characters")
        if "<" in description or ">" in description:
            errors.append("description cannot contain angle brackets")
        if description.startswith("[TODO:"):
            errors.append("description contains an unfinished TODO placeholder")

    license_value = normalized_license(fm)
    if not isinstance(fm.get("license", ""), str):
        errors.append("license must be a string")
    if strict and license_value == "NOASSERTION":
        errors.append("license is unverified; NOASSERTION is allowed only in inventory mode")

    metadata = metadata_of(fm)
    if not metadata:
        errors.append("metadata must be a non-empty mapping")
    for key in ("author", "source"):
        value = metadata.get(key)
        if value is None or not str(value).strip():
            errors.append(f"metadata.{key} is required")
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append("metadata.tags must be a list")

    if not doc.body.strip():
        errors.append("SKILL.md body is empty")
    if "[TODO:" in doc.body:
        errors.append("SKILL.md body contains an unfinished TODO placeholder")

    if strict:
        for key in ("license_status", "provenance_status"):
            if str(metadata.get(key, "")).strip() != "verified":
                errors.append(f"metadata.{key} must be verified for a public release")
        for key in ("license_evidence", "retrieved_at", "modifications"):
            if not str(metadata.get(key, "")).strip():
                errors.append(f"metadata.{key} is required for a public release")
        evidence = str(metadata.get("license_evidence", "")).strip()
        if evidence:
            evidence_path = Path(evidence)
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                errors.append("metadata.license_evidence must be a repository-relative path")
            elif not (repo_root() / evidence_path).is_file():
                errors.append(f"license evidence does not exist: {evidence}")
        if "authorized use only" not in doc.raw.casefold():
            errors.append("SKILL.md is missing an explicit 'Authorized use only' boundary")

    agent_file = skill_dir / "agents" / "openai.yaml"
    if not agent_file.is_file():
        errors.append("agents/openai.yaml is missing")
    else:
        try:
            agent = yaml.safe_load(agent_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"agents/openai.yaml is invalid YAML: {exc}")
        else:
            interface = agent.get("interface") if isinstance(agent, dict) else None
            if not isinstance(interface, dict):
                errors.append("agents/openai.yaml interface must be a mapping")
            else:
                for key in ("display_name", "short_description", "default_prompt"):
                    if not isinstance(interface.get(key), str) or not interface[key].strip():
                        errors.append(f"agents/openai.yaml interface.{key} is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the structural contract of skills in publication scope. "
        "The default inventory mode permits unverified licenses; strict mode does not."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="reject unverified licenses and incomplete publication metadata",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="validate every local staging skill instead of the public allowlist",
    )
    args = parser.parse_args()

    failures = 0
    skills = iter_skills(include_all=args.all)
    for skill_dir in skills:
        try:
            errors = validate_one(skill_dir, strict=args.strict)
        except Exception as exc:  # noqa: BLE001
            errors = [f"validation crashed: {exc}"]
        if errors:
            failures += 1
            print(f"FAIL {skill_dir.name}")
            for error in errors:
                print(f"  - {error}")

    mode = "strict" if args.strict else "inventory"
    scope = "all staging skills" if args.all else "public allowlist"
    print(f"validated {len(skills)} {scope} skills in {mode} mode; failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
