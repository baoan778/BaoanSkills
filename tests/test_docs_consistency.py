from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from _skill_utils import iter_skills, load_skill, metadata_of, publication_names

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
GROUP_ROW_RE = re.compile(r"^\| (?P<group>[^|]+?) \| (?P<count>\d+) \|", re.MULTILINE)


def readme_group_counts() -> dict[str, int]:
    return {
        match.group("group").strip(): int(match.group("count"))
        for match in GROUP_ROW_RE.finditer(README)
    }


def test_readme_headline_count_matches_public_allowlist() -> None:
    match = re.search(r"collection of (\d+) security skills", README)
    assert match is not None
    assert int(match.group(1)) == len(publication_names() or [])


def test_readme_origin_group_counts_match_metadata() -> None:
    origin_counts: Counter[str] = Counter()
    for skill_dir in iter_skills():
        metadata = metadata_of(load_skill(skill_dir).frontmatter)
        source_repo = str(metadata.get("source_repo", ""))
        if source_repo.endswith("zebbern/claude-code-guide"):
            origin_counts["Authorized security testing"] += 1
        elif source_repo.endswith("trailofbits/skills"):
            origin_counts["Security auditing tools"] += 1
        else:
            origin_counts["Original CTF workflows"] += 1

    assert readme_group_counts() == {
        "Original CTF workflows": origin_counts["Original CTF workflows"],
        "Authorized security testing": origin_counts["Authorized security testing"],
        "Security auditing tools": origin_counts["Security auditing tools"],
    }
