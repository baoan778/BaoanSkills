<p align="center">
  <img src="docs/assets/banner.svg" alt="BaoanSkills: 39 provenance-verified security skills" width="100%">
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="docs/INSTALL.md">Install guide</a> ·
  <a href="docs/SKILLS_INDEX.md">Skill catalog</a> ·
  <a href="docs/ROUTING.md">Routing guide</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/baoan778/BaoanSkills/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/baoan778/BaoanSkills?display_name=tag&sort=semver"></a>
  <a href="https://github.com/baoan778/BaoanSkills/actions/workflows/validate.yml"><img alt="Validate" src="https://github.com/baoan778/BaoanSkills/actions/workflows/validate.yml/badge.svg"></a>
  <a href="https://github.com/baoan778/BaoanSkills/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://github.com/baoan778/BaoanSkills/actions/workflows/codeql.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <a href="NOTICE"><img alt="License: MIT + CC BY-SA 4.0" src="https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--SA%204.0-blue.svg"></a>
</p>

<p align="center">
  <strong>Give your coding agent a disciplined security playbook.</strong><br>
  Focused workflows, on-demand references, and explicit authorization boundaries.
</p>

A provenance-aware collection of 39 security skills for Codex-compatible agents.
The public release covers CTF solving, authorized application security testing,
privilege assessment, and security auditing tooling.

> [!IMPORTANT]
> **Authorized use only.** Use these skills only in CTF environments, owned labs,
> or systems for which you have explicit written permission. A public target, a
> discovered service, or the presence of a tool is never authorization. Read
> [docs/AUTHORIZATION.md](docs/AUTHORIZATION.md) before active testing.

## Why BaoanSkills

| Common problem | BaoanSkills approach |
|---|---|
| Giant prompts bury the actual workflow | A focused `SKILL.md` entrypoint routes to detailed references only when needed |
| Agent output varies between sessions | Explicit evidence, stop conditions, and output criteria make runs reproducible |
| Offensive tooling is easy to misuse | Every skill starts with an authorization boundary and scope-aware execution rules |
| Third-party content is hard to trust | Pinned sources, license evidence, per-file SHA-256 locks, and fail-closed installation |
| Installing everything adds noise | Dependency-free installer supports individual skills, starter bundles, or the full catalog |

## Quick start

**Requirements:** Python 3.10+, Git, and Codex or another agent that discovers
`SKILL.md` directories.

### macOS / Linux

```bash
git clone https://github.com/baoan778/BaoanSkills.git
cd BaoanSkills
python3 scripts/install_skills.py --list
python3 scripts/install_skills.py solve-challenge ctf-web ctf-crypto ctf-writeup
```

### Windows PowerShell

```powershell
git clone https://github.com/baoan778/BaoanSkills.git
Set-Location BaoanSkills
python scripts\install_skills.py --list
python scripts\install_skills.py solve-challenge ctf-web ctf-crypto ctf-writeup
```

Restart or reload your agent after installation. The default destination is
`$CODEX_HOME/skills` when `CODEX_HOME` is set, otherwise `~/.codex/skills`.
Use `--dest PATH` for another location and `--force` to update existing skills.

[Release archives](https://github.com/baoan778/BaoanSkills/releases/latest),
checksum verification, update steps, and troubleshooting are documented in the
**[installation guide](docs/INSTALL.md)**.

### Choose a starter bundle

| Goal | Install command |
|---|---|
| CTF fundamentals | `python scripts/install_skills.py solve-challenge ctf-web ctf-crypto ctf-forensics ctf-reverse ctf-pwn ctf-writeup` |
| Authorized web testing | `python scripts/install_skills.py ethical-hacking-methodology top-web-vulnerabilities sql-injection-testing xss-html-injection idor-testing pentest-checklist` |
| Cloud and host review | `python scripts/install_skills.py aws-penetration-testing linux-privilege-escalation windows-privilege-escalation ssh-penetration-testing` |
| Code and CI audit | `python scripts/install_skills.py agentic-actions-auditor semgrep-rule-creator burpsuite-project-parser` |
| Everything | `python scripts/install_skills.py --all` |

Use `python3` instead of `python` on macOS or Linux when required.

## Find the right skill

| You are working on | Start with | When to branch |
|---|---|---|
| An unfamiliar CTF bundle | `solve-challenge` | Route to the narrowest specialist after triage |
| RSA, ECC, ciphers, or PRNGs | `ctf-crypto` | Use `ctf-misc` only when crypto is incidental |
| Native binary exploitation | `ctf-pwn` | Use `ctf-reverse` first when the main blocker is understanding the binary |
| Reverse engineering | `ctf-reverse` | Move to `ctf-pwn` once exploitation is the primary task |
| A CTF web application | `ctf-web` | Use AppSec skills only for authorized professional assessments |
| Disk, memory, network, or signal artifacts | `ctf-forensics` | Use `wireshark-analysis` for a standalone authorized PCAP review |
| A solved challenge that needs documentation | `ctf-writeup` | Pair with the specialist skill that produced the evidence |
| An authorized web application | `top-web-vulnerabilities` | Specialize by vulnerability class once evidence is clear |
| An authorized API or bug-bounty scope | `api-fuzzing-bug-bounty` | Add authentication, IDOR, or injection skills as the scope requires |
| An AWS, Linux, or Windows environment | `aws-penetration-testing`, `linux-privilege-escalation`, or `windows-privilege-escalation` | Confirm written scope before any active or mutating action |
| GitHub Actions that invoke AI agents | `agentic-actions-auditor` | Use `semgrep-rule-creator` when a reusable static check is needed |
| A local CTF knowledge lookup | `ctf-knowledge-base` | Route the actual solve to the matching specialist |

The complete routing rules and overlap guidance live in
[docs/ROUTING.md](docs/ROUTING.md).

## Skill catalog

<details>
<summary><strong>CTF · 12 skills</strong></summary>

`ctf-ai-ml` · `ctf-crypto` · `ctf-forensics` · `ctf-knowledge-base` · `ctf-malware` ·
`ctf-misc` · `ctf-osint` · `ctf-pwn` · `ctf-reverse` · `ctf-web` · `ctf-writeup` ·
`solve-challenge`

</details>

<details>
<summary><strong>Application security and code review · 16 skills</strong></summary>

`agentic-actions-auditor` · `api-fuzzing-bug-bounty` · `broken-authentication` ·
`ethical-hacking-methodology` · `file-path-traversal` · `html-injection-testing` ·
`idor-testing` · `pentest-checklist` · `pentest-commands` · `red-team-tools` ·
`smtp-penetration-testing` · `sql-injection-testing` · `sqlmap-database-pentesting` ·
`top-web-vulnerabilities` · `wordpress-penetration-testing` · `xss-html-injection`

</details>

<details>
<summary><strong>Cloud, identity, and infrastructure · 5 skills</strong></summary>

`aws-penetration-testing` · `linux-privilege-escalation` ·
`privilege-escalation-methods` · `ssh-penetration-testing` ·
`windows-privilege-escalation`

</details>

<details>
<summary><strong>Tools, scanning, and supply chain · 6 skills</strong></summary>

`burpsuite-project-parser` · `metasploit-framework` · `scanning-tools` ·
`semgrep-rule-creator` · `shodan-reconnaissance` · `wireshark-analysis`

</details>

Browse descriptions, risk levels, licenses, and direct links in the generated
**[skill catalog](docs/SKILLS_INDEX.md)**.

## How a skill is used

```mermaid
flowchart LR
    A["Task + scope"] --> B["Agent selects\nthe narrowest skill"]
    B --> C["SKILL.md\nrouting + guardrails"]
    C --> D["References and scripts\nloaded on demand"]
    D --> E["Reproducible result"]
    A -. "authorization check" .-> C

    classDef task fill:#0d263b,stroke:#58a6ff,color:#e2e8f0
    classDef skill fill:#123a3a,stroke:#38e8c4,color:#e2e8f0
    classDef result fill:#3b2c18,stroke:#f4b860,color:#fff7e6
    class A,B task
    class C,D skill
    class E result
```

Each skill uses **progressive disclosure**:

- frontmatter gives the agent a concise discovery description;
- `SKILL.md` contains the routing decision, authorization boundary, core workflow,
  and output criteria;
- `references/` and `scripts/` carry detailed material that is loaded only when
  the current task needs it.

This keeps context focused while preserving the depth needed for real work.

## Example prompts

```text
Use the ctf-crypto skill to analyze the attached RSA challenge and produce a
reproducible solve path with the recovered flag.
```

```text
Use the idor-testing skill to review the API endpoints in ./lab-scope.json.
The written scope and test window are in ./AUTHORIZATION.md. Stop before any
request outside that scope.
```

```text
Use agentic-actions-auditor to review the AI-agent workflows under
.github/workflows for prompt-injection and secret-exposure risks.
```

```text
Use semgrep-rule-creator to turn this vulnerable code pattern into a tested
Semgrep rule with positive and negative fixtures.
```

## Provenance and quality

The release allowlist is [release/public-skills.txt](release/public-skills.txt).
Every published skill file is locked by SHA-256 in
[release/provenance.lock.json](release/provenance.lock.json).

| Origin | Skills | License | Source |
|---|---:|---|---|
| Original CTF workflows | 12 | MIT | BaoanSkills contributors |
| Authorized security testing | 24 | MIT | `zebbern/claude-code-guide` at a pinned commit |
| Security auditing tools | 3 | CC BY-SA 4.0 | `trailofbits/skills` at a pinned commit |

Additional guarantees:

- the installer verifies requested files before copying and aborts on any
  missing, extra, symlinked, or hash-mismatched file;
- release archives include SHA-256 checksum files and are smoke-tested before
  publication;
- CI validates Linux and Windows across Python 3.10, 3.11, and 3.12;
- CodeQL, gitleaks, link checks, resource checks, Markdown checks, provenance
  checks, and release-readiness checks are required quality gates.

Read [docs/PROVENANCE.md](docs/PROVENANCE.md) and
[docs/SKILL_REVIEW.md](docs/SKILL_REVIEW.md) for the review model.

## Repository map

```text
skills/     focused SKILL.md entrypoints, references, scripts, and assets
docs/       installation, routing, authorization, provenance, and review guides
release/    public allowlist and per-file SHA-256 provenance lock
scripts/    installer, generators, validators, and release tooling
tests/      regression coverage for metadata, routing, layout, and packaging
.github/    CI, CodeQL, release automation, and contribution templates
```

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pre_commit install
python3 scripts/check_all.py
```

`check_all.py` runs the same release-scoped quality suite used by CI. See
[CONTRIBUTING.md](CONTRIBUTING.md) before changing skills, routing metadata,
generated files, or the provenance lock.

## Security

Do not open a public issue containing live credentials, private target data, or
unpatched vulnerability details. Follow [SECURITY.md](SECURITY.md) for private
reporting and disclosure guidance.

## License

Repository scaffolding, scripts, documentation, and the 12 original CTF skills
use the root [MIT License](LICENSE). The 24 skills derived from
`zebbern/claude-code-guide` are MIT-licensed. The 3 skills derived from
`trailofbits/skills` are CC BY-SA 4.0. Attribution and full license texts are in
[NOTICE](NOTICE) and [licenses/](licenses/).

The root MIT License does not relicense third-party material. `source: original`
records the maintainer's attribution for the 12 CTF skills; no external
historical record was available to independently prove that status.

## Contributing

Contributions are welcome when they preserve provenance, licensing, routing
quality, and the authorization boundary. Start with
[CONTRIBUTING.md](CONTRIBUTING.md),
[docs/ADDING_A_SKILL.md](docs/ADDING_A_SKILL.md), and
[docs/SKILL_REVIEW.md](docs/SKILL_REVIEW.md).

Maintained by [@baoan778](https://github.com/baoan778).
