# SQL injection

Authorized CTF and owned-lab use only.

## Signals

- User-controlled data changes SQL syntax, ordering, error text, response length, or timing.
- A login, search, filter, sort, or report endpoint exposes a database-backed behavior.
- Source code concatenates input into a query or uses an ORM escape hatch.
- The challenge supplies a database schema, seed data, or an intentionally weak query.

## Establish the context

Before choosing a technique, identify the database family, parameter location, query structure, and response channel.

| Question | Why it matters |
|---|---|
| SQLite, MySQL, MariaDB, PostgreSQL, MSSQL, or Oracle? | Comment syntax, casts, errors, metadata tables, and stacked query support differ. |
| String, numeric, identifier, `ORDER BY`, or `LIMIT` context? | The same value can terminate different grammar positions. |
| Is the query parameterized? | A bound value is not injectable even when it contains SQL-looking text. |
| What changes are observable? | Errors, rows, redirects, timing, and out-of-band behavior are different evidence channels. |
| Are multiple statements enabled? | Stacked queries may be unavailable even when a single-statement union works. |
| Is the endpoint second-order? | Input may be stored, escaped, and concatenated later in another context. |

## Source-led workflow

1. Read the query construction and reconstruct the resulting SQL with a benign marker.
2. Determine whether the value is quoted, numeric, an identifier, or a reusable fragment.
3. Start with a boolean or arithmetic discriminator that changes only the intended predicate.
4. Choose union, error-based, boolean-blind, time-blind, or stacked reasoning based on the observed channel.
5. Enumerate data one item at a time and record deterministic proofs.
6. Stop if the query causes destructive writes or affects data outside the challenge scope.

## Technique map

| Technique | Best fit | Main trap |
|---|---|---|
| Boolean discrimination | Login, filter, or single-row checks | Confusing application logic with database behavior |
| Union | Visible columns and compatible types | Wrong column count, type coercion, or comment handling |
| Error-based | Database errors reach the response | Leaking a version-specific error format instead of explaining it |
| Boolean blind | Only true/false responses differ | Rate limits, caching, or unstable response normalization |
| Time blind | No useful content difference | Network jitter and unsafe load generation |
| Stacked queries | Driver explicitly supports multiple statements | Assuming support from the database alone |
| Second-order | Stored value is later reused unsafely | Testing only the first request |
| NoSQL-like behavior | JSON/object parameters reach a document query | Assuming SQL syntax applies to a non-SQL backend |

## Safe ordering of evidence

For a CTF challenge, a compact evidence trail is more useful than a large dump:

- the exact input that changes the predicate;
- the query or source path it reaches;
- a true/false control pair;
- the schema or table name derived from the challenge;
- one row or field proving access;
- the database version when it explains syntax;
- the stop condition used to avoid unnecessary writes.

Use placeholders for hostnames, credentials, and table values when writing a public note.

## Tool handoff

Use [the SQLMap workflow](../tools/sqlmap.md) when SQLMap is the explicit tool. Keep manual reasoning separate: understand the query, then decide whether automation is justified. SQLMap options are version-sensitive, so verify `--help` and begin with low impact.

## Common false conclusions

- A quote causing an HTTP 500 is not automatically SQL injection.
- A response-length change may come from input validation or WAF behavior.
- A database error may be intentionally simulated by the challenge.
- A successful union does not prove file read, file write, or command execution.
- A hash or encoded flag still needs a reproducible decoding or verification step.

## Pivot

Use [PHP source audit](php-audit.md) for the surrounding source, [SSRF](ssrf.md) when a database feature initiates a request, and `ctf-web` for the complete challenge workflow. Use `sql-injection-testing` or `sqlmap-database-pentesting` for authorized non-CTF assessment.
