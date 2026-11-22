---
name: html-injection-testing
description: Test explicitly authorized web applications for HTML injection, content spoofing, phishing surfaces, form injection, and sanitization gaps. Pair with XSS testing when script execution is also in scope.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/html-injection-testing/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: application-security
  tags:
  - web
  - html-injection
  - xss
  - phishing
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/html-injection-testing/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> AUTHORIZED USE ONLY: Use this skill only for authorized security assessments, defensive validation, or controlled educational environments.

# HTML Injection Testing

## Purpose

Identify and exploit HTML injection vulnerabilities that allow attackers to inject malicious HTML content into web applications. This vulnerability enables attackers to modify page appearance, create phishing pages, and steal user credentials through injected forms.

## Prerequisites

### Required Tools
- Web browser with developer tools
- Burp Suite or OWASP ZAP
- Tamper Data or similar proxy
- cURL for testing payloads

### Required Knowledge
- HTML fundamentals
- HTTP request/response structure
- Web application input handling
- Difference between HTML injection and XSS

## Outputs and Deliverables

1. **Vulnerability Report** - Identified injection points
2. **Exploitation Proof** - Demonstrated content manipulation
3. **Impact Assessment** - Potential phishing and defacement risks
4. **Remediation Guidance** - Input validation recommendations

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Attack Limitations
- Modern browsers may sanitize some injections
- CSP can prevent inline styles and scripts
- WAFs may block common payloads
- Some applications escape output properly

### Testing Considerations
- Distinguish between HTML injection and XSS
- Verify visual impact in browser
- Test in multiple browsers
- Check for stored vs reflected

### Severity Assessment
- Lower severity than XSS (no script execution)
- Higher impact when combined with phishing
- Consider defacement/reputation damage
- Evaluate credential theft potential

## When to Use
Use this skill when the task matches its reviewed scope: Test explicitly authorized web applications for HTML injection, content spoofing, phishing surfaces, form injection, and sanitization gaps. Pair with XSS testing when script execution is also in scope.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
