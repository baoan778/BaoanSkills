from __future__ import annotations

import hashlib
import tarfile
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


def test_build_archives_contains_both_portable_formats(tmp_path: Path) -> None:
    snapshot = make_snapshot(tmp_path)
    output = tmp_path / "artifacts"

    artifacts = build_archives(snapshot, output)
    paths = {path.name: path for path in artifacts}

    assert set(paths) == {
        "baoanskills-release.tar.gz",
        "baoanskills-release.tar.gz.sha256",
        "baoanskills-release.zip",
        "baoanskills-release.zip.sha256",
    }

    tar_path = paths["baoanskills-release.tar.gz"]
    with tarfile.open(tar_path, "r:gz") as archive:
        assert (
            archive.extractfile("BaoanSkills-public/README.md").read()
            == (snapshot / "README.md").read_bytes()
        )
        assert (
            archive.extractfile("BaoanSkills-public/docs/说明.md").read()
            == (snapshot / "docs" / "说明.md").read_bytes()
        )

    zip_path = paths["baoanskills-release.zip"]
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "BaoanSkills-public/README.md" in names
        assert "BaoanSkills-public/docs/说明.md" in names
        assert archive.read("BaoanSkills-public/README.md") == (snapshot / "README.md").read_bytes()

    for archive_path in (tar_path, zip_path):
        checksum_path = paths[f"{archive_path.name}.sha256"]
        digest, filename = checksum_path.read_text(encoding="utf-8").strip().split("  ", 1)
        assert filename == archive_path.name
        assert digest == hashlib.sha256(archive_path.read_bytes()).hexdigest()


def test_archives_are_reproducible_across_output_directories(tmp_path: Path) -> None:
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
