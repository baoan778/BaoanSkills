from __future__ import annotations

from _skill_utils import iter_skills


def test_ctf_topic_documents_live_under_references() -> None:
    ctf_skills = [path for path in iter_skills() if path.name.startswith("ctf-")]
    assert len(ctf_skills) == 11
    for skill in ctf_skills:
        root_topics = sorted(path.name for path in skill.glob("*.md") if path.name != "SKILL.md")
        assert root_topics == [], f"{skill.name} has root-level topic documents: {root_topics}"


def test_core_ctf_skills_have_reference_material() -> None:
    expected = {
        "ctf-ai-ml": 3,
        "ctf-crypto": 16,
        "ctf-forensics": 14,
        "ctf-malware": 3,
        "ctf-misc": 13,
        "ctf-osint": 3,
        "ctf-pwn": 18,
        "ctf-reverse": 18,
        "ctf-web": 20,
    }
    by_name = {path.name: path for path in iter_skills()}
    for name, count in expected.items():
        assert len(list((by_name[name] / "references").glob("*.md"))) == count
