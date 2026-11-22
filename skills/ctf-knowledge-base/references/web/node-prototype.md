# Node.js prototype pollution

Authorized CTF and owned-lab use only.

## Signals

- User input reaches a recursive merge, deep assignment, path setter, query parser, or object clone.
- The stack contains Express, body parsers, template engines, logging, configuration merging, or a custom `set` helper.
- A payload uses `__proto__`, `constructor`, or `prototype` as ordinary-looking keys.
- Behavior changes globally after one request, or a later request gains an unexpected property.

## Model the primitive

JavaScript property lookup follows the prototype chain. If attacker-controlled keys can mutate `Object.prototype`, every later object lookup may inherit the injected value, even when the object was not part of the original request.

The useful reasoning chain is:

```text
controlled key path -> unsafe recursive write -> polluted prototype
-> gadget reads an inherited property -> sensitive sink is reached
```

Pollution alone is not command execution. Prove the write, the inherited read, and the sink separately.

## Safe local demonstration

Run this only in an isolated challenge process. It demonstrates inheritance, not a target exploit.

```javascript
const target = {};
target["__proto__"]["ctfMarker"] = "observed";
console.log(({}).ctfMarker); // observed
```

The marker should not appear in JSON serialization because inherited properties are not own properties. A verifier that checks only `Object.keys` or JSON output can therefore miss pollution.

## Source-to-sink review

1. Find the parser that turns request data into nested objects.
2. Trace key names through merge, clone, set, `Object.assign`, lodash-style helpers, or templating locals.
3. Identify whether keys such as `__proto__`, `constructor`, and `prototype` are filtered at every recursion level.
4. Locate gadgets that read properties without an own-property check.
5. Check whether a gadget reaches a template option, child process option, logging formatter, URL, file path, or authorization decision.
6. Prove the smallest harmless gadget before attempting a stronger sink.

## High-value sinks and gadgets

- template engine options and cache keys;
- `child_process` option objects;
- HTTP client option bags;
- logging or serialization libraries;
- configuration objects read after request parsing;
- authorization branches that treat an inherited property as present;
- object-to-query or object-to-path serializers.

Library names are leads, not proof. Version, call path, and the exact merge implementation determine whether a gadget is reachable.

## Test matrix

| Variable | Observation |
|---|---|
| One polluted key | Does a fresh object inherit the marker? |
| Nested path | Is only the first level filtered? |
| JSON versus query parser | Do both produce the same key structure? |
| `Object.freeze` or null-prototype target | Does the write fail or become local? |
| Process restart | Is the effect per request, per worker, or persistent? |
| Template or child process gadget | Does the inherited value reach the sink? |

## Corpus anchors

- `WP汇总/Nodejs/Nodejs原型链污染.md`
- `WP汇总/Nodejs/`
- `WP汇总/ctfshow-php特性.md` for contrast with PHP type and variable quirks

Check every path against [the manifest](../archive/file-manifest.csv) before opening it.

## Pivot

Use [SSTI](ssti.md) when the polluted value reaches a template option. Use [command execution](command-execution.md) when a gadget reaches process execution. Hand the request workflow to `ctf-web`.
