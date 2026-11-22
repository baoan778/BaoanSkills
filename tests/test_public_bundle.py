from __future__ import annotations

from pathlib import Path

from build_public_bundle import remove_transient_artifacts, run


def test_snapshot_cleanup_removes_runtime_caches(tmp_path: Path) -> None:
    root = tmp_path / "BaoanSkills-public"
    (root / ".pytest_cache").mkdir(parents=True)
    (root / ".ruff_cache").mkdir()
    (root / "scripts" / "__pycache__").mkdir(parents=True)
    (root / "scripts" / "__pycache__" / "helper.pyc").write_bytes(b"cache")
    (root / ".coverage").write_text("coverage", encoding="utf-8")
    (root / "keep.txt").write_text("keep", encoding="utf-8")

    removed = remove_transient_artifacts(root)

    assert removed == 5
    assert not (root / ".pytest_cache").exists()
    assert not (root / ".ruff_cache").exists()
    assert not (root / "scripts" / "__pycache__").exists()
    assert not (root / ".coverage").exists()
    assert (root / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_validation_subprocesses_do_not_write_bytecode(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_run(command, cwd, check, env):
        assert command == ["python", "-c", "pass"]
        assert cwd == tmp_path
        assert check is True
        captured.update(env)

    monkeypatch.setattr("build_public_bundle.subprocess.run", fake_run)
    run(["python", "-c", "pass"], tmp_path)

    assert captured["PYTHONDONTWRITEBYTECODE"] == "1"
