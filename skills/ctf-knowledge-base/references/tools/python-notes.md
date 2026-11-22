# Python CTF notes

Authorized CTF and owned-lab use only.

This card collects small, reproducible Python patterns that are useful across CTF categories. Prefer the standard library unless the challenge supplies a trusted dependency. Keep scripts deterministic and write outputs to a dedicated challenge directory.

## Binary and text

```python
from pathlib import Path

data = Path("artifact.bin").read_bytes()
print(len(data), data[:32].hex())
Path("decoded.bin").write_bytes(data)
```

- Open binary formats with `rb`/`wb`; do not round-trip through text.
- Use `utf-8-sig` only when a source may have a BOM.
- Record hash values before transforming an artifact.

## Structs and integers

```python
import struct

value = struct.unpack("<I", data[:4])[0]
chunk = struct.pack(">H", 0x4142)
```

State the endianness and field width explicitly. A wrong signedness or width often produces a plausible but false result.

## Encodings and hashing

```python
import base64
import hashlib
import zlib

blob = zlib.compress(b"marker")
encoded = base64.b64encode(blob).decode("ascii")
digest = hashlib.sha256(blob).hexdigest()
```

- Base64 is an encoding, not encryption.
- Try raw, URL-safe, and padded variants deliberately.
- A hash identifies bytes; it does not prove authorship or safety.
- Use `hmac.compare_digest` for comparing authentication values.

## Files and archives

```python
from pathlib import Path
import zipfile

with zipfile.ZipFile("challenge.zip") as archive:
    for info in archive.infolist():
        print(info.filename, info.file_size, info.compress_size)
```

Inspect archive members before extraction. Reject absolute paths, `..` traversal, symlinks, and unexpected expanded sizes. Extract only into a new challenge directory.

## HTTP requests

```python
import requests

response = requests.get("http://127.0.0.1:8080/health", timeout=5)
response.raise_for_status()
print(response.status_code, response.headers.get("content-type"))
print(response.text[:500])
```

- Use loopback or a challenge placeholder.
- Set a timeout.
- Do not disable certificate validation by default.
- Avoid printing full cookies, tokens, or private response bodies.
- For large responses, stream and cap the bytes written.

## Iteration and bit operations

```python
payload = bytes.fromhex("00 01 ff")
bits = "".join(f"{byte:08b}" for byte in payload)
print(bits)
```

When extracting stego data, document channel order, bit order, row order, padding, and the marker/checksum that proves the result.

## Debugging discipline

- Print lengths, offsets, and hashes before decoding them.
- Keep the original artifact untouched.
- Separate collection, transformation, and interpretation in the script.
- Do not let an exception path write a partial result over the only copy.
- Use a fixed random seed only when reproducing a challenge; never use it to fake a solution.

## Corpus anchor

`CTF常用脚本及工具/python-note.md` is a local study note. Validate its examples against the current Python version and the actual challenge artifacts before reuse.

## Pivot

Use the specialized CTF card for the artifact category. Use `ctf-reverse` for binary format internals and `ctf-forensics` for evidence handling.
