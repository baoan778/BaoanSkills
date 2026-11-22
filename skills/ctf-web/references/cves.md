# CTF Web - CVE-Driven Techniques

Use this page when a challenge exposes a product name, framework version,
dependency lockfile, response header, or recognizable error page. Match the
version to the affected range before attempting a payload. These notes are for
authorized CTF/lab targets; do not test third-party production systems without
permission.

## CVE-2012-0053: Apache HttpOnly Cookie Leak via 400 Bad Request (RC3 CTF 2016)

Apache HTTP Server 2.2.0 through 2.2.21 (and some vendor builds) could include
cookie values in a 400 Bad Request response. An oversized `Cookie` header could
trip the error path and expose a cookie that JavaScript normally could not read.

Practical checks:

1. Identify the Apache version and error-page behavior.
2. Send a deliberately oversized but harmless cookie in a local/CTF instance.
3. Look for cookie material in the error body.
4. If found, determine whether the affected cookie is session-bearing and
   whether the challenge objective depends on it.

See [field-notes.md](./field-notes.md#apache-cve-2012-0053-httponly-cookie-leak) for
the compact lab note.

<a id="cve-2024-28184-weasyprint-attachment-ssrf--file-read"></a>
## CVE-2024-28184: WeasyPrint Attachment SSRF and File Read

WeasyPrint versions before 61.2 are associated with attachment handling that
can fetch URLs outside the normal fetcher path. In a CTF, a user-controlled
HTML-to-PDF conversion may allow `<a rel="attachment" href="...">` or
`<link rel="attachment" href="...">` to reach `file://` paths or internal HTTP
services.

A safe verification sequence is:

1. Generate a document with a benign attachment to a controlled endpoint.
2. Confirm whether the endpoint receives the request from the PDF worker.
3. Use a local file marker, not production data, to test file attachment.
4. Check the resulting PDF for an embedded file stream.

See [server-side-advanced-4.md](./server-side-advanced-4.md#weasyprint-ssrf--file-read-cve-2024-28184-nullcon-2026)
for the full challenge pattern and mitigation notes.

<a id="cve-2025-55182--cve-2025-66478-react-server-components-flight-protocol-rce"></a>
## CVE-2025-55182 and CVE-2025-66478: React Server Components Flight Protocol RCE

These CVEs concern unsafe deserialization/processing in the React Server
Components Flight protocol. A challenge may expose the protocol through
`Next-Action` and `Accept: text/x-component` headers. A crafted Flight chunk can
reach a constructor chain and execute server-side JavaScript.

High-level checks:

- Identify the React/Next.js version and whether the action endpoint is exposed.
- Confirm that the endpoint accepts Flight/action requests.
- Reproduce only with a challenge-owned callback or local marker.
- Prefer a harmless command such as a controlled file read for proof, and stop
  if the test affects availability or data outside scope.

See [server-side-advanced-4.md](./server-side-advanced-4.md#react-server-components-flight-protocol-rce-ehax-2026)
for the challenge-specific chain and WAF notes.

## Other CVEs in the Notes

The surrounding notes also cover ExifTool, Gogs, Flask/Werkzeug debug exposure,
and application-specific parser bugs. Search the detailed files for the
component and version before building a chain:

- [server-side-advanced.md](./server-side-advanced.md)
- [server-side-advanced-2.md](./server-side-advanced-2.md)
- [server-side-advanced-3.md](./server-side-advanced-3.md)
- [server-side-advanced-4.md](./server-side-advanced-4.md)
- [server-side-exec.md](./server-side-exec.md)

## Verification and Reporting

A CVE reference is not proof of exploitability. Report the product/version,
affected range, configuration preconditions, the observed primitive, and the
impact. If the version is unknown or the path is unreachable, classify the
finding as unverified rather than inflating it into an exploit.
