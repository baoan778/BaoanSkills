from __future__ import annotations

import csv
import hashlib
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest
from build_kb_manifest import (
    ManifestError,
    build_records,
    render_manifest,
    validate_rendered_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = ROOT / "skills" / "ctf-knowledge-base" / "scripts" / "search_kb.py"


def test_manifest_is_deterministic_and_content_free(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    (source / "WP\u6c47\u603b").mkdir(parents=True)
    (source / "CTF\u5e38\u7528\u811a\u672c\u53ca\u5de5\u5177").mkdir()
    (source / "\u5de5\u5177\u4f7f\u7528").mkdir()
    (source / "CTF\u5de5\u5177\u96c6" / "sample-tool").mkdir(parents=True)
    (source / "SQL.md").write_bytes(b"SELECT 1;\n")
    (source / "WP\u6c47\u603b" / "case.md").write_text("case body\n", encoding="utf-8")
    (source / "CTF\u5e38\u7528\u811a\u672c\u53ca\u5de5\u5177" / "solve.py").write_text("print(1)\n", encoding="utf-8")
    (source / "\u5de5\u5177\u4f7f\u7528" / "guide.md").write_text("guide body\n", encoding="utf-8")
    (source / "CTF\u5de5\u5177\u96c6" / "sample-tool" / "README.txt").write_text("tool body\n", encoding="utf-8")

    records = build_records(source)
    rendered = render_manifest(records)
    rows = list(csv.DictReader(io.StringIO(rendered)))

    assert [record.relative_path for record in records] == sorted(
        record.relative_path for record in records
    )
    assert {record.relative_path: record.category for record in records} == {
        "CTF\u5de5\u5177\u96c6/sample-tool/README.txt": "toolset",
        "CTF\u5e38\u7528\u811a\u672c\u53ca\u5de5\u5177/solve.py": "script",
        "SQL.md": "topic-note",
        "WP\u6c47\u603b/case.md": "writeup",
        "\u5de5\u5177\u4f7f\u7528/guide.md": "tool-guide",
    }
    root_record = next(record for record in records if record.relative_path == "SQL.md")
    assert root_record.sha256 == hashlib.sha256(b"SELECT 1;\n").hexdigest()
    assert root_record.extension == ".md"
    assert len(rows) == len(records)
    assert str(source) not in rendered
    assert "SELECT 1" not in rendered
    assert rendered == render_manifest(build_records(source))


def test_manifest_static_validation_accepts_canonical_content_free_manifest(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    source.mkdir()
    (source / "SQL.md").write_text("SELECT 1;\n", encoding="utf-8")

    rendered = render_manifest(build_records(source))
    records = validate_rendered_manifest(rendered)

    assert [record.relative_path for record in records] == ["SQL.md"]
    assert "SELECT 1" not in rendered


def test_manifest_static_validation_rejects_unsafe_or_stale_records() -> None:
    record = (
        "relative_path,category,extension,bytes,sha256\n"
        "SQL.md,topic-note,.md,9," + "0" * 64 + "\n"
    )
    assert validate_rendered_manifest(record)[0].relative_path == "SQL.md"

    with pytest.raises(ManifestError, match="unsafe or non-portable"):
        validate_rendered_manifest(record.replace("SQL.md", "../SQL.md"))
    with pytest.raises(ManifestError, match="sha256"):
        validate_rendered_manifest(record.replace("0" * 64, "A" * 64))
    with pytest.raises(ManifestError, match="category"):
        validate_rendered_manifest(record.replace("topic-note", "writeup"))
    with pytest.raises(ManifestError, match="canonical CSV"):
        validate_rendered_manifest(record.replace("9", "09"))


def test_manifest_rejects_unknown_top_level_directory(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    (source / "unexpected").mkdir(parents=True)
    (source / "unexpected" / "file.txt").write_text("x", encoding="utf-8")

    with pytest.raises(ManifestError, match="unrecognized top-level"):
        build_records(source)


def test_manifest_rejects_symlinks(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    source.mkdir()
    target = tmp_path / "outside.txt"
    target.write_text("outside", encoding="utf-8")
    try:
        (source / "linked.txt").symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    with pytest.raises(ManifestError, match="symlinked files"):
        build_records(source)


def test_search_script_uses_category_and_context_filters(tmp_path: Path) -> None:
    source = tmp_path / "corpus"
    (source / "WP\u6c47\u603b").mkdir(parents=True)
    (source / "CTF\u5de5\u5177\u96c6").mkdir()
    (source / "WP\u6c47\u603b" / "case.md").write_text(
        "before\nSQL injection needle\nafter\n", encoding="utf-8"
    )
    (source / "CTF\u5de5\u5177\u96c6" / "tool.py").write_text("needle\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SEARCH_SCRIPT),
            "needle",
            "--source",
            str(source),
            "--category",
            "writeup",
            "--extension",
            "md",
            "--context",
            "1",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "[writeup] WP\u6c47\u603b/case.md:2" in result.stdout
    assert "before" in result.stdout
    assert "after" in result.stdout
    assert "tool.py" not in result.stdout
