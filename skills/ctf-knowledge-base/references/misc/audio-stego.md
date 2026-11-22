# Audio steganography

Authorized CTF and owned-lab use only.

## Triage order

1. Identify the container and codec.
2. Read metadata, comments, tags, and embedded files.
3. Inspect the waveform and spectrogram.
4. Compare channels and sample-level data.
5. Test known audio signaling modes such as DTMF or SSTV only when the clue supports them.

```bash
file challenge.wav
ffprobe -hide_banner challenge.wav
exiftool challenge.wav
sox challenge.wav -n spectrogram -o spectrogram.png
```

Commands are examples; verify the local tool version and output format.

## Container and codec review

| Format | Useful checks |
|---|---|
| WAV | RIFF chunk sizes, sample format, channels, unusual chunks, data after the declared payload |
| MP3 | ID3 tags, frame headers, encoder delay, appended data, MP3 stego tools |
| FLAC | Metadata blocks, comments, picture blocks, frame boundaries |
| OGG/Opus | Vorbis comments, packet structure, chained streams |
| M4A/AAC | Container atoms, metadata, cover art, trailing atoms |
| AIFF | Chunk layout, sample rate, compression type |

Use `binwalk` and `strings` as discovery aids, then validate offsets against the container structure.

## Spectrogram and waveform

- Open the whole file first, then inspect short windows.
- Change FFT size, overlap, and color scale to reveal text or tones without inventing patterns.
- Check both channels separately and in mid/side form.
- Inspect the beginning, end, silence, and low-amplitude regions.
- For waveform-readable data, use a high-resolution time view and record the exact segment.
- For DTMF, decode tones and compare the resulting digits across two independent methods.

A visually suggestive pattern is not enough. Reproduce it with a second view or decode the signaling layer.

## LSB and sample-level data

For PCM audio, determine:

- sample width and endianness;
- channel interleaving;
- signed versus unsigned representation;
- bit order and traversal;
- frame or header delimiters;
- whether the payload is in the least significant bit or a lower bit plane.

Never treat compressed MP3 or AAC bytes as raw PCM samples. Decode to a documented sample format first, or use a tool designed for the exact codec.

## MP3 stego

MP3 stego can hide data in frame-level redundancy, unused fields, or an accompanying tool-specific structure. First compare multiple decoders and inspect ID3/trailing data. If a challenge supplies a password or tool name, use it within the isolated lab and record the version. Do not reuse a tool-specific recipe that lacks the matching artifact format.

## SSTV and signaling

If the clue mentions radio, image transmission, or tones, inspect for SSTV, DTMF, Morse, modem, or other signaling. Decode with the matching mode and record the sample rate and timing. A wrong mode can still produce an image-like result, so validate synchronization and structure.

## Evidence standard

- Original hash, duration, sample rate, channel count, and codec.
- Spectrogram or waveform parameters.
- The exact segment, channel, and bit order used.
- A decoded marker plus a second confirmation where possible.
- Any tool version that affects decoding.

## Tool workspace

Common tools include SoX, FFmpeg, Audacity, `exiftool`, `binwalk`, `strings`, `steghide`, and dedicated MP3 stego utilities. Do not execute bundled binaries from an untrusted corpus outside an isolated environment.

## Pivot

Use `ctf-forensics` for the broader media workflow and [image steganography](image-stego.md) when an extracted image is the next layer. Route signal or hardware analysis to `ctf-misc` or `ctf-forensics` as appropriate.
