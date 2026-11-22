# File inclusion

Authorized CTF and owned-lab use only.

## Signals

- A parameter selects a template, language file, log, cache entry, or path.
- The application appends or prefixes an extension.
- Error messages reveal the resolved path or include function.
- PHP wrappers such as `php://`, `file://`, `data://`, or `phar://` reach a filesystem or stream API.
- A user-controlled value is concatenated into `include`, `require`, `include_once`, or `require_once`.

## First questions

1. Is the inclusion local or remote?
2. Is the path absolute, relative, normalized, or truncated?
3. Is an extension or directory prefix added?
4. Which wrappers are enabled?
5. Is the included content executed, displayed, or only read?
6. Can a controlled file be created in a readable location?

## Analysis workflow

1. Use a harmless existing file to prove inclusion and identify the base directory.
2. Test one path-normalization boundary at a time.
3. If a wrapper is accepted, determine whether it reads, encodes, writes, or executes.
4. Map every location where the application writes attacker-influenced data: logs, sessions, uploads, caches, and temporary files.
5. Prove code execution with a non-destructive marker before reading sensitive files.
6. Record the exact request, response, include path, and relevant source line.

## Wrapper reasoning

| Wrapper | Useful question |
|---|---|
| `php://filter` | Can the target source be transformed or disclosed? |
| `php://input` | Is request-body inclusion enabled and reachable? |
| `data://` | Is remote-style inclusion permitted, and how is encoding handled? |
| `phar://` | Does a filesystem operation trigger metadata deserialization? |
| `file://` | Is local file disclosure possible without execution? |
| `zip://` | Can an archive member be mounted or included? |

Wrapper support is configuration- and version-dependent. Confirm behavior instead of assuming a universal payload.

## Log and session poisoning

When an application includes a file that can contain user input:

- identify a log file whose path is predictable and readable;
- determine how newlines, quotes, and PHP tags are encoded in that log;
- use a harmless marker that is valid in the included context;
- verify the marker executes rather than merely appears;
- clean up only files you created inside the lab.

For sessions, inspect the session save path, serialization format, cookie-controlled session identifier, and whether uploaded or supplied content reaches the session file.

## Prefix, suffix, and traversal controls

- Determine whether `../` is normalized before or after validation.
- Check whether the application uses string replacement, basename, realpath, or a whitelist.
- Test null-byte and truncation behavior only on historical runtimes where it is plausible.
- URL encoding, double encoding, path separators, and Unicode normalization can affect the parser differently from the validator.
- Do not enumerate unrelated system paths; stay inside the challenge scope.

## Evidence standard

- Baseline response versus included response.
- Exact resolved path or wrapper behavior.
- A marker that proves execution or disclosure.
- Relevant source snippet and runtime version.
- Any failed hypothesis needed to distinguish local from remote inclusion.

## Pivot

Use [PHP source audit](php-audit.md) when a source tree is available, [file upload](file-upload.md) when the prerequisite is writing a file, [deserialization](deserialization.md) for PHAR metadata chains, and `ctf-forensics` when the hard part becomes log or artifact reconstruction.
