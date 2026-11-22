# Case-family index

Authorized CTF and owned-lab use only.

These cards summarize recurring reasoning patterns from the local corpus. They intentionally omit copied writeup prose, flags, credentials, screenshots, and ready-to-run exploit payloads. Use them to choose the next evidence question, then open the cited local path only when the corpus is available and reviewed for the current lab.

## Families

| Family | Pattern | Card | Typical starting evidence |
|---|---|---|---|
| Command execution | Input reaches a command or code sink through a filter chain | [Command execution](command-execution.md) | Source function, command grammar, output channel |
| File upload | Validation, storage, and execution are separate layers | [File upload](file-upload.md) | Stored filename/path and server parser |
| PHP features | Type coercion and variable indirection change control flow | [PHP features](php-features.md) | The exact comparison or dynamic lookup |
| Deserialization | A magic-method call graph reaches a sensitive sink | [Deserialization](deserialization.md) | Decoder entry point and class graph |
| SSTI | Template source or context exposes an evaluable expression | [SSTI](ssti.md) | Engine, delimiters, context, and output channel |
| Node prototype chain | A recursive write pollutes a prototype used by a gadget | [Node prototype pollution](node-prototype.md) | Controlled key path and inherited-property read |

## How to use a case

1. Select the family from the dominant technical signal.
2. Write the expected source-to-sink chain before opening the corpus.
3. Check the anchor path in [the manifest](../archive/file-manifest.csv).
4. Read only the relevant part of the source and record its path and observation.
5. Separate copied claims from behavior you reproduced in the current lab.
6. Route the next execution step to the matching specialized skill.

## Case-to-reference map

- Command execution: [technique card](../web/command-execution.md), [Python notes](../tools/python-notes.md).
- File upload: [technique card](../web/file-upload.md), [file inclusion](../web/file-inclusion.md).
- PHP features: [source audit](../web/php-audit.md), [SQL injection](../web/sqli.md).
- Deserialization: [technique card](../web/deserialization.md), [PHP audit](../web/php-audit.md).
- SSTI: [technique card](../web/ssti.md), [Node prototype pollution](../web/node-prototype.md).
- Node prototype chain: [technique card](../web/node-prototype.md), [SSTI](../web/ssti.md).

## Evidence rule

A case is useful only when you can state the controlled input, the transformation, the sink, the observed result, and the limits of the test. A path in the corpus is a lead, not a verified claim.
