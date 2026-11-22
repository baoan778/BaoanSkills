# Server-side request forgery

Authorized CTF and owned-lab use only.

## Signals

- A parameter contains a URL, host, scheme, IP, webhook, image source, import source, or remote document.
- The server fetches the value and returns content, a status, a rendered preview, or a timing difference.
- Source code uses an HTTP client, `curl`, `file_get_contents`, URL openers, browser automation, or an image proxy.
- The challenge hints at an internal service, loopback interface, metadata endpoint, or protocol handler.

## Model the fetch

Write down the complete path:

```text
user value -> validation/normalization -> URL parser -> DNS resolution
-> connection target -> redirect policy -> protocol handler -> response handling
```

A mismatch anywhere in that chain can change the effective destination. The input shown in the request is not necessarily the address the server connects to.

## Review questions

| Layer | Question |
|---|---|
| Parser | Is the URL parsed once or multiple times? Which library and version perform the parse? |
| Scheme | Are only `http` and `https` allowed, or can `file`, `gopher`, or another enabled handler reach a different sink? |
| Host | Is the hostname checked before or after DNS resolution? Can the result change between check and use? |
| Address | Are IPv4, IPv6, numeric forms, loopback, private ranges, and link-local ranges blocked consistently? |
| Port | Is the port restricted, and does the client support non-HTTP protocols? |
| Redirect | Can the first URL be approved and a redirect target be fetched without revalidation? |
| Proxy | Does an environment or challenge proxy rewrite the destination? |
| Response | Is the response reflected, stored, previewed, or only observable through timing/errors? |
| DNS | Is DNS resolution bounded, cached, and checked for special-use records? |

## Controlled workflow

1. Start with a loopback HTTP service you control in the challenge lab and a unique marker path.
2. Confirm that the server fetched your marker and record the request log.
3. Change one property at a time: host form, scheme, port, redirect, or DNS behavior.
4. If the response is not reflected, use a local timing or error marker rather than an external callback.
5. Enumerate only services and paths relevant to the challenge objective.
6. If the challenge exposes a metadata service, stop at proving reachability or reading a non-sensitive challenge marker. Do not use discovered credentials outside the lab.
7. Capture the original input, parser result, connection destination, and response evidence.

## Common parser gaps

- credentials or fragments that confuse a simple prefix check;
- hostname suffix checks that accept an attacker-controlled parent domain;
- decimal, octal, hexadecimal, shortened, or IPv6 forms interpreted differently by parser and connector;
- a URL accepted by the application but normalized differently by the HTTP client;
- redirects that leave the approved origin;
- DNS answers that change after validation;
- allowlist checks on a hostname while the request uses a proxy or alternate resolver;
- CRLF or whitespace handling that changes the request target.

Treat these as review hypotheses. Validate the exact behavior in the challenge environment.

## Evidence standard

- The source of the URL and the exact validation code.
- The parser and client libraries with versions.
- The effective protocol, host, port, and resolved address.
- A local request-log entry or a controlled loopback marker.
- Whether redirects were followed and revalidated.
- The response channel and the limit that kept testing non-destructive.

## Pivot

Use [file inclusion](file-inclusion.md) when a local scheme handler overlaps with file access. Use [command execution](command-execution.md) only when a separate source-to-sink path supports it. Route the overall request workflow to `ctf-web`; use `file-path-traversal` for non-CTF path abuse.
