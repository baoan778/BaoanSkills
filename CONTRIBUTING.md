# Contributing

Thank you for improving BaoanSkills. Contributions must be useful in an
authorized security context and must not provide instructions for attacking
systems without permission.

## Before you start

Install the development dependencies and local hooks:

```bash
python -m pip install -r requirements-dev.txt
python -m pre_commit install
python -m pytest
```

Read [`docs/SKILL_REVIEW.md`](docs/SKILL_REVIEW.md) before creating or
substantially changing a public skill.

## Public scope

The repository distinguishes between a broad local staging inventory and the
public release. Only skills listed in `release/public-skills.txt` are published.
Adding a directory under `skills/` does not add it to the public release.

Do not add a skill to the allowlist merely to make a validation pass. The
allowlist is a reviewed publication decision.

## Skill requirements

Every new or substantially changed public skill must include:

- a lowercase hyphenated `name` matching the directory;
- a discriminating `description` with an explicit boundary where useful;
- `license`, `author`, and `source` metadata;
- a clear **Authorized use only** boundary and explicit non-goals;
- required inputs, a core workflow, stop conditions, and output verification;
- valid relative links and existing referenced resources;
- `agents/openai.yaml` for UI discovery.

Public skills also require these metadata fields under `metadata`:

```yaml
license_status: verified
provenance_status: verified
license_evidence: licenses/example-license.txt
retrieved_at: '2026-11-22'
modifications: Describe all modifications from the upstream source.
```

`modifications` must describe changes rather than claim the content is
unmodified when it is not.

## Quality and routing metadata

Discovery text, UI presentation, risk, tags, and allowed tools are controlled by
[`scripts/skill_quality.py`](scripts/skill_quality.py). Add or update the
catalog entry, then synchronize frontmatter and `agents/openai.yaml`:

```bash
python scripts/apply_skill_quality.py --write
python scripts/generate_agent_metadata.py --write
```

Display names must be specific. Short descriptions must remain between 25 and
64 characters. Default prompts must name the skill with `$skill-name` and
describe a concrete authorized outcome. Update [`docs/ROUTING.md`](docs/ROUTING.md)
and routing tests when selection behavior changes.

## References and scripts

Keep the entrypoint focused on shared routing, safety, workflow, and output
requirements.

- Put conditional detail under `references/`.
- Do not create root-level topic documents other than `SKILL.md`.
- Link every reference directly from `SKILL.md`.
- Ensure every Markdown filename mentioned in prose, including bare names such
  as `workflow.md`, resolves from the skill root or the current reference.
- Name any required script in the entrypoint.
- Keep `SKILL.md` below the hard layout limit; move detail into references before
  the file becomes a context-budget problem.

The layout checker reports advisory warnings above 500 lines and fails above
700 lines or 6,000 words.

## Third-party content

For third-party content, record all of the following:

- the author and upstream repository;
- a 40-character lowercase Git commit;
- the exact upstream path;
- a source URL in the form
  `<source_repo>/blob/<upstream_commit>/<upstream_path>`;
- an accepted SPDX license identifier;
- license evidence stored under `licenses/`;
- the retrieval date and a concrete modification summary.

Copy the complete upstream license text into the evidence file and preserve
copyright notices. If redistribution rights are unclear, do not publish the
skill. Keep it as local staging material or open an issue for review.

For maintainer-original content, use `source: original` and
`license_evidence: LICENSE`. Do not set `source_repo`, `upstream_commit`, or
`upstream_path` for original content.

## Knowledge-base contributions

The local CTF corpus is source material, not a publishable skill. A public
knowledge-base skill may include original summaries, search/navigation code, a
tool-category catalog, and relative-path/size/hash metadata. Do not include raw
notes, writeup bodies, screenshots, captures, binaries, tool archives, NASL
plugins, credentials, private target data, or host-specific paths.

Generate and verify the metadata-only manifest with:

```bash
python scripts/build_kb_manifest.py --write
python scripts/build_kb_manifest.py --check
```

Review the diff for unexpected paths or size changes. A SHA-256 hash proves byte
identity only; it is not a license, safety check, or authorship attestation.

## Authorization boundary

Every public `SKILL.md` must include the phrase **Authorized use only** near the
top and explain that the skill applies only to CTF environments, owned labs, or
systems covered by explicit written authorization. Do not treat a tool's
presence or a public target as permission to test it.

## Adding to the public allowlist

A skill enters the public release only after provenance, license, quality, and
safety review:

1. Add the skill directory under `skills/`.
2. Add its name to `release/public-skills.txt`.
3. Add both `!<name>/` and `!<name>/**` to `skills/.gitignore`.
4. Add the quality catalog entry and regenerate UI metadata.
5. Update routing and meaningful regression tests.
6. Regenerate the release lock, index, and provenance reports.
7. Run the full validation suite.

The publication check verifies that the allowlist and `skills/.gitignore` have
exactly the same unignore set.

```bash
python scripts/check_publication.py --write
python scripts/build_index.py --write
python scripts/build_provenance.py --write
```

Review the resulting changes before committing. The lock records hashes for
every file in every allowlisted skill, so any later content change requires
another lock update.

## Validation

Run the canonical release-scoped suite from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python scripts/check_all.py
```

`check_all.py` runs compilation, Ruff, pytest, provenance and publication
checks, generated-file drift checks, Markdown/link/resource/layout checks, smoke
tests, workflow pinning, and release readiness. The same stages are visible in
[`.github/workflows/validate.yml`](.github/workflows/validate.yml). Run an
individual command from that workflow when you need to debug one failure.

To inventory every local staging skill, use:

```bash
python scripts/validate_skills.py --all
```

That command is not a publication gate and may report expected failures for
unreviewed staging content.

## Generated files

Do not hand-edit these generated artifacts:

- `docs/SKILLS_INDEX.md`
- `docs/PROVENANCE.md`
- `docs/provenance.csv`
- `release/provenance.lock.json`
- `skills/ctf-knowledge-base/references/archive/file-manifest.csv`

Regenerate them with the scripts in `scripts/`.

## Pull requests

Keep changes focused. A publication-related pull request should state:

- which skills are added, changed, or removed from the allowlist;
- the source, commit, license, and evidence for third-party content;
- whether any CC BY-SA material was adapted;
- which tests or validation checks demonstrate the change;
- confirmation that no credentials, private target data, or raw local
  knowledge-base files are included; original cards and path-only manifests are
  allowed.

Never commit the raw local `CTF本地知识库` directory or unrelated staging
skills. The reviewed `ctf-knowledge-base` skill directory is the only public
knowledge-base artifact.
