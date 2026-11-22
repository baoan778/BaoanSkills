---
name: linux-privilege-escalation
description: Enumerate and validate Linux privilege escalation paths on explicitly authorized hosts, covering sudo, SUID, capabilities, cron, services, credentials, containers, and kernel exposure.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/linux-privilege-escalation/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: cloud-identity-infrastructure
  tags:
  - linux
  - privilege-escalation
  - post-exploitation
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/linux-privilege-escalation/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> AUTHORIZED USE ONLY: Use this skill only for authorized security assessments, defensive validation, or controlled educational environments.

<!-- security-allowlist: curl-pipe-bash -->

# Linux Privilege Escalation

## Purpose

Execute systematic privilege escalation assessments on Linux systems to identify and exploit misconfigurations, vulnerable services, and security weaknesses that allow elevation from low-privilege user access to root-level control. This skill enables comprehensive enumeration and exploitation of kernel vulnerabilities, sudo misconfigurations, SUID binaries, cron jobs, capabilities, PATH hijacking, and NFS weaknesses.

## Inputs / Prerequisites

### Required Access
- Low-privilege shell access to target Linux system
- Ability to execute commands (interactive or semi-interactive shell)
- Network access for reverse shell connections (if needed)
- Attacker machine for payload hosting and receiving shells

### Technical Requirements
- Understanding of Linux filesystem permissions and ownership
- Familiarity with common Linux utilities and scripting
- Knowledge of kernel versions and associated vulnerabilities
- Basic understanding of compilation (gcc) for custom exploits

### Recommended Tools
- LinPEAS, LinEnum, or Linux Smart Enumeration scripts
- Linux Exploit Suggester (LES)
- GTFOBins reference for binary exploitation
- John the Ripper or Hashcat for password cracking
- Netcat or similar for reverse shells

## Outputs / Deliverables

### Primary Outputs
- Root shell access on target system
- Privilege escalation path documentation
- System enumeration findings report
- Recommendations for remediation

### Evidence Artifacts
- Screenshots of successful privilege escalation
- Command output logs demonstrating root access
- Identified vulnerability details
- Exploited configuration files

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Guardrails

### Operational Boundaries
- Verify kernel exploits in test environment before production use
- Failed kernel exploits may crash the system
- Document all changes made during privilege escalation
- Maintain access persistence only as authorized

### Technical Limitations
- Modern kernels may have exploit mitigations (ASLR, SMEP, SMAP)
- AppArmor/SELinux may restrict exploitation techniques
- Container environments limit kernel-level exploits
- Hardened systems may have restricted sudo configurations

### Legal and Ethical Requirements
- Written authorization required before testing
- Stay within defined scope boundaries
- Report critical findings immediately
- Do not access data beyond scope requirements

## When to Use
Use this skill when the task matches its reviewed scope: Enumerate and validate Linux privilege escalation paths on explicitly authorized hosts, covering sudo, SUID, capabilities, cron, services, credentials, containers, and kernel exposure.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
