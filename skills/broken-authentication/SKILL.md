---
name: broken-authentication
description: Assess authentication, session management, password recovery, MFA, token handling, and account-takeover risks in explicitly authorized web applications.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/broken-authentication/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: application-security
  tags:
  - web
  - authentication
  - session
  - owasp
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/broken-authentication/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed workflow, quick reference, examples, and troubleshooting into a directly linked references/playbook.md.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# Broken Authentication Testing

## Purpose

Identify and exploit authentication and session management vulnerabilities in web applications. Broken authentication consistently ranks in the OWASP Top 10 and can lead to account takeover, identity theft, and unauthorized access to sensitive systems. This skill covers testing methodologies for password policies, session handling, multi-factor authentication, and credential management.

## Prerequisites

### Required Knowledge
- HTTP protocol and session mechanisms
- Authentication types (SFA, 2FA, MFA)
- Cookie and token handling
- Common authentication frameworks

### Required Tools
- Burp Suite Professional or Community
- Hydra or similar brute-force tools
- Custom wordlists for credential testing
- Browser developer tools

### Required Access
- Target application URL
- Test account credentials
- Written authorization for testing

## Outputs and Deliverables

1. **Authentication Assessment Report** - Document all identified vulnerabilities
2. **Credential Testing Results** - Brute-force and dictionary attack outcomes
3. **Session Security Analysis** - Token randomness and timeout evaluation
4. **Remediation Recommendations** - Security hardening guidance

## Detailed Playbook

Read [the complete playbook](references/playbook.md) for the phase-by-phase procedure, command reference, worked examples, and troubleshooting. Treat every command as a hypothesis until it is validated in the authorized environment.

## Constraints and Limitations

### Legal Requirements
- Only test with explicit written authorization
- Avoid testing with real breached credentials
- Do not access actual user accounts
- Document all testing activities

### Technical Limitations
- CAPTCHA may prevent automated testing
- Rate limiting affects brute force timing
- MFA significantly increases attack difficulty
- Some vulnerabilities require victim interaction

### Scope Considerations
- Test accounts may behave differently than production
- Some features may be disabled in test environments
- Third-party authentication may be out of scope
- Production testing requires extra caution

## When to Use
Use this skill when the task matches its reviewed scope: Assess authentication, session management, password recovery, MFA, token handling, and account-takeover risks in explicitly authorized web applications.

Before execution, confirm target ownership or written authorization, scope boundaries, permitted actions, time window, and stop conditions. Do not use it for unauthorized testing or when a more specific routing entry clearly applies.
