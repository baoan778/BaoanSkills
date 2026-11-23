# Release process

Releases are built from a clean public snapshot, never from the broad local
staging checkout.

## Preconditions

- CI is green on the release commit.
- `release/public-skills.txt` contains only reviewed skills.
- `release/provenance.lock.json` matches every published skill file.
- Generated index and provenance reports are current.
- No published skill has `license: NOASSERTION`.
- Third-party licenses, pinned commits, evidence, and notices are current.
- No credentials, private target data, personal absolute paths, or raw local
  knowledge-base content are present. The allowlisted `ctf-knowledge-base` cards,
  retrieval code, and path-only manifest are expected.
- Release-scoped text files and license evidence use canonical LF line endings,
  and the provenance lock uses POSIX relative-path ordering.
- The changelog is updated.
- The release tag uses `vMAJOR.MINOR.PATCH` or a valid prerelease suffix.

## Build and validate

Install the development dependencies and run the source checks first:

```bash
python -m pip install -r requirements-dev.txt
python scripts/check_all.py
```

The aggregate checker runs the release-scoped validation stages used by CI.

Build a fresh snapshot:

```bash
python scripts/build_public_bundle.py --output ../baoanskills-public
```

To replace a previously generated snapshot, use `--force` only after verifying
the destination is the expected `baoanskills-public` directory. The builder
fails on source publication drift and runs exclusive checks on the output,
including the copied tests and development configuration.

The installer verifies every requested skill file against the snapshot's
`release/provenance.lock.json` before copying. Treat the lock as the published
integrity manifest: do not edit it to make a drifted checkout installable.

If Windows line endings are reported, run `python scripts/check_whitespace.py
--fix`, review the normalized files, regenerate the lock with
`python scripts/check_publication.py --write`, and rerun all checks.

## Release automation

[`release.yml`](../.github/workflows/release.yml) runs when a `v*` tag is pushed
to `baoan778/BaoanSkills`. It:

1. validates the tag format;
2. installs the pinned development dependencies;
3. builds and validates the clean public snapshot;
4. creates a deterministic `baoanskills-release.zip` archive and a
   `SHA256SUMS` manifest;
5. verifies the manifest, extracts the zip, installs a sample skill, and
   confirms that a tampered snapshot is rejected without creating a target;
6. uploads the zip and checksum manifest to the workflow run;
7. creates a GitHub release with generated notes, the zip, and the manifest.

Only create the tag after the release commit is merged and the validation and
CodeQL checks are green. Sign the tag when a signing key is available.

The workflow is limited to the canonical repository. Forks and local staging
checkouts cannot create an official release from it.

## Repository settings

These controls live in GitHub settings rather than repository files:

- protect `main` and require the `validate` and CodeQL checks;
- require a pull request and maintainer approval before merging;
- enable GitHub Security Advisories and secret scanning;
- require signed commits or signed tags when the maintainer workflow supports
  them;
- restrict release creation to the release workflow when organization policy
  permits it.

## Verify downloaded artifacts

Linux and macOS:

```bash
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c SHA256SUMS
else
  shasum -a 256 -c SHA256SUMS
fi
```

Windows PowerShell:

```powershell
$line = Get-Content .\SHA256SUMS | Where-Object { $_ -match '\s+baoanskills-release\.zip$' }
if (-not $line) { throw 'SHA256SUMS does not list baoanskills-release.zip' }
$expected = ($line -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash .\baoanskills-release.zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'Archive checksum mismatch' }
```

Releases built by this workflow contain only the ZIP and its `SHA256SUMS`
manifest. The ZIP contains the `baoanskills-public` directory as its single
top-level payload. The `v1.0.1` release predates this layout and keeps its
legacy assets unchanged.

The checksum in `SHA256SUMS` protects transfer integrity. The embedded provenance
lock detects per-file drift inside the snapshot, but it is not a cryptographic
signature; verify release provenance separately when that assurance is needed.

## Publish

1. Publish the contents of `baoanskills-public` as the public repository root or
   use the workflow release archive.
2. Do not publish ignored staging directories from the development checkout.
3. Include the generated `NOTICE`, `docs/PROVENANCE.md`, and
   `docs/provenance.csv`.
4. State that the three Trail of Bits-derived skills remain CC BY-SA 4.0.
5. Include migration notes, known limitations, and the authorization policy in
   the release notes.
6. Verify the published tree contains exactly the allowlisted skill directories.
7. Confirm `ctf-knowledge-base` contains only curated cards, retrieval tooling, a
   tool catalog, and a path-only manifest, with no raw corpus files.

A local secret scan before publication is recommended when gitleaks is
installed:

```bash
gitleaks dir ../baoanskills-public --redact --verbose
```

## Post-release

- Confirm the tagged tree still passes the exclusive publication checks.
- Verify the release archive contains no unlisted skills or raw local
  knowledge-base files. Curated `ctf-knowledge-base` references and its path-only
  manifest are allowed.
- Verify the attached `SHA256SUMS` manifest against the attached ZIP.
- Keep the previous release available if users need to roll back.
- If a secret is discovered, revoke it first and then remove it from history.
