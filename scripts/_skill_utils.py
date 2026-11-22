from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9-]+$")
PUBLICATION_REL = Path("release") / "public-skills.txt"


@dataclass
class SkillDocument:
    directory: Path
    skill_file: Path
    frontmatter: dict[str, Any]
    body: str
    raw: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def skills_root() -> Path:
    return repo_root() / "skills"


def publication_file() -> Path:
    return repo_root() / PUBLICATION_REL


def publication_names() -> list[str] | None:
    """Return the public allowlist, or None when the repository is inventory-only."""
    path = publication_file()
    if not path.is_file():
        return None
    names: list[str] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


def is_release_scope_path(path: Path) -> bool:
    """Whether a repository path belongs to the publication payload.

    When an allowlist exists, unaudited sibling skill directories remain local
    staging material and are excluded from repository-wide release checks.
    """
    names = publication_names()
    if names is None:
        return True
    try:
        relative = path.resolve().relative_to(skills_root().resolve())
    except ValueError:
        return True
    if not relative.parts:
        return True
    first = relative.parts[0]
    return first == ".gitignore" or first in set(names)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def load_skill(skill_dir: Path) -> SkillDocument:
    skill_file = skill_dir / "SKILL.md"
    raw = read_text(skill_file)
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError("missing or malformed YAML frontmatter delimiters")
    try:
        # Keep the installer usable in a bare Python environment. Only the
        # scripts that parse skill metadata require the optional PyYAML dependency.
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to parse SKILL.md frontmatter") from exc
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a mapping")
    return SkillDocument(
        directory=skill_dir,
        skill_file=skill_file,
        frontmatter=frontmatter,
        body=raw[match.end():],
        raw=raw,
    )


def iter_skills(include_all: bool = False) -> list[Path]:
    root = skills_root()
    available = sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())
    names = publication_names()
    if include_all or names is None:
        return available
    by_name = {path.name: path for path in available}
    return [by_name.get(name, root / name) for name in names]


def metadata_of(frontmatter: dict[str, Any]) -> dict[str, Any]:
    metadata = frontmatter.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def normalized_license(frontmatter: dict[str, Any]) -> str:
    value = frontmatter.get("license")
    if value is None or not str(value).strip():
        return "NOASSERTION"
    return str(value).strip()


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(flatten(item) for item in value if item is not None)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {flatten(item)}" for key, item in value.items())
    return " ".join(str(value).split())
