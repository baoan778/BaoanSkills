#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _skill_utils import repo_root

USE_RE = re.compile(r"^(?P<indent>\s*)(?:-\s*)?uses:\s*(?P<target>\S+)(?P<suffix>.*)$", re.MULTILINE)
PERMISSIONS_RE = re.compile(r"^permissions:\s*(?:#.*)?$", re.MULTILINE)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_COMMENT_RE = re.compile(r"#\s*v?[0-9A-Za-z][0-9A-Za-z._-]*")
WORKFLOW_SUFFIXES = {".yml", ".yaml"}


def workflow_files(root: Path) -> list[Path]:
    directory = root / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.iterdir() if path.is_file() and path.suffix in WORKFLOW_SUFFIXES)


def check_workflow(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    if not PERMISSIONS_RE.search(text):
        errors.append("top-level permissions block is required")

    for match in USE_RE.finditer(text):
        target = match.group("target")
        suffix = match.group("suffix")
        line_number = text.count("\n", 0, match.start()) + 1
        if target.startswith("./"):
            continue
        if target.startswith("docker://"):
            if "@sha256:" not in target:
                errors.append(f"line {line_number}: container action must use a sha256 digest")
            continue
        if "@" not in target:
            errors.append(f"line {line_number}: action reference is missing an immutable revision")
            continue
        _, revision = target.rsplit("@", 1)
        if not SHA_RE.fullmatch(revision):
            errors.append(f"line {line_number}: action must be pinned to a full 40-character commit SHA")
        if not VERSION_COMMENT_RE.search(suffix):
            errors.append(f"line {line_number}: pinned action should include a '# vX' version comment")
    return errors


def main() -> int:
    root = repo_root().resolve()
    files = workflow_files(root)
    failures: list[tuple[Path, str]] = []
    if not files:
        failures.append((root / ".github" / "workflows", "no workflow files found"))
    for path in files:
        failures.extend((path, error) for error in check_workflow(path))
    for path, failure in failures:
        print(f"FAIL {path.relative_to(root)}: {failure}")
    print(f"checked {len(files)} GitHub workflow files; failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
