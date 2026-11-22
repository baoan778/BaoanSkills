# Command execution

Authorized CTF and owned-lab use only.

## Signals

Look for:

- direct functions such as `system`, `exec`, `shell_exec`, `passthru`, `popen`, and backticks;
- indirect wrappers such as `assert`, `call_user_func`, `preg_replace` with the deprecated `/e` modifier, or template/expression evaluation;
- shell metacharacters reaching a process spawn;
- parameters that change command output, timing, error text, or filesystem state.

Record the operating system, shell, working directory, user, and whether output is returned. These facts determine which separators and built-ins are available.

## Analysis workflow

1. Prove the sink with a harmless marker that distinguishes command execution from ordinary reflection, for example a unique arithmetic result or a file created under the lab's temporary directory.
2. Determine whether the value is concatenated into a shell command or evaluated as code. Shell injection and code injection have different escape rules.
3. Identify quote context, argument position, filtering, and output channel.
4. Start with one separator. Do not enumerate a large payload list before understanding the parser.
5. Move to blind or second-order verification if output is unavailable.
6. Preserve the exact request, response, and command output as evidence.

## Common injection classes

| Class | Test concept | Evidence |
|---|---|---|
| Semicolon or newline | Terminate one command and start another | Distinct output or delay |
| Pipe | Send output into another process | Changed response shape |
| Logical operator | Execute conditionally | Response differs by condition |
| Substitution | Evaluate a nested command | Arithmetic or file result appears |
| Argument injection | Add an option to an existing command | Error/version/output changes |
| Code evaluation | Escape string context into evaluator | Marker evaluated by language runtime |

Use synthetic markers rather than destructive commands. In CTF labs, `id`, `pwd`, `whoami`, `ls`, and controlled file reads are usually enough to establish impact.

## Filter bypass reasoning

Treat filtering as a parser problem:

- **Spaces:** tabs, newlines, shell variable expansion, brace expansion, or redirection can change tokenization.
- **Separators:** alternate operators, newlines, command substitution, or pipeline stages may survive.
- **Keywords:** quoted fragments, escape characters, wildcard expansion, variable indirection, encoding, or path aliases can defeat naive string matching.
- **Punctuation:** shell quoting, locale behavior, and encoded input may alter what the application checks versus what the shell parses.
- **Length:** use short commands, built-ins, and response-free side effects.

Never assume a bypass works because a payload is accepted. Confirm that actual execution occurred.

## Blind execution

Use one of these channels:

- timing with a bounded sleep;
- a conditional delay tied to a boolean predicate;
- outbound interaction to a listener you control in the lab;
- writing a small marker into a location the application can later serve or read;
- DNS or HTTP interaction where the environment explicitly permits it.

Keep delays short and reproducible. Clean up temporary files at the end of the exercise.

## Code-execution variants

For `eval`, `assert`, template engines, and custom interpreters:

- determine the language and expression wrapper;
- test syntax errors to reveal error handling;
- escape the current string/expression context;
- call built-ins only after proving evaluation;
- prefer file read or a controlled marker over a destructive command.

## Verification checklist

- [ ] The marker cannot be explained by reflection or a cached response.
- [ ] The same result is reproducible with a second independent request.
- [ ] The command is scoped to the authorized target.
- [ ] The output path or timing difference has a measured baseline.
- [ ] The correct specialized skill is used for deeper exploitation.

## Pivot

Use `ctf-web` for a broader web workflow, `ctf-pwn` for binary-level exploitation, and `ctf-forensics` when the hard part becomes log or packet reconstruction.
