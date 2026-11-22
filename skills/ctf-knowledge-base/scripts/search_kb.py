#!/usr/bin/env python3
"""Search a local CTF corpus while keeping raw third-party text out of releases."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SOURCE_REL = Path("CTF\u672c\u5730\u77e5\u8bc6\u5e93")
CATEGORY_BY_TOP = {
    "WP\u6c47\u603b": "writeup",
    "CTF\u5e38\u7528\u811a\u672c\u53ca\u5de5\u5177": "script",
    "\u5de5\u5177\u4f7f\u7528": "tool-guide",
    "CTF\u5de5\u5177\u96c6": "toolset",
}
DEFAULT_EXTENSIONS = (
    ".md",
    ".txt",
    ".html",
    ".htm",
    ".py",
    ".sh",
    ".sql",
    ".yaml",
    ".yml",
    ".json",
    ".nasl",
    ".desc",
)


@dataclass(frozen=True)
class SearchMatch:
    path: Path
    relative_path: str
    category: str
    line_number: int
    lines: tuple[str, ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def category_for(relative: Path) -> str:
    if len(relative.parts) == 1:
        return "topic-note"
    return CATEGORY_BY_TOP.get(relative.parts[0], "other")


def normalize_extensions(values: list[str] | None) -> set[str]:
    extensions = values or list(DEFAULT_EXTENSIONS)
    normalized: set[str] = set()
    for value in extensions:
        for part in value.split(","):
            suffix = part.strip().lower()
            if not suffix:
                continue
            normalized.add(suffix if suffix.startswith(".") else f".{suffix}")
    if not normalized:
        raise ValueError("at least one non-empty extension is required")
    return normalized


def candidate_files(source: Path, categories: set[str], extensions: set[str]) -> list[Path]:
    if not source.is_dir():
        raise ValueError(f"knowledge-base source does not exist or is not a directory: {source}")

    files: list[Path] = []
    for directory, dirnames, filenames in os.walk(source, followlinks=False):
        current = Path(directory)
        dirnames[:] = [
            name for name in sorted(dirnames) if not (current / name).is_symlink()
        ]
        for name in sorted(filenames):
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(source)
            if path.suffix.lower() not in extensions:
                continue
            if categories and category_for(relative) not in categories:
                continue
            files.append(path)
    return files


def search(
    source: Path,
    query: str,
    *,
    categories: set[str],
    extensions: set[str],
    context: int,
    max_results: int,
) -> list[SearchMatch]:
    needle = query.casefold()
    matches: list[SearchMatch] = []
    if not needle:
        raise ValueError("query must not be empty")

    for path in candidate_files(source, categories, extensions):
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines):
            if needle not in line.casefold():
                continue
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            relative = path.relative_to(source)
            matches.append(
                SearchMatch(
                    path=path,
                    relative_path=relative.as_posix(),
                    category=category_for(relative),
                    line_number=index + 1,
                    lines=tuple(lines[start:end]),
                )
            )
            if len(matches) >= max_results:
                return matches
    return matches


def render_matches(matches: list[SearchMatch], context: int) -> str:
    blocks: list[str] = []
    for match in matches:
        first_line = match.line_number - context
        block = [f"[{match.category}] {match.relative_path}:{match.line_number}"]
        for offset, line in enumerate(match.lines):
            line_number = first_line + offset
            marker = ">" if line_number == match.line_number else " "
            block.append(f"  {marker} {line_number:>6} | {line}")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search an authorized local CTF corpus with category and extension filters."
    )
    parser.add_argument("query", help="case-insensitive text to find")
    parser.add_argument(
        "--source",
        type=Path,
        help="local corpus root; defaults to CTF_KB_ROOT or the repository corpus directory",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=("topic-note", "writeup", "script", "tool-guide", "toolset", "other"),
        help="limit results to a category; repeat for multiple categories",
    )
    parser.add_argument(
        "--extension",
        action="append",
        help="limit text extensions (for example: .md or md,py); defaults to common text formats",
    )
    parser.add_argument("--context", type=int, default=2, help="context lines before and after each match")
    parser.add_argument("--max-results", type=int, default=20, help="maximum matching lines to print")
    args = parser.parse_args()

    if args.context < 0:
        parser.error("--context must be non-negative")
    if args.max_results < 1:
        parser.error("--max-results must be positive")

    default_source = Path(os.environ.get("CTF_KB_ROOT", repo_root() / DEFAULT_SOURCE_REL))
    source = args.source if args.source is not None else default_source
    source = source.resolve() if source.is_absolute() else (Path.cwd() / source).resolve()
    try:
        extensions = normalize_extensions(args.extension)
        categories = set(args.category or ())
        matches = search(
            source,
            args.query,
            categories=categories,
            extensions=extensions,
            context=args.context,
            max_results=args.max_results,
        )
    except (ValueError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    if not matches:
        print(f"no matches for {args.query!r} under {source}")
        return 0
    print(render_matches(matches, args.context))
    print(f"\nmatched {len(matches)} result(s); source: {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
