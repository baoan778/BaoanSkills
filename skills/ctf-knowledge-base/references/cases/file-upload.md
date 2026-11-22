# File upload case family

Authorized CTF and owned-lab use only.

## What this family teaches

Upload challenges are layered. A file can pass validation, be stored, be retrieved, and still not execute. The solve path appears when the storage location, effective filename, parser mapping, and secondary sink are understood separately.

## Corpus anchors

- `WP汇总/ctfshow-文件上传wp.md`
- `WP汇总/文件上传/`
- `文件上传漏洞.md`
- `WP汇总/文件包含/` when upload leads into an include flow

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Layer map

| Layer | Evidence question |
|---|---|
| Client | Is the restriction only in JavaScript or the file picker? |
| Transport | Is `Content-Type` checked independently from bytes? |
| Name | Is the original name, normalized name, or suffix used at storage? |
| Content | Are magic bytes, image decode, dimensions, or re-encoding involved? |
| Storage | What is the final path, permissions, and retrieval URL? |
| Execution | Which handler parses the stored suffix or content? |
| Secondary sink | Does an include, archive, template, or desktop viewer consume it? |

## Reasoning pattern

1. Upload a harmless marker and find the stored path.
2. Change one validation property per request.
3. Compare original bytes with stored bytes.
4. Establish whether the server renames, re-encodes, or relocates the file.
5. Find the component that later executes or interprets it.
6. Prove the sink with a challenge-scoped marker.

Do not call an upload vulnerable merely because it is accepted. Execution is a separate claim.

## Common traps

- The server validates the original path but writes a normalized path.
- A blacklist misses a handler suffix or alternate case.
- Image validation and image processing use different library versions.
- `.htaccess` or server routing changes behavior only in a specific directory.
- A polyglot must satisfy both parsers, not just the first one.
- An upload path may be reachable only from an internal service.

## Next pivot

Use [file upload](../web/file-upload.md), then [file inclusion](../web/file-inclusion.md) if the stored file is included. Route the full web chain to `ctf-web`.
