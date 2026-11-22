#!/usr/bin/env python3
"""Build a deterministic, path-only manifest for the local CTF corpus.

The manifest intentionally contains no document bodies and no absolute paths.
It lets the public knowledge-base skill discover corpus structure without
redistributing third-party material.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _skill_utils import repo_root

DEFAULT_SOURCE_REL = Path("CTF\u672c\u5730\u77e5\u8bc6\u5e93")
DEFAULT_OUTPUT_REL = Path("skills") / "ctf-knowledge-base" / "references" / "archive" / "file-manifest.csv"
FIELDNAMES = ("relative_path", "category", "extension", "bytes", "sha256")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CATEGORY_BY_TOP = {
    "WP\u6c47\u603b": "writeup",
    "CTF\u5e38\u7528\u811a\u672c\u53ca\u5de5\u5177": "script",
    "\u5de5\u5177\u4f7f\u7528": "tool-guide",
    "CTF\u5de5\u5177\u96c6": "toolset",
}


class ManifestError(RuntimeError):
    """A user-actionable manifest generation failure."""


@dataclass(frozen=True)
class ManifestRecord:
    relative_path: str
    category: str
    extension: str
    bytes: int
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def category_for(relative: Path) -> str:
    parts = relative.parts
    if len(parts) == 1:
        return "topic-note"
    category = CATEGORY_BY_TOP.get(parts[0])
    if category is None:
        raise ManifestError(f"unrecognized top-level corpus directory: {parts[0]}")
    return category


def discover_files(source: Path) -> list[Path]:
    if not source.is_dir():
        raise ManifestError(f"knowledge-base source does not exist or is not a directory: {source}")

    files: list[Path] = []
    for directory, dirnames, filenames in os.walk(source, followlinks=False):
        current = Path(directory)
        for name in sorted(dirnames):
            candidate = current / name
            if candidate.is_symlink():
                raise ManifestError(f"symlinked directories are not allowed: {candidate}")
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            candidate = current / name
            if candidate.is_symlink():
                raise ManifestError(f"symlinked files are not allowed: {candidate}")
            if candidate.is_file():
                files.append(candidate)
    return sorted(files, key=lambda path: path.relative_to(source).as_posix())


def build_records(source: Path) -> list[ManifestRecord]:
    records: list[ManifestRecord] = []
    for path in discover_files(source):
        relative = path.relative_to(source)
        records.append(
            ManifestRecord(
                relative_path=relative.as_posix(),
                category=category_for(relative),
                extension=path.suffix.lower(),
                bytes=path.stat().st_size,
                sha256=sha256_file(path),
            )
        )
    return records


def render_manifest(records: list[ManifestRecord]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "relative_path": record.relative_path,
                "category": record.category,
                "extension": record.extension,
                "bytes": record.bytes,
                "sha256": record.sha256,
            }
        )
    return buffer.getvalue()


def validate_rendered_manifest(rendered: str) -> list[ManifestRecord]:
    """Validate a committed manifest when the local corpus is unavailable."""
    try:
        reader = csv.DictReader(io.StringIO(rendered, newline=""), strict=True)
        if reader.fieldnames != list(FIELDNAMES):
            raise ManifestError(
                "manifest header must be: " + ",".join(FIELDNAMES)
            )
        rows = list(reader)
    except csv.Error as exc:
        raise ManifestError(f"manifest is not valid CSV: {exc}") from exc

    if not rows:
        raise ManifestError("manifest must contain at least one record")

    records: list[ManifestRecord] = []
    seen: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        if None in row or any(row.get(field) is None for field in FIELDNAMES):
            raise ManifestError(f"manifest line {line_number}: unexpected column count")

        relative_path = str(row["relative_path"])
        if (
            not relative_path
            or relative_path != relative_path.strip()
            or "\\" in relative_path
            or relative_path.startswith("/")
            or "//" in relative_path
            or re.match(r"^[A-Za-z]:", relative_path)
            or any(part in {"", ".", ".."} for part in Path(relative_path).parts)
        ):
            raise ManifestError(
                f"manifest line {line_number}: unsafe or non-portable relative path: {relative_path!r}"
            )
        if relative_path in seen:
            raise ManifestError(f"manifest line {line_number}: duplicate path: {relative_path}")
        seen.add(relative_path)

        path = Path(relative_path)
        try:
            expected_category = category_for(path)
        except ManifestError as exc:
            raise ManifestError(f"manifest line {line_number}: {exc}") from exc
        category = str(row["category"])
        if category != expected_category:
            raise ManifestError(
                f"manifest line {line_number}: category {category!r} does not match path {relative_path!r}"
            )

        extension = str(row["extension"])
        if extension != path.suffix.lower():
            raise ManifestError(
                f"manifest line {line_number}: extension {extension!r} does not match path {relative_path!r}"
            )

        try:
            byte_count = int(str(row["bytes"]))
        except ValueError as exc:
            raise ManifestError(f"manifest line {line_number}: bytes must be an integer") from exc
        if byte_count < 0:
            raise ManifestError(f"manifest line {line_number}: bytes must not be negative")

        sha256 = str(row["sha256"])
        if not SHA256_RE.fullmatch(sha256):
            raise ManifestError(
                f"manifest line {line_number}: sha256 must be 64 lowercase hexadecimal characters"
            )

        records.append(
            ManifestRecord(
                relative_path=relative_path,
                category=category,
                extension=extension,
                bytes=byte_count,
                sha256=sha256,
            )
        )

    paths = [record.relative_path for record in records]
    if paths != sorted(paths):
        raise ManifestError("manifest records are not sorted by relative_path")
    if rendered != render_manifest(records):
        raise ManifestError("manifest is not in canonical CSV form")
    return records


def resolve_cli_path(value: Path | None, default: Path) -> Path:
    candidate = value if value is not None else default
    if candidate.is_absolute():
        return candidate.resolve()
    return (Path.cwd() / candidate).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify the local CTF corpus file manifest without publishing document contents."
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="local knowledge-base root; defaults to CTF_KB_ROOT or the repository corpus directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="manifest CSV path; defaults to the ctf-knowledge-base archive location",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the manifest")
    mode.add_argument("--check", action="store_true", help="verify the manifest is current")
    args = parser.parse_args()

    default_source = Path(os.environ.get("CTF_KB_ROOT", repo_root() / DEFAULT_SOURCE_REL))
    source = resolve_cli_path(args.source, default_source)
    output = resolve_cli_path(args.output, repo_root() / DEFAULT_OUTPUT_REL)

    try:
        static_fallback = (
            args.check
            and args.source is None
            and "CTF_KB_ROOT" not in os.environ
            and not source.is_dir()
        )
        if static_fallback:
            if not output.is_file():
                raise ManifestError(f"manifest does not exist: {output}")
            records = validate_rendered_manifest(output.read_text(encoding="utf-8"))
            print(
                f"manifest structure is valid: {len(records)} records "
                "(corpus source unavailable; static check only)"
            )
            return 0

        records = build_records(source)
        rendered = render_manifest(records)
        if args.write:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"wrote {len(records)} records to {output}")
            return 0
        if not output.is_file():
            raise ManifestError(f"manifest does not exist: {output}")
        current = output.read_text(encoding="utf-8")
        if current != rendered:
            raise ManifestError("manifest is stale; rerun with --write")
        print(f"manifest is current: {len(records)} records")
        return 0
    except (ManifestError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
