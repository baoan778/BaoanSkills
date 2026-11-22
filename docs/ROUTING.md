# Skill routing

Routing covers the public allowlist only. Unlisted local staging skills are not
part of the published release and should not be selected by an installed public
snapshot.

Use the narrowest skill that matches an explicit technical signal. Confirm
authorization before any active testing.

## Precedence

1. Explicit target platform, product, or framework.
2. Explicit vulnerability class or primitive.
3. Explicit tool and its workflow.
4. Broad methodology or checklist.
5. General-purpose fallback.

## Safety and routing boundaries

- Broad skills are not default execution entry points. Route to a narrower
  skill when platform, vulnerability, or tool evidence is available.
- CTF-specific web skills are not a substitute for a professional assessment
  workflow and reporting process.
- If scope or written authorization is missing, stop before any active testing.

## CTF entry points

| Request | Preferred skill |
|---|---|
| Unknown category or mixed challenge bundle | `solve-challenge` |
| Local CTF corpus lookup | `ctf-knowledge-base` |
| AI/ML challenge | `ctf-ai-ml` |
| Cryptography or cryptanalysis | `ctf-crypto` |
| Disk, memory, network, or signal forensics | `ctf-forensics` |
| Malware behavior or traffic | `ctf-malware` |
| Encoding, jail, RF, or cross-category puzzle | `ctf-misc` |
| Public-source investigation | `ctf-osint` |
| Binary exploitation, including 64-bit ELF | `ctf-pwn` |
| Reverse engineering | `ctf-reverse` |
| Web or API exploitation | `ctf-web` |
| Post-solve documentation | `ctf-writeup` |

## Application security

| Request | Preferred skill |
|---|---|
| Broad web vulnerability taxonomy or triage | `top-web-vulnerabilities` |
| Manual SQL injection assessment | `sql-injection-testing` |
| SQLMap-driven workflow | `sqlmap-database-pentesting` |
| XSS or combined XSS/HTML injection | `xss-html-injection` |
| HTML injection specifically | `html-injection-testing` |
| Authentication or session weakness | `broken-authentication` |
| IDOR or object-level authorization | `idor-testing` |
| Path traversal or file path abuse | `file-path-traversal` |
| API fuzzing and bug-bounty triage | `api-fuzzing-bug-bounty` |
| WordPress assessment | `wordpress-penetration-testing` |
| Workflow/deliverable checks or engagement checklist | `pentest-checklist` |
| Quick command or command reference lookup | `pentest-commands` |
| Overall or broad engagement methodology | `ethical-hacking-methodology` |

## Infrastructure and tooling

| Request | Preferred skill |
|---|---|
| Linux privilege escalation | `linux-privilege-escalation` |
| Windows privilege escalation | `windows-privilege-escalation` |
| General privilege-escalation methods | `privilege-escalation-methods` |
| SSH assessment | `ssh-penetration-testing` |
| SMTP assessment | `smtp-penetration-testing` |
| AWS assessment | `aws-penetration-testing` |
| Shodan reconnaissance | `shodan-reconnaissance` |
| Scanner selection | `scanning-tools` |
| Tool-selection index or red-team tooling overview | `red-team-tools` |
| Metasploit workflow | `metasploit-framework` |
| Packet capture analysis | `wireshark-analysis` |

## Auditing and analysis

| Request | Preferred skill |
|---|---|
| GitHub Actions with AI agents | `agentic-actions-auditor` |
| Search or extract a Burp project | `burpsuite-project-parser` |
| Create custom Semgrep detections | `semgrep-rule-creator` |

## Overlap rules

- Use `ctf-knowledge-base` to locate curated cards, case families, or manifest
  paths; it is a discovery and retrieval aid, not an execution skill. Route the
  actual workflow to `ctf-web`, `ctf-misc`, `ctf-forensics`, `ctf-crypto`,
  `ctf-pwn`, `ctf-reverse`, or another matching specialist once the category is
  known.
- Use `solve-challenge` only when the category is unclear; route directly to a
  specialized CTF skill once the dominant signal is known.
- Use `ctf-web` for competition-scoped web exploitation. Use the application
  security skills for authorized professional assessments with reporting and
  remediation requirements.
- Prefer `sql-injection-testing` for manual reasoning and
  `sqlmap-database-pentesting` when SQLMap is the explicit tool.
- Prefer `xss-html-injection` for combined or general client-side injection and
  `html-injection-testing` when HTML injection is the primary issue.
- Treat `top-web-vulnerabilities` as a taxonomy and triage reference, not a
  substitute for the specific testing workflow.
- Prefer a specific service or platform skill over `scanning-tools`,
  `red-team-tools`, or `ethical-hacking-methodology` when a narrower match
  exists.
- When two skills overlap and neither signal is decisive, state the ambiguity
  and load the broader methodology first, then branch to one specialist.
