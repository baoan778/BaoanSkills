from __future__ import annotations

import re
from pathlib import Path

from _skill_utils import publication_names

ROOT = Path(__file__).resolve().parents[1]
ROUTING = (ROOT / "docs" / "ROUTING.md").read_text(encoding="utf-8")
ROW_RE = re.compile(r"^\|\s*(?P<request>[^|]+?)\s*\|\s*`(?P<skill>[a-z0-9-]+)`\s*\|$", re.MULTILINE)


def route_rows() -> list[tuple[str, str]]:
    return [
        (match.group("request").strip(), match.group("skill"))
        for match in ROW_RE.finditer(ROUTING)
    ]


def route_map() -> dict[str, str]:
    return dict(route_rows())


def test_all_routed_skills_are_public() -> None:
    names = set(publication_names() or [])
    routed = set(route_map().values())
    assert routed
    assert routed == names


def test_key_disambiguation_routes() -> None:
    routes = route_map()
    assert routes["Binary exploitation, including 64-bit ELF"] == "ctf-pwn"
    assert routes["Local CTF corpus lookup"] == "ctf-knowledge-base"
    assert routes["GitHub Actions with AI agents"] == "agentic-actions-auditor"
    assert routes["Search or extract a Burp project"] == "burpsuite-project-parser"
    assert routes["Quick command or command reference lookup"] == "pentest-commands"
    assert routes["Workflow/deliverable checks or engagement checklist"] == "pentest-checklist"
    assert routes["Tool-selection index or red-team tooling overview"] == "red-team-tools"
    assert routes["Overall or broad engagement methodology"] == "ethical-hacking-methodology"


def test_routing_requests_and_destinations_are_unique() -> None:
    rows = route_rows()
    requests = [request for request, _ in rows]
    destinations = [destination for _, destination in rows]
    assert len(requests) == len(set(requests))
    assert len(destinations) == len(set(destinations))


def test_routing_requires_authorization() -> None:
    normalized = " ".join(ROUTING.split())
    assert "Confirm authorization before any active testing" in normalized
    assert "CTF-specific web skills are not a substitute" in ROUTING
    assert "Broad skills are not default execution entry points" in ROUTING
    assert "stop before any active testing" in ROUTING
    assert "broad methodology" in ROUTING.casefold()
