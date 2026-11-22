# Dirsearch workflow

Authorized CTF and owned-lab use only.

## Purpose

Use Dirsearch to discover HTTP paths and files with a controlled wordlist. The goal is a defensible inventory of responses, not maximum request volume.

## Preflight

- Confirm the base URL and allowed host scope.
- Prefer a challenge-provided wordlist or a small reviewed list.
- Record the Dirsearch version and wordlist hash.
- Set a request rate and concurrency appropriate for the lab.
- Confirm that redirects and extensions remain within scope.

```bash
python3 dirsearch.py --version
python3 dirsearch.py -u http://127.0.0.1:8080/ -e php,html,txt -w words.txt \
  --threads 5 --delay 0.1 --full-url --output report.txt
```

Flags differ by release. Check `--help` before using an unfamiliar option.

## Option map

| Option | Use |
|---|---|
| `-u` | Explicit base URL; keep it inside the authorized target |
| `-w` | Wordlist path; do not silently use an unreviewed large list |
| `-e` | Extensions to append; include only plausible server-side suffixes |
| `-r` | Recurse into discovered directories |
| `-R` | Recursion depth where supported |
| `--exclude-status` | Remove noisy status codes after a baseline run |
| `--threads` | Concurrency; start low |
| `--delay` | Delay between requests |
| `--full-url` | Make result paths unambiguous in the report |
| `--output` | Preserve a machine-readable artifact when supported |

## Workflow

1. Fetch a known-good path and record its status, body length, headers, and redirect behavior.
2. Run a small baseline list without recursion.
3. Group results by status and response shape.
4. Remove the wildcard or catch-all behavior if the server returns the same page for every path.
5. Expand only the directories and extensions supported by evidence.
6. Open promising paths manually; do not treat a non-404 status as a vulnerability.
7. Stop when the challenge objective is met or the scope limit is reached.

## Evidence standard

- Base URL, wordlist, extension set, and concurrency.
- Exact Dirsearch version.
- Raw report plus a small table of reviewed paths.
- Baseline and catch-all behavior.
- A manual request/response for every claimed finding.
- No undisclosed scanning outside the challenge host.

## Pivot

Use [ffuf](ffuf.md) for flexible request, value, or virtual-host fuzzing. Route discovered SQL, upload, or template behavior to the matching web card and `ctf-web`.
