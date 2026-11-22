# PHP and application deserialization

Authorized CTF and owned-lab use only.

## Identify the format

| Format | Typical indicator |
|---|---|
| PHP serialized data | `O:`, `a:`, `s:`, `i:`, `b:` tokens |
| Python pickle | Binary protocol bytes, often starts with protocol markers; unsafe to unpickle untrusted input |
| Java serialization | `AC ED` bytes, base64 `rO0AB` |
| .NET | Type metadata in `BinaryFormatter` or view-state payloads |
| Ruby | Marshal tags such as `\x04\x08` |

Do not load an untrusted serialized object in a privileged environment just to inspect it. Use an isolated analysis environment.

## PHP object model

A serialized object records a class name, property names, property values, and references. Magic methods react to lifecycle events:

- `__construct`, `__destruct`, `__wakeup`, `__sleep`, `__toString`, `__invoke`, `__call`, `__get`, `__set`, `__isset`, `__unset`, and `__serialize`/`__unserialize` on newer versions.

A POP chain is a path from an attacker-controlled property to a sensitive sink through these callbacks.

## Source-led workflow

1. Find the `unserialize` or decoder sink, including cookies, cache values, queue messages, metadata, and PHAR activation.
2. Enumerate classes and magic methods in the supplied source.
3. Build a call graph from magic-method entry points to file, process, SQL, HTTP, or template sinks.
4. Identify the exact property visibility and type needed at each hop.
5. Construct the object graph locally and decode it to verify the serialized representation.
6. Trigger the lifecycle event through the application and capture evidence.

The class index shown in a public writeup is usually environment-specific. Enumerate classes in the current target source rather than reusing an index.

## Property and parser edge cases

- Private and protected property names include visibility information in serialized keys. Match the class exactly.
- References (`R`/`r`) can preserve aliasing between object properties.
- Serialized string lengths must match the encoded bytes, not display characters.
- PHP versions differ on `__wakeup` bypass and visibility handling; verify the target version.
- Some chains use `__destruct` during request shutdown, so output may appear late or only in logs.
- PHAR metadata can be deserialized when a filesystem function touches a `phar://` path. Treat this as a source-to-sink chain, not a universal trigger.

## Java and Python notes

For Java, inspect `readObject`, `readResolve`, proxy usage, and gadget libraries in the classpath. For Python pickle, identify the opcode stream and imports; never execute a pickle from an untrusted source outside a sandbox.

## Constructing a test object

Use the application's own classes and a minimal property graph. A useful local test prints the serialized object and then round-trips it in an isolated PHP process. Do not install or call network-facing gadgets during construction.

```php
<?php
$o = new Example();
$o->property = 'marker';
$s = serialize($o);
echo $s, PHP_EOL;
var_dump(unserialize($s));
```

Replace `Example` with a class discovered in the challenge. Record whether private/protected properties are represented as expected.

## Verification checklist

- [ ] The serialized payload is accepted and reaches the intended decoder.
- [ ] The magic-method path is explained from source, not guessed from a class index.
- [ ] Property visibility, class name, and encoding match the target.
- [ ] A harmless marker proves the chain before any stronger sink is used.
- [ ] Version-specific behavior is documented.

## Pivot

Use `ctf-web` for the surrounding HTTP workflow. Use `ctf-reverse` when binary serialization or custom codecs must be reversed first.
