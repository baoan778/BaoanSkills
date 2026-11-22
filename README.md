# BaoanSkills

[![Validate](https://github.com/baoan778/BaoanSkills/actions/workflows/validate.yml/badge.svg)](https://github.com/baoan778/BaoanSkills/actions/workflows/validate.yml)
[![CodeQL](https://github.com/baoan778/BaoanSkills/actions/workflows/codeql.yml/badge.svg)](https://github.com/baoan778/BaoanSkills/actions/workflows/codeql.yml)
[![License: MIT + CC BY-SA 4.0](https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--SA%204.0-blue.svg)](NOTICE)

A provenance-aware collection of 39 security skills for Codex-compatible
agents. The public release covers CTF solving, authorized application security
testing, privilege assessment, and security auditing tooling.

> **Authorized use only.** Use these skills only in CTF environments, owned labs,
> or systems for which you have explicit written permission. See
> [docs/AUTHORIZATION.md](docs/AUTHORIZATION.md), [SECURITY.md](SECURITY.md), and the
> authorization section in every `SKILL.md`.

## Install

The installer copies only skills on the reviewed public allowlist and has no
runtime dependencies beyond Python 3.10+. Before copying, it verifies every
requested skill file against `release/provenance.lock.json`. A missing or invalid
lock, an unlocked or missing file, a symlink, or a size/hash mismatch aborts
installation without copying anything.

Normal installation does not import PyYAML; that dependency is only needed by
maintainer tooling that parses skill frontmatter.

```bash
git clone https://github.com/baoan778/BaoanSkills.git
cd BaoanSkills
python3 scripts/install_skills.py --list
python3 scripts/install_skills.py ctf-web ctf-crypto
```

Windows PowerShell:

```powershell
git clone https://github.com/baoan778/BaoanSkills.git
Set-Location BaoanSkills
python scripts\install_skills.py --list
python scripts\install_skills.py ctf-web ctf-crypto
```

Install every public skill:

```bash
python3 scripts/install_skills.py --all
```

The default destination is `$CODEX_HOME/skills` when `CODEX_HOME` is set,
otherwise `~/.codex/skills`. Choose another directory with `--dest PATH`,
preview with `--dry-run`, and update existing installations with `--force`.
Restart or reload Codex after installation so it discovers the new skills. To
install manually, copy complete skill directories; do not copy only `SKILL.md`.

### Release archive

Prebuilt archives are attached to each [GitHub Release](https://github.com/baoan778/BaoanSkills/releases)
with a matching SHA-256 file. Each tagged release is smoke-tested in CI before
publication, including checksum verification, zip extraction, a sample install,
and a tamper-rejection check. Use the `.zip` archive on Windows and the
`.tar.gz` archive on macOS or Linux.

```powershell
# After downloading baoanskills-release.zip and its .sha256 file:
$expected = (Get-Content .\baoanskills-release.zip.sha256 -Raw).Split()[0]
$actual = (Get-FileHash .\baoanskills-release.zip -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw 'Archive checksum mismatch' }
Expand-Archive .\baoanskills-release.zip -DestinationPath .
Set-Location .\baoanskills-public
python scripts\install_skills.py --all
```

The archive contains a validated `baoanskills-public` snapshot, including the
installer, tests, provenance reports, and only allowlisted skills.

## What is included

The authoritative release list is
[release/public-skills.txt](release/public-skills.txt). The matching file-level
SHA-256 lock is [release/provenance.lock.json](release/provenance.lock.json).

| Group | Count | License | Origin |
|---|---:|---|---|
| Original CTF workflows | 12 | MIT | BaoanSkills contributors |
| Authorized security testing | 24 | MIT | `zebbern/claude-code-guide` at a pinned commit |
| Security auditing tools | 3 | CC BY-SA 4.0 | `trailofbits/skills` at a pinned commit |

Capabilities:

- **CTF:** AI/ML, crypto, forensics, malware, misc, OSINT, pwn, reverse
  engineering, web exploitation, writeups, a curated knowledge-base/corpus
  index, and a first-pass challenge router.
- **Application security:** SQL injection, XSS/HTML injection, authentication,
  IDOR, path traversal, WordPress, and broad web vulnerability workflows.
- **Infrastructure:** AWS, Linux and Windows privilege escalation, SSH, SMTP,
  Shodan reconnaissance, Wireshark analysis, Metasploit, and scanner selection.
- **Auditing:** GitHub agentic-actions review, Burp project parsing, and Semgrep
  rule creation.

Each skill follows this layout. Topic documents live under `references/` so the
entrypoint stays focused and context loading remains predictable.

```text
<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/        # optional
├── scripts/           # optional
└── assets/            # optional
```

## Routing and discovery

Start with [docs/ROUTING.md](docs/ROUTING.md) when choosing between overlapping
skills. Prefer explicit platform, vulnerability, or tool signals over broad
methodology skills. The generated catalog is
[docs/SKILLS_INDEX.md](docs/SKILLS_INDEX.md); provenance details are in
[docs/PROVENANCE.md](docs/PROVENANCE.md) and
[docs/provenance.csv](docs/provenance.csv).

When a workflow requires active testing, establish scope and explicit
authorization first. CTF-specific web skills are not a substitute for a
professional assessment workflow and reporting process.

## Repository layout

```text
.github/       CI, CodeQL, release automation, and contribution templates
docs/          architecture, routing, publication, provenance, and review guides
licenses/      complete upstream license evidence
release/       public allowlist and file-level provenance lock
scripts/       validation, generation, installation, and snapshot tooling
skills/        allowlisted skill directories only in the public snapshot
tests/         regression tests for metadata, routing, installation, and layout
```

## Development

Install the development dependencies, enable the local hooks, and run the test
suite:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pre_commit install
python3 -m pytest
```

Core validation commands:

```bash
python3 -m ruff check scripts tests
python3 scripts/validate_skills.py --strict
python3 scripts/build_kb_manifest.py --check
python3 scripts/check_publication.py --check
python3 scripts/check_workflows.py
python3 scripts/check_links.py
python3 scripts/check_whitespace.py
python3 scripts/check_markdown_structure.py
python3 scripts/check_resources.py
python3 scripts/check_skill_layout.py
python3 scripts/check_encoding.py
python3 scripts/smoke_test_scripts.py
python3 scripts/apply_skill_quality.py --check
python3 scripts/generate_agent_metadata.py --check
python3 scripts/build_index.py --check
python3 scripts/build_provenance.py --check
python3 scripts/check_release_readiness.py --strict
```

On Windows, replace `python3` with `python`. Validate the full local staging
inventory, including non-public material, with
`python scripts/validate_skills.py --all`.

When changing discovery text, UI metadata, risk, tags, or allowed tools, update
[scripts/skill_quality.py](scripts/skill_quality.py), then run:

```bash
python3 scripts/apply_skill_quality.py --write
python3 scripts/generate_agent_metadata.py --write
```

After content changes, regenerate the lock and reports before release:

```bash
python3 scripts/check_publication.py --write
python3 scripts/build_index.py --write
python3 scripts/build_provenance.py --write
```

`check_publication.py --write` regenerates the release lock. Do not edit the lock
by hand; a checked-in lock must match the published files exactly.

## Quality gates

The validation workflow runs on Linux and Windows with Python 3.10, 3.11, and
3.12. It checks:

- frontmatter, license evidence, provenance, and the public allowlist;
- reviewed discovery metadata, route coverage, and UI presentation;
- local links, referenced files, skill layout, and reference reachability;
- Markdown structure, UTF-8 encoding, whitespace, and shell/Python smoke tests;
- Python lint, regression tests, generated-report drift, the canonical
  knowledge-base manifest, and release readiness;
- immutable GitHub Actions pinning, CodeQL, gitleaks, and a clean snapshot build.

See [docs/SKILL_REVIEW.md](docs/SKILL_REVIEW.md) for the maintainer review rubric.

## Public snapshot

This repository publishes a clean snapshot, not the broad local staging
checkout. Additional unverified material may exist in a maintainer's staging
repository; it is excluded by both the allowlist and `skills/.gitignore`.

Build and validate the publishable snapshot with:

```bash
python3 scripts/build_public_bundle.py --output ../baoanskills-public
```

The builder copies only allowlisted skills and governance files, includes the
tests and development configuration, regenerates the index and provenance
reports, and runs exclusive release checks. `ctf-knowledge-base` publishes
original cards, search tooling, a tool catalog, and a path/hash manifest; the raw
`CTF本地知识库` corpus and risky attachments remain local. Never publish the
staging checkout directly. See [docs/PUBLICATION.md](docs/PUBLICATION.md) and
[docs/RELEASE.md](docs/RELEASE.md).

## License

- Repository scaffolding, scripts, documentation, and the 12 original CTF
  skills use the root [MIT License](LICENSE).
- The 24 skills derived from `zebbern/claude-code-guide` are MIT-licensed; the
  upstream notice is in
  [licenses/zebbern-claude-code-guide-MIT.txt](licenses/zebbern-claude-code-guide-MIT.txt).
- The 3 skills derived from `trailofbits/skills` are CC BY-SA 4.0. Attribution
  and the full license are preserved in [NOTICE](NOTICE) and
  [licenses/trailofbits-skills-CC-BY-SA-4.0.txt](licenses/trailofbits-skills-CC-BY-SA-4.0.txt).
  Adapted material in those skill directories must remain under CC BY-SA 4.0.

The root MIT License does not relicense third-party material. `source: original`
records the maintainer's attribution for the 12 CTF skills; no external
historical record was available to independently prove that status.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md),
[docs/ADDING_A_SKILL.md](docs/ADDING_A_SKILL.md),
[docs/SKILL_REVIEW.md](docs/SKILL_REVIEW.md),
[docs/PUBLICATION.md](docs/PUBLICATION.md), and
[docs/ROUTING.md](docs/ROUTING.md). Every public skill requires verified source,
license, evidence, authorization boundaries, and a matching lock entry.

Do not open a public issue containing live credentials, private target data, or
unpatched vulnerability details. Follow [SECURITY.md](SECURITY.md).
