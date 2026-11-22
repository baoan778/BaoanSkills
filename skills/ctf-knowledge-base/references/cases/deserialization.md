# Deserialization case family

Authorized CTF and owned-lab use only.

## What this family teaches

Deserialization challenges are call-graph problems. The serialized bytes are only the transport. The solve path is an object graph whose magic methods or protocol hooks reach a useful sink under the target's exact class definitions and version.

## Corpus anchors

- `PHP反序列化漏洞总结.md`
- `WP汇总/CTfshow-反序序列化wp.md`
- `WP汇总/代码审计/`
- `CTF常用脚本及工具/python-Picke序列化/` for format-contrast notes

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Entry points

| Format | Entry question |
|---|---|
| PHP `unserialize` | Which classes are autoloadable, and which magic methods can be reached? |
| PHAR metadata | Is a filesystem operation touching a `phar://` path? |
| Java | Are `readObject`, `readResolve`, proxies, or gadget libraries present? |
| Python pickle | Which opcodes/imports are reachable, and is the environment isolated? |
| .NET | Is a legacy formatter or view-state parser accepting untrusted data? |
| Ruby Marshal | Which classes and hooks are loaded? |

## Evidence chain

1. The decoder or trigger.
2. The class loading boundary.
3. The magic-method or hook entry.
4. Each property read and method call.
5. The final file, process, SQL, HTTP, or template sink.
6. The lifecycle timing and output channel.

## Reasoning pattern

1. Build the object graph from source, not from a public gadget list.
2. Confirm property visibility and serialized string lengths.
3. Use a harmless marker property and inspect the round-trip.
4. Prove the first magic method is reached.
5. Add one hop at a time until the sink is demonstrated.
6. Record the PHP or runtime version because wakeup and visibility behavior can differ.

## Common traps

- A serialized-looking string may be the wrong format.
- The class name may include a namespace or be defined only in one include path.
- Private/protected keys include visibility bytes that must match.
- A payload may trigger on shutdown, producing delayed output.
- PHAR metadata is not a universal trigger; the filesystem operation and path matter.
- Loading a malicious pickle or gadget outside an isolated lab can execute code.

## Next pivot

Use [deserialization](../web/deserialization.md) for the format map and [PHP source audit](../web/php-audit.md) for source review. Route binary serialization to `ctf-reverse` and the complete web flow to `ctf-web`.
