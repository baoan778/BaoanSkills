---
name: wordpress-penetration-testing
description: Assess explicitly authorized WordPress installations for core, plugin, theme, user, authentication, upload, and configuration weaknesses without relying on destructive exploitation.
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
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/wordpress-penetration-testing/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: application-security
  tags:
  - web
  - wordpress
  - cms
  - plugins
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/wordpress-penetration-testing/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Moved the long enumeration and controlled validation commands into a directly linked assessment playbook, moved WordPress 7.0 endpoint checks into a second linked reference, and condensed the entrypoint into scope, validation, reporting, and stop-condition guidance.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> AUTHORIZED USE ONLY: Use this skill only for authorized security assessments, defensive validation, or controlled educational environments.

# WordPress Penetration Testing

## WordPress 7.0 Security Considerations

WordPress 7.0 (April 2026) introduces new features that create additional attack surfaces:

### Real-Time Collaboration (RTC)
- Yjs CRDT sync provider endpoints
- `wp_sync_storage` post meta
- Collaboration session hijacking
- Data sync interception

### AI Connector API
- `/wp-json/ai/v1/` endpoints
- Credential storage in Settings > Connectors
- Prompt injection vulnerabilities
- AI response manipulation

### Abilities API
- `/wp-json/abilities/v1/` manifest exposure
- Ability invocation endpoints
- Permission boundary bypass
- MCP adapter integration points

### DataViews
- New admin interface endpoints
- Client-side validation bypass
- Filter/sort parameter injection

### PHP Requirements
- PHP 7.2/7.3 no longer supported (upgrade attacks)
- PHP 8.3+ recommended (new attack vectors)

## Purpose

Conduct comprehensive security assessments of WordPress installations including enumeration of users, themes, and plugins, vulnerability scanning, credential attacks, and exploitation techniques. WordPress powers approximately 35% of websites, making it a critical target for security testing.

## Prerequisites

### Required Tools
- WPScan (pre-installed in Kali Linux)
- Metasploit Framework
- Burp Suite or OWASP ZAP
- Nmap for initial discovery
- cURL or wget

### Required Knowledge
- WordPress architecture and structure
- Web application testing fundamentals
- HTTP protocol understanding
- Common web vulnerabilities (OWASP Top 10)

## Outputs and Deliverables

1. **WordPress Enumeration Report** - Version, themes, plugins, users
2. **Vulnerability Assessment** - Identified CVEs and misconfigurations
3. **Credential Assessment** - Weak password findings
4. **Exploitation Proof** - Shell access documentation

## Core Workflow

1. **Confirm the assessment contract.** Record the site URLs, host and network boundaries, permitted accounts, upload or authentication tests that are allowed, rate limits, backup and rollback arrangements, and the person who can authorize escalation.
2. **Fingerprint without assuming.** Establish whether the target is WordPress, identify the public site and any staging or multisite components, and check response headers, generator data, feeds, REST routes, and known paths at a conservative request rate.
3. **Enumerate the attack surface.** Use [assessment-playbook.md](references/assessment-playbook.md) for WPScan discovery, core and plugin/theme version checks, user enumeration, REST/XML-RPC review, and controlled authentication testing. Record uncertainty rather than inferring a vulnerable version from a single artifact.
4. **Validate findings safely.** Confirm configuration and version evidence with a second independent source. Prefer read-only checks; do not upload a plugin, change settings, or use a webshell unless the written scope explicitly permits that action and recovery path.
5. **Review the 7.0-specific surface.** Use [wordpress-7-security.md](references/wordpress-7-security.md) when AI connectors, Abilities API, real-time collaboration, or DataViews endpoints are present. Treat AI prompt injection and ability invocation as high-impact tests requiring separate approval.
6. **Report and retest.** Document the affected component, evidence, exploit preconditions, business impact, remediation, and a safe retest method.

### Assessment routes

| Question | Reference |
|---|---|
| Discovery, WPScan flags, user and plugin/theme enumeration | [assessment-playbook.md](references/assessment-playbook.md) |
| Low-volume authentication testing and XML-RPC checks | [assessment-playbook.md](references/assessment-playbook.md) |
| WordPress 7.0 AI, Abilities, RTC, and DataViews checks | [wordpress-7-security.md](references/wordpress-7-security.md) |

### Stop conditions

Stop when the target redirects to a third party, a scan or login test causes lockouts or service degradation, credentials are shared outside the approved test account, an exploit would write to the site, or the available evidence cannot distinguish a real issue from an expected configuration.

## Quick Reference

### WPScan Enumeration Flags

| Flag | Description |
|------|-------------|
| `-e at` | All themes |
| `-e vt` | Vulnerable themes |
| `-e ap` | All plugins |
| `-e vp` | Vulnerable plugins |
| `-e u` | Users (1-10) |
| `-e cb` | Config backups |
| `-e dbe` | Database exports |

### Common WordPress Paths

| Path | Purpose |
|------|---------|
| `/wp-admin/` | Admin dashboard |
| `/wp-login.php` | Login page |
| `/wp-content/uploads/` | User uploads |
| `/wp-includes/` | Core files |
| `/xmlrpc.php` | XML-RPC API |
| `/wp-json/` | REST API |

### WPScan Command Examples

| Purpose | Command |
|---------|---------|
| Basic scan | `wpscan --url http://target.com` |
| All enumeration | `wpscan --url http://target.com -e at,ap,u` |
| Password attack | `wpscan --url http://target.com -U admin -P pass.txt` |
| Aggressive | `wpscan --url http://target.com --detection-mode aggressive` |

## Constraints and Limitations

### Legal Considerations
- Obtain written authorization before testing
- Stay within defined scope
- Document all testing activities
- Follow responsible disclosure

### Technical Limitations
- WAF may block scanning
- Rate limiting may prevent brute-force
- Some plugins may have false negatives
- XML-RPC may be disabled

### Detection Evasion
- Use random user agents: `--random-user-agent`
- Throttle requests: `--throttle 1000`
- Use proxy rotation
- Avoid aggressive modes on monitored sites

## Troubleshooting

### WPScan Shows No Vulnerabilities

**Solutions:**
1. Use API token for vulnerability database
2. Try aggressive detection mode
3. Check for WAF blocking scans
4. Verify WordPress is actually installed

### Brute-Force Blocked

**Solutions:**
1. Use XML-RPC method instead of wp-login
2. Add throttling: `--throttle 500`
3. Use different user agents
4. Check for IP blocking/fail2ban

### Cannot Access Admin Panel

**Solutions:**
1. Verify credentials are correct
2. Check for two-factor authentication
3. Look for IP whitelist restrictions
4. Check for login URL changes (security plugins)

## WordPress 7.0 Security Notes

WordPress 7.0 adds AI connector, Abilities API, real-time collaboration, and DataViews surfaces. Use [wordpress-7-security.md](references/wordpress-7-security.md) for endpoint enumeration and controlled validation notes. Confirm each feature is enabled and separately authorized before invoking an ability, changing collaboration state, or sending an AI prompt that could expose data.

## When to Use
Use this skill to assess a known WordPress site for core, theme, plugin, user, authentication, REST/XML-RPC, and configuration weaknesses after authorization and scope are recorded.

Do not use it for opportunistic internet-wide enumeration, unattended password spraying, destructive plugin or theme modification, or a non-WordPress web application. Route a single confirmed vulnerability class to the corresponding focused skill when one exists.
