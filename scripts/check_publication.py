#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from _skill_utils import (
    NAME_RE,
    flatten,
    load_skill,
    metadata_of,
    normalized_license,
    repo_root,
)

LOCK_REL = Path("release") / "provenance.lock.json"
ALLOWLIST_REL = Path("release") / "public-skills.txt"
GITIGNORE_REL = Path("skills") / ".gitignore"
SCHEMA_VERSION = 1
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".sh", ".txt", ".json", ".toml", ".csv"}
IGNORED_FILE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_allowlist(root: Path) -> tuple[list[str], list[str]]:
    path = root / ALLOWLIST_REL
    errors: list[str] = []
    if not path.is_file():
        return [], [f"missing public allowlist: {ALLOWLIST_REL.as_posix()}"]
    names: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        name = raw_line.strip()
        if not name or name.startswith("#"):
            continue
        if name in names:
            errors.append(f"{ALLOWLIST_REL.as_posix()}:{line_number}: duplicate skill '{name}'")
            continue
        if not NAME_RE.fullmatch(name):
            errors.append(f"{ALLOWLIST_REL.as_posix()}:{line_number}: invalid skill name '{name}'")
            continue
        names.append(name)
    if not names:
        errors.append("public allowlist is empty")
    return names, errors


def validate_skill_gitignore(root: Path, names: list[str]) -> list[str]:
    """Require the unignore set to match the public allowlist exactly."""
    path = root / GITIGNORE_REL
    if not path.is_file():
        return [f"missing skill ignore policy: {GITIGNORE_REL.as_posix()}"]
    patterns = [
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    expected = ["/*", "!.gitignore"]
    for name in names:
        expected.extend([f"!{name}/", f"!{name}/**"])

    actual_set = set(patterns)
    expected_set = set(expected)
    errors: list[str] = []
    missing = sorted(expected_set - actual_set)
    unexpected = sorted(actual_set - expected_set)
    if missing:
        errors.append(
            f"{GITIGNORE_REL.as_posix()} is missing allowlist patterns: " + ", ".join(missing)
        )
    if unexpected:
        errors.append(
            f"{GITIGNORE_REL.as_posix()} contains non-allowlisted patterns: "
            + ", ".join(unexpected)
        )
    duplicate_count = len(patterns) - len(actual_set)
    if duplicate_count:
        errors.append(
            f"{GITIGNORE_REL.as_posix()} contains {duplicate_count} duplicate ignore pattern(s)"
        )
    return errors


def has_non_lf_line_endings(path: Path) -> bool:
    """Return whether a file contains CR bytes instead of canonical LF endings."""
    return b"\r" in path.read_bytes()


def skill_files(skill_dir: Path) -> list[Path]:
    files = [
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() not in {".pyc", ".pyo"}
        and not any(part in IGNORED_FILE_PARTS for part in path.relative_to(skill_dir).parts)
    ]
    return sorted(files, key=lambda path: path.relative_to(skill_dir).as_posix())


def manifest_entry(root: Path, name: str) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    skill_dir = root / "skills" / name
    skill_file = skill_dir / "SKILL.md"
    if not skill_dir.is_dir():
        return None, [f"{name}: skill directory does not exist"]
    if not skill_file.is_file():
        return None, [f"{name}: SKILL.md does not exist"]
    try:
        doc = load_skill(skill_dir)
    except Exception as exc:  # noqa: BLE001
        return None, [f"{name}: {exc}"]

    fm = doc.frontmatter
    metadata = metadata_of(fm)
    license_value = normalized_license(fm)
    fields = {
        "license": license_value,
        "license_status": flatten(metadata.get("license_status", "")) or "unknown",
        "provenance_status": flatten(metadata.get("provenance_status", "")) or "unknown",
        "author": flatten(metadata.get("author", "")) or "unknown",
        "source": flatten(metadata.get("source", "")) or "unknown",
        "source_repo": flatten(metadata.get("source_repo", "")) or "",
        "upstream_commit": flatten(metadata.get("upstream_commit", "")) or "",
        "upstream_path": flatten(metadata.get("upstream_path", "")) or "",
        "license_evidence": flatten(metadata.get("license_evidence", "")) or "",
        "retrieved_at": flatten(metadata.get("retrieved_at", "")) or "",
        "modifications": flatten(metadata.get("modifications", "")) or "",
    }

    if fields["license_status"] != "verified":
        errors.append(f"{name}: metadata.license_status must be verified")
    if fields["provenance_status"] != "verified":
        errors.append(f"{name}: metadata.provenance_status must be verified")
    if license_value == "NOASSERTION":
        errors.append(f"{name}: license must not be NOASSERTION")
    for field in ("author", "source", "license_evidence", "retrieved_at", "modifications"):
        if fields[field] in {"", "unknown"}:
            errors.append(f"{name}: metadata.{field} is required")

    retrieved_at = fields["retrieved_at"]
    if retrieved_at:
        try:
            date.fromisoformat(retrieved_at)
        except ValueError:
            errors.append(f"{name}: metadata.retrieved_at must be an ISO date (YYYY-MM-DD)")

    evidence_path = Path(fields["license_evidence"]) if fields["license_evidence"] else None
    evidence_sha256 = ""
    if evidence_path is not None:
        if evidence_path.is_absolute() or ".." in evidence_path.parts:
            errors.append(f"{name}: license evidence must be repository-relative")
        else:
            full_evidence = root / evidence_path
            if not full_evidence.is_file():
                errors.append(f"{name}: license evidence does not exist: {evidence_path.as_posix()}")
            else:
                evidence_sha256 = sha256_file(full_evidence)
                if has_non_lf_line_endings(full_evidence):
                    errors.append(
                        f"{name}: license evidence must use LF line endings: {evidence_path.as_posix()}"
                    )

    source = fields["source"]
    if source == "original":
        if fields["source_repo"] or fields["upstream_commit"] or fields["upstream_path"]:
            errors.append(f"{name}: original content must not declare upstream fields")
        if evidence_path is not None and evidence_path.name not in {"LICENSE", "LICENSE.md"}:
            errors.append(f"{name}: original content should cite the root LICENSE")
    else:
        for field in ("source_repo", "upstream_commit", "upstream_path"):
            if not fields[field]:
                errors.append(f"{name}: metadata.{field} is required for third-party content")
        if fields["upstream_commit"] and not COMMIT_RE.fullmatch(fields["upstream_commit"]):
            errors.append(f"{name}: metadata.upstream_commit must be a 40-character lowercase Git commit")
        if fields["source_repo"] and fields["upstream_commit"] and fields["upstream_path"]:
            expected_source = (
                f"{fields['source_repo'].rstrip('/')}/blob/"
                f"{fields['upstream_commit']}/{fields['upstream_path']}"
            )
            if source != expected_source:
                errors.append(f"{name}: metadata.source must match the pinned upstream URL")
        if evidence_path is not None and (not evidence_path.parts or evidence_path.parts[0] != "licenses"):
            errors.append(f"{name}: third-party evidence must be stored under licenses/")

    if "authorized use only" not in doc.raw.casefold():
        errors.append(f"{name}: missing explicit 'Authorized use only' boundary")

    files: list[dict[str, Any]] = []
    for path in skill_files(skill_dir):
        if path.is_symlink():
            errors.append(f"{name}: symlinks are not allowed in published skills ({path.relative_to(skill_dir)})")
            continue
        relative = path.relative_to(skill_dir).as_posix()
        data = path.read_bytes()
        files.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        if path.suffix.lower() in TEXT_SUFFIXES:
            if b"\r" in data:
                errors.append(
                    f"{name}: {relative} must use LF line endings; run python scripts/check_whitespace.py --fix"
                )
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                errors.append(f"{name}: {relative} is not valid UTF-8: {exc}")
                continue
            if "NOASSERTION" in text:
                errors.append(f"{name}: published file {relative} contains NOASSERTION")

    entry = {
        **fields,
        "skill_md_sha256": sha256_file(skill_file),
        "license_evidence_sha256": evidence_sha256,
        "files": files,
    }
    return entry, errors


def build_payload(root: Path) -> tuple[dict[str, Any], list[str]]:
    names, errors = parse_allowlist(root)
    errors.extend(validate_skill_gitignore(root, names))
    skills: dict[str, Any] = {}
    for name in names:
        entry, entry_errors = manifest_entry(root, name)
        errors.extend(entry_errors)
        if entry is not None:
            skills[name] = entry
    payload = {
        "schema_version": SCHEMA_VERSION,
        "selection": ALLOWLIST_REL.as_posix(),
        "skills": skills,
    }
    return payload, errors


def render_lock(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def compare_entry(name: str, actual: Any, expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(actual, dict):
        return [f"lock entry for {name} must be a JSON object"]

    for field in sorted(set(expected) | set(actual)):
        if field == "files":
            continue
        if actual.get(field) != expected.get(field):
            errors.append(f"lock entry has drifted for {name}: field '{field}'")

    actual_files = actual.get("files")
    if not isinstance(actual_files, list):
        errors.append(f"lock entry has drifted for {name}: field 'files' must be a list")
        return errors

    expected_files = expected["files"]
    expected_by_path = {item["path"]: item for item in expected_files}
    actual_by_path: dict[str, dict[str, Any]] = {}
    for item in actual_files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append(f"lock entry has drifted for {name}: malformed file entry")
            continue
        path = item["path"]
        if path in actual_by_path:
            errors.append(f"lock entry has drifted for {name}: duplicate file entry {path}")
            continue
        actual_by_path[path] = item

    expected_paths = [item["path"] for item in expected_files]
    for path in sorted(set(expected_by_path) - set(actual_by_path)):
        errors.append(f"lock entry has drifted for {name}: missing file {path}")
    for path in sorted(set(actual_by_path) - set(expected_by_path)):
        errors.append(f"lock entry has drifted for {name}: unexpected file {path}")
    for path in sorted(set(expected_by_path) & set(actual_by_path)):
        if actual_by_path[path] != expected_by_path[path]:
            errors.append(f"lock entry has drifted for {name}: file metadata changed: {path}")

    actual_paths = [
        item["path"]
        for item in actual_files
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    ]
    if set(actual_paths) == set(expected_paths) and actual_paths != expected_paths:
        errors.append(f"lock entry has drifted for {name}: canonical file order changed")
    return errors


def compare_lock(actual: Any, expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(actual, dict):
        return ["release/provenance.lock.json must contain a JSON object"]
    if actual.get("schema_version") != expected["schema_version"]:
        errors.append("release/provenance.lock.json has an unsupported schema_version")
    if actual.get("selection") != expected["selection"]:
        errors.append("release/provenance.lock.json has an unexpected selection field")
    actual_skills = actual.get("skills")
    if not isinstance(actual_skills, dict):
        return errors + ["release/provenance.lock.json skills must be a JSON object"]
    expected_skills = expected["skills"]
    missing = sorted(set(expected_skills) - set(actual_skills))
    extra = sorted(set(actual_skills) - set(expected_skills))
    if missing:
        errors.append("lock is missing skills: " + ", ".join(missing))
    if extra:
        errors.append("lock contains non-allowlisted skills: " + ", ".join(extra))
    for name in sorted(set(expected_skills) & set(actual_skills)):
        if actual_skills[name] != expected_skills[name]:
            errors.extend(compare_entry(name, actual_skills[name], expected_skills[name]))
    return errors


def validate_publication(
    root: Path,
    *,
    exclusive: bool = False,
    require_lock: bool = True,
) -> list[str]:
    expected, errors = build_payload(root)
    if require_lock:
        lock_path = root / LOCK_REL
        if not lock_path.is_file():
            errors.append("missing release/provenance.lock.json; run python scripts/check_publication.py --write")
        else:
            try:
                actual = json.loads(lock_path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as exc:
                errors.append(f"release/provenance.lock.json is invalid JSON: {exc}")
            else:
                errors.extend(compare_lock(actual, expected))
    if exclusive:
        names, _ = parse_allowlist(root)
        on_disk = sorted(
            path.name
            for path in (root / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
        extras = sorted(set(on_disk) - set(names))
        missing = sorted(set(names) - set(on_disk))
        if extras:
            errors.append("clean snapshot contains non-allowlisted skill directories: " + ", ".join(extras))
        if missing:
            errors.append("clean snapshot is missing allowlisted skill directories: " + ", ".join(missing))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the public allowlist, provenance fields, license evidence, and file lock."
    )
    parser.add_argument("--write", action="store_true", help="write release/provenance.lock.json")
    parser.add_argument("--check", action="store_true", help="verify the existing lock without changing files")
    parser.add_argument(
        "--exclusive",
        action="store_true",
        help="require the snapshot to contain only allowlisted skill directories",
    )
    parser.add_argument("--root", type=Path, default=repo_root(), help="repository or release-snapshot root")
    args = parser.parse_args()
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    root = args.root.resolve()
    if args.write:
        payload, errors = build_payload(root)
        if errors:
            for error in errors:
                print(f"FAIL {error}")
            print("cannot write provenance lock until publication errors are fixed")
            return 1
        lock_path = root / LOCK_REL
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(render_lock(payload), encoding="utf-8", newline="\n")
        print(f"wrote {lock_path}")
    errors = validate_publication(root, exclusive=args.exclusive, require_lock=True)
    for error in errors:
        print(f"FAIL {error}")
    names, _ = parse_allowlist(root)
    if errors:
        print(f"publication check failed for {len(names)} allowlisted skills; failures: {len(errors)}")
        return 1
    print(f"publication check passed for {len(names)} allowlisted skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
