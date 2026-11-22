---
name: scanning-tools
description: Choose and operate network, web, wireless, and vulnerability scanners for explicitly authorized assessments, including scope controls, safe defaults, result validation, and evidence capture.
license: MIT
allowed-tools:
- Bash
- Read
- Write
- Edit
- Glob
- Grep
- Task
- WebFetch
- WebSearch
metadata:
  risk: offensive
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/scanning-tools/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: tools-supply-chain
  tags:
  - network
  - scanning
  - vulnerability-assessment
  - tooling
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/scanning-tools/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Moved the detailed multi-tool command catalog and scanning methodology into a directly linked reference and condensed the entrypoint into scope, pilot, validation, evidence, and reporting guidance.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# Security Scanning Tools

## Purpose

Master essential security scanning tools for network discovery, vulnerability assessment, web application testing, wireless security, and compliance validation. This skill covers tool selection, configuration, and practical usage across different scanning categories.

## Prerequisites

### Required Environment
- Linux-based system (Kali Linux recommended)
- Network access to target systems
- Proper authorization for scanning activities

### Required Knowledge
- Basic networking concepts (TCP/IP, ports, protocols)
- Understanding of common vulnerabilities
- Familiarity with command-line interfaces

## Outputs and Deliverables

1. **Network Discovery Reports** - Identified hosts, ports, and services
2. **Vulnerability Assessment Reports** - CVEs, misconfigurations, risk ratings
3. **Web Application Security Reports** - OWASP Top 10 findings
4. **Compliance Reports** - CIS benchmarks, PCI-DSS, HIPAA checks

## Core Workflow

1. **Establish the assessment boundary.** Record the authorized targets, excluded assets, source addresses, permitted scan classes, time window, rate limits, and emergency stop contact. Do not treat a discovered host as in scope.
2. **Choose the least intrusive tool.** Read [assessment-playbook.md](references/assessment-playbook.md) for the full network, vulnerability, web, wireless, malware, cloud, and compliance tool catalog. Start with passive discovery or a small bounded scan, then escalate only when the previous result justifies it.
3. **Run a narrow pilot.** Confirm one target and one port or URL before expanding. Capture the exact command, tool version, start time, source address, and output path.
4. **Validate before escalating.** Correlate scanner output with manual evidence, remove false positives, and distinguish exposure from exploitability. Stop if the scan affects availability, crosses scope, or produces unexpected third-party traffic.
5. **Preserve evidence.** Keep raw output, normalized findings, hashes of evidence files, and a chronology. Do not overwrite or silently edit raw scanner output.
6. **Report and remediate.** Prioritize by validated impact and exploitation preconditions; include affected asset, evidence, root cause, remediation, retest criteria, and residual uncertainty.

### Tool routes

| Assessment need | Typical starting point |
|---|---|
| Host and service discovery | Nmap or Masscan after rate and scope approval |
| Broad vulnerability inventory | Nessus or OpenVAS with credentials only when authorized |
| Web application coverage | Burp Suite or OWASP ZAP, with Nikto as a supplementary server check |
| Wireless assessment | Passive Kismet first; active capture only on owned spectrum and hardware |
| Malware or local file inspection | ClamAV plus separate static analysis |
| Cloud configuration review | Prowler or ScoutSuite using read-only credentials |
| Host hardening or compliance | Lynis or OpenSCAP with a defined benchmark |

### Stop conditions

Stop and ask the owner before continuing when a scan reaches a shared or third-party service, causes errors or latency, triggers an unexpected defensive response, exceeds the approved rate, or cannot be validated without an intrusive test.

## Quick Reference

### Nmap Cheat Sheet

| Scan Type | Command |
|-----------|---------|
| Ping Scan | `nmap -sn <target>` |
| Quick Scan | `nmap -T4 -F <target>` |
| Full Scan | `nmap -p- <target>` |
| Service Scan | `nmap -sV <target>` |
| OS Detection | `nmap -O <target>` |
| Aggressive | `nmap -A <target>` |
| Vuln Scripts | `nmap --script=vuln <target>` |
| Stealth Scan | `nmap -sS -T2 <target>` |

### Common Ports Reference

| Port | Service |
|------|---------|
| 21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 445 | SMB |
| 3306 | MySQL |
| 3389 | RDP |

## Constraints and Limitations

### Legal Considerations
- Always obtain written authorization
- Respect scope boundaries
- Follow responsible disclosure practices
- Comply with local laws and regulations

### Technical Limitations
- Some scans may trigger IDS/IPS alerts
- Heavy scanning can impact network performance
- False positives require manual verification
- Encrypted traffic may limit analysis

### Best Practices
- Start with non-intrusive scans
- Gradually increase scan intensity
- Document all scanning activities
- Validate findings before reporting

## Troubleshooting

### Scan Not Detecting Hosts

**Solutions:**
1. Try different discovery methods: `nmap -Pn` or `nmap -sn -PS/PA/PU`
2. Check firewall rules blocking ICMP
3. Use TCP SYN scan: `nmap -PS22,80,443`
4. Verify network connectivity

### Slow Scan Performance

**Solutions:**
1. Increase timing: `nmap -T4` or `-T5`
2. Reduce port range: `--top-ports 100`
3. Use Masscan for initial discovery
4. Disable DNS resolution: `-n`

### Web Scanner Missing Vulnerabilities

**Solutions:**
1. Authenticate to access protected areas
2. Increase crawl depth
3. Add custom injection points
4. Use multiple tools for coverage
5. Perform manual testing

## When to Use
Use this skill to select, configure, and validate network, web, wireless, cloud, or compliance scanners during an explicitly authorized assessment. It is a good fit when the target and scope are known but the safest scanner and escalation path still need to be chosen.

Do not use it to justify scanning an unknown public target, to run destructive or high-volume checks without explicit approval, or when a more focused skill already governs the specific vulnerability or platform.
