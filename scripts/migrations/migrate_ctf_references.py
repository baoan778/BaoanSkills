#!/usr/bin/env python3
"""Move CTF topic documents into each skill's references directory.

The migration keeps the topic filename stable, so links between documents in
the same skill remain valid after both files move. Every local Markdown link is
resolved against the pre-migration layout and rewritten relative to the new
source and target paths.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _skill_utils import is_release_scope_path, iter_skills, repo_root  # noqa: E402

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def collect_moves() -> tuple[dict[Path, Path], list[str]]:
    moves: dict[Path, Path] = {}
    errors: list[str] = []
    for skill_dir in iter_skills():
        if not skill_dir.name.startswith("ctf-"):
            continue
        references = skill_dir / "references"
        for source in sorted(skill_dir.glob("*.md")):
            if source.name == "SKILL.md":
                continue
            target = references / source.name
            if target.exists():
                errors.append(f"target already exists: {target.relative_to(repo_root())}")
                continue
            moves[source.resolve()] = target.resolve()
    return moves, errors


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
        and not any(part in ignored for part in path.parts)
        and is_release_scope_path(path)
    )


def rewrite_target(raw: str, old_source: Path, new_source: Path, moves: dict[Path, Path]) -> str:
    target = raw.strip()
    wrapped = target.startswith("<") and target.endswith(">")
    if wrapped:
        target = target[1:-1].strip()
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:", "tel:", "codex://")):
        return raw
    if any(char.isspace() for char in target):
        return raw
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return raw
    path_text = unquote(parsed.path)
    if not path_text or path_text.startswith(("/", "\\")):
        return raw
    if re.match(r"^[A-Za-z]:[\\/]", path_text):
        return raw

    old_target = (old_source.parent / path_text).resolve(strict=False)
    new_target = moves.get(old_target)
    if new_target is None and old_target.exists() and old_target.is_file():
        new_target = old_target
    if new_target is None:
        return raw

    relative = Path(os.path.relpath(new_target, new_source.parent)).as_posix()
    if not relative.startswith("."):
        relative = "./" + relative
    suffix = ""
    if parsed.query:
        suffix += "?" + parsed.query
    if parsed.fragment:
        suffix += "#" + parsed.fragment
    result = relative + suffix
    return f"<{result}>" if wrapped else result


def rewrite_line(line: str, old_source: Path, new_source: Path, moves: dict[Path, Path]) -> str:
    code_spans = [match.span() for match in INLINE_CODE_RE.finditer(line)]
    replacements: list[tuple[int, int, str]] = []
    for match in LINK_RE.finditer(line):
        if any(start <= match.start() < end for start, end in code_spans):
            continue
        start, end = match.span(1)
        rewritten = rewrite_target(match.group(1), old_source, new_source, moves)
        if rewritten != match.group(1):
            replacements.append((start, end, rewritten))
    for start, end, value in reversed(replacements):
        line = line[:start] + value + line[end:]
    return line


def rewrite_document(
    path: Path, moves: dict[Path, Path], reverse_moves: dict[Path, Path]
) -> tuple[str, bool]:
    new_source = path.resolve()
    old_source = reverse_moves.get(new_source, new_source)
    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    result: list[str] = []
    marker: str | None = None
    for line in lines:
        fence = FENCE_RE.match(line)
        if fence:
            current = fence.group(1)
            if marker is None:
                marker = current[0]
            elif marker == current[0]:
                marker = None
            result.append(line)
            continue
        if marker is not None:
            result.append(line)
            continue
        result.append(rewrite_line(line, old_source, new_source, moves))
    rewritten = "".join(result)
    original = path.read_text(encoding="utf-8-sig")
    return rewritten, rewritten != original


def main() -> int:
    parser = argparse.ArgumentParser(description="Move CTF topic Markdown files under references/ and rewrite links.")
    parser.add_argument("--write", action="store_true", help="apply the migration")
    parser.add_argument("--dry-run", action="store_true", help="report planned moves and rewrites")
    args = parser.parse_args()
    if not args.write and not args.dry_run:
        parser.error("choose --write or --dry-run")

    moves, errors = collect_moves()
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    root = repo_root()
    print(f"planned moves: {len(moves)}")
    for source, target in moves.items():
        print(f"MOVE {source.relative_to(root)} -> {target.relative_to(root)}")

    if args.write:
        for source, target in moves.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            source.replace(target)

    changed = 0
    reverse_moves = {new: old for old, new in moves.items()}
    for path in markdown_files(root):
        rewritten, changed_here = rewrite_document(path, moves, reverse_moves)
        if changed_here:
            changed += 1
            print(f"REWRITE {path.relative_to(root)}")
            if args.write:
                path.write_text(rewritten, encoding="utf-8", newline="\n")

    if args.write:
        print(f"moved {len(moves)} CTF reference files; rewrote links in {changed} Markdown files")
    else:
        print(f"dry run: {len(moves)} moves and {changed} link rewrites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
