---
name: top-web-vulnerabilities
description: Use a taxonomy of common web vulnerabilities for triage, impact assessment, and remediation planning. Prefer a specific active-testing skill once the vulnerability class is known.
license: MIT
allowed-tools:
- Read
- Glob
- Grep
- WebFetch
- WebSearch
metadata:
  risk: reference
  source: https://github.com/zebbern/claude-code-guide/blob/b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0/skills/top-web-vulnerabilities/SKILL.md
  author: zebbern
  date_added: '2026-02-27'
  category: application-security
  tags:
  - web
  - owasp
  - reference
  - remediation
  license_status: verified
  provenance_status: verified
  source_repo: https://github.com/zebbern/claude-code-guide
  upstream_commit: b67ee2b149bdd6e35bbeeb800bc2cc9e4a34b4e0
  upstream_path: skills/top-web-vulnerabilities/SKILL.md
  retrieved_at: '2026-11-22'
  modifications: 'Normalized frontmatter, metadata, and formatting; preserved or added an authorization boundary and made other non-substantive editorial changes. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Moved the full vulnerability taxonomy and supporting assessment tables into directly linked references and turned the entrypoint into a concise taxonomy-selection, delegation, evidence, and stop-condition router.'
  license_evidence: licenses/zebbern-claude-code-guide-MIT.txt
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# Top 100 Web Vulnerabilities Reference

## Purpose

Provide a comprehensive, structured reference for the 100 most critical web application vulnerabilities organized by category. This skill enables systematic vulnerability identification, impact assessment, and remediation guidance across the full spectrum of web security threats. Content organized into 15 major vulnerability categories aligned with industry standards and real-world attack patterns.

## Prerequisites

- Basic understanding of web application architecture (client-server model, HTTP protocol)
- Familiarity with common web technologies (HTML, JavaScript, SQL, XML, APIs)
- Understanding of authentication and authorization concepts
- Access to web application security testing tools (Burp Suite, OWASP ZAP)
- Knowledge of secure coding principles recommended

## Outputs and Deliverables

- Complete vulnerability catalog with definitions, root causes, impacts, and mitigations
- Category-based vulnerability groupings for systematic assessment
- Quick reference for security testing and remediation
- Foundation for vulnerability assessment checklists and security policies

---

## How to Use This Skill

1. **Define the evidence question.** State whether the task is taxonomy lookup, finding triage, impact assessment, remediation planning, or test-case design. Record the application type, technology stack, and authorization boundary.
2. **Locate the vulnerability class.** Open [vulnerability-catalog.md](references/vulnerability-catalog.md) and use the 15 category headings to find the closest definition, root cause, impact, and mitigation.
3. **Choose a verification path.** Use [assessment-tables.md](references/assessment-tables.md) for the category summary, security-header baseline, OWASP mapping, common challenges, and verification approaches. Prefer passive review until active testing is explicitly authorized.
4. **Delegate active testing.** Once the class is known, route SQL injection, XSS, HTML injection, authentication, IDOR, path traversal, or another focused workflow to the matching skill. This reference does not replace a scoped test plan.
5. **Produce an evidence-backed result.** Report the class, observed behavior, affected component, exploit preconditions, impact, confidence, remediation, and retest criteria. Mark taxonomy-only hypotheses as unverified.

### Reference Map

| Need | Reference |
|---|---|
| Definitions, root causes, impacts, and mitigations by category | [vulnerability-catalog.md](references/vulnerability-catalog.md) |
| OWASP mapping, security headers, and verification prompts | [assessment-tables.md](references/assessment-tables.md) |

### Stop Conditions

Stop when the task moves from taxonomy or passive review into active testing without written authorization, when a proposed DoS or destructive validation could affect availability, or when the finding cannot be supported by application-specific evidence.

## Constraints and Limitations

- Vulnerability definitions represent common patterns; specific implementations vary
- Mitigations must be adapted to technology stack and architecture
- New vulnerabilities emerge continuously; reference should be updated
- Some vulnerabilities overlap across categories (e.g., IDOR appears in multiple contexts)
- Effectiveness of mitigations depends on proper implementation
- Automated scanners cannot detect all vulnerability types (especially business logic)

---

## References

- OWASP Top 10 Web Application Security Risks
- CWE/SANS Top 25 Most Dangerous Software Errors
- OWASP Testing Guide
- OWASP Application Security Verification Standard (ASVS)
- NIST Cybersecurity Framework
- Source: Kumar MS - Top 100 Web Vulnerabilities

## When to Use
Use this skill as a web vulnerability taxonomy and triage aid when a broad list of classes, impacts, mitigations, or OWASP mappings is useful.

Do not use it as permission to test a live target or as a substitute for a focused exploit workflow. Once the likely class is known, route to the specific skill and establish authorization, scope, evidence requirements, and stop conditions.
