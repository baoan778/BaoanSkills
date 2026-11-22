#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _skill_utils import is_release_scope_path, repo_root
from build_provenance import collect_records
from check_publication import validate_publication

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".sh", ".txt", ".json", ".toml", ".csv"}
IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}
# Detect concrete user-home paths while ignoring documented placeholders and
# training/CTF fixture accounts used throughout the skills.
NON_PERSONAL_HOME_USERS = {
    "admin",
    "all users",
    "anonymous",
    "attacker",
    "ctf",
    "ctfuser",
    "default",
    "default user",
    "demo",
    "example",
    "guest",
    "johnsieberr",
    "loluser",
    "papercut",
    "public",
    "shared",
    "suspect",
    "target",
    "test",
    "user",
    "username",
    "victim",
}
HOME_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/](?P<user>\w[^\\/\s]*)"),
    re.compile(r"(?<![A-Za-z0-9])/Users/(?P<user>\w[^/\s]*)"),
    re.compile(r"(?<![A-Za-z0-9])/home/(?P<user>\w[^/\s]*)"),
)
LEGACY_KB_RE = re.compile(r"E:\\CTF工具集", re.IGNORECASE)


def find_personal_path(line: str) -> str | None:
    for pattern in HOME_PATH_PATTERNS:
        for match in pattern.finditer(line):
            user = match.group("user").rstrip(".,;:)]}`'\"")
            if user.casefold() not in NON_PERSONAL_HOME_USERS:
                return match.group(0)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit release scope for licensing, provenance, and leaks.")
    parser.add_argument("--strict", action="store_true", help="fail on any release-readiness finding")
    parser.add_argument(
        "--exclusive",
        action="store_true",
        help="also require the checkout to contain only allowlisted skill directories",
    )
    args = parser.parse_args()
    root = repo_root()
    records = collect_records()
    noassertion = [record.name for record in records if record.license == "NOASSERTION"]
    review_required = [record.name for record in records if record.status != "verified"]

    path_findings: list[tuple[Path, int, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if not is_release_scope_path(path):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), start=1):
            if find_personal_path(line) or LEGACY_KB_RE.search(line):
                path_findings.append((path.relative_to(root), line_number, line.strip()))

    publication_errors = validate_publication(root, exclusive=args.exclusive, require_lock=True)

    print(f"skills in release scope: {len(records)}")
    print(f"NOASSERTION: {len(noassertion)}")
    print(f"review-required: {len(review_required)}")
    print(f"publication errors: {len(publication_errors)}")
    print(f"personal or legacy absolute paths: {len(path_findings)}")
    for name in noassertion[:20]:
        print(f"  NOASSERTION {name}")
    for name in review_required[:20]:
        print(f"  REVIEW {name}")
    for error in publication_errors[:20]:
        print(f"  PUBLICATION {error}")
    for file_path, line_number, line in path_findings[:20]:
        print(f"  PATH {file_path}:{line_number}: {line[:160]}")
    if not args.strict:
        print("non-strict audit completed")
        return 0
    if noassertion or review_required or path_findings or publication_errors:
        print("strict release readiness check failed")
        return 1
    print("strict release readiness check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
