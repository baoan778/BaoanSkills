# Node prototype pollution case family

Authorized CTF and owned-lab use only.

## What this family teaches

Prototype pollution is a chain of small facts: a recursive write accepts a special key, the target prototype is reached, a later component reads an inherited property, and that value changes a security-relevant sink. Each fact needs separate evidence.

## Corpus anchors

- `WP汇总/Nodejs/Nodejs原型链污染.md`
- `WP汇总/Nodejs/`
- `WP汇总/ctfshow-php特性.md` for a different dynamic-language comparison family

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Chain map

| Hop | Review question |
|---|---|
| Parser | Does query-string or JSON parsing preserve `__proto__`, `constructor`, or `prototype`? |
| Merge | Does a recursive merge or setter write the key into a prototype? |
| Scope | Is the change local to one object, one process, or all later requests? |
| Gadget | Does a component read an inherited property without an own-property check? |
| Sink | Does the inherited value reach a template, process, URL, file, or authorization decision? |
| Lifecycle | Does a restart, worker isolation, or cache reset change the result? |

## Reasoning pattern

1. Send an isolated marker through the suspected parser.
2. Confirm it appears on a fresh object, not just the request object.
3. Trace which recursive helper writes the nested key.
4. Identify the gadget and the exact property it reads.
5. Demonstrate a harmless sink before attempting a stronger one.
6. Record Node.js and dependency versions because gadgets and merge behavior drift.

## Common traps

- A prototype change can be invisible in JSON serialization.
- A request may appear successful while the pollution is confined to one worker.
- `Object.create(null)` or frozen objects may block the chain.
- Filtering the first key level may leave nested paths open.
- A gadget name is not proof that the installed version or call path reaches it.
- A template option or child-process option may require an additional type or value shape.

## Next pivot

Use [Node prototype pollution](../web/node-prototype.md), then [SSTI](../web/ssti.md) or [command execution](../web/command-execution.md) if the gadget reaches those sinks. Route the HTTP workflow to `ctf-web`.
