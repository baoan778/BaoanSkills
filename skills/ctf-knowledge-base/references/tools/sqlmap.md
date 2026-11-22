# SQLMap workflow

Authorized CTF and owned-lab use only.

## Purpose

Use SQLMap to automate a hypothesis that is already supported by a manually observed request. It is not a substitute for understanding the query, and it should never be pointed at a target outside explicit scope.

## Preflight

- Save one exact request in a challenge workspace, for example `request.txt`.
- Remove unrelated cookies, tokens, and private headers or replace them with challenge values.
- Identify the parameter and the expected database family.
- Record the SQLMap version.
- Choose a low impact level and risk.
- Set an output directory inside the challenge workspace.
- Define a stop condition before starting.

## Minimal invocation

```bash
sqlmap --version
sqlmap -r request.txt --batch --level=1 --risk=1 --threads=1 \
  --output-dir=sqlmap-output
```

Check `sqlmap -hh` for the installed release. Do not copy flags from an old cheat sheet without verifying them.

## Option map

| Option | Use |
|---|---|
| `-r` | Load a saved raw HTTP request; preserves method, headers, and body |
| `--data` | Inline body for a simple local request |
| `--cookie` | Challenge session value when a request file is not used |
| `--dbms` | Reduce probing after the database family is known |
| `--technique` | Limit the inference classes to those justified by the response |
| `--level`, `--risk` | Keep initial probes conservative |
| `--threads` | Concurrency; use one or a small value |
| `--batch` | Use defaults without interactive prompts |
| `--output-dir` | Keep logs and session data contained |

## Workflow

1. Replay the saved request without SQLMap and record the baseline.
2. Ask SQLMap to identify the parameter and database; do not jump to extraction.
3. Review the inferred technique and payloads against the source or response.
4. Prefer a narrow query that proves the intended data access.
5. Stop before writes unless the challenge explicitly requires a documented, reversible change.
6. Preserve the SQLMap log and a manual verification request.

Do not use `--os-shell`, file-write, privilege escalation, or broad dump options merely because they are available. Those actions cross a different impact boundary and require explicit challenge or written authorization.

## Interpretation

- An injected parameter is not proof of a particular database version.
- A retrieved table may be a decoy or may not contain the intended objective.
- A hash or encoded value must still be decoded and verified.
- Rate limits, WAF behavior, and session changes can make a negative result inconclusive.
- SQLMap output can be noisy; cite only the observations needed for the writeup.

## Evidence standard

- Request file hash and parameter.
- SQLMap version, command, and output directory.
- Baseline response and one verified true/false or data-access result.
- Database type/version when it matters.
- The exact stop condition and confirmation that no destructive action occurred.

## Pivot

Use [SQL injection](../web/sqli.md) for manual reasoning and `sql-injection-testing` for an authorized assessment workflow. Route the surrounding challenge to `ctf-web`.
