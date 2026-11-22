---
name: wireshark-analysis
description: Analyze packet captures with Wireshark and tshark for explicitly authorized investigations, including protocol filtering, traffic reconstruction, credential exposure, and evidence capture.
license: MIT
allowed-tools:
- Bash
- Read
- Write
- Edit
- Glob
- Grep
metadata:
  risk: offensive
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/wireshark-analysis/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: reverse-forensics-malware
  tags:
  - network
  - pcap
  - wireshark
  - forensics
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/wireshark-analysis/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# Wireshark Network Traffic Analysis

## Purpose

Execute comprehensive network traffic analysis using Wireshark to capture, filter, and examine network packets for security investigations, performance optimization, and troubleshooting. This skill enables systematic analysis of network protocols, detection of anomalies, and reconstruction of network conversations from PCAP files.

## Inputs / Prerequisites

### Required Tools
- Wireshark installed (Windows, macOS, or Linux)
- Network interface with capture permissions
- PCAP/PCAPNG files for offline analysis
- Administrator/root privileges for live capture

### Technical Requirements
- Understanding of network protocols (TCP, UDP, HTTP, DNS)
- Familiarity with IP addressing and ports
- Knowledge of OSI model layers
- Understanding of common attack patterns

### Use Cases
- Network troubleshooting and connectivity issues
- Security incident investigation
- Malware traffic analysis
- Performance monitoring and optimization
- Protocol learning and education

## Outputs / Deliverables

### Primary Outputs
- Filtered packet captures for specific traffic
- Reconstructed communication streams
- Traffic statistics and visualizations
- Evidence documentation for incidents

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Guardrails

### Operational Boundaries
- Capture only authorized network traffic
- Handle captured data according to privacy policies
- Avoid capturing sensitive credentials unnecessarily
- Properly secure PCAP files containing sensitive data

### Technical Limitations
- Large captures consume significant memory
- Encrypted traffic content not visible without keys
- High-speed networks may drop packets
- Some protocols require plugins for full decoding

### Best Practices
- Use capture filters to limit data collection
- Save captures regularly during long sessions
- Use display filters rather than deleting packets
- Document analysis findings and methodology

## When to Use
Use this skill when the task matches its reviewed scope: Analyze packet captures with Wireshark and tshark for explicitly authorized investigations, including protocol filtering, traffic reconstruction, credential exposure, and evidence capture.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
