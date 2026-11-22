from __future__ import annotations

from pathlib import Path

from check_workflows import check_workflow, workflow_files


def test_repository_workflows_are_immutable_and_scoped() -> None:
    root = Path(__file__).resolve().parents[1]
    files = workflow_files(root)
    assert files
    errors = [error for path in files for error in check_workflow(path)]
    assert errors == []


def test_validation_workflow_checks_knowledge_base_manifest() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "python scripts/build_kb_manifest.py --check" in workflow


def test_release_workflow_ships_zip_and_tar_archives() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "python scripts/package_release.py" in workflow
    for artifact in (
        "baoanskills-release.tar.gz",
        "baoanskills-release.tar.gz.sha256",
        "baoanskills-release.zip",
        "baoanskills-release.zip.sha256",
    ):
        assert artifact in workflow


def test_release_workflow_smoke_tests_archives_before_upload() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    smoke_step = "Smoke-test release archives"
    upload_step = "Upload release artifact"
    assert smoke_step in workflow
    assert upload_step in workflow
    assert workflow.index(smoke_step) < workflow.index(upload_step)
    assert 'sha256sum -c "${archive}.sha256"' in workflow
    assert "unzip -q baoanskills-release.zip" in workflow
    assert 'python "$snapshot/scripts/install_skills.py" ctf-writeup --dest' in workflow
    assert 'test ! -e "$smoke_root/tampered"' in workflow


def test_mutable_action_reference_is_rejected(tmp_path: Path) -> None:
    workflow = tmp_path / "test.yml"
    workflow.write_text(
        "name: test\n"
        "on: push\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )
    errors = check_workflow(workflow)
    assert any("40-character commit SHA" in error for error in errors)
