# Corpus archive guide

This directory is the metadata-only archive view of the local CTF corpus. It is
safe to publish with the skill because it contains paths, sizes, categories, and
hashes, not source documents.

## Files

| File | Purpose |
|---|---|
| [file-manifest.csv](file-manifest.csv) | Deterministic inventory of every reviewed local corpus file |
| [known-gaps.md](known-gaps.md) | Missing source assets and authorized synthetic reconstruction steps |
| [tool-catalog.md](tool-catalog.md) | High-level map of the 55 top-level tool directories |
| [exclusions.md](exclusions.md) | Rules for material that must never enter the public snapshot |

## Corpus baseline

The checked-in manifest describes:

- **14,835 files**;
- **1,407 directories**;
- **3,656,564,703 bytes** (approximately 3.41 GiB);
- five categories: `topic-note`, `writeup`, `script`, `tool-guide`, and
  `toolset`.

Counts and hashes can change when the maintainer refreshes the local corpus.
Treat the manifest as the current inventory and rerun the check after any
corpus change.

## Manifest fields

| Field | Meaning |
|---|---|
| `relative_path` | POSIX-style path below the corpus root; no host prefix |
| `category` | One of the five reviewed inventory categories |
| `extension` | Lowercase final suffix, or empty when the file has none |
| `bytes` | Exact file size observed during generation |
| `sha256` | SHA-256 of the file bytes |

The category mapping is intentionally narrow:

| Top-level location | Category |
|---|---|
| Repository-root files | `topic-note` |
| `WP汇总/` | `writeup` |
| `CTF常用脚本及工具/` | `script` |
| `工具使用/` | `tool-guide` |
| `CTF工具集/` | `toolset` |

Any other top-level directory is rejected instead of silently misclassified.

## Regenerate and verify

From the repository root, with the local corpus available:

```bash
python scripts/build_kb_manifest.py --check
python scripts/build_kb_manifest.py --write
```

The default source is `CTF_KB_ROOT` when that environment variable is set,
otherwise the repository-local `CTF本地知识库` directory. To review a different
authorized copy without hard-coding a machine path:

```bash
python scripts/build_kb_manifest.py --write --source /path/to/authorized-corpus
```

The generator refuses symlinks, unsupported top-level directories, and
non-file entries. It sorts paths before writing and uses LF line endings so the
same inputs produce byte-for-byte identical output.

After a refresh, run at least:

```bash
python scripts/build_kb_manifest.py --check
python scripts/check_publication.py --check
python scripts/check_resources.py
python scripts/check_release_readiness.py --strict
```

## Interpretation and limits

- A hash confirms byte identity, not safety, authorship, correctness, or
  redistribution rights.
- The manifest is not a substitute for opening a source file and validating its
  claims in an authorized lab.
- A path can be listed while the corresponding raw file remains unavailable in
  the public package.
- A missing path means it was absent when the manifest was generated; it is not
  evidence about an external or updated copy.

See [the corpus index](../index.md), [the provenance model](../provenance.md),
[known corpus gaps](known-gaps.md), [the tool catalog](tool-catalog.md), and
[the exclusion rules](exclusions.md).
