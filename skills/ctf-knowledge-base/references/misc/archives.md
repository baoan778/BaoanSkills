# Archive analysis

Authorized CTF and owned-lab use only.

## Safety first

Archives can contain absolute paths, traversal entries, symlinks, nested bombs, or executable content. Treat every challenge archive as untrusted.

- Inspect the listing before extraction.
- Extract into a new empty challenge directory.
- Keep size and time limits.
- Do not execute extracted installers, scripts, or shortcut files.
- Do not follow symlinks created by the archive.

## Identify and list

```bash
file challenge.zip
zipinfo -v challenge.zip
7z l -slt challenge.zip
```

For RAR or 7z, use the matching `unrar` or `7z` listing mode and record the tool version. A file extension is not proof of the actual format.

## ZIP structure

A ZIP file commonly contains:

1. local file headers and file data;
2. a central directory describing names and offsets;
3. an end-of-central-directory record, optionally followed by comments or another archive.

Useful fields include compression method, general-purpose flags, CRC-32, compressed size, uncompressed size, local header offset, filename, and comment. Review both local and central metadata when a tool reports a malformed archive.

## RAR and 7z structure

- Confirm the signature and archive version.
- Inspect encrypted headers, solid-block behavior, recovery records, and volume naming.
- Check whether the archive is split, nested, or concatenated.
- Treat a reported password failure differently from corruption or unsupported compression.

## Common CTF families

| Family | Core question |
|---|---|
| Fake or removed encryption | Do local and central flags disagree, and does a parser accept the corrected state? |
| CRC-only verification | Does the small search space come from an unknown byte or filename, not the password? |
| Known-plaintext attack | Do you possess a correctly compressed copy of a file inside the encrypted archive? |
| Password guessing | Is a challenge-owned wordlist or explicit clue supplied? |
| Nested archive | What is the actual layer order, and does each layer change format? |
| Split archive | Are volumes complete, consistently named, and from the same archive? |
| Archive comment or metadata | Does the comment, extra field, or filename encode the next clue? |
| Archive traversal | Does an entry resolve outside the extraction directory? |
| Compression bomb | Does declared or expanded size exceed the challenge limit? |
| Concatenated data | Is there a second format after the end record? |

## Controlled extraction

After reviewing the listing, extract with the safest available mode into a dedicated directory. If the archive contains unexpected links or paths, stop and analyze it without extraction.

Record:

- entry names and ordering;
- compression methods;
- encryption flags;
- CRC and size values;
- extracted-file hashes;
- any path-normalization or overwrite behavior;
- the tool and version used.

## Password work

Password recovery is appropriate only for a challenge archive or explicit authorization. Before running a candidate search:

1. estimate the key space;
2. use a challenge-provided dictionary or a small documented candidate set;
3. set a time limit;
4. avoid high concurrency that exhausts the workstation;
5. stop when the intended marker is recovered.

Do not download unrelated breach corpora or target a third-party archive.

## Evidence standard

- Original archive hash and format.
- Listing and selected structural fields.
- Extraction tool, version, and destination.
- Whether encryption was real, malformed, or only partially applied.
- The recovered filename or marker and a second verification step.
- No assumption that a hash match proves legitimate ownership.

## Pivot

Use [image steganography](image-stego.md) or [audio steganography](audio-stego.md) when an extracted file changes category. Use `ctf-misc` for puzzle-layer routing and `ctf-forensics` for disk or memory artifacts.
