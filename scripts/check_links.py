#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from _skill_utils import is_release_scope_path, repo_root

FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "codex://", "#")


def mask_inline_code(text: str) -> str:
    """Replace inline code with spaces while preserving line numbers.

    Shell snippets such as ``row['x']('return')`` otherwise look like Markdown
    links and create false positives in the link checker.
    """

    def replace(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group(0))

    return INLINE_CODE_RE.sub(replace, text)


def strip_fenced_code(text: str) -> str:
    lines: list[str] = []
    marker: str | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            current = match.group(1)
            if marker is None:
                marker = current[0]
                lines.append("")
                continue
            if current[0] == marker:
                marker = None
                lines.append("")
                continue
        lines.append("" if marker is not None else line)
    return "\n".join(lines)


def clean_target(raw: str) -> str | None:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target or target.startswith(SKIP_PREFIXES):
        return None
    if " " in target:
        target = target.split(" ", 1)[0]
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path or path.startswith(("/", "\\")):
        return None
    if re.match(r"^[A-Za-z]:[\\/]", path):
        return None
    if "{" in path or "}" in path:
        return None
    return path


def local_markdown_files(root: Path) -> list[Path]:
    ignored = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}
    results: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in ignored for part in path.parts):
            continue
        if not is_release_scope_path(path):
            continue
        results.append(path)
    return sorted(results)


def main() -> int:
    root = repo_root()
    broken: list[tuple[Path, int, str]] = []
    checked = 0
    for md_file in local_markdown_files(root):
        text = strip_fenced_code(md_file.read_text(encoding="utf-8-sig"))
        text = mask_inline_code(text)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                target = clean_target(match.group(1))
                if target is None:
                    continue
                checked += 1
                resolved = (md_file.parent / target).resolve()
                if not resolved.exists():
                    broken.append((md_file.relative_to(root), line_number, target))
    for file_path, line_number, target in broken:
        print(f"BROKEN {file_path}:{line_number} -> {target}")
    print(f"checked {checked} local links; broken: {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
