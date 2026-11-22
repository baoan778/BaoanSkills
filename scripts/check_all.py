#!/usr/bin/env python3
"""Run the release-scoped validation suite used by CI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Compile Python sources", ("-m", "compileall", "-q", "scripts", "tests")),
    ("Lint Python sources", ("-m", "ruff", "check", "scripts", "tests")),
    ("Run tests", ("-m", "pytest")),
    ("Validate skill schema", ("scripts/validate_skills.py", "--strict")),
    ("Check whitespace", ("scripts/check_whitespace.py",)),
    ("Check UTF-8 encoding", ("scripts/check_encoding.py",)),
    ("Check publication allowlist and lock", ("scripts/check_publication.py", "--check")),
    ("Check Markdown structure", ("scripts/check_markdown_structure.py",)),
    ("Check local links", ("scripts/check_links.py",)),
    ("Check referenced resources", ("scripts/check_resources.py",)),
    ("Check skill layout", ("scripts/check_skill_layout.py",)),
    ("Check quality catalog", ("scripts/apply_skill_quality.py", "--check")),
    ("Check generated agent metadata", ("scripts/generate_agent_metadata.py", "--check")),
    ("Run script smoke tests", ("scripts/smoke_test_scripts.py",)),
    ("Check generated skill index", ("scripts/build_index.py", "--check")),
    ("Check generated provenance", ("scripts/build_provenance.py", "--check")),
    ("Check generated knowledge-base manifest", ("scripts/build_kb_manifest.py", "--check")),
    ("Check pinned workflows", ("scripts/check_workflows.py",)),
    ("Check release readiness", ("scripts/check_release_readiness.py", "--strict")),
)


def main() -> int:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    failures: list[str] = []

    print(f"BaoanSkills validation suite ({len(STAGES)} stages)")
    for number, (label, command) in enumerate(STAGES, start=1):
        print(f"\n[{number}/{len(STAGES)}] {label}")
        try:
            subprocess.run(
                [sys.executable, *command],
                cwd=ROOT,
                env=env,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            failures.append(label)
            print(f"FAIL {label} (exit code {exc.returncode})", file=sys.stderr)

    if failures:
        print("\nValidation failed in:")
        for label in failures:
            print(f"  - {label}")
        return 1

    print(f"\nAll {len(STAGES)} validation stages passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
