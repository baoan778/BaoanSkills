# Publication model

BaoanSkills keeps a broad local staging inventory but publishes only an
explicitly reviewed subset. The staging checkout and the public snapshot are not
the same artifact.

## Source of truth

The following files define the public release:

- `release/public-skills.txt` is the authoritative allowlist.
- `scripts/skill_quality.py` is the reviewed source of discovery text, risk,
  tags, and allowed tools.
- `skills/.gitignore` hides every local staging skill that is not allowlisted.
- `release/provenance.lock.json` records the license evidence and SHA-256 hashes
  of every file in every allowlisted skill.

Do not infer release scope from the number of directories under `skills/`.
In the maintainers' staging checkout, the current inventory contains 169 local
skill directories and the public allowlist contains 39. The remaining 130
directories are staging material that has not met the publication requirements
and are absent from the clean snapshot.

## Publication requirements

A skill may enter the allowlist only when all of the following are true:

- `license_status` and `provenance_status` are both `verified`;
- the license is an accepted identifier such as `MIT` or `CC-BY-SA-4.0`, not
  `NOASSERTION`;
- `author`, `source`, `license_evidence`, `retrieved_at`, and `modifications`
  are documented;
- third-party content has a pinned `source_repo`, 40-character lowercase
  `upstream_commit`, `upstream_path`, and a source URL that exactly matches the
  pinned repository, commit, and path;
- license evidence is stored under `licenses/` and its SHA-256 is locked;
- the skill body contains an explicit **Authorized use only** boundary;
- no allowlisted skill file contains `NOASSERTION`;
- no symlinks, credentials, private target data, or machine-specific personal
  paths are present;
- all referenced resources exist and all skill files match the release lock.

Original skills use `source: original` and cite the repository `LICENSE`. They
must not declare upstream repository fields. The 12 original CTF skills are
maintainer-attributed originals; no independent historical record was available
to prove that status, and that limitation is recorded in the generated
provenance inventory.

## Licensing boundaries

The root MIT License covers maintainer-originated scaffolding, scripts,
documentation, and the 12 original CTF skills. It does not override third-party
rights.

- The 24 skills derived from `zebbern/claude-code-guide` are MIT-licensed. The
  upstream copyright and license text is preserved in
  `licenses/zebbern-claude-code-guide-MIT.txt`.
- The 3 skills derived from `trailofbits/skills` are licensed under CC BY-SA
  4.0. Attribution and the full license are retained in `NOTICE` and
  `licenses/trailofbits-skills-CC-BY-SA-4.0.txt`. Adapted material in those
  skill directories must remain available under CC BY-SA 4.0.

See `NOTICE` and the generated `docs/PROVENANCE.md` for the authoritative
attribution details.

### Local corpus boundary

The local `CTF本地知识库` directory is staging input, not a public skill. The
allowlisted `ctf-knowledge-base` skill may publish maintainer-authored cards,
retrieval code, a tool-category catalog, and path-only manifest metadata. It
must not publish raw notes or writeups, screenshots, captures, binaries, tool
archives, NASL plugins, credentials, private target data, or machine-specific
absolute paths. A SHA-256 value establishes byte identity only; it is not
evidence of safety, authorship, or redistribution rights.

## Lock workflow

Review the skill and its evidence before adding it to the allowlist. Then run:

```bash
python scripts/check_publication.py --write
python scripts/check_publication.py --check
```

`--write` regenerates `release/provenance.lock.json`; `--check` fails on any
allowlist drift, metadata drift, evidence hash drift, or file hash drift. Commit
the allowlist, `.gitignore`, metadata, evidence, and lock together.

## Validation scopes

Use the normal checks in the staging checkout:

```bash
python -m pytest
python -m ruff check scripts tests
python scripts/validate_skills.py --strict
python scripts/build_kb_manifest.py --check
python scripts/check_publication.py --check
python scripts/check_workflows.py
python scripts/check_links.py
python scripts/check_whitespace.py
python scripts/check_markdown_structure.py
python scripts/check_resources.py
python scripts/check_skill_layout.py
python scripts/check_encoding.py
python scripts/smoke_test_scripts.py
python scripts/apply_skill_quality.py --check
python scripts/generate_agent_metadata.py --check
python scripts/build_index.py --check
python scripts/build_provenance.py --check
python scripts/check_release_readiness.py --strict
```

When the raw `CTF本地知识库` corpus is present, `build_kb_manifest.py --check`
regenerates the manifest and compares every path, size, and hash. In CI or a
public snapshot where the corpus is intentionally absent, the same command
validates the committed manifest's canonical CSV structure, sorted unique
relative paths, categories, extensions, byte counts, and SHA-256 format without
redistributing corpus content.

Use the exclusive checks only in a clean public snapshot, where no unlisted
skill directories may exist:

```bash
python scripts/check_publication.py --check --exclusive
python scripts/check_release_readiness.py --strict --exclusive
```

The default scanners are release-scoped. They inspect public skills and
repository governance files while ignoring unaudited staging directories.
`python scripts/validate_skills.py --all` is an inventory helper, not a
publication gate.

## Build the public snapshot

Never publish the staging checkout directly. Generate a payload that contains
only allowlisted skills and the required governance files:

```bash
python scripts/build_public_bundle.py --output ../baoanskills-public
```

The builder:

1. verifies the source allowlist and release lock;
2. copies governance files, scripts, tests, development configuration,
   evidence, and only the 39 allowlisted skills;
3. runs lint, tests, quality synchronization, and workflow pinning checks;
4. regenerates the skill index and provenance reports;
5. runs strict, exclusive publication, layout, link, whitespace, resource,
   encoding, script, and readiness checks;
6. removes transient caches created by those checks and reruns the exclusive
   publication check on the clean payload.

Publish the resulting directory, not the staging checkout. The snapshot contains
a `.publication-snapshot` marker to make its role explicit.

## Exclusions and review queue

Raw local knowledge-base files, third-party writeup bodies, screenshots,
binaries, tool archives, NASL content, credentials, and material with uncertain
redistribution rights remain outside the public allowlist. Curated original
cards, retrieval code, and a path-only manifest may be published because they do
not reproduce the raw corpus. Skills with `license: NOASSERTION`, incomplete
source data, missing evidence, or unverified embedded third-party content also
remain outside the allowlist, as do skills whose upstream history could not be
established.

Removing an entry from the allowlist is a release-scope change. Also remove its
unignore rules from `skills/.gitignore`, regenerate the lock, and rerun the full
validation suite.
