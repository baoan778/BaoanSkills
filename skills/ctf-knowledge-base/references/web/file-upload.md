# File upload

Authorized CTF and owned-lab use only.

## Signals

- The application accepts a file and later serves, parses, includes, or executes it.
- Validation is described in client JavaScript, MIME headers, extensions, magic bytes, or image dimensions.
- The filename is preserved, normalized, randomized, or written into a predictable directory.
- A secondary feature can read the uploaded file through an include, archive, template, or media parser.

## Detection layers

| Layer | Question | Evidence |
|---|---|---|
| Client UI | Is `accept` or JavaScript validation the only control? | Direct request differs from browser behavior |
| Transport | Is `Content-Type` trusted? | Server response after changing the header |
| Name | Is a blacklist, whitelist, or suffix check used? | Accepted/rejected filename and stored name |
| Content | Are magic bytes, image decode, or parser output checked? | Re-encoded file or validation error |
| Storage | Where is the file written and under what name? | Stable retrieval path and server headers |
| Execution | Is the file interpreted by a web server or secondary parser? | Controlled marker is evaluated |

Do not treat an accepted upload as code execution. Prove the storage and execution stages separately.

## Analysis workflow

1. Upload a harmless text or image file and identify the stored path, name, and response headers.
2. Change one validation-relevant property at a time: extension, MIME type, magic bytes, dimensions, and trailing bytes.
3. Determine whether the server re-encodes, renames, or relocates the file.
4. Test whether a server configuration file, archive member, or include path can turn the stored content into execution.
5. Keep the marker non-destructive and scoped to a file you created.
6. Capture the request, response, stored bytes, and evidence that the marker was evaluated.

## Common defense gaps

- front-end-only extension checks;
- trusting `Content-Type` without content inspection;
- blacklist omissions and case or separator normalization differences;
- validation of the original name but storage of a normalized name;
- image validation followed by use of the original bytes;
- predictable upload directories with executable server mappings;
- archive extraction that preserves traversal or overwrites a target;
- permissive server configuration for `.htaccess`, handler suffixes, or alternate interpreters.

## Polyglot reasoning

A polyglot file satisfies more than one parser. When investigating one:

- determine which parser validates the file;
- determine which parser later consumes it;
- keep the file within the challenge's size and format constraints;
- verify the actual execution path rather than relying on an online polyglot generator;
- record the byte offsets or structural features that matter.

## Image re-rendering

If the application validates an image and then re-renders it:

- compare the bytes before and after the round trip;
- identify preserved metadata, comments, palettes, trailing data, or appended archives;
- check whether the re-encoded result is still accepted by the execution sink;
- do not assume an original payload survives image processing.

## Evidence standard

- Original and stored filename.
- Validation layer observed.
- Exact stored path and retrieval response.
- Whether the server re-encoded or relocated content.
- The execution sink and a harmless proof marker.
- Relevant server or application configuration.

## Pivot

Use [file inclusion](file-inclusion.md) for log, session, archive, or wrapper chains. Use `ctf-web` for the surrounding request workflow and `ctf-reverse` if a custom file format must be reversed before upload.
