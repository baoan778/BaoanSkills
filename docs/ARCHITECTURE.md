# Architecture

## Repository boundaries

The working repository may contain a large local staging inventory. The public
release contains only the skills in `release/public-skills.txt` plus repository
governance files. The local `CTF本地知识库` directory is never copied wholesale
into the public payload. The allowlisted `ctf-knowledge-base` skill may publish
maintainer-authored summaries, retrieval code, and path-only inventory
metadata; raw corpus content remains outside the release.

## Public scope control

Three files work together:

- `release/public-skills.txt` defines release membership.
- `skills/.gitignore` prevents non-allowlisted staging skills from entering Git.
- `release/provenance.lock.json` locks every file in every public skill.

Repository-wide checks are release-scoped when these files are present.
Unaudited sibling directories are ignored until they are explicitly reviewed
and allowlisted.

## Skill discovery

A skill is a directory containing `SKILL.md`:

```text
skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/
└── assets/
```

Directory names use lowercase hyphen-case and match frontmatter `name`. In a
clean public snapshot, every top-level directory under `skills/` is an
allowlisted skill.

## Progressive disclosure

- Frontmatter `name` and `description` support discovery.
- `SKILL.md` contains routing, authorization constraints, core workflow, and
  output criteria.
- `references/` contains mode-specific detail.
- `scripts/` contains deterministic helpers.
- `assets/` contains templates or other generated-output inputs.

Keep public `SKILL.md` entrypoints at or below 500 lines. New detail should go
into directly linked references when it is not needed for every invocation.

## Publication states

- `verified`: license, provenance, evidence, and modifications passed the
  repository publication checks.
- `review-required`: source, license, evidence, or modification data is
  incomplete. Such a skill stays out of the allowlist.
- `NOASSERTION`: redistribution rights are unknown. It is inventory-only and
  must never appear in a public skill file.

`verified` is a release-control state, not a legal opinion.

## Knowledge-base boundary

A path-only manifest is inventory metadata, not a redistribution license.
`ctf-knowledge-base` may publish original technique cards, case indexes,
retrieval scripts, a tool-category catalog, and relative-path/size/hash records.
It must not publish raw notes, writeup bodies, screenshots, captures, binaries,
tool archives, NASL plugins, secrets, private target data, or absolute host
paths.

## Generated artifacts

The following files are generated and must not be hand-edited:

- `docs/SKILLS_INDEX.md`
- `docs/PROVENANCE.md`
- `docs/provenance.csv`
- `release/provenance.lock.json`
- `skills/ctf-knowledge-base/references/archive/file-manifest.csv`

Regenerate them with the scripts in `scripts/` and run checks before committing.

## Clean snapshot

`scripts/build_public_bundle.py` copies the governance files and only the
allowlisted skills into a sibling `-public` directory. It regenerates release
reports and runs exclusive checks that fail if any unlisted skill directory
remains. Publish the generated snapshot rather than the staging checkout.
