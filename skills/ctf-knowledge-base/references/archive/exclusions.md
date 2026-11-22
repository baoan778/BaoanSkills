# Corpus exclusions

The public `ctf-knowledge-base` skill deliberately stops at discovery metadata
and original synthesis. The following material stays local even when it appears
in the corpus manifest.

## Never publish

| Class | Examples | Reason |
|---|---|---|
| Executables and installers | `.exe`, `.dll`, `.msi`, `.apk`, `.jar`, `.bin`, `.iso`, disk images | Unsafe to run, difficult to review, and often subject to separate terms |
| Tool archives and bundled dependencies | ZIP/RAR/7z toolsets, dictionaries, rules, JREs, JARs, runtimes | The corpus does not establish redistribution or support scope |
| Scanner content | NASL plugins, exploit scripts, signatures, generated scanner output | May encode third-party code, target data, or obsolete offensive content |
| Screenshots and captures | PNG/JPEG/GIF, PCAPs, audio, video, challenge attachments | May contain flags, personal data, target data, or copied third-party material |
| Credentials and secrets | Passwords, API keys, tokens, cookies, private keys, certificates, `.env` files | Disclosure or misuse risk |
| Private target data | Internal hostnames, IP inventories, customer names, logs, findings, reports | Privacy and authorization boundaries |
| Machine-specific metadata | Absolute home paths, usernames, mounted-drive labels, temporary paths | Leaks maintainer identity or local configuration |
| Unknown or commercial software | Shareware, patched tools, abandoned binaries, unclear-license packages | No reliable public redistribution decision |
| Symlinks and junctions | Links into another checkout, home directory, or network share | Breaks snapshot determinism and can leak external files |

The file manifest may still contain a relative path, size, and hash for an
excluded local file. That is inventory evidence, not permission to publish or
run the file.

## Excerpts and adapted text

A file that is safe to read is not automatically safe to republish. Before
turning corpus prose, diagrams, code, or tables into a public card:

1. identify the original author and source where possible;
2. verify the license or permission for the intended reuse;
3. avoid distinctive wording, long code excerpts, challenge flags, and copied
   screenshots;
4. write a new explanation around behavior you can reproduce;
5. record unresolved attribution in the output.

If those checks fail, keep the source local. Cite the curated card and the
relative manifest path instead of reproducing the source.

## Import checklist

Before adding a new corpus file family:

- confirm the top-level directory is supported by the manifest generator;
- scan names and contents for secrets and personal paths;
- reject symlinks, executable payloads, and unknown archives;
- decide whether the public artifact is a new card, a path-only index, or no
  publication at all;
- regenerate the manifest and run the release checks;
- review the public snapshot, not the staging checkout.

Useful commands:

```bash
python scripts/build_kb_manifest.py --write
python scripts/build_kb_manifest.py --check
python scripts/check_release_readiness.py --strict
```

## Stop conditions

Stop and leave the material out when:

- the license or permission cannot be established;
- the content contains live credentials, keys, or private target data;
- the only useful public artifact would be a copied binary or full writeup;
- the source path cannot be represented without an absolute host path;
- a bundled tool would need to be executed to explain the technique;
- the maintainer cannot describe what changed and why it is safe to publish.

See [the archive guide](README.md), [the tool catalog](tool-catalog.md), and
[the provenance model](../provenance.md).
