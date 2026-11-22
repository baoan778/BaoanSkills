# Adding a skill

## 1. Choose a discoverable name

Use lowercase letters, digits, and hyphens. Name the directory after the skill.
The directory name must exactly match frontmatter `name`, and the name must be
unique in the public allowlist.

## 2. Create the frontmatter

Third-party content must pin the exact source revision and provide license
evidence:

```yaml
---
name: example-skill
description: Explain what the skill does and when it applies.
license: MIT
allowed-tools:
  - Bash
  - Read
metadata:
  category: web-security
  risk: high
  tags:
    - example
  author: Example Author
  source: https://github.com/example/project/blob/0123456789abcdef0123456789abcdef01234567/skills/example-skill/SKILL.md
  source_repo: https://github.com/example/project
  upstream_commit: 0123456789abcdef0123456789abcdef01234567
  upstream_path: skills/example-skill/SKILL.md
  license_evidence: licenses/example-project-MIT.txt
  license_status: verified
  provenance_status: verified
  retrieved_at: '2026-11-22'
  modifications: Describe every adaptation from the upstream source.
  date_added: '2026-11-22'
---
```

The `source` value must exactly match
`<source_repo>/blob/<upstream_commit>/<upstream_path>`. The commit must be a
40-character lowercase Git SHA. Store the complete upstream license text in the
evidence file, including its copyright notice.

For maintainer-original content, use:

```yaml
license: MIT
metadata:
  author: BaoanSkills contributors
  source: original
  license_evidence: LICENSE
  license_status: verified
  provenance_status: verified
  retrieved_at: '2026-11-22'
  modifications: Original BaoanSkills content; metadata normalized; authorization boundary added.
```

Do not declare `source_repo`, `upstream_commit`, or `upstream_path` for original
content. If rights are unclear, use `license: NOASSERTION` only in local
staging and do not add the skill to the public allowlist.

## 3. Write the entrypoint

Include an explicit boundary near the top:

```markdown
> **Authorized use only.** Use this skill only in CTF environments, owned labs,
> or systems for which you have explicit written permission.
```

Also include:

- when to use and when not to use the skill;
- required inputs and authorization checks;
- the core workflow and stop conditions;
- output and verification requirements;
- direct links to every supporting reference.

Keep the entrypoint focused on shared decisions. Put conditional detail in
`references/`; do not create root-level topic documents. A `references/` file
that is not directly linked from `SKILL.md` fails validation. Bare Markdown
filenames mentioned in prose are checked too, so write `see [workflow.md](
references/workflow.md)` rather than an unresolved filename. If a script is
needed, name it in the entrypoint and add a smoke test when feasible.

## Knowledge-base skills

A knowledge-base skill is a retrieval interface, not a license to republish its
source corpus. Publish only new synthesis, search/navigation code, and
path-level metadata such as relative paths, categories, sizes, and SHA-256
hashes. Keep raw notes, writeups, images, captures, binaries, tool archives,
NASL plugins, credentials, private target data, and absolute paths out of the
skill directory.

For a corpus-backed skill:

1. Keep the source outside the public skill tree and pass it with
   `CTF_KB_ROOT` or `--source`.
2. Generate the manifest with
   `python scripts/build_kb_manifest.py --write`.
3. Review unexpected path, category, size, or hash changes; a hash is evidence
   of byte identity, not redistribution permission.
4. Link every public card from `SKILL.md` and document missing local resources
   as retrieval gaps rather than fabricating replacements.
5. Run `python scripts/build_kb_manifest.py --check` before the normal release
   checks.

Do not hand-edit generated manifests. Treat every addition as a new publication
review, even when the path is already present in the local corpus.

## 4. Add reviewed quality metadata

Discovery text, risk, tags, and allowed tools are controlled by the catalog in
[`scripts/skill_quality.py`](../scripts/skill_quality.py). Add a `SkillQuality`
entry with:

- a specific display name;
- a short description between 25 and 64 characters;
- a default prompt that names `$skill-name` and requests a concrete authorized
  outcome;
- a discriminating description, risk level, tags, and minimal tool set.

Then synchronize the generated metadata:

```bash
python scripts/apply_skill_quality.py --write
python scripts/generate_agent_metadata.py --write
```

The resulting `agents/openai.yaml` should contain specific UI text. Do not use a
generic prompt such as "complete the current authorized task" and do not use a
display name such as `Ctf Web`.

## 5. Add routing and tests

If the skill changes selection behavior, update
[`docs/ROUTING.md`](ROUTING.md) and the routing regression tests. Add tests only
for meaningful invariants or demonstrated failures; avoid tests that merely
duplicate generated prose.

Useful focused checks:

```bash
python -m pytest tests/test_routing.py
python -m pytest tests/test_quality_catalog.py
python -m pytest tests/test_skill_layout.py
```

Review the skill against [`SKILL_REVIEW.md`](SKILL_REVIEW.md) before publication.

## 6. Register the skill for publication

Only after provenance, license, quality, and safety review:

1. Add the name to `release/public-skills.txt`.
2. Add `!<name>/` and `!<name>/**` to `skills/.gitignore`.
3. Regenerate the lock and generated reports.

```bash
python scripts/check_publication.py --write
python scripts/build_index.py --write
python scripts/build_provenance.py --write
```

The publication check requires the allowlist and unignore set to match exactly.
Commit the skill, allowlist, `.gitignore`, evidence, lock, and generated reports
together.

## 7. Validate

Install the development dependencies and run the full suite:

```bash
python -m pip install -r requirements-dev.txt
python scripts/check_all.py
```

The aggregate check covers compilation, Ruff, tests, publication and provenance
drift, Markdown, links, resources, layout, generated metadata, smoke tests,
workflow pinning, and release readiness.

Finally, build a clean snapshot to prove that the published payload contains no
unlisted skills:

```bash
python scripts/build_public_bundle.py --output ../baoanskills-public
```
