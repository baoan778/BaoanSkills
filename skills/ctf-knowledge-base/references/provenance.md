# Provenance and trust model

The knowledge base was assembled from a local CTF study collection. It is useful as a discovery index, but it is not a uniformly reviewed or redistributable archive.

## What the public skill contains

- Original topic cards written for this repository.
- Original case-family summaries that point to relative corpus locations.
- A deterministic manifest of relative paths, categories, sizes, and SHA-256 hashes.
- Tool and archive guides that describe review boundaries.
- No raw third-party Markdown or HTML bodies.
- No screenshots, captures, binaries, installers, JAR/JRE bundles, NASL plugins, or packaged tool archives.
- No credentials, keys, certificates, environment files, or private target data.

## What the local corpus contains

The staging corpus mixes:

- maintainer-authored practice notes;
- copied or adapted study material;
- writeups and screenshots from public blogs or challenge platforms;
- scripts obtained from multiple sources;
- commercial, shareware, abandoned, or provenance-unknown tools;
- dictionaries, rules, captures, and generated files;
- broken or duplicated exports.

A path being present in the manifest does not establish that the underlying file is safe, accurate, current, or licensed for redistribution.

## Why the raw corpus is excluded

The collection is too large and heterogeneous for a responsible blanket publication decision. The current public release therefore separates:

1. **Discovery metadata** - paths, categories, sizes, and hashes.
2. **Original synthesis** - curated cards and case patterns.
3. **Raw source** - retained locally and not published.
4. **Execution** - delegated to reviewed specialized skills.

This boundary preserves the retrieval value of the collection without pretending that every historical file has a verified license.

## Hash semantics

- A SHA-256 value identifies the exact bytes observed when the manifest was generated.
- Matching hashes can support duplicate detection or confirm that a local file still matches the index.
- A hash is not a malware scan, a signature, a license review, or an endorsement.
- A zero-byte file has the SHA-256 of empty input and is still represented in the manifest for completeness.

## Content reliability

Treat corpus claims as leads, not ground truth:

- Historical challenge behavior may depend on a specific PHP, Java, Python, browser, kernel, or tool version.
- Screenshots may be cropped, stale, or missing.
- Copy-pasted payload lists often omit prerequisites and failure modes.
- Some notes depend on remote images or third-party sites that may no longer exist.
- Translation, character encoding, and filename capitalization can change tool behavior.
- Scripts may contain absolute paths, interactive prompts, network calls, or destructive cleanup.

Reproduce the minimum observation in the current authorized lab before using any technique.

## Rights and review

Before extracting more than short factual observations from a corpus file:

1. identify the original author and source when possible;
2. confirm the license or permission for the intended use;
3. avoid copying distinctive prose, images, code blocks, or challenge flags;
4. write a new explanation grounded in observed behavior;
5. record unresolved attribution or version uncertainty in the output.

If rights remain unclear, do not republish the source. Keep it local and cite only the curated card or manifest path.

The maintainers should review [the exclusions](archive/exclusions.md) and rerun the manifest check whenever the local corpus changes.
