---
name: windows-privilege-escalation
description: Enumerate and validate Windows privilege escalation paths on explicitly authorized hosts, covering tokens, services, scheduled tasks, ACLs, credentials, and local misconfigurations.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/windows-privilege-escalation/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: cloud-identity-infrastructure
  tags:
  - windows
  - privilege-escalation
  - post-exploitation
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/windows-privilege-escalation/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> AUTHORIZED USE ONLY: Use this skill only for authorized security assessments, defensive validation, or controlled educational environments.

# Windows Privilege Escalation

## Purpose

Provide systematic methodologies for discovering and exploiting privilege escalation vulnerabilities on Windows systems during penetration testing engagements. This skill covers system enumeration, credential harvesting, service exploitation, token impersonation, kernel exploits, and various misconfigurations that enable escalation from standard user to Administrator or SYSTEM privileges.

## Inputs / Prerequisites

- **Initial Access**: Shell or RDP access as standard user on Windows system
- **Enumeration Tools**: WinPEAS, PowerUp, Seatbelt, or manual commands
- **Exploit Binaries**: Pre-compiled exploits or ability to transfer tools
- **Knowledge**: Understanding of Windows security model and privileges
- **Authorization**: Written permission for penetration testing activities

## Outputs / Deliverables

- **Privilege Escalation Path**: Identified vector to higher privileges
- **Credential Dump**: Harvested passwords, hashes, or tokens
- **Elevated Shell**: Command execution as Administrator or SYSTEM
- **Vulnerability Report**: Documentation of misconfigurations and exploits
- **Remediation Recommendations**: Fixes for identified weaknesses

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Operational Boundaries
- Kernel exploits may cause system instability
- Some exploits require specific Windows versions
- AV/EDR may detect and block common tools
- Token impersonation requires service account context
- Some techniques require GUI access

### Detection Considerations
- Credential dumping triggers security alerts
- Service modification logged in Event Logs
- PowerShell execution may be monitored
- Known exploit signatures detected by AV

### Legal Requirements
- Only test systems with written authorization
- Document all escalation attempts
- Avoid disrupting production systems
- Report all findings through proper channels

## When to Use
Use this skill when the task matches its reviewed scope: Enumerate and validate Windows privilege escalation paths on explicitly authorized hosts, covering tokens, services, scheduled tasks, ACLs, credentials, and local misconfigurations.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
