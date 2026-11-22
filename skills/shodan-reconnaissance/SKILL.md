---
name: shodan-reconnaissance
description: Use Shodan to map an explicitly authorized organization's internet exposure, identify services and versions, and pivot into validated reconnaissance without treating search results as permission to test.
license: MIT
allowed-tools:
- Bash
- Read
- Write
- Edit
- Glob
- Grep
- WebFetch
- WebSearch
metadata:
  risk: offensive
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/shodan-reconnaissance/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: tools-supply-chain
  tags:
  - reconnaissance
  - shodan
  - osint
  - exposure
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/shodan-reconnaissance/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# Shodan Reconnaissance and Pentesting

## Purpose

Provide systematic methodologies for leveraging Shodan as a reconnaissance tool during penetration testing engagements. This skill covers the Shodan web interface, command-line interface (CLI), REST API, search filters, on-demand scanning, and network monitoring capabilities for discovering exposed services, vulnerable systems, and IoT devices.

## Inputs / Prerequisites

- **Shodan Account**: Free or paid account at shodan.io
- **API Key**: Obtained from Shodan account dashboard
- **Target Information**: IP addresses, domains, or network ranges to investigate
- **Shodan CLI**: Python-based command-line tool installed
- **Authorization**: Written permission for reconnaissance on target networks

## Outputs / Deliverables

- **Asset Inventory**: List of discovered hosts, ports, and services
- **Vulnerability Report**: Identified CVEs and exposed vulnerable services
- **Banner Data**: Service banners revealing software versions
- **Network Mapping**: Geographic and organizational distribution of assets
- **Screenshot Gallery**: Visual reconnaissance of exposed interfaces
- **Exported Data**: JSON/CSV files for further analysis

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Operational Boundaries
- Rate limited to 1 request per second
- Scan results not immediate (asynchronous)
- Cannot re-scan same IP within 24 hours (non-Enterprise)
- Free accounts have limited credits
- Some data requires paid subscription

### Data Freshness
- Shodan crawls continuously but data may be days/weeks old
- On-demand scans provide current data but cost credits
- Historical data available with paid plans

### Legal Requirements
- Only perform reconnaissance on authorized targets
- Passive reconnaissance generally legal but verify jurisdiction
- Active scanning (scan submit) requires authorization
- Document all reconnaissance activities

## When to Use
Use this skill when the task matches its reviewed scope: Use Shodan to map an explicitly authorized organization's internet exposure, identify services and versions, and pivot into validated reconnaissance without treating search results as permission to test.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
