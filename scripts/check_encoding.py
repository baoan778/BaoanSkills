#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from _skill_utils import is_release_scope_path, repo_root

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".sh", ".txt", ".json", ".toml", ".csv"}
IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}


def main() -> int:
    root = repo_root()
    failures: list[tuple[Path, str]] = []
    checked = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if not is_release_scope_path(path):
            continue
        checked += 1
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            failures.append((path.relative_to(root), "UTF-8 BOM is not allowed"))
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append((path.relative_to(root), f"not valid UTF-8: {exc}"))
    for path, message in failures:
        print(f"INVALID {path}: {message}")
    print(f"checked {checked} text files; invalid: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
