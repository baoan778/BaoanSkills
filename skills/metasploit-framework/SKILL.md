---
name: metasploit-framework
description: Use Metasploit Framework for explicitly authorized assessments, including module selection, target validation, payload configuration, session handling, and evidence capture.
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
  risk: high
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/metasploit-framework/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: tools-supply-chain
  tags:
  - tooling
  - metasploit
  - exploitation
  - payload
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/metasploit-framework/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

# Metasploit Framework

> **⚠️ AUTHORIZED USE ONLY**
> This skill is for educational purposes or authorized security assessments only.
> You must have explicit, written permission from the system owner before using this tool.
> Misuse of this tool is illegal and strictly prohibited.

## Purpose

Leverage the Metasploit Framework for comprehensive penetration testing, from initial exploitation through post-exploitation activities. Metasploit provides a unified platform for vulnerability exploitation, payload generation, auxiliary scanning, and maintaining access to compromised systems during authorized security assessments.

## Prerequisites

### Required Tools
```bash
# Metasploit must already be installed before using this skill.
# Kali Linux usually ships with it preinstalled.
msfconsole --version
```

Installation varies by operating system and package source. Follow your platform's documented package-manager or vendor installation process before using this skill. Do not rely on an unpinned remote installer script from inside this skill.

If you want database-backed features such as workspace tracking, initialize `msfdb` using the instructions for your local installation. This skill assumes Metasploit is already available and does not require `sudo`, `systemctl`, or other privileged host-level setup steps.

### Required Knowledge
- Network and system fundamentals
- Understanding of vulnerabilities and exploits
- Basic programming concepts
- Target enumeration techniques

### Required Access
- Written authorization for testing
- Network access to target systems
- Understanding of scope and rules of engagement

Before running exploit modules, ask the user to confirm the exact target host, scope, and authorization state.

## Outputs and Deliverables

1. **Exploitation Evidence** - Screenshots and logs of successful compromises
2. **Session Logs** - Command history and extracted data
3. **Vulnerability Mapping** - Exploited vulnerabilities with CVE references
4. **Post-Exploitation Artifacts** - Credentials, files, and system information

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Legal Requirements
- Only use on systems you own or have written authorization to test
- Document all testing activities
- Follow rules of engagement
- Report all findings to appropriate parties

### Technical Limitations
- Modern AV/EDR may detect Metasploit payloads
- Some exploits require specific target configurations
- Firewall rules may block reverse connections
- Not all exploits work on all target versions

### Operational Security
- Use encrypted channels (reverse_https) when possible
- Clean up artifacts after testing
- Avoid detection by monitoring systems
- Limit post-exploitation to agreed scope

## When to Use
Use this skill when the task matches its reviewed scope: Use Metasploit Framework for explicitly authorized assessments, including module selection, target validation, payload configuration, session handling, and evidence capture.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
