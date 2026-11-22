#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from _skill_utils import is_release_scope_path, repo_root

# Paths that a skill promises to ship with it. Both component directories and
# executable helpers are included. Bare ``assets/`` references are accepted only
# when explicitly marked as bundled resources (see ``is_resource_declaration``).
RESOURCE_ROOTS = (
    "references",
    "scripts",
    "assets",
    "agents",
    "resources",
    "schemas",
    "tools",
    "configs",
    "prompts",
    "workflows",
    "ct_analyzer",
)
# In fenced code blocks, only these roots are checked unless the path uses the
# explicit ``{baseDir}`` prefix. This catches wrapper/tool invocations without
# treating target-project paths such as ``assets/app.asar`` as bundled files.
FENCED_CODE_ROOTS = {"scripts", "tools", "ct_analyzer"}
IGNORED_PARTS = {".git", "CTF本地知识库", "__pycache__", ".venv", "node_modules"}
RESOURCE_RE = re.compile(
    r"(?<![\w./\\-])(?P<base>\{baseDir\}/)?"
    r"(?P<root>" + "|".join(map(re.escape, RESOURCE_ROOTS)) + r")/"
    r"(?P<rest>[A-Za-z0-9_.@+/\-]+)"
)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "codex://", "#")
GOVERNANCE_DOCUMENTS = {"skill.md", "readme.md", "contributing.md", "security.md", "changelog.md"}
REFERENCE_CUE_RE = re.compile(
    r"(?i)\b(?:see|read|open|refer(?:ring)?\s+to|load|consult|check|follow)\b"
)
BARE_MD_RE = re.compile(
    r"(?<![\w./\\-])(?P<token>[A-Za-z0-9_@+-]+(?:\.[A-Za-z0-9_@+-]+)*\.md)"
    r"(?![A-Za-z0-9_/\\-])(?!\.[A-Za-z0-9])"
)
SKILL_MENTION_RE = re.compile(
    r"(?<![\w-])(?:/|in\s+)(?P<skill>[a-z0-9]+(?:-[a-z0-9]+)*)(?![\w-])"
)


@dataclass(frozen=True)
class Reference:
    token: str
    explicit_base: bool
    is_link: bool

    @property
    def root(self) -> str:
        return self.token.split("/", 1)[0]


def candidate_files(root: Path) -> list[Path]:
    skills_root = root / "skills"
    return sorted(
        path
        for path in skills_root.rglob("*.md")
        if not any(part in IGNORED_PARTS for part in path.parts)
        and is_release_scope_path(path)
    )


def skill_root_for(path: Path) -> Path | None:
    for parent in path.parents:
        if (parent / "SKILL.md").is_file():
            return parent
    return None


def trim_token(token: str) -> str:
    token = token.rstrip(".,:;)]}")
    if token.endswith("**"):
        token = token[:-2]
    return token


def looks_like_markup_or_variable(token: str) -> bool:
    return any(char in token for char in ("<", ">", "{", "}", "$", "`", '"', "'"))


def is_resource_declaration(line: str, match: re.Match[str]) -> bool:
    """Return whether a bare assets path is declared as a bundled file.

    CTF and tooling guides often mention paths inside a target application
    (for example ``assets/bin/Data/...``). Those are not files that this skill
    ships. A bundled asset must use ``{baseDir}/assets/...``, a Markdown link,
    or the conventional bold resource-list form ``**assets/file**``.
    """

    if match.group("base") or match.group("root") != "assets":
        return True
    before = line[max(0, match.start() - 2) : match.start()]
    after = line[match.end() : match.end() + 2]
    return before == "**" or after == "**"


def links_in(line: str) -> list[str]:
    targets: list[str] = []
    for match in LINK_RE.finditer(line):
        raw = match.group(1).strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        if not raw or raw.startswith(SKIP_LINK_PREFIXES):
            continue
        if " " in raw:
            raw = raw.split(" ", 1)[0]
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc:
            continue
        path = unquote(parsed.path)
        if not path or path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", path):
            continue
        targets.append(path)
    return targets


def mask_markdown_links(line: str) -> str:
    """Replace Markdown links with spaces so bare filenames can be checked separately."""
    return LINK_RE.sub(lambda match: " " * len(match.group(0)), line)


def bare_markdown_tokens(line: str) -> list[str]:
    """Find prose references to Markdown files that are not explicit links.

    The resource scanner historically only checked paths that start with a known
    resource directory or that appear as Markdown links.  That missed prose such
    as ``see quick-reference.md``.  Keep this intentionally narrow: only inspect
    lines with a reference cue and ignore governance documents and path-like
    mentions, which are handled by the regular link/resource scanners.
    """
    masked = mask_markdown_links(line)
    if not REFERENCE_CUE_RE.search(masked):
        return []
    tokens: list[str] = []
    for match in BARE_MD_RE.finditer(masked):
        token = match.group("token")
        if token.casefold() in GOVERNANCE_DOCUMENTS:
            continue
        tokens.append(token)
    return tokens


def bare_markdown_candidates(
    md_file: Path,
    skill_root: Path,
    token: str,
    line: str,
    root: Path,
) -> list[Path]:
    """Return safe candidate locations for a bare Markdown filename reference."""
    candidates = [
        (md_file.parent / token).resolve(strict=False),
        (skill_root / token).resolve(strict=False),
        (skill_root / "references" / token).resolve(strict=False),
    ]
    for match in SKILL_MENTION_RE.finditer(line):
        other_skill = match.group("skill")
        candidates.extend(
            [
                (root / "skills" / other_skill / token).resolve(strict=False),
                (root / "skills" / other_skill / "references" / token).resolve(strict=False),
            ]
        )
    return [path for path in candidates if path_within(path, root)]


def missing_bare_markdown_references(
    md_file: Path,
    skill_root: Path,
    line: str,
    root: Path,
) -> list[str]:
    """Return bare Markdown filenames that cannot be resolved from this context."""
    tokens = bare_markdown_tokens(line)
    missing: list[str] = []
    for token in tokens:
        candidates = bare_markdown_candidates(md_file, skill_root, token, line, root)
        if not any(exists_case_sensitive(path, root) for path in candidates):
            missing.append(token)
    return missing


def scan_line(line: str, *, in_fence: bool) -> list[Reference]:
    refs: list[Reference] = []
    seen: set[tuple[str, bool, bool]] = set()

    stripped = line.lstrip()
    is_comment = in_fence and (stripped.startswith("#") or stripped.startswith("//"))
    if not is_comment:
        for match in RESOURCE_RE.finditer(line):
            explicit = bool(match.group("base"))
            # A match immediately followed by a shell brace or glob marker is a
            # template such as ``references/vector-{a..i}-*.md``, not a concrete
            # file reference.
            following = line[match.end() : match.end() + 2]
            if following[:1] in {"{", "}"} or (
                following[:1] in {"*", "?"} and following != "**"
            ):
                continue
            raw = trim_token(match.group(0))
            check_token = raw.removeprefix("{baseDir}/")
            if looks_like_markup_or_variable(check_token) or "*" in check_token or "?" in check_token:
                continue
            if in_fence and not explicit and match.group("root") not in FENCED_CODE_ROOTS:
                continue
            if not in_fence and not is_resource_declaration(line, match):
                continue
            key = (raw, explicit, False)
            if key not in seen:
                seen.add(key)
                refs.append(Reference(raw, explicit, False))

    # Parenthesised OSM expressions such as ``(area.searchArea)`` look like
    # Markdown links if the scanner ignores fenced-code context.
    if in_fence:
        return refs

    for target in links_in(line):
        token = trim_token(target)
        while token.startswith("./"):
            token = token[2:]
        if not token or looks_like_markup_or_variable(token) or "*" in token:
            continue
        key = (token, False, True)
        if key not in seen:
            seen.add(key)
            refs.append(Reference(token, False, True))
    return refs


def path_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def exists_case_sensitive(path: Path, root: Path) -> bool:
    """Check a path without relying on Windows' case-insensitive filesystem."""

    resolved = path.resolve(strict=False)
    if not path_within(resolved, root):
        return False
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in relative.parts:
        if not current.is_dir():
            return False
        if not any(child.name == part for child in current.iterdir()):
            return False
        current = current / part
    return current.exists()


def main() -> int:
    root = repo_root().resolve()
    files = candidate_files(root)
    missing: list[tuple[Path, int, str]] = []
    bare_missing: list[tuple[Path, int, str]] = []
    invalid: list[tuple[Path, int, str]] = []
    checked = 0
    bare_checked = 0
    skipped = 0

    for md_file in files:
        skill_root = skill_root_for(md_file) or md_file.parent
        in_fence = False
        fence_char = ""
        fence_length = 0
        for line_number, line in enumerate(md_file.read_text(encoding="utf-8-sig").splitlines(), start=1):
            fence = FENCE_RE.match(line)
            if fence:
                marker = fence.group(1)
                if not in_fence:
                    in_fence = True
                    fence_char = marker[0]
                    fence_length = len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_length:
                    in_fence = False
                continue

            for ref in scan_line(line, in_fence=in_fence):
                if "*" in ref.token or "?" in ref.token:
                    skipped += 1
                    continue
                if ref.explicit_base:
                    relative_token = ref.token.removeprefix("{baseDir}/")
                    candidates = [(skill_root / relative_token).resolve(strict=False)]
                elif ref.is_link:
                    candidates = [
                        (md_file.parent / ref.token).resolve(strict=False),
                        (skill_root / ref.token).resolve(strict=False),
                    ]
                else:
                    candidates = [
                        (skill_root / ref.token).resolve(strict=False),
                        (md_file.parent / ref.token).resolve(strict=False),
                        (root / ref.token).resolve(strict=False),
                    ]
                checked += 1
                safe_candidates = [path for path in candidates if path_within(path, root)]
                if not safe_candidates:
                    invalid.append((md_file.relative_to(root), line_number, ref.token))
                elif not any(exists_case_sensitive(path, root) for path in safe_candidates):
                    missing.append((md_file.relative_to(root), line_number, ref.token))

            if not in_fence:
                tokens = bare_markdown_tokens(line)
                bare_checked += len(tokens)
                for token in missing_bare_markdown_references(md_file, skill_root, line, root):
                    bare_missing.append((md_file.relative_to(root), line_number, token))

    for file_path, line_number, token in invalid:
        print(f"INVALID {file_path}:{line_number} -> {token} (outside repository)")
    for file_path, line_number, token in missing:
        print(f"MISSING {file_path}:{line_number} -> {token}")
    for file_path, line_number, token in bare_missing:
        print(f"MISSING_BARE {file_path}:{line_number} -> {token}")
    print(
        f"checked {checked} resource references and {bare_checked} bare Markdown references "
        f"in {len(files)} Markdown files; missing: {len(missing)}; "
        f"missing bare: {len(bare_missing)}; invalid: {len(invalid)}; "
        f"skipped wildcard/template: {skipped}"
    )
    return 1 if missing or bare_missing or invalid else 0


if __name__ == "__main__":
    sys.exit(main())
