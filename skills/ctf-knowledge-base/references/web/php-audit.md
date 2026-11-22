# PHP source audit

Authorized CTF and owned-lab use only.

## Objective

Read the supplied PHP application as a data-flow problem. The goal is to connect an externally controlled value to a security-sensitive operation and explain the conditions under which the connection succeeds.

## Build a source map

1. List entry points: query, body, cookies, headers, files, sessions, environment, and included configuration.
2. Find normalization and validation between input and sink.
3. Enumerate classes, autoloaders, includes, and framework bootstrapping.
4. Identify dangerous sinks and the exact data they receive.
5. Check whether error handling, type juggling, variable indirection, or filesystem behavior creates an alternate path.

## Input-to-sink checklist

| Source | Typical sink | Review question |
|---|---|---|
| Request parameter | `include`, `require`, file read/write | Is the path canonicalized, prefixed, or allowlisted? |
| Request value | `system`, `exec`, `shell_exec`, `popen`, backticks | Is the value an argument, a command string, or code? |
| Serialized data | `unserialize`, PHAR metadata | Which classes and magic methods become reachable? |
| Template value | template engine render | Is the value treated as data or template source? |
| Header or host | URL fetch, redirect, mail, logging | Is the destination parsed and allowlisted? |
| Uploaded file | move, include, archive extraction | Where is it stored and which parser later consumes it? |
| SQL fragment | query builder or raw SQL | Is the value bound as a parameter or concatenated? |

## PHP behavior points

| Feature | CTF-relevant question |
|---|---|
| Loose comparison | Does `==`, `in_array`, or a switch make different strings equivalent? |
| Numeric strings | Does PHP version change the interpretation of the value? |
| `strcmp`, `preg_match`, arrays | Can the expected type be changed so validation returns unexpectedly? |
| Variable variables | Can a key in user-controlled data select or overwrite a sensitive variable? |
| `extract`, `parse_str` | Can input overwrite configuration or authentication state? |
| `assert` or dynamic calls | Is input interpreted as code or as a callable name? |
| `preg_replace` with `e` | Is the application old enough to evaluate replacement text? |
| `is_file`, `file_exists` | Can validation and later open disagree because of a wrapper or race? |
| `disable_functions` | Are only selected functions disabled while equivalent primitives remain? |
| PHP filter chains | Can an `iconv` chain expose source under the target's exact version and converters? |

These are hypotheses. Confirm behavior with the supplied PHP version and configuration instead of assuming that a common trick applies.

## File and include audit

- Record the include path base, current working directory, and any prefix or suffix.
- Check whether null bytes, stream wrappers, path normalization, or absolute paths are accepted on the target version.
- Distinguish LFI, RFI, source disclosure, and code execution.
- For log or session poisoning, prove that the injection reaches a file the include sink can read.
- For uploads, prove storage, name control, parser mapping, and include reachability separately.

See [file inclusion](file-inclusion.md), [file upload](file-upload.md), and [deserialization](deserialization.md) for the corresponding chains.

## Command and code execution audit

- Determine whether the input is concatenated into a shell string or passed as an argument vector.
- List escaping functions and their exact call order.
- Check for shell metacharacters, newline handling, environment differences, and output suppression.
- For an `eval`-like sink, distinguish PHP code evaluation from shell execution.
- For no-output cases, prefer a local timing or file marker over a remote side channel.
- Do not use an external callback unless the challenge scope permits it.

## Deserialization audit

1. Find the decoder and its reachable object types.
2. Map magic methods to the call graph.
3. Confirm property visibility, class name, and serialized string lengths.
4. Check whether PHAR metadata is touched by a filesystem function.
5. Use a harmless property marker before targeting a sensitive sink.

## Verification standard

- Cite the file and function that establishes each data-flow hop.
- State the PHP version and relevant configuration.
- Show a failing control and a succeeding observation.
- Avoid relying on a copied gadget list for a different application build.
- Keep any file created for proof inside the challenge workspace.

## Pivot

Use [JWT](jwt.md) for token parsing, [SQL injection](sqli.md) for database branches, and `ctf-web` for the HTTP workflow. Route binary or custom codec analysis to `ctf-reverse`.
