#!/usr/bin/env python3
"""Build deterministic tar.gz and zip distributions from a public snapshot."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import stat
import sys
import tarfile
import zipfile
from pathlib import Path

ARCHIVE_STEM = "baoanskills-release"
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


def build_tar_gz(snapshot: Path) -> bytes:
    root_name, directories, files = snapshot_entries(snapshot)
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for directory in directories:
            relative = directory.relative_to(snapshot).as_posix()
            name = root_name if relative == "." else f"{root_name}/{relative}"
            info = tarfile.TarInfo(name=f"{name}/")
            info.type = tarfile.DIRTYPE
            info.mode = archive_mode(directory, is_directory=True)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            archive.addfile(info)
        for path in files:
            relative = path.relative_to(snapshot).as_posix()
            info = tarfile.TarInfo(name=f"{root_name}/{relative}")
            info.type = tarfile.REGTYPE
            info.mode = archive_mode(path, is_directory=False)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            info.size = path.stat().st_size
            with path.open("rb") as source:
                archive.addfile(info, source)

    compressed = io.BytesIO()
    with gzip.GzipFile(
        filename="",
        mode="wb",
        fileobj=compressed,
        compresslevel=9,
        mtime=0,
    ) as archive:
        archive.write(tar_buffer.getvalue())
    return compressed.getvalue()


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


def write_artifact(path: Path, content: bytes) -> Path:
    path.write_bytes(content)
    checksum_path = path.with_name(f"{path.name}.sha256")
    checksum_path.write_text(
        f"{sha256_bytes(content)}  {path.name}\n",
        encoding="utf-8",
        newline="\n",
    )
    return checksum_path


def build_archives(snapshot: Path, output_dir: Path) -> list[Path]:
    snapshot = snapshot.resolve()
    output_dir = output_dir.resolve()
    if output_dir == snapshot or output_dir.is_relative_to(snapshot):
        raise PackagingError("output directory must be outside the snapshot")

    output_dir.mkdir(parents=True, exist_ok=True)
    tar_gz = output_dir / f"{ARCHIVE_STEM}.tar.gz"
    zip_path = output_dir / f"{ARCHIVE_STEM}.zip"
    tar_checksum = write_artifact(tar_gz, build_tar_gz(snapshot))
    zip_checksum = write_artifact(zip_path, build_zip(snapshot))
    return [tar_gz, tar_checksum, zip_path, zip_checksum]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic tar.gz and zip release archives with SHA-256 checksums."
    )
    parser.add_argument("--snapshot", type=Path, required=True, help="validated public snapshot directory")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="directory for archives and checksum files (default: current directory)",
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
