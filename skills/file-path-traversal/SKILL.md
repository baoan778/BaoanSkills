---
name: file-path-traversal
description: Identify, validate, and explain file path traversal vulnerabilities in explicitly authorized applications, including encoding bypasses, absolute paths, and restricted-file-read impact.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/file-path-traversal/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: application-security
  tags:
  - web
  - path-traversal
  - file-read
  - owasp
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/file-path-traversal/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> AUTHORIZED USE ONLY: Use this skill only for authorized security assessments, defensive validation, or controlled educational environments.

# File Path Traversal Testing

## Purpose

Identify and exploit file path traversal (directory traversal) vulnerabilities that allow attackers to read arbitrary files on the server, potentially including sensitive configuration files, credentials, and source code. This vulnerability occurs when user-controllable input is passed to filesystem APIs without proper validation.

## Prerequisites

### Required Tools
- Web browser with developer tools
- Burp Suite or OWASP ZAP
- cURL for testing payloads
- Wordlists for automation
- ffuf or wfuzz for fuzzing

### Required Knowledge
- HTTP request/response structure
- Linux and Windows filesystem layout
- Web application architecture
- Basic understanding of file APIs

## Outputs and Deliverables

1. **Vulnerability Report** - Identified traversal points and severity
2. **Exploitation Proof** - Extracted file contents
3. **Impact Assessment** - Accessible files and data exposure
4. **Remediation Guidance** - Secure coding recommendations

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Permission Restrictions
- Cannot read files application user cannot access
- Shadow file requires root privileges
- Many files have restrictive permissions

### Application Restrictions
- Extension validation may limit file types
- Base path validation may restrict scope
- WAF may block common payloads

### Testing Considerations
- Respect authorized scope
- Avoid accessing genuinely sensitive data
- Document all successful access

## When to Use
Use this skill when the task matches its reviewed scope: Identify, validate, and explain file path traversal vulnerabilities in explicitly authorized applications, including encoding bypasses, absolute paths, and restricted-file-read impact.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
