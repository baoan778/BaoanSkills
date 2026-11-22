# Command execution case family

Authorized CTF and owned-lab use only.

## What this family teaches

Command execution challenges often combine several small gates: input concatenation, escaping, shell grammar, output suppression, length limits, or a function that evaluates PHP rather than a shell command. The useful question is not "which bypass string works", but "which parser sees which character, and where is the result observed".

## Corpus anchors

- `WP汇总/ctfshow-命令执行wp.md`
- `命令执行.md`
- `CTF常用脚本及工具/` for historical helper scripts

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Evidence chain

| Hop | Record |
|---|---|
| Entry | Parameter, header, cookie, or file that supplies the value |
| Sink | `system`, `exec`, `shell_exec`, `eval`, backticks, or another evaluator |
| Grammar | How the value is quoted, concatenated, split, or escaped |
| Filter | Which characters or words are removed, and in what order |
| Environment | Shell, OS, PHP version, working directory, disabled functions |
| Observation | Response, timing, local file marker, or request log |

## Reasoning pattern

1. Reproduce a harmless command or syntax marker.
2. Remove one filter at a time and observe the exact response.
3. Use a local side effect before an out-of-band callback.
4. Test whether the sink is shell execution or PHP code evaluation.
5. Check for alternate primitives when one function is disabled; do not assume a complete blocklist.
6. Stop at the challenge marker and document the parser behavior.

## Common traps

- A filtered keyword can be reassembled from multiple parser stages.
- A request that returns no body may still execute.
- A shell operator may be interpreted by the web server before the application.
- Length limits may require a multi-stage write, not a single request.
- Windows and Linux command syntax differ.
- A successful `phpinfo()` or file marker is not command execution by itself.

## Next pivot

Read [command execution](../web/command-execution.md) for the detailed technique map. Use [PHP source audit](../web/php-audit.md) for the source-to-sink explanation and `ctf-web` for the surrounding request flow.
