#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _skill_utils import is_release_scope_path, repo_root

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".sh", ".txt", ".json", ".toml", ".csv"}
IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}


def candidate_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )


def findings(path: Path, text: str) -> list[tuple[int | None, str]]:
    problems: list[tuple[int | None, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            problems.append((line_number, "trailing whitespace"))
    if not text.endswith("\n"):
        problems.append((None, "missing final newline"))
    if text.endswith(("\n\n", "\r\n\r\n")):
        problems.append((None, "blank line at end of file"))
    return problems


def normalize(text: str) -> str:
    lines = [line.rstrip(" \t") for line in text.splitlines()]
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release-scoped text files for whitespace defects.")
    parser.add_argument("--fix", action="store_true", help="trim trailing whitespace and normalize final newline")
    args = parser.parse_args()

    root = repo_root()
    failures: list[tuple[Path, int | None, str]] = []
    changed = 0
    files = candidate_files(root)
    for path in files:
        text = path.read_bytes().decode("utf-8-sig")
        problems = findings(path, text)
        if args.fix and problems:
            fixed = normalize(text)
            if fixed != text:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                changed += 1
            continue
        failures.extend((path.relative_to(root), line, message) for line, message in problems)

    if args.fix:
        print(f"normalized whitespace in {changed} of {len(files)} text files")
        return 0
    for path, line, message in failures:
        location = f"{path}:{line}" if line is not None else str(path)
        print(f"FAIL {location}: {message}")
    print(f"checked {len(files)} text files; whitespace failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
