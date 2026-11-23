# Changelog

All notable changes will be documented here. The project intends to use
[Semantic Versioning](https://semver.org/).

## [1.0.1] - 2026-11-23

### Added

- Redesigned the English and Simplified Chinese README landing pages with a
  stronger hero banner, a one-command quick start, mobile-friendly terminology
  lists, collapsible starter bundles, and a concise catalog.
- Added `docs/INSTALL.md` with platform-specific installation, archive checksum
  verification, upgrades, manual installation, and troubleshooting guidance.
- Added `scripts/check_all.py` as the canonical 19-stage validation command for
  contributors and CI-ready local checks.
- Added documentation regression coverage for the banner, installation guide,
  Chinese README skill counts, starter-bundle allowlists, and release scoping.

### Changed

- Included `README.zh-CN.md` in generated public snapshots and release archives.
- Moved `wireshark-analysis` into the tools, scanning, and supply-chain category
  in the generated skill index.
- Updated contributor and maintainer documentation to use the aggregate
  validation command.
- Moved the frontmatter migration report default to the ignored `reports/`
  directory and removed the stale report from the public documentation payload.

### Fixed

- Regenerated `docs/SKILLS_INDEX.md` so the published catalog reflects the
  current 39-skill classification and metadata.

## [1.0.0] - 2026-11-22

### Added

- Public allowlist with 39 provenance-verified skills and a file-level SHA-256
  release lock for every published file.
- Pinned upstream commits, SPDX license evidence, attribution notices, and
  modification summaries for all third-party material.
- Clean public snapshot builder with exclusive publication checks, generated
  indexes, provenance reports, and reproducible release packaging.
- Dependency-free Python installer with allowlist-only selection, destination
  control, dry-run previews, and safe update behavior.
- Installer source verification against the release provenance lock, including
  rejection of missing, extra, symlinked, or size/hash-mismatched files before
  any copy operation.
- Regression coverage for lock acceptance, tampered files, unlocked files, and
  missing-lock installation attempts.
- Maintainer documentation for architecture, authorization, routing,
  publication, release, provenance, skill review, and adding new skills.
- New original `ctf-knowledge-base` skill with 24 curated technique, case, and
tool cards; a 55-directory tool catalog; and a deterministic manifest of 14,835
local corpus paths, sizes, and hashes.
- A known-gaps card with authorized synthetic replacement steps for missing
  corpus images and remote dependencies.
- CI coverage for the canonical knowledge-base manifest, including a safe
  source-free validation mode for public snapshots.
- Deterministic `.tar.gz` and Windows-friendly `.zip` release archives with
  individual SHA-256 checksum files.
- Release workflow smoke tests that verify checksums, extract the zip, install a
  sample skill, and reject a tampered snapshot before artifacts are published.
- Regression tests for installation, routing, quality metadata, generated UI
  metadata, references, layout, workflows, CTF reference organization, corpus
  manifest generation, and knowledge-base search.
- Reviewed quality catalog for discovery descriptions, risk, tags, allowed
  tools, display names, short descriptions, and default prompts.
- Pre-commit configuration and CI coverage for Linux and Windows across Python
  3.10, 3.11, and 3.12, plus CodeQL, Dependabot, gitleaks, and tagged-release
  automation. Pinned `pre-commit` 4.6.2 because 4.7.0 requires Python 3.11 and
  would break the supported Python 3.10 matrix.

### Changed

- Ordered every `release/provenance.lock.json` file entry by POSIX relative
  path and hashed raw bytes, so the generated lock is identical on Windows and
  Linux.
- Required canonical LF line endings for release-scoped text files and license
  evidence; `check_whitespace.py --fix` performs the reviewed normalization.
- Refreshed SHA-pinned GitHub Actions for checkout, Python setup, artifact
  upload, CodeQL, and secret scanning.
- Normalized frontmatter and `agents/openai.yaml` metadata across all 39 public
  skills, including explicit risk, tags, provenance, and authorization fields.
- Replaced placeholder applicability text with skill-specific use and non-use
  guidance in 24 security-testing skills.
- Moved 107 CTF topic documents into `references/` directories and kept every
  reference directly reachable from its `SKILL.md`.
- Reworked `scanning-tools`, `wordpress-penetration-testing`, and
  `top-web-vulnerabilities` into concise entrypoints backed by detailed,
  directly linked references.
- Split 12 entrypoints above 500 lines into concise authorization/routing
  surfaces plus directly linked playbooks or field notes, preserving the full
  technical detail.
- Added a public-skill regression guard that rejects future `SKILL.md`
  entrypoints above 500 lines.
- Added an explicit resource-resolution rule for bare Markdown filenames used
  in prose, in addition to ordinary Markdown links.
- Clarified publication scope: the staging checkout is an inventory, while only
  the generated public snapshot is eligible for GitHub publication.
- Distinguished raw local CTF corpus material from publishable original cards,
  retrieval code, tool catalogs, and path-only manifest metadata.
- Consolidated duplicate routing destinations into single canonical aliases and
  added regression checks for unique request labels and destinations.

### Fixed

- Made publication drift errors identify the affected metadata field, missing
  or unexpected file, changed file record, duplicate record, or non-canonical
  order instead of reporting only a generic skill-level mismatch.
- Normalized residual CRLF line endings in four allowlisted skills before
  regenerating the provenance lock, removing Windows-only publication drift.
- Restored the missing Semgrep quick-reference and workflow documents from the
  pinned upstream commit and linked them from the skill entrypoint.
- Repaired missing or ambiguous cross-skill references in CTF forensics, misc,
  crypto, reverse, and challenge-routing material.
- Fixed the resource checker so English sentence punctuation is not treated as
  part of a referenced filename.
- Replaced the stale development-dependency comment that incorrectly claimed a
  dependency declaration existed in `pyproject.toml`.
- Prevented test and lint caches from leaking into release snapshots by
  cleaning transient artifacts after validation and rechecking the payload.
- Restored the missing `file-path-traversal` reference playbook that the skill
  entrypoint linked to.
- Made installer imports work in a bare Python environment without PyYAML;
  frontmatter parsing still reports a clear error when PyYAML is required.

### Security

- Every public skill contains an explicit authorized-use boundary.
- Public snapshots reject `NOASSERTION`, missing evidence, unpinned upstream
  sources, symlinks, personal absolute paths, and unlisted skill directories.
- Active-testing guidance requires scope, authorization, time-window, and
  stop-condition confirmation before execution.
- Raw local CTF corpus files, third-party writeup bodies, screenshots,
  binaries, tool archives, NASL content, credentials, and unrelated staging
  material remain excluded from the public payload.
- Release publication is restricted to the canonical repository and a
  semver-validated tag workflow.
- The installer refuses to copy a skill when the shipped provenance lock is
  missing, malformed, incomplete, or inconsistent with the source files.
