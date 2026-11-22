# PHP feature case family

Authorized CTF and owned-lab use only.

## What this family teaches

Many PHP challenges turn a small language behavior into an authorization or validation bypass. The key is to identify the exact expression that makes two values equivalent, the variable that the application believes it controls, and the later sink that trusts the result.

## Corpus anchors

- `WP汇总/ctfshow-php特性.md`
- `php代码审计.md`
- `WP汇总/代码审计/`

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Feature map

| Feature | Review question |
|---|---|
| Loose comparison | Does `==` or a switch coerce values in a way the check did not intend? |
| Array/type surprises | Can a scalar check receive an array or object? |
| Numeric strings | Does the target PHP version treat the value as numeric? |
| Variable variables | Can input choose which variable is read or written? |
| `extract`/`parse_str` | Is configuration or authentication state overwritten? |
| Dynamic calls | Can input choose a callable, class, or include target? |
| Error behavior | Does a warning or type error skip a security branch? |
| Encoding | Do URL, Unicode, or case normalization rules differ between check and sink? |

## Reasoning pattern

1. Find the branch that grants access or selects a sink.
2. Replace the input with a type and value that exercises the exact comparison.
3. Read the PHP version and configuration.
4. Prove the branch outcome with a marker, not a guessed flag.
5. Trace the selected variable or callable to its sink.
6. Record whether the behavior is a language feature, a library bug, or challenge logic.

## Common traps

- PHP version changes numeric-string and comparison behavior.
- `in_array` may use loose comparison unless strict mode is set.
- A warning may be hidden while the branch continues.
- Input normalization may make a payload valid only at one layer.
- A source-level bypass is not automatically remote exploitation.
- Copied tables of "magic hashes" or constants usually miss the actual comparison context.

## Next pivot

Use [PHP source audit](../web/php-audit.md) for the complete data-flow method. Use [SQL injection](../web/sqli.md), [deserialization](../web/deserialization.md), or [command execution](../web/command-execution.md) when the branch reaches that sink.
