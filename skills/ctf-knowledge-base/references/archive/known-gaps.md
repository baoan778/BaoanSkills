# Known corpus gaps and synthetic replacements

This card records source dependencies that are absent from the local corpus and
gives maintainers a safe way to reconstruct equivalent test material without
redistributing missing images. A missing asset does not invalidate the technique
card, but it does mean the original note is not self-contained.

Authorized CTF and owned-lab use only. Generate test fixtures locally, avoid real
target data, and do not add generated images or captures to the public release
unless a separate license and privacy review approves them.

## `SQL.md`: missing `Less-1.jpg`

- **Source note:** `SQL.md`
- **Curated route:** [SQL injection](../web/sqli.md)
- **Observed gap:** the source note refers to `../images/Less-1.jpg`, but that
  image is not present in the indexed corpus.
- **Why it matters:** the image may have shown the lab layout, request context,
  or response evidence needed to understand the note.

Reconstruct the missing context as text in an authorized local SQLi lab:

1. Start a disposable lesson or challenge instance bound to loopback.
2. Record the page’s title, database family, input location, and the expected
   benign response.
3. Capture a baseline request and one controlled discriminator response. Keep
   the pair minimal and avoid dumping more data than the challenge requires.
4. Sanitize hostnames, cookies, tokens, and personal data before saving notes.
5. Store the request/response excerpt with the challenge hash and tool versions
   instead of trying to recreate a screenshot.

```http
GET /sqli-labs/Less-1/?id=1 HTTP/1.1
Host: 127.0.0.1
```

The exact path is only an example. Use the target supplied by the authorized
lab, record the real route, and explain which observable difference supports
the conclusion. Do not treat a single error response as proof of injection.

## `图片隐写.md`: missing `.figureqr*.jpg`

- **Source note:** `图片隐写.md`
- **Curated route:** [image steganography](../misc/image-stego.md)
- **Observed gap:** the note refers to `.figureqr*.jpg` files that are not
  present in the indexed corpus.
- **Why it matters:** the missing examples may have demonstrated QR placement,
  distortion, channel separation, or reassembly.

Generate a synthetic QR fixture locally:

```bash
python -m pip install "qrcode[pil]"
python - <<'PY'
from pathlib import Path
import qrcode

marker = "CTF{authorized_synthetic_qr}"
path = Path("figureqr-synthetic.png")
qrcode.make(marker).save(path)
print(marker, path.resolve(), path.stat().st_size)
PY
```

Verify the fixture before using it in a steganography exercise:

```bash
zbarimg figureqr-synthetic.png
```

If `zbarimg` is unavailable, use a reviewed QR decoder from the authorized lab.
Keep the generated image outside Git and the release snapshot. To recreate a
harder case, apply one documented transformation at a time, such as inversion,
cropping, perspective changes, channel separation, or frame reassembly, and
record the transformation order.

## Remote image dependencies

When a source note embeds a remote image:

1. Prefer an original textual explanation of the technique and evidence.
2. Do not hotlink the remote resource from a public skill.
3. Cache a copy only after confirming the license, privacy implications, and
   the stability of the source.
4. Strip unnecessary metadata and record the source URL, retrieval date, hash,
   and intended use.
5. Treat the cached file as a new release asset that requires review; never
   assume that public availability grants redistribution rights.

## Review checklist

- The curated route still explains the technique without the missing image.
- Synthetic fixtures use a local test marker, not a real flag or credential.
- Commands are run only in an authorized CTF, owned lab, or equivalent scope.
- Generated files stay out of the public snapshot unless explicitly reviewed.
- The limitation is recorded instead of fabricating what the missing image showed.
