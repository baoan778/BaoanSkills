#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from _skill_utils import NAME_RE, iter_skills, publication_names, repo_root

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db", ".pytest_cache")
LOCK_REL = Path("release") / "provenance.lock.json"
IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def default_destination() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home).expanduser() / "skills" if codex_home else Path.home() / ".codex" / "skills"


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_skill_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        if path.is_dir() and not path.is_symlink():
            continue
        files.append(path)
    return files


def verify_skill_integrity(source_root: Path, names: list[str]) -> list[str]:
    """Verify requested skill files against the release provenance lock."""
    lock_path = source_root / LOCK_REL
    if not lock_path.is_file():
        return [f"missing {LOCK_REL.as_posix()}; cannot verify installer source"]
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid {LOCK_REL.as_posix()}: {exc}"]
    if not isinstance(lock, dict) or lock.get("schema_version") != 1:
        return [f"{LOCK_REL.as_posix()} must use schema_version 1"]
    skills = lock.get("skills")
    if not isinstance(skills, dict):
        return [f"{LOCK_REL.as_posix()} skills must be a mapping"]

    errors: list[str] = []
    for name in names:
        entry = skills.get(name)
        if not isinstance(entry, dict):
            errors.append(f"{name}: no provenance lock entry")
            continue
        records = entry.get("files")
        if not isinstance(records, list) or not records:
            errors.append(f"{name}: provenance lock has no file records")
            continue

        skill_dir = source_root / "skills" / name
        if skill_dir.is_symlink():
            errors.append(f"{name}: skill directory must not be a symlink")
            continue
        expected: dict[str, tuple[object, object]] = {}
        for record in records:
            if not isinstance(record, dict):
                errors.append(f"{name}: malformed file record")
                continue
            relative = record.get("path")
            if not isinstance(relative, str) or not relative.strip():
                errors.append(f"{name}: file record has no path")
                continue
            relative_path = Path(relative)
            if relative_path.is_absolute() or ".." in relative_path.parts or "\\" in relative:
                errors.append(f"{name}: unsafe locked path {relative!r}")
                continue
            if relative in expected:
                errors.append(f"{name}: duplicate locked path {relative}")
                continue
            expected[relative] = (record.get("bytes"), record.get("sha256"))

        actual: dict[str, Path] = {}
        for path in expected_skill_files(skill_dir):
            relative = path.relative_to(skill_dir).as_posix()
            if path.is_symlink():
                errors.append(f"{name}: symlinks are not installable ({relative})")
                continue
            actual[relative] = path

        for relative in sorted(set(expected) - set(actual)):
            errors.append(f"{name}: locked file is missing ({relative})")
        for relative in sorted(set(actual) - set(expected)):
            errors.append(f"{name}: unexpected file is not locked ({relative})")

        for relative, (expected_bytes, expected_digest) in sorted(expected.items()):
            path = actual.get(relative)
            if path is None:
                continue
            if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool):
                errors.append(f"{name}: invalid byte count for {relative}")
            elif path.stat().st_size != expected_bytes:
                errors.append(f"{name}: size mismatch for {relative}")
            if not isinstance(expected_digest, str) or len(expected_digest) != 64:
                errors.append(f"{name}: invalid SHA-256 for {relative}")
            elif sha256_file(path) != expected_digest:
                errors.append(f"{name}: hash mismatch for {relative}")
    return errors


def validate_names(requested: list[str], available: list[str]) -> list[str]:
    errors: list[str] = []
    if len(requested) != len(set(requested)):
        errors.append("skill names must not be repeated")
    for name in requested:
        if not NAME_RE.fullmatch(name):
            errors.append(f"invalid skill name: {name!r}")
        elif name not in available:
            errors.append(f"skill is not in the public allowlist: {name}")
    return errors


def copy_skill(source: Path, destination: Path, *, force: bool, dry_run: bool) -> None:
    target = destination / source.name
    action = "replace" if target.exists() and force else "install"
    print(f"{'WOULD ' if dry_run else ''}{action.upper()} {source.name} -> {target}")
    if dry_run:
        return
    if target.exists() or target.is_symlink():
        if not force:
            raise FileExistsError(target)
        if target.is_symlink() or not target.is_dir():
            target.unlink()
        else:
            shutil.rmtree(target)
    shutil.copytree(source, target, ignore=IGNORE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install allowlisted BaoanSkills into a Codex skills directory.")
    parser.add_argument("skills", nargs="*", help="skill names to install")
    parser.add_argument("--all", action="store_true", help="install every public allowlisted skill")
    parser.add_argument("--dest", type=Path, default=default_destination(), help="destination skills directory")
    parser.add_argument("--force", action="store_true", help="replace already installed skill directories")
    parser.add_argument("--list", action="store_true", help="list installable public skills")
    parser.add_argument("--dry-run", action="store_true", help="show planned operations without copying")
    args = parser.parse_args()

    available = publication_names() or []
    if args.list:
        for name in available:
            print(name)
        return 0
    if args.all and args.skills:
        parser.error("use either skill names or --all, not both")
    if not args.all and not args.skills:
        parser.error("provide at least one skill name, --all, or --list")
    if not available:
        print("FAIL release/public-skills.txt is missing or empty")
        return 1

    requested = available if args.all else args.skills
    errors = validate_names(requested, available)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    source_root = repo_root().resolve()
    integrity_errors = verify_skill_integrity(source_root, requested)
    if integrity_errors:
        for error in integrity_errors:
            print(f"FAIL {error}")
        print("installer source failed provenance verification; no files were copied")
        return 1

    destination = args.dest.expanduser().resolve()
    if is_within(destination, source_root):
        print("FAIL destination must be outside the source checkout")
        return 1

    by_name = {path.name: path for path in iter_skills()}
    missing = [name for name in requested if not (by_name.get(name, Path()) / "SKILL.md").is_file()]
    if missing:
        for name in missing:
            print(f"FAIL source skill is missing: {name}")
        return 1

    conflicts = [
        name
        for name in requested
        if ((destination / name).exists() or (destination / name).is_symlink()) and not args.force
    ]
    if conflicts:
        print("FAIL already installed (use --force to replace): " + ", ".join(conflicts))
        return 1

    if not args.dry_run:
        destination.mkdir(parents=True, exist_ok=True)
    for name in requested:
        copy_skill(by_name[name], destination, force=args.force, dry_run=args.dry_run)
    print(f"{'would install' if args.dry_run else 'installed'} {len(requested)} skill(s) in {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
