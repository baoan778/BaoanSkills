# Server-side template injection

Authorized CTF and owned-lab use only.

## Signals

- User text appears in a rendered page and expression-like syntax is evaluated.
- A name, greeting, report, email, PDF, or error page is rendered through a template engine.
- Source code passes request data to `render`, `render_template_string`, a template string, or a custom formatter.
- The challenge supplies a sandbox, blocklist, filter, or restricted object model.

## Fingerprint before payloading

Use a harmless arithmetic marker in several common syntaxes and compare the rendered output. This identifies the engine family and context, not an exploit.

| Syntax family | Example probe |
|---|---|
| Jinja/Twig-style | `{{7*7}}` |
| Expression-language style | `${7*7}` |
| ERB/EJS-style | `<%= 7 * 7 %>` |
| Ruby interpolation style | `#{7*7}` |
| Handlebars-like | `{{7*7}}` with engine-specific escaping |

A result of `49` is a lead. Check whether the same expression is HTML-escaped, evaluated twice, interpreted only in one field, or cached.

## Context map

1. Is the whole template attacker-controlled, or only a value inserted into a fixed template?
2. Is the input rendered server-side, client-side, in a PDF worker, or in a separate microservice?
3. Which engine, version, delimiters, autoescaping, and sandbox are configured?
4. Can the input reach template source, a template name, a cache key, or a filter argument?
5. What objects and globals are exposed to the render context?
6. What output channel exists: response body, error, file, email, or timing?

## Source-led workflow

1. Read the render call and reconstruct the full template source.
2. Classify the injection as template-source control or expression/value injection.
3. Enumerate the actual context variables and available helpers.
4. Test property access with a harmless string marker before attempting any sensitive object.
5. Map sandbox restrictions and confirm whether they are enforced before or after expression evaluation.
6. For blind rendering, use a local timing or file-marker technique with a strict stop condition.
7. Record the engine, version, exact context, and observation.

## Common escalation questions

- Can the expression access built-in classes, global functions, imports, or filesystem helpers?
- Is a sandbox object exposed unintentionally through a helper, exception, debug endpoint, or template loader?
- Can template inheritance, includes, or macros read an unintended path?
- Does autoescaping differ between text, attribute, JavaScript, and URL contexts?
- Can cached or compiled templates retain one request's content for another?
- Does the rendered output go to a privileged PDF or email worker?

Do not assume a public sandbox-escape chain matches the target. Engine version and context determine reachability.

## Evidence standard

- The exact render path and the source of template control.
- A negative control that does not evaluate and a positive arithmetic control.
- The engine and version.
- The object or helper used for each hop.
- A non-destructive proof of the final sink.
- Any sandbox warning, exception, or timeout that limits confidence.

## Pivot

Use [Node prototype pollution](node-prototype.md) when template options or locals are polluted through an object merge. Use [command execution](command-execution.md) only after a distinct source-to-sink path reaches a process sink. Route the complete CTF request flow to `ctf-web`.
