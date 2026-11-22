#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _skill_utils import is_release_scope_path, repo_root

IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}
FENCE_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*(`{3,}|~{3,})(.*)$")
H1_RE = re.compile(r"^[ \t]{0,3}#(?!#)[ \t]+(\S.*?)[ \t]*$")
HEADING_RE = re.compile(r"^[ \t]{0,3}(#{1,6})(?:[ \t]+|$)(.*)$")


@dataclass(frozen=True)
class Problem:
    path: Path
    line: int | None
    message: str


def candidate_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )


def frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index + 1
    return 0


def check_file(root: Path, path: Path) -> list[Problem]:
    problems: list[Problem] = []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = frontmatter_end(lines) if path.name == "SKILL.md" else 0

    in_fence = False
    fence_char = ""
    fence_length = 0
    fence_start = 0
    h1_lines: list[int] = []
    first_heading: tuple[int, int] | None = None

    for line_number, line in enumerate(lines, start=1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            trailing = fence.group(2)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_length = len(marker)
                fence_start = line_number
            elif marker[0] == fence_char and len(marker) >= fence_length and not trailing.strip():
                in_fence = False
            continue

        if in_fence or line_number <= start:
            continue

        heading = HEADING_RE.match(line)
        if not heading:
            continue
        level = len(heading.group(1))
        text = heading.group(2).strip()
        if not text:
            problems.append(Problem(path, line_number, "heading text is empty"))
        if first_heading is None:
            first_heading = (line_number, level)
        if level == 1:
            h1_lines.append(line_number)

    if in_fence:
        problems.append(Problem(path, fence_start, "unclosed fenced code block"))

    if path.name == "SKILL.md":
        if not h1_lines:
            problems.append(Problem(path, None, "SKILL.md must contain exactly one H1 heading"))
        elif len(h1_lines) > 1:
            locations = ", ".join(str(line) for line in h1_lines)
            problems.append(Problem(path, h1_lines[1], f"SKILL.md contains multiple H1 headings (lines {locations})"))
        if first_heading and first_heading[1] != 1:
            problems.append(Problem(path, first_heading[0], "first heading in SKILL.md must be H1"))

    relative = path.relative_to(root)
    return [Problem(relative, item.line, item.message) for item in problems]


def main() -> int:
    root = repo_root().resolve()
    files = candidate_files(root)
    problems: list[Problem] = []
    for path in files:
        problems.extend(check_file(root, path))

    for problem in problems:
        location = f"{problem.path}:{problem.line}" if problem.line else str(problem.path)
        print(f"FAIL {location}: {problem.message}")
    print(f"checked {len(files)} Markdown files; structure failures: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
