from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest
from package_release import PackagingError, build_archives


def make_snapshot(tmp_path: Path) -> Path:
    snapshot = tmp_path / "BaoanSkills-public"
    (snapshot / "skills" / "demo" / "scripts").mkdir(parents=True)
    (snapshot / "README.md").write_text("read me\n", encoding="utf-8")
    (snapshot / "skills" / "demo" / "SKILL.md").write_text("demo\n", encoding="utf-8")
    (snapshot / "skills" / "demo" / "scripts" / "run.py").write_text(
        "print('demo')\n", encoding="utf-8"
    )
    (snapshot / "docs").mkdir()
    (snapshot / "docs" / "说明.md").write_text("中文\n", encoding="utf-8")
    return snapshot


def test_build_archives_contains_zip_and_checksum_manifest(tmp_path: Path) -> None:
    snapshot = make_snapshot(tmp_path)
    output = tmp_path / "artifacts"

    artifacts = build_archives(snapshot, output)
    paths = {path.name: path for path in artifacts}

    assert set(paths) == {
        "baoanskills-release.zip",
        "SHA256SUMS",
    }

    zip_path = paths["baoanskills-release.zip"]
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "BaoanSkills-public/" in names
        assert "BaoanSkills-public/README.md" in names
        assert "BaoanSkills-public/docs/说明.md" in names
        assert archive.read("BaoanSkills-public/README.md") == (snapshot / "README.md").read_bytes()

    sums_path = paths["SHA256SUMS"]
    lines = sums_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    digest, filename = lines[0].split("  ", 1)
    assert filename == zip_path.name
    assert digest == hashlib.sha256(zip_path.read_bytes()).hexdigest()


def test_artifacts_are_reproducible_across_output_directories(tmp_path: Path) -> None:
    snapshot = make_snapshot(tmp_path)
    first = build_archives(snapshot, tmp_path / "first")
    second = build_archives(snapshot, tmp_path / "second")

    first_by_name = {path.name: path.read_bytes() for path in first}
    second_by_name = {path.name: path.read_bytes() for path in second}
    assert first_by_name == second_by_name


def test_output_directory_cannot_be_inside_snapshot(tmp_path: Path) -> None:
    snapshot = make_snapshot(tmp_path)
    with pytest.raises(PackagingError, match="outside the snapshot"):
        build_archives(snapshot, snapshot / "artifacts")
