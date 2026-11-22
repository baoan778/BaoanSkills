# Image steganography

Authorized CTF and owned-lab use only.

## Triage order

Start with the cheapest, least destructive observations and keep a copy of the original file.

1. Identify the real format and dimensions.
2. Check metadata, comments, thumbnails, and trailing data.
3. Validate structural chunks and compression fields.
4. Inspect pixels, palettes, alpha, bit planes, and frame timing.
5. Compare suspected channels with the challenge clue or a derived key.

```bash
file challenge.png
identify -verbose challenge.png
exiftool challenge.png
pngcheck -v challenge.png
strings -n 6 challenge.png
```

Tool names and flags vary by installation; verify availability and version before relying on output.

## Format-specific review

| Format | Useful checks |
|---|---|
| PNG | Chunk order and length, IHDR dimensions/CRC, PLTE, tRNS, IDAT decompression, ancillary text chunks, concatenated files |
| JPEG | EXIF/comment segments, quantization tables, dimensions, thumbnail, DCT-coefficient tools, data after EOI |
| GIF | Frames, delays, disposal method, palettes, comments, text extensions, trailing data |
| BMP | Header fields, palette layout, row padding, bit depth |
| WebP | RIFF chunk sizes, VP8/VP8L/ALPH metadata, animation frames |
| TIFF | IFD chain, tags, offsets, embedded thumbnails, multiple pages |

## High-value paths

### Metadata and appended content

Run `strings`, `binwalk`, and a hex preview around the declared end of file. A recognizable archive marker after the image terminator may be an embedded file, but confirm boundaries before extracting. Store extracted content in a dedicated challenge directory.

### Dimensions and CRCs

A changed width or height can hide cropped content or make decoders disagree. For PNG, verify IHDR CRC and chunk lengths. For JPEG/GIF, compare header dimensions with the decoder's actual view. Fixing a field is a challenge transformation, not a normal viewer operation; keep the original untouched.

### Palettes and alpha

- Sort or reorder palette entries.
- Inspect alpha as a separate bit plane.
- Check whether transparent pixels retain hidden RGB data.
- Compare declared color depth with decoded channel depth.
- Inspect individual bit planes, not only the least significant bit.

### LSB and bit planes

LSB extraction is only a hypothesis. Determine:

- channel order: RGB, BGR, RGBA, or luminance;
- bit order within each byte;
- row or column traversal;
- channel selection and skipping;
- whether a header, length, delimiter, or known plaintext defines the payload.

Keep extraction scripts deterministic and record the exact ordering that produced readable output.

### QR, barcodes, and overlays

Try normal decoding, inverted colors, separate channels, perspective correction, and frame extraction. If a QR code is split across frames or layers, reconstruct it from a documented rule rather than guessing repeatedly.

### Animation

Extract all frames with timestamps. Compare frames for changing pixels, palette entries, comments, and timing channels. Record frame disposal and delay because a viewer can render a different composite than a naive frame dump.

## Tool workspace

Common CTF tools include `zsteg`, `steghide`, `tweakpng`, `pngcheck`, `exiftool`, `binwalk`, `foremost`, ImageMagick, and a hex editor. The local corpus may contain packaged Windows utilities; do not execute them outside an isolated lab, and do not publish their binaries.

## Evidence standard

- Original file hash and dimensions.
- Extraction or transformation command with version.
- The channel and traversal order used.
- A readable marker and, when possible, a checksum.
- Any missing image dependency or remote resource noted in the source note.
- A clear distinction between recovered data and later interpretation.

## Pivot

Use `ctf-forensics` for the full artifact workflow and `ctf-misc` when the image is one layer in a broader puzzle. Consult [archive analysis](archives.md) for embedded ZIP/RAR/7z content.
