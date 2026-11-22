#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from _skill_utils import iter_skills, load_skill, metadata_of, publication_names
from skill_quality import QUALITY, SkillQuality

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.DOTALL)
QUALITY_MODIFICATION = (
    "Public quality normalization: concise discovery description, reviewed risk and tags, "
    "explicit tool scope, and skill-specific UI presentation."
)
RISK_VALUES = {"safe", "offensive", "high", "reference"}
ALLOWED_TOOL_VALUES = {
    "Bash",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
    "Skill",
}


def catalog_errors() -> list[str]:
    errors: list[str] = []
    names = publication_names() or []
    missing = sorted(set(names) - set(QUALITY))
    extra = sorted(set(QUALITY) - set(names))
    if missing:
        errors.append("quality catalog is missing public skills: " + ", ".join(missing))
    if extra:
        errors.append("quality catalog contains non-public skills: " + ", ".join(extra))
    for name, quality in QUALITY.items():
        if not 25 <= len(quality.short_description) <= 64:
            errors.append(f"{name}: short_description must be 25-64 characters")
        if not 80 <= len(quality.description) <= 240:
            errors.append(f"{name}: description must be 80-240 characters")
        if quality.risk not in RISK_VALUES:
            errors.append(f"{name}: unsupported risk value {quality.risk!r}")
        if not quality.tags or len(set(quality.tags)) != len(quality.tags):
            errors.append(f"{name}: tags must be a non-empty unique list")
        if not quality.allowed_tools:
            errors.append(f"{name}: allowed_tools must not be empty")
        unknown_tools = sorted(set(quality.allowed_tools) - ALLOWED_TOOL_VALUES)
        if unknown_tools:
            errors.append(f"{name}: unsupported allowed tools: {', '.join(unknown_tools)}")
        if f"${name}" not in quality.default_prompt:
            errors.append(f"{name}: default_prompt must explicitly name ${name}")
    return errors


def build_frontmatter(frontmatter: dict, quality: SkillQuality) -> dict:
    metadata = metadata_of(frontmatter).copy()
    prior = str(metadata.get("modifications", "")).strip()
    if QUALITY_MODIFICATION not in prior:
        prior = f"{prior} {QUALITY_MODIFICATION}".strip()
    metadata["risk"] = quality.risk
    metadata["tags"] = list(quality.tags)
    metadata["modifications"] = prior

    # Keep the canonical discovery keys first while preserving any future
    # extension keys that are not controlled by this catalog.
    ordered: dict = {}
    for key in ("name", "description", "license", "allowed-tools", "metadata"):
        if key == "description":
            ordered[key] = quality.description
        elif key == "allowed-tools":
            ordered[key] = list(quality.allowed_tools)
        elif key == "metadata":
            ordered[key] = metadata
        elif key in frontmatter:
            ordered[key] = frontmatter[key]
    for key, value in frontmatter.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def render_document(raw: str, frontmatter: dict) -> str:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError("missing or malformed YAML frontmatter delimiters")
    rendered = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{rendered}---\n{raw[match.end():]}"


def check_skill(skill_dir: Path, quality: SkillQuality) -> tuple[list[str], str | None]:
    errors: list[str] = []
    try:
        doc = load_skill(skill_dir)
    except Exception as exc:  # noqa: BLE001
        return [str(exc)], None
    fm = doc.frontmatter
    metadata = metadata_of(fm)
    expected = build_frontmatter(fm, quality)
    expected_metadata = expected["metadata"]
    if fm.get("description") != quality.description:
        errors.append("description does not match the reviewed quality catalog")
    if fm.get("allowed-tools") != list(quality.allowed_tools):
        errors.append("allowed-tools does not match the reviewed quality catalog")
    if metadata.get("risk") != quality.risk:
        errors.append("metadata.risk does not match the reviewed quality catalog")
    if metadata.get("tags") != list(quality.tags):
        errors.append("metadata.tags does not match the reviewed quality catalog")
    if metadata.get("modifications") != expected_metadata.get("modifications"):
        errors.append("metadata.modifications is missing the quality-normalization record")
    return errors, render_document(doc.raw, expected)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply reviewed discovery and quality metadata to public skills.")
    parser.add_argument("--write", action="store_true", help="update skill frontmatter in place")
    parser.add_argument("--check", action="store_true", help="verify frontmatter matches the quality catalog")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --write or --check")

    failures = catalog_errors()
    skills = iter_skills()
    changed = 0
    for skill_dir in skills:
        quality = QUALITY.get(skill_dir.name)
        if quality is None:
            failures.append(f"{skill_dir.name}: no reviewed quality catalog entry")
            continue
        try:
            if args.write:
                doc = load_skill(skill_dir)
                expected = build_frontmatter(doc.frontmatter, quality)
                rendered = render_document(doc.raw, expected)
                errors = []
            else:
                errors, rendered = check_skill(skill_dir, quality)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{skill_dir.name}: {exc}")
            continue
        failures.extend(f"{skill_dir.name}: {error}" for error in errors)
        if rendered is None:
            continue
        current = (skill_dir / "SKILL.md").read_text(encoding="utf-8-sig")
        if rendered != current:
            changed += 1
            if args.write:
                (skill_dir / "SKILL.md").write_text(rendered, encoding="utf-8", newline="\n")

    for failure in failures:
        print(f"FAIL {failure}")
    if args.write:
        print(f"updated {changed} public skill frontmatter files; failures: {len(failures)}")
    else:
        print(f"checked {len(skills)} public skills; failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
