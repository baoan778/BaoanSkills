#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _skill_utils import iter_skills
from check_links import LINK_RE, clean_target, mask_inline_code, strip_fenced_code

MAX_SKILL_LINES = 700
ADVISORY_SKILL_LINES = 500
MAX_SKILL_WORDS = 6000


def check_skill(skill: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    advisories: list[str] = []
    skill_file = skill / "SKILL.md"
    if not skill_file.is_file():
        return [f"missing SKILL.md in {skill.name}"], advisories

    text = skill_file.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    word_count = len(text.split())
    if len(lines) > MAX_SKILL_LINES:
        errors.append(f"SKILL.md has {len(lines)} lines; move conditional detail into references (limit {MAX_SKILL_LINES})")
    elif len(lines) > ADVISORY_SKILL_LINES:
        advisories.append(f"SKILL.md has {len(lines)} lines; consider moving conditional detail into references")
    if word_count > MAX_SKILL_WORDS:
        errors.append(f"SKILL.md has {word_count} words; move conditional detail into references (limit {MAX_SKILL_WORDS})")

    root_docs = sorted(path.name for path in skill.glob("*.md") if path.name != "SKILL.md")
    if root_docs:
        errors.append("topic documents must live under references/: " + ", ".join(root_docs))

    masked = mask_inline_code(strip_fenced_code(text))
    linked_paths: set[str] = set()
    for match in LINK_RE.finditer(masked):
        target = clean_target(match.group(1))
        if target is None:
            continue
        resolved = (skill / target).resolve()
        try:
            linked_paths.add(resolved.relative_to(skill.resolve()).as_posix())
        except ValueError:
            continue

    references = sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []
    missing_references = []
    for reference in references:
        relative = reference.relative_to(skill).as_posix()
        if relative not in linked_paths:
            missing_references.append(relative)
    if missing_references:
        errors.append("references are not directly linked from SKILL.md: " + ", ".join(missing_references))

    scripts = (
        sorted(path for path in (skill / "scripts").rglob("*") if path.is_file())
        if (skill / "scripts").is_dir()
        else []
    )
    unreferenced_scripts = [
        path.relative_to(skill).as_posix()
        for path in scripts
        if path.name not in text and path.relative_to(skill).as_posix() not in text
    ]
    if unreferenced_scripts:
        errors.append("scripts are not referenced by SKILL.md: " + ", ".join(unreferenced_scripts))
    return errors, advisories


def main() -> int:
    skills = iter_skills()
    failures: list[tuple[str, str]] = []
    advisories: list[tuple[str, str]] = []
    for skill in skills:
        errors, notices = check_skill(skill)
        failures.extend((skill.name, error) for error in errors)
        advisories.extend((skill.name, notice) for notice in notices)
    for name, failure in failures:
        print(f"FAIL {name}: {failure}")
    for name, notice in advisories:
        print(f"ADVISORY {name}: {notice}")
    print(
        f"checked {len(skills)} skills; failures: {len(failures)}; "
        f"advisories: {len(advisories)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
