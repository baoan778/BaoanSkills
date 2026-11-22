from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import install_skills
from install_skills import validate_names, verify_skill_integrity

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_integrity_fixture(root: Path, *, tamper: bool = False, extra: bool = False) -> Path:
    skill_dir = root / "skills" / "demo-skill"
    references = skill_dir / "references"
    references.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: fixture\n---\n# Demo\n",
        encoding="utf-8",
    )
    (references / "guide.md").write_text("# Guide\n", encoding="utf-8")

    files = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir).as_posix()
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    release = root / "release"
    release.mkdir()
    lock = {
        "schema_version": 1,
        "selection": "release/public-skills.txt",
        "skills": {"demo-skill": {"files": files}},
    }
    (release / "provenance.lock.json").write_text(
        json.dumps(lock, indent=2) + "\n",
        encoding="utf-8",
    )

    if tamper:
        (skill_dir / "SKILL.md").write_text("tampered after lock generation\n", encoding="utf-8")
    if extra:
        (references / "unlocked.md").write_text("# Unlocked\n", encoding="utf-8")
    return skill_dir


def test_install_name_validation_rejects_unlisted_skills() -> None:
    errors = validate_names(["ctf-web", "not-public", "../escape"], ["ctf-web"])
    assert any("not-public" in error for error in errors)
    assert any("invalid skill name" in error for error in errors)


def test_installer_copies_selected_skill(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "install_skills.py"), "ctf-writeup", "--dest", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "ctf-writeup" / "SKILL.md").is_file()
    assert (tmp_path / "ctf-writeup" / "agents" / "openai.yaml").is_file()


def test_install_module_imports_without_pyyaml() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(ROOT / "scripts"), env.get("PYTHONPATH", "")])
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.modules['yaml'] = None; import install_skills; print(install_skills.NAME_RE.pattern)",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "^[a-z0-9-]+$"


def test_integrity_accepts_matching_lock(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _write_integrity_fixture(root)

    assert verify_skill_integrity(root, ["demo-skill"]) == []


def test_integrity_rejects_tampered_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _write_integrity_fixture(root, tamper=True)

    errors = verify_skill_integrity(root, ["demo-skill"])

    assert any("size mismatch" in error for error in errors)
    assert any("hash mismatch" in error for error in errors)


def test_integrity_rejects_unlocked_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _write_integrity_fixture(root, extra=True)

    errors = verify_skill_integrity(root, ["demo-skill"])

    assert any("unexpected file is not locked" in error for error in errors)


def test_integrity_rejects_missing_lock(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "skills" / "demo-skill").mkdir(parents=True)
    (root / "skills" / "demo-skill" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    errors = verify_skill_integrity(root, ["demo-skill"])

    assert errors == ["missing release/provenance.lock.json; cannot verify installer source"]


def test_installer_does_not_copy_after_integrity_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    skill_dir = _write_integrity_fixture(root, tamper=True)
    destination = tmp_path / "destination"

    monkeypatch.setattr(install_skills, "publication_names", lambda: ["demo-skill"])
    monkeypatch.setattr(install_skills, "repo_root", lambda: root)
    monkeypatch.setattr(install_skills, "iter_skills", lambda: [skill_dir])
    monkeypatch.setattr(
        sys,
        "argv",
        ["install_skills.py", "demo-skill", "--dest", str(destination)],
    )

    assert install_skills.main() == 1
    assert not destination.exists()
    assert "no files were copied" in capsys.readouterr().out
