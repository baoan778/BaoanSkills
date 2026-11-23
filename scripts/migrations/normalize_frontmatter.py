#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n)?", re.DOTALL)
ALLOWED = {"name", "description", "license", "allowed-tools", "metadata"}


def family_slug(name: str) -> str:
    if "local-kb" in name or "local-knowledge-base" in name:
        return "local-knowledge-base"
    if name.startswith("ctf-") or name == "solve-challenge":
        return "ctf"
    if name.startswith("src-") or name in {"ldsk-src", "cnvd-src-reporting", "auto-specialty-routing-score"}:
        return "src-bounty"
    if any(token in name for token in ("aws", "azure", "gcp", "cloud", "k8s", "container", "active-directory", "mtls", "ssh-penetration", "privilege-escalation")):
        return "cloud-identity-infrastructure"
    if any(token in name for token in ("reverse", "forensic", "malware", "firmware", "binary", "gdb", "wireshark", "memory-", "protocol-", "anti-reversing", "constant-time", "zeroize", "js-reverse")):
        return "reverse-forensics-malware"
    if any(token in name for token in ("compliance", "privacy", "gdpr", "pci", "security-requirement", "security-career", "security-bluebook", "threat-", "attack-tree", "stride-")):
        return "compliance-governance"
    if any(token in name for token in ("ffuf", "burp", "semgrep", "metasploit", "shodan", "scanning", "vulnerability-scanner", "supply-chain", "protect-mcp", "sast", "secrets-management")):
        return "tools-supply-chain"
    if name in {"007", "audit-skills", "langgpt", "combat-learning-value-refiner", "adhx", "aegisops-ai", "cred-omega"}:
        return "meta-workflow"
    return "application-security"


def normalize_tags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [value]


def normalize(path: Path) -> tuple[str, dict, list[str]]:
    raw = path.read_text(encoding="utf-8-sig")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError("missing frontmatter")
    fm = yaml.safe_load(match.group(1))
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a mapping")
    body = raw[match.end():].lstrip("\r\n")
    metadata = fm.get("metadata")
    metadata = dict(metadata) if isinstance(metadata, dict) else {}
    conflicts: list[str] = []

    for key, value in list(fm.items()):
        if key in ALLOWED:
            continue
        fm.pop(key)
        if key in metadata and metadata[key] != value:
            conflicts.append(f"{path.parent.name}: {key}: kept metadata value {metadata[key]!r}, dropped top-level {value!r}")
        else:
            metadata[key] = value

    license_value = fm.get("license")
    if not isinstance(license_value, str) or not license_value.strip():
        license_value = "NOASSERTION"
    license_value = license_value.strip()

    author = metadata.get("author")
    if not isinstance(author, str) or not author.strip():
        metadata["author"] = "unknown"
    source = metadata.get("source")
    if not isinstance(source, str) or not source.strip():
        metadata["source"] = "unknown"
    category = metadata.get("category")
    if not isinstance(category, str) or not category.strip():
        metadata["category"] = family_slug(path.parent.name)
    risk = metadata.get("risk")
    if not isinstance(risk, str) or not risk.strip():
        metadata["risk"] = "unknown"
    metadata["tags"] = normalize_tags(metadata.get("tags"))

    if license_value == "NOASSERTION":
        metadata["license_status"] = "unverified"
        metadata["provenance_status"] = "review-required"
    else:
        metadata["license_status"] = "declared"
        metadata["provenance_status"] = "declared"
    if metadata["author"] == "unknown" or metadata["source"] == "unknown":
        metadata["provenance_status"] = "review-required"

    ordered = {
        "name": fm.get("name", path.parent.name),
        "description": fm.get("description", ""),
        "license": license_value,
    }
    if "allowed-tools" in fm:
        ordered["allowed-tools"] = fm["allowed-tools"]
    ordered["metadata"] = metadata

    dumped = yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False, width=1000)
    normalized = "---\n" + dumped + "---\n\n" + body
    return normalized, ordered, conflicts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path, default=ROOT / "reports" / "frontmatter-migration-report.json")
    args = parser.parse_args()
    changed = 0
    failures = 0
    conflicts: list[str] = []
    for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()):
        try:
            normalized, _, skill_conflicts = normalize(skill_dir / "SKILL.md")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {skill_dir.name}: {exc}")
            continue
        conflicts.extend(skill_conflicts)
        if normalized != (skill_dir / "SKILL.md").read_text(encoding="utf-8-sig"):
            changed += 1
        if args.write:
            (skill_dir / "SKILL.md").write_text(normalized, encoding="utf-8", newline="\n")
    report = {
        "skills_changed": changed,
        "failures": failures,
        "conflicts": conflicts,
    }
    if args.write:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    mode = "updated" if args.write else "would update"
    print(f"{mode} {changed} skills; failures: {failures}; metadata conflicts: {len(conflicts)}")
    for conflict in conflicts:
        print(f"CONFLICT {conflict}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
