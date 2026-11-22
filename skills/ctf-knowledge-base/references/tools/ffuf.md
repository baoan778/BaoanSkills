# ffuf workflow

Authorized CTF and owned-lab use only.

## Purpose

Use ffuf for controlled fuzzing of a path, parameter, header, host, or other explicitly marked input. Calibrate the normal response before sending a large candidate set.

## Basic path fuzzing

```bash
ffuf -u http://127.0.0.1:8080/FUZZ -w words.txt \
  -mc 200,204,301,302,307,401,403 -rate 20 -t 5 -of json -o ffuf.json
```

Check `ffuf -h` for the installed version; option names and behavior can change.

## Calibration

1. Request a known-missing path and a known-existing path.
2. Record status, size, word count, line count, and content type.
3. Configure filters that remove only the observed catch-all response.
4. Re-run the filters against both controls.
5. Start with a small wordlist and a low request rate.

Useful filters include:

| Filter | Typical use |
|---|---|
| `-mc` | Match expected status codes |
| `-fc` | Filter repetitive status codes |
| `-fs` | Filter by response size |
| `-fw` | Filter by word count |
| `-fl` | Filter by line count |
| `-fr` | Filter by a repeated response regex |
| `-rate` | Cap requests per second |
| `-t` | Concurrency |
| `-recursion` | Expand discovered directories |

## Common modes

### Hidden paths

Use a reviewed path list, then manually inspect candidates. A 403 may reveal an existing resource; a 302 may reveal an access-control flow.

### Virtual hosts

```bash
ffuf -u http://127.0.0.1/ -H 'Host: FUZZ.example.test' -w hosts.txt \
  -fs 0 -rate 10 -t 5
```

Only use this against a target whose routing is in scope. Establish a baseline host first.

### Parameters

```bash
ffuf -u http://127.0.0.1:8080/search?q=FUZZ -w values.txt \
  -mc all -fs 1234 -rate 10 -t 5
```

For POST or JSON bodies, set the correct method and headers and mark exactly one fuzz location. Keep request bodies synthetic and non-destructive.

## Evidence standard

- Full command, wordlist hash, version, and rate.
- Control responses and the filter logic.
- Raw output plus a manually verified finding.
- Request/response for each claimed path or parameter.
- A clear record of the stop condition.

## Pivot

Use [Dirsearch](dirsearch.md) for conventional directory discovery. Route confirmed injection, upload, SSRF, or template behavior to its web card and then `ctf-web`.
