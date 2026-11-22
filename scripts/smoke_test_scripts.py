#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from _skill_utils import is_release_scope_path, repo_root

IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}


def main() -> int:
    root = repo_root()
    failures: list[tuple[Path, str]] = []
    python_files = sorted(
        path
        for path in root.rglob("*.py")
        if not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )
    yaml_files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".yaml", ".yml"}
        and not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )
    shell_files = sorted(
        path
        for path in root.rglob("*.sh")
        if not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        for path in python_files:
            try:
                py_compile.compile(str(path), cfile=str(Path(temp_dir) / f"{abs(hash(path))}.pyc"), doraise=True)
            except Exception as exc:  # noqa: BLE001
                failures.append((path.relative_to(root), f"Python compile failed: {exc}"))

    for path in yaml_files:
        try:
            # Kubernetes and similar assets commonly contain multiple YAML
            # documents in one file. Consume the iterator so every document is
            # parsed, while still accepting a single-document file.
            list(yaml.safe_load_all(path.read_text(encoding="utf-8-sig")))
        except yaml.YAMLError as exc:
            failures.append((path.relative_to(root), f"YAML parse failed: {exc}"))

    bash = shutil.which("bash")
    if bash:
        for path in shell_files:
            result = subprocess.run(
                [bash, "-n", path.relative_to(root).as_posix()],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                failures.append((path.relative_to(root), f"shell syntax failed: {result.stderr.strip()}"))

    for path, message in failures:
        print(f"FAIL {path}: {message}")
    print(
        f"checked {len(python_files)} Python files, {len(yaml_files)} YAML files, "
        f"and {len(shell_files)} shell files; failures: {len(failures)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
