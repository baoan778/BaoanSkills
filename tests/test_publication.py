from __future__ import annotations

import copy
import json
from pathlib import Path

from check_publication import compare_lock, has_non_lf_line_endings, skill_files
from check_whitespace import findings, normalize

ROOT = Path(__file__).resolve().parents[1]


def test_skill_files_use_platform_independent_posix_order(tmp_path: Path) -> None:
    skill = tmp_path / "demo-skill"
    (skill / "agents").mkdir(parents=True)
    (skill / "references").mkdir()
    (skill / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
    (skill / "agents" / "openai.yaml").write_text("name: demo\n", encoding="utf-8")
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")

    relative = [path.relative_to(skill).as_posix() for path in skill_files(skill)]

    assert relative == ["SKILL.md", "agents/openai.yaml", "references/guide.md"]


def test_provenance_lock_uses_canonical_file_order() -> None:
    lock = json.loads((ROOT / "release" / "provenance.lock.json").read_text(encoding="utf-8"))

    for name, entry in lock["skills"].items():
        paths = [item["path"] for item in entry["files"]]
        assert paths == sorted(paths), f"{name} has a non-canonical file order"


def test_compare_lock_reports_actionable_entry_drift() -> None:
    expected = {
        "schema_version": 1,
        "selection": "release/public-skills.txt",
        "skills": {
            "demo-skill": {
                "author": "Example",
                "files": [
                    {"path": "SKILL.md", "sha256": "a", "bytes": 1},
                    {"path": "agents/openai.yaml", "sha256": "b", "bytes": 2},
                ],
            }
        },
    }
    actual = copy.deepcopy(expected)
    actual["skills"]["demo-skill"]["author"] = "Changed"
    actual["skills"]["demo-skill"]["files"].reverse()
    actual["skills"]["demo-skill"]["files"][1]["sha256"] = "changed"

    errors = compare_lock(actual, expected)

    assert any("field 'author'" in error for error in errors)
    assert any("file metadata changed: SKILL.md" in error for error in errors)
    assert any("canonical file order changed" in error for error in errors)


def test_crlf_and_lone_cr_are_rejected(tmp_path: Path) -> None:
    crlf = tmp_path / "crlf.md"
    crlf.write_bytes(b"# Heading\r\n\r\nBody\r\n")
    lone_cr = tmp_path / "lone-cr.md"
    lone_cr.write_bytes(b"# Heading\rBody\r")
    lf = tmp_path / "lf.md"
    lf.write_bytes(b"# Heading\n\nBody\n")

    assert has_non_lf_line_endings(crlf)
    assert has_non_lf_line_endings(lone_cr)
    assert not has_non_lf_line_endings(lf)
    crlf_text = crlf.read_bytes().decode("utf-8")
    assert any("line endings" in message for _, message in findings(crlf, crlf_text))
    assert "\r" not in normalize(crlf_text)
