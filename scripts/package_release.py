#!/usr/bin/env python3
"""Build a deterministic zip release and SHA-256 manifest from a public snapshot."""

from __future__ import annotations

import argparse
import hashlib
import io
import stat
import sys
import zipfile
from pathlib import Path

ARCHIVE_STEM = "baoanskills-release"
CHECKSUM_FILE = "SHA256SUMS"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


class PackagingError(RuntimeError):
    """A user-actionable release packaging failure."""


def archive_mode(path: Path, *, is_directory: bool) -> int:
    if is_directory:
        return 0o755
    return 0o755 if path.stat().st_mode & 0o111 else 0o644


def snapshot_entries(snapshot: Path) -> tuple[str, list[Path], list[Path]]:
    snapshot = snapshot.resolve()
    if not snapshot.is_dir():
        raise PackagingError(f"snapshot directory does not exist: {snapshot}")
    if snapshot == Path(snapshot.anchor):
        raise PackagingError("refusing to package a filesystem root")

    for path in snapshot.rglob("*"):
        if path.is_symlink():
            raise PackagingError(f"snapshot contains a symlink: {path}")

    directories = [snapshot]
    files: list[Path] = []
    for path in snapshot.rglob("*"):
        if path.is_symlink():
            raise PackagingError(f"snapshot contains a symlink: {path}")
        if path.is_dir():
            directories.append(path)
        elif path.is_file():
            files.append(path)

    directories.sort(key=lambda path: path.relative_to(snapshot).as_posix())
    files.sort(key=lambda path: path.relative_to(snapshot).as_posix())
    return snapshot.name, directories, files


def build_zip(snapshot: Path) -> bytes:
    root_name, directories, files = snapshot_entries(snapshot)
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for directory in directories:
            relative = directory.relative_to(snapshot).as_posix()
            name = root_name if relative == "." else f"{root_name}/{relative}"
            info = zipfile.ZipInfo(f"{name}/", date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (stat.S_IFDIR | archive_mode(directory, is_directory=True)) << 16
            info.external_attr |= 0x10
            archive.writestr(info, b"")
        for path in files:
            relative = path.relative_to(snapshot).as_posix()
            info = zipfile.ZipInfo(f"{root_name}/{relative}", date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | archive_mode(path, is_directory=False)) << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_checksums(output_dir: Path, archives: list[Path]) -> Path:
    lines = [f"{sha256_bytes(archive.read_bytes())}  {archive.name}" for archive in archives]
    checksum_path = output_dir / CHECKSUM_FILE
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return checksum_path


def build_archives(snapshot: Path, output_dir: Path) -> list[Path]:
    snapshot = snapshot.resolve()
    output_dir = output_dir.resolve()
    if output_dir == snapshot or output_dir.is_relative_to(snapshot):
        raise PackagingError("output directory must be outside the snapshot")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{ARCHIVE_STEM}.zip"
    archive_path.write_bytes(build_zip(snapshot))
    checksum_path = write_checksums(output_dir, [archive_path])
    return [archive_path, checksum_path]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic zip release archive and SHA-256 manifest."
    )
    parser.add_argument("--snapshot", type=Path, required=True, help="validated public snapshot directory")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="directory for the archive and checksum manifest (default: current directory)",
    )
    args = parser.parse_args()
    try:
        artifacts = build_archives(args.snapshot, args.output_dir)
    except (OSError, PackagingError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    for artifact in artifacts:
        print(f"wrote {artifact}")
    print(f"wrote {len(artifacts)} release artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
