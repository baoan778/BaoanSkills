# CTF Web - Core Server-Side Techniques

This page is the entry point for core server-side web techniques. It is a
routing and quick-reference layer for the more detailed notes in this skill;
use it only against a CTF/lab service or a target for which you have explicit
written authorization.

## Table of Contents

- [PHP Type Juggling](#php-type-juggling)
- [PHP File Inclusion and php://filter](#php-file-inclusion--phpfilter)
- [Python str.format() Attribute Traversal](#python-strformat-attribute-traversal-plaidctf-2017)
- [Mako SSTI](#mako-ssti)
- [Twig SSTI](#twig-ssti)
- [ERB SSTI: Sequel::DATABASES Bypass](#erb-ssti--sequeldatabases-bypass-bearcatctf-2026)
- [SSTI Quote Filter Bypass](#ssti-quote-filter-bypass-via-__dict__update-apoorvctf-2026)
- [Host Header SSRF](#host-header-ssrf-mireactf)
- [SSRF](#ssrf)
- [Related Notes](#related-notes)

## PHP Type Juggling

Loose comparison (`==`) can coerce different types. Classic CTF cases include
magic hashes, JSON numbers replacing strings, and arrays passed to string
functions.

```php
// Vulnerable examples
if ($_POST['password'] == $stored_hash) { /* ... */ }
if (!strcmp($_POST['password'], $secret)) { /* ... */ }
```

Use strict comparison and type validation in fixes. For exploitation, test
whether the application accepts JSON numbers/arrays, whether a hash is compared
with `==`, and whether the expected value can be supplied as `0` or an array.
See [auth-and-access.md](./auth-and-access.md) and
[sql-injection.md](./sql-injection.md) for adjacent authentication and database
workflows.

<a id="php-file-inclusion--phpfilter"></a>
## PHP File Inclusion and php://filter

When user input reaches `include`, `require`, or a file-read primitive, use
`php://filter` to read source without executing it:

```text
php://filter/convert.base64-encode/resource=config
php://filter/convert.base64-encode/resource=/var/www/html/index.php
```

Check for wrapper restrictions, path normalization, and upload-to-inclusion
chains. See [server-side-exec.md](./server-side-exec.md) for wrapper and upload
execution paths.

<a id="python-strformat-attribute-traversal-plaidctf-2017"></a>
## Python str.format() Attribute Traversal (PlaidCTF 2017)

Python format strings can traverse object attributes and indexes when the
format string itself is attacker-controlled:

```python
{0.__class__.__mro__}
{0[key]}
```

This is distinct from server-side template injection: the sink is
`str.format()` rather than a template engine. Map the object passed to
`format()` and look for fields that expose configuration, secrets, or files.
See [field-notes.md](./field-notes.md#python-strformat-attribute-traversal-plaidctf-2017).

<a id="mako-ssti"></a>
## Mako SSTI

Mako templates evaluate Python expressions and blocks. A minimal probe is:

```text
${7*7}
${__import__('os').popen('id').read()}
```

Treat any successful expression evaluation as code execution. Identify the
engine from syntax and error messages before choosing a payload. Mako has no
Jinja-style sandbox by default, so a seemingly simple template bug can become
RCE. See [server-side-exec.md](./server-side-exec.md) for execution and
exfiltration patterns.

<a id="twig-ssti"></a>
## Twig SSTI

Twig expressions can be distinguished from Jinja2 with a multiplication probe:
Twig repeats a string for `7*'7'`, while Jinja2 typically returns `49`.
Useful Twig sinks include `map`, `filter`, and object-method access when the
application exposes them.

```twig
{{7*'7'}}
{{['id']|map('system')|join}}
```

Confirm the engine, version, and available filters before testing a payload.
See [server-side-exec.md](./server-side-exec.md) for the execution workflow.

<a id="erb-ssti--sequeldatabases-bypass-bearcatctf-2026"></a>
## ERB SSTI: Sequel::DATABASES Bypass (BearcatCTF 2026)

Ruby/Sinatra ERB injection may be constrained by an `ERBSandbox` that blocks
local variable names. A global object can still provide a path to application
data:

```erb
<%= Sequel::DATABASES.first[:table].all %>
```

Any expression evaluation that reaches a live database connection should be
treated as a data-exfiltration primitive. See
[server-side-exec.md](./server-side-exec.md#ruby-code-injection).

<a id="ssti-quote-filter-bypass-via-__dict__update-apoorvctf-2026"></a>
## SSTI Quote Filter Bypass via __dict__.update (ApoorvCTF 2026)

When an SSTI filter blocks quotes but allows keyword arguments, object
dictionary updates can provide a quote-free route to values:

```text
{{ url_for.__globals__.current_app.config.__dict__.update(key=value) }}
```

Adapt the expression to the actual object graph. Do not assume the payload is
portable between template engines. See
[field-notes.md](./field-notes.md) for the surrounding SSTI notes.

<a id="host-header-ssrf-mireactf"></a>
## Host Header SSRF (MireaCTF)

If an application constructs an internal URL from the request `Host` header,
the validation request can be redirected to an attacker-controlled service:

```text
Host: attacker.example
```

Probe with a controlled endpoint and compare server-side callback evidence.
Check allowlists, host normalization, and forwarded-header handling before
reporting. See [server-side-advanced-2.md](./server-side-advanced-2.md) for
related parser discrepancies.

## SSRF

Server-side request forgery is a data-flow bug: attacker input controls a URL,
host, scheme, redirect, or DNS answer. Test only internal endpoints within the
challenge scope. Useful checks include:

- loopback and private-address representations;
- DNS rebinding and redirect chains;
- parser discrepancies between validation and the HTTP client;
- non-HTTP schemes such as `gopher://`, `file://`, and `dict://`;
- internal services (metadata, Redis, MySQL, SMTP, Docker API) that accept a
  crafted request.

Start with [server-side-advanced.md](./server-side-advanced.md), then follow
[server-side-advanced-2.md](./server-side-advanced-2.md),
[server-side-advanced-3.md](./server-side-advanced-3.md), and
[server-side-advanced-4.md](./server-side-advanced-4.md) for concrete chains.

## Related Notes

- [sql-injection.md](./sql-injection.md) - SQL injection and database extraction.
- [server-side-2.md](./server-side-2.md) - XXE, XML injection, command injection,
  and GraphQL.
- [server-side-exec.md](./server-side-exec.md) - Code execution and upload-to-RCE.
- [server-side-exec-2.md](./server-side-exec-2.md) - Extended execution chains.
- [server-side-deser.md](./server-side-deser.md) - Deserialization and races.
- [field-notes.md](./field-notes.md) - Long-form quick references.
- [cves.md](./cves.md) - CVE-specific techniques.

## Verification

Record the request/response pair or callback that proves the primitive, then
state the affected component, preconditions, and impact. If the evidence does
not establish a complete path, report the result as a hypothesis rather than a
confirmed vulnerability.
