---
name: ctf-knowledge-base
description: Navigate a curated CTF knowledge base covering web exploitation, PHP audit and deserialization, SQLi, SSRF, SSTI, file inclusion/upload, steganography, tool workflows, and writeup retrieval.
license: MIT
allowed-tools:
- Read
- Glob
- Grep
- Bash
metadata:
  user-invocable: 'true'
  argument-hint: '[topic or corpus question]'
  author: BaoanSkills contributors
  source: original
  category: ctf
  risk: offensive
  tags:
  - ctf
  - knowledge-base
  - web
  - stego
  - tooling
  license_status: verified
  provenance_status: verified
  retrieved_at: '2026-11-22'
  modifications: 'Original curated index derived from the maintainer local CTF corpus; raw third-party text, screenshots, binaries, credentials, and unverified redistribution material were excluded. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation.'
  license_evidence: LICENSE
---

# CTF Knowledge Base

> **Authorized use only.** Use this skill only in CTF environments, owned labs, or systems for which you have explicit written permission. A knowledge-base entry is a study aid and never grants permission to test a target.

Use this skill to find the most relevant topic card, case pattern, tool workflow, or corpus path before diving into a full technique skill. The public package ships curated summaries and metadata; it does not ship the original third-party writeups, screenshots, binaries, captures, credentials, or tool archives.

## Use and non-use

Use when:

- the user asks what the local CTF corpus contains;
- a challenge needs a quick technique map or likely next pivot;
- a tool workflow or writeup family must be located before execution;
- a specialized CTF skill needs historical examples or terminology.

Do not use when:

- the user expects a complete exploit walkthrough without a specialized skill;
- the task is a professional assessment outside an authorized CTF or lab;
- the requested action depends on redistributing unverified third-party text or binaries.

## Retrieval workflow

1. Establish the dominant signal: web primitive, steganography, archive, tool, or case family.
2. Read the matching card from the reference map below. Start with the curated card, not raw source material.
3. If the local corpus is installed, run the bundled search helper to locate related notes and writeups. Keep searches offline and authorized.
4. Correlate results with the file manifest. Use relative paths, hashes, extensions, and categories as retrieval evidence.
5. Route execution to `ctf-web`, `ctf-misc`, `ctf-forensics`, `ctf-crypto`, `ctf-pwn`, `ctf-reverse`, or the matching tool skill once the category is clear.
6. State which card and corpus paths support the answer. Distinguish source facts, inference, and untested hypotheses.

```bash
# Search case material for a phrase.
python3 scripts/search_kb.py "prototype pollution" --category writeup --context 2

# Search text notes and source snippets, but not binary tool archives.
python3 scripts/search_kb.py "php://filter" --extension md,html --max-results 10

# Search an alternate local corpus root.
CTF_KB_ROOT=/path/to/authorized-corpus python3 scripts/search_kb.py "SSTI"
```

On Windows, use `python` instead of `python3`. If the helper is unavailable and the corpus is present, use `Glob` and `Grep` against that root. Never index or quote a corpus imported from an untrusted source without reviewing it first.

## Card selection

| Signal | Start with |
|---|---|
| OS command, shell metacharacter, filter bypass | [command execution](references/web/command-execution.md) |
| PHP `serialize`, magic methods, POP chains | [deserialization](references/web/deserialization.md) |
| LFI, RFI, wrappers, log poisoning | [file inclusion](references/web/file-inclusion.md) |
| Content-type, extension, polyglot, upload chain | [file upload](references/web/file-upload.md) |
| JWT structure, `alg`, key, claim abuse | [JWT](references/web/jwt.md) |
| JavaScript prototype chain and server-side merge | [Node prototype pollution](references/web/node-prototype.md) |
| Loose comparison, PHP quirks, source review | [PHP audit](references/web/php-audit.md) |
| Union, error, blind, stacked SQL injection | [SQL injection](references/web/sqli.md) |
| Server-side URL fetch and internal reachability | [SSRF](references/web/ssrf.md) |
| Template expression evaluation and sandbox escape | [SSTI](references/web/ssti.md) |
| Image metadata, pixels, palettes, dimensions | [image steganography](references/misc/image-stego.md) |
| Audio spectrogram, waveform, LSB, MP3 | [audio steganography](references/misc/audio-stego.md) |
| ZIP, RAR, 7z, pseudo-encryption, archives | [archive analysis](references/misc/archives.md) |

## Reference map

- [Corpus index and search vocabulary](references/index.md)
- [Provenance, exclusion rationale, and trust model](references/provenance.md)
- [Known corpus gaps and synthetic replacements](references/archive/known-gaps.md)
- [Command execution](references/web/command-execution.md)
- [PHP deserialization](references/web/deserialization.md)
- [File inclusion](references/web/file-inclusion.md)
- [File upload](references/web/file-upload.md)
- [JWT](references/web/jwt.md)
- [Node.js prototype pollution](references/web/node-prototype.md)
- [PHP source audit](references/web/php-audit.md)
- [SQL injection](references/web/sqli.md)
- [SSRF](references/web/ssrf.md)
- [SSTI](references/web/ssti.md)
- [Image steganography](references/misc/image-stego.md)
- [Audio steganography](references/misc/audio-stego.md)
- [Archive analysis](references/misc/archives.md)
- [Dirsearch workflow](references/tools/dirsearch.md)
- [ffuf workflow](references/tools/ffuf.md)
- [Packet analysis workflow](references/tools/packet-analysis.md)
- [SQLMap workflow](references/tools/sqlmap.md)
- [Python CTF notes](references/tools/python-notes.md)
- [Case-family index](references/cases/index.md)
- [Command-execution case](references/cases/command-execution.md)
- [File-upload case](references/cases/file-upload.md)
- [PHP-features case](references/cases/php-features.md)
- [Deserialization case](references/cases/deserialization.md)
- [SSTI case](references/cases/ssti.md)
- [Node prototype case](references/cases/node-prototype.md)
- [Archive and manifest guide](references/archive/README.md)
- [Tool catalog](references/archive/tool-catalog.md)
- [Corpus exclusion rules](references/archive/exclusions.md)

## Evidence standard

- Prefer reproducible observations over copied payload lists.
- Record the tool version when behavior depends on flags or output format.
- Use synthetic placeholders in notes and examples; never add live secrets or private target data.
- Treat a manifest hash as file identity, not as a safety or license verdict.
- Do not present a writeup path as a runnable script without inspecting the source and its dependencies.

## Output contract

Return a compact answer with:

1. the selected card or case family;
2. the relevant relative corpus paths, when a local corpus is available;
3. the technique logic and next verification step;
4. the specialized skill to use for execution;
5. any provenance, licensing, or version uncertainty.

Stop before active testing when authorization is absent. Stop before republishing content when its license or source is unclear. If the corpus is not installed, continue with the curated cards and the checked-in manifest; do not invent raw file contents.
