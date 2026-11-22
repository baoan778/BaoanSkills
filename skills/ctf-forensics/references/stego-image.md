# CTF Forensics - Image Steganography

Techniques specific to hiding data in image formats (JPEG, PNG, BMP, GIF). For non-image steganography (PDF, audio, terminal, text), see [steganography.md](./steganography.md). For advanced techniques (FFT, SSTV, audio, video, JPEG XL), see [stego-advanced.md](./stego-advanced.md) and [stego-advanced-2.md](./stego-advanced-2.md).

## Table of Contents
- [JPEG Unused Quantization Table LSB Steganography (EHAX 2026)](#jpeg-unused-quantization-table-lsb-steganography-ehax-2026)
- [BMP Bitplane QR Code Extraction + Steghide (BYPASS CTF 2025)](#bmp-bitplane-qr-code-extraction--steghide-bypass-ctf-2025)
- [Image Jigsaw Puzzle Reassembly via Edge Matching (BYPASS CTF 2025)](#image-jigsaw-puzzle-reassembly-via-edge-matching-bypass-ctf-2025)
- [F5 JPEG DCT Coefficient Ratio Detection (ApoorvCTF 2026)](#f5-jpeg-dct-coefficient-ratio-detection-apoorvctf-2026)
- [PNG Unused Palette Entry Steganography (ApoorvCTF 2026)](#png-unused-palette-entry-steganography-apoorvctf-2026)
- [QR Code Tile Reconstruction (UTCTF 2026)](#qr-code-tile-reconstruction-utctf-2026)
- [Seed-Based Pixel Permutation + Multi-Bitplane QR (L3m0nCTF 2025)](#seed-based-pixel-permutation--multi-bitplane-qr-l3m0nctf-2025)
- [JPEG Thumbnail Pixel-to-Text Mapping (RuCTF 2013)](#jpeg-thumbnail-pixel-to-text-mapping-ructf-2013)
- [Conditional LSB Extraction — Near-Black Pixel Filter (BaltCTF 2013)](#conditional-lsb-extraction--near-black-pixel-filter-baltctf-2013)
- [JPEG Slack Space Steganography (BSidesSF 2025)](#jpeg-slack-space-steganography-bsidessf-2025)
- [Nearest-Neighbor Interpolation Steganography (BSidesSF 2025)](#nearest-neighbor-interpolation-steganography-bsidessf-2025)
- [RGB Parity Steganography (Break In 2016)](#rgb-parity-steganography-break-in-2016)
- [Pixel Coordinate Chain Steganography (H4ckIT CTF 2016)](#pixel-coordinate-chain-steganography-h4ckit-ctf-2016)
- [AVI Frame Differential Pixel Steganography (H4ckIT CTF 2016)](#avi-frame-differential-pixel-steganography-h4ckit-ctf-2016)
- [JPEG Single-Bit-Flip Brute Force with OCR (SECCON 2017)](#jpeg-single-bit-flip-brute-force-with-ocr-seccon-2017)
- [GIF Frame PLTE Chunk Concatenation to ELF (IceCTF 2018)](#gif-frame-plte-chunk-concatenation-to-elf-icectf-2018)
- [Nested-Resize QR Overlay at Survivor Pixels (SECCON 2018)](#nested-resize-qr-overlay-at-survivor-pixels-seccon-2018)
- [ImageMagick +append Puzzle Stitching + gaps Solver (X-MAS CTF 2018)](#imagemagick-append-puzzle-stitching--gaps-solver-x-mas-ctf-2018)
- [Steghide Passphrase in JPEG Header Metadata (Saudi/Oman CTF 2019)](#steghide-passphrase-in-jpeg-header-metadata-saudioman-ctf-2019)
- [Corrupted PNG Magic and Lowercase Chunk Repair (Pragyan CTF 2019)](#corrupted-png-magic-and-lowercase-chunk-repair-pragyan-ctf-2019)

---

## JPEG Unused Quantization Table LSB Steganography (EHAX 2026)

**Pattern (Jpeg Soul):** "Insignificant" hint points to least significant bits in JPEG quantization tables (DQT). JPEG can embed DQT tables (ID 2, 3) that are never referenced by frame markers — invisible to renderers but carry hidden data.

**Detection:** JPEG has more DQT tables than components reference. Standard JPEG uses 2 tables (luminance + chrominance); extra tables with IDs 2, 3 are suspicious.

```python
from PIL import Image

img = Image.open('challenge.jpg')

# Access quantization tables (PIL exposes them as dict)
# Standard: tables 0 (luminance) and 1 (chrominance)
# Hidden: tables 2, 3 (unreferenced by SOF marker)
qtables = img.quantization

bits = []
for table_id in sorted(qtables.keys()):
    if table_id >= 2:  # Unused tables
        table = qtables[table_id]
        for i in range(64):  # 8x8 = 64 values per DQT
            bits.append(table[i] & 1)  # Extract LSB

# Convert bits to ASCII
flag = ''
for i in range(0, len(bits) - 7, 8):
    byte = int(''.join(str(b) for b in bits[i:i+8]), 2)
    if 32 <= byte <= 126:
        flag += chr(byte)
print(flag)
```

**Manual DQT extraction (when PIL doesn't expose all tables):**
```python
# Parse JPEG manually to find all DQT markers (0xFFDB)
data = open('challenge.jpg', 'rb').read()
pos = 0
while pos < len(data) - 1:
    if data[pos] == 0xFF and data[pos+1] == 0xDB:
        length = int.from_bytes(data[pos+2:pos+4], 'big')
        dqt_data = data[pos+4:pos+2+length]
        table_id = dqt_data[0] & 0x0F
        precision = (dqt_data[0] >> 4) & 0x0F  # 0=8-bit, 1=16-bit
        values = list(dqt_data[1:65]) if precision == 0 else []
        print(f"DQT table {table_id}: {values[:8]}...")
        pos += 2 + length
    else:
        pos += 1
```

**Key insight:** JPEG quantization tables are metadata — they survive recompression and most image processing. Unused table IDs (2-15) can carry arbitrary data without affecting the image.

---

## BMP Bitplane QR Code Extraction + Steghide (BYPASS CTF 2025)

**Pattern (Gold Challenge):** BMP image with QR code hidden in a specific bitplane. Extract the QR code to obtain a steghide password.

**Technique:** Extract individual bitplanes (bits 0-2) for each RGB channel, render as images, scan for QR codes.

```python
from PIL import Image
import numpy as np

img = Image.open('challenge.bmp')
pixels = np.array(img)

# Extract individual bitplanes
for ch_idx, ch_name in enumerate(['R', 'G', 'B']):
    for bit in range(3):  # Check bits 0, 1, 2
        channel = pixels[:, :, ch_idx]
        bit_plane = ((channel >> bit) & 1) * 255
        Image.fromarray(bit_plane.astype(np.uint8)).save(f'bit_{ch_name}_{bit}.png')

# Combined LSB across all channels
lsb_img = np.zeros_like(pixels)
for ch in range(3):
    lsb_img[:, :, ch] = (pixels[:, :, ch] & 1) * 255
Image.fromarray(lsb_img).save('lsb_all.png')
```

**Full attack chain:**
1. Extract bitplanes → find QR code in specific bitplane (often bit 1, not bit 0)
2. Scan QR with `zbarimg bit_G_1.png` → get steghide password
3. `steghide extract -sf challenge.bmp -p <password>` → extract hidden file

**Key insight:** Standard LSB (least significant bit) tools check bit 0 only. Hidden QR codes may be in bit 1 or bit 2 — always check multiple bitplanes systematically. BMP format preserves exact pixel values (no compression artifacts).

---

## Image Jigsaw Puzzle Reassembly via Edge Matching (BYPASS CTF 2025)

**Pattern (Jigsaw Puzzle):** Archive containing multiple puzzle piece images that must be reassembled into the original image. Reassembled image contains the flag (possibly ROT13 encoded).

**Technique:** Compute pixel intensity differences at shared edges between all piece pairs, then greedily place pieces to minimize total edge difference.

```python
from PIL import Image
import numpy as np
import os

# Load all pieces
pieces = {}
for f in sorted(os.listdir('pieces/')):
    pieces[f] = np.array(Image.open(f'pieces/{f}'))

piece_list = list(pieces.keys())
n = len(piece_list)
grid_size = int(n ** 0.5)  # e.g., 25 pieces → 5x5

# Calculate edge compatibility
def edge_diff(img1, img2, direction):
    if direction == 'right':
        return np.sum(np.abs(img1[:, -1].astype(int) - img2[:, 0].astype(int)))
    elif direction == 'bottom':
        return np.sum(np.abs(img1[-1, :].astype(int) - img2[0, :].astype(int)))

# Build compatibility matrices
right_compat = np.full((n, n), float('inf'))
bottom_compat = np.full((n, n), float('inf'))
for i in range(n):
    for j in range(n):
        if i != j:
            right_compat[i, j] = edge_diff(pieces[piece_list[i]], pieces[piece_list[j]], 'right')
            bottom_compat[i, j] = edge_diff(pieces[piece_list[i]], pieces[piece_list[j]], 'bottom')

# Greedy placement
grid = [[None] * grid_size for _ in range(grid_size)]
used = set()
for row in range(grid_size):
    for col in range(grid_size):
        best_piece, best_diff = None, float('inf')
        for idx in range(n):
            if idx in used:
                continue
            diff = 0
            if col > 0:
                diff += right_compat[grid[row][col-1], idx]
            if row > 0:
                diff += bottom_compat[grid[row-1][col], idx]
            if diff < best_diff:
                best_diff, best_piece = diff, idx
        grid[row][col] = best_piece
        used.add(best_piece)

# Reassemble
piece_h, piece_w = pieces[piece_list[0]].shape[:2]
final = Image.new('RGB', (grid_size * piece_w, grid_size * piece_h))
for row in range(grid_size):
    for col in range(grid_size):
        final.paste(Image.open(f'pieces/{piece_list[grid[row][col]]}'),
                     (col * piece_w, row * piece_h))
final.save('reassembled.png')
```

**Post-processing:** Check if reassembled image text is ROT13 encoded. Decode with `tr 'A-Za-z' 'N-ZA-Mn-za-m'`.

**Key insight:** Edge-matching works by minimizing pixel differences at shared borders. The greedy approach (place piece with smallest total edge difference to already-placed neighbors) works well for most CTF puzzles. For harder puzzles, add backtracking.

---

## F5 JPEG DCT Coefficient Ratio Detection (ApoorvCTF 2026)

**Pattern (Engraver's Fault):** Detect F5 steganography in JPEG images by analyzing DCT coefficient distributions. F5 decrements ±1 AC coefficients toward 0, creating a measurable ratio shift.

**Detection metric — ±1/±2 AC coefficient ratio:**
```python
import numpy as np
from PIL import Image
import jpegio  # or use jpeg_toolbox

def f5_ratio(jpeg_path):
    """Ratio below 0.15 indicates F5 modification; above 0.20 indicates clean."""
    jpg = jpegio.read(jpeg_path)
    coeffs = jpg.coef_arrays[0].flatten()  # Luminance Y channel
    coeffs = coeffs[coeffs != 0]  # Remove DC/zeros
    count_1 = np.sum(np.abs(coeffs) == 1)
    count_2 = np.sum(np.abs(coeffs) == 2)
    return count_1 / max(count_2, 1)
```

**Sparse image edge case:** Images with >80% zero DCT coefficients give misleading ±1/±2 ratios. Use a secondary metric:
```python
def f5_sparse_check(jpeg_path):
    """For sparse images, ±2/±3 ratio below 2.5 indicates modification."""
    jpg = jpegio.read(jpeg_path)
    coeffs = jpg.coef_arrays[0].flatten()
    count_2 = np.sum(np.abs(coeffs) == 2)
    count_3 = np.sum(np.abs(coeffs) == 3)
    return count_2 / max(count_3, 1)

# Combined classifier:
r12 = f5_ratio(path)
r23 = f5_sparse_check(path)
is_modified = r12 < 0.15 or (r12 < 0.25 and r23 < 2.5)
```

**Key insight:** F5 steganography shifts ±1 coefficients toward 0, reducing the ±1/±2 ratio. Natural JPEGs have ratio 0.25-0.45; F5-modified drop below 0.10. Sparse images (mostly flat/white) need the secondary ±2/±3 metric because their ±1 counts are inherently low.

---

## PNG Unused Palette Entry Steganography (ApoorvCTF 2026)

**Pattern (The Gotham Files):** Paletted PNG (8-bit indexed color) hides data in palette entries that no pixel references. The image uses indices 0-199 but the PLTE chunk has 256 entries — indices 200-255 contain hidden ASCII in their red channel values.

```python
from PIL import Image
import struct

def extract_unused_plte(png_path):
    img = Image.open(png_path)
    palette = img.getpalette()  # Flat list: [R0,G0,B0, R1,G1,B1, ...]
    pixels = list(img.getdata())
    used_indices = set(pixels)

    # Extract red channel from unused palette entries
    flag = ''
    for i in range(256):
        if i not in used_indices:
            r = palette[i * 3]  # Red channel
            if 32 <= r <= 126:
                flag += chr(r)
    return flag
```

**Key insight:** PNG palette can have up to 256 entries but images typically use fewer. Unused entries are invisible to viewers but persist in the file. Metadata hints like "collector", "the entries that don't make it to the page", or "red light" point to this technique. Always check which palette indices are actually referenced vs. allocated.

---

## QR Code Tile Reconstruction (UTCTF 2026)

**Pattern (QRecreate):** QR code split into tiles/pieces that must be reassembled. Tiles may be scrambled, rotated, or have missing alignment patterns.

**Reconstruction workflow:**
```python
from PIL import Image
import numpy as np

# Load scrambled tiles
tiles = []
for i in range(N_TILES):
    tile = Image.open(f'tile_{i}.png')
    tiles.append(np.array(tile))

# Strategy 1: Edge matching (like jigsaw puzzle)
# Each tile edge has a unique bit pattern — match adjacent edges
def edge_signature(tile, side):
    if side == 'top': return tuple(tile[0, :].flatten())
    if side == 'bottom': return tuple(tile[-1, :].flatten())
    if side == 'left': return tuple(tile[:, 0].flatten())
    if side == 'right': return tuple(tile[:, -1].flatten())

# Strategy 2: QR structure constraints
# - Finder patterns (large squares) MUST be at 3 corners
# - Timing patterns (alternating B/W) run between finders
# - Use these as anchors to orient remaining tiles

# Strategy 3: Brute force small grids
# For 3x3 or 4x4 grids, try all permutations and scan with zbarimg
from itertools import permutations
import subprocess

grid_size = 3
tile_size = tiles[0].shape[0]
for perm in permutations(range(len(tiles))):
    img = Image.new('L', (grid_size * tile_size, grid_size * tile_size))
    for idx, tile_idx in enumerate(perm):
        row, col = divmod(idx, grid_size)
        img.paste(Image.fromarray(tiles[tile_idx]),
                  (col * tile_size, row * tile_size))
    img.save('/tmp/qr_attempt.png')
    result = subprocess.run(['zbarimg', '/tmp/qr_attempt.png'],
                          capture_output=True, text=True)
    if result.stdout.strip():
        print(f"DECODED: {result.stdout}")
        break
```

**Key insight:** QR codes have structural constraints (finder patterns, timing patterns, format info) that drastically reduce the search space. Use QR structure as anchors before brute-forcing tile positions.

---

## Seed-Based Pixel Permutation + Multi-Bitplane QR (L3m0nCTF 2025)

**Pattern (Lost Signal):** Image with randomized pixel colors hides a QR code. Pixels are visited in a seed-determined permutation order, and data is interleaved across multiple bitplanes of the luminance (Y) channel.

**Extraction workflow:**
1. Convert image to YCbCr and extract Y (luminance) channel
2. Generate the pixel visit order using the known seed
3. Extract LSB bits from multiple bitplanes in interleaved order
4. Reconstruct as a binary image and scan as QR code

```python
from PIL import Image
import numpy as np

SEED = 739391  # Given or brute-forced

# 1. Extract Y channel
img = Image.open("challenge.png").convert("YCbCr")
Y = np.array(img.split()[0], dtype=np.uint8)
h, w = Y.shape

# 2. Generate deterministic pixel permutation
rng = np.random.RandomState(SEED)
perm = np.arange(h * w)
rng.shuffle(perm)

# 3. Extract bits from multiple bitplanes (interleaved)
bitplanes = [0, 1]  # LSB0 and LSB1
total_bits = h * w
bits = np.zeros(total_bits, dtype=np.uint8)

for i in range(total_bits):
    pix_idx = perm[i // len(bitplanes)]
    bp = bitplanes[i % len(bitplanes)]
    y, x = divmod(pix_idx, w)
    bits[i] = (Y[y, x] >> bp) & 1

# 4. Reconstruct QR code
qr = bits.reshape((h, w))
qr_img = Image.fromarray((255 * (1 - qr)).astype(np.uint8))
qr_img.save("recovered_qr.png")
# zbarimg recovered_qr.png
```

**Key insight:** The seed defines a deterministic pixel visit order (Fisher-Yates shuffle via `RandomState`). Without the correct seed, output is random noise. Bits from different bitplanes are interleaved (bit 0 from pixel N, bit 1 from pixel N, bit 0 from pixel N+1, ...), doubling the data density. Try the Y (luminance) channel first — it has the highest contrast for hidden binary data.

**Seed recovery:** If the seed is unknown, look for it in: EXIF metadata, filename, image dimensions, challenge description numbers, or brute-force small ranges.

**Detection:** Image appears as random colored noise but has suspicious dimensions (perfect square, power of 2). Challenge mentions "seed", "random", or "signal".

---

## JPEG Thumbnail Pixel-to-Text Mapping (RuCTF 2013)

**Pattern:** JPEG contains an embedded thumbnail where dark pixels map 1:1 to character positions in visible text on the main image.

```python
from PIL import Image
# Extract thumbnail: exiftool -b -ThumbnailImage secret.jpg > thumb.jpg
thumb = Image.open('thumb.jpg')
text_lines = ["line1 of visible text...", "line2..."]  # OCR or type from photo
result = ''
for y in range(thumb.height):
    for x in range(thumb.width):
        r, g, b = thumb.getpixel((x, y))[:3]
        if r < 100 and g < 100 and b < 100:  # Dark pixel = selected char
            result += text_lines[y][x]
```

**Key insight:** Extract thumbnails with `exiftool -b -ThumbnailImage`. Dark pixels act as a selection mask over the photographed text. Use OCR (ABBYY FineReader, Tesseract) to get the text grid, then map dark thumbnail pixels to character positions.

---

## Conditional LSB Extraction — Near-Black Pixel Filter (BaltCTF 2013)

**Pattern:** Only pixels with R<=1 AND G<=1 AND B<=1 carry steganographic data. Standard LSB tools miss the data because they process all pixels.

```python
from PIL import Image
img = Image.open('image.png')
bits = ''
for pixel in img.getdata():
    r, g, b = pixel[0], pixel[1], pixel[2]
    if not (r <= 1 and g <= 1 and b <= 1):
        continue  # Skip non-carrier pixels
    bits += str(r & 1) + str(g & 1) + str(b & 1)
# Convert bits to bytes
flag = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits)-7, 8))
```

**Key insight:** When standard `zsteg`/`stegsolve` find nothing, try filtering pixels by value range before LSB extraction. The carrier pixels may be restricted to near-black, near-white, or specific color ranges.

---

## JPEG Slack Space Steganography (BSidesSF 2025)

JPEG compression pads images to 8x8 pixel block boundaries. Data hidden in the padding pixels beyond the visible image dimensions:

1. **Identify padded dimensions:** JPEG rounds up to nearest multiple of 8. A 253x195 image pads to 256x200
2. **Extract slack pixels:** Use tools to extend visible region to true block dimensions

```bash
# Extend image to see slack pixels
python3 jpeg_uncrop.py input.jpg --width 256 --height 200
# Or use ImageMagick to force full decode
magick input.jpg -define jpeg:size=256x200 extended.png
```

3. **Decode binary from slack pixels:** Black=0, white=1 in the padding region. Common encoding:
   - 2 bytes: magic number
   - 1 byte: key length
   - N bytes: encryption key
   - 1 byte: message length
   - N bytes: encrypted message

**Key insight:** Most image editors and viewers crop to the stated dimensions, hiding the padding. Use `jpegtran -crop` or raw DCT decoders to access full block data.

---

## Nearest-Neighbor Interpolation Steganography (BSidesSF 2025)

Hidden data encoded as a pixel grid at regular intervals within a high-resolution image. Downscaling with nearest-neighbor interpolation extracts only the hidden pixels:

```bash
# Hidden pixels spaced 16 apart in a 4096x3072 image
# Downscale by 16x with nearest-neighbor to recover 256x192 hidden image
magick flag.webp -interpolate nearest-neighbor -interpolative-resize 256x192 flag_visible.png
```

**Key insight:** Nearest-neighbor interpolation selects exact pixel values (no blending), preserving the hidden data. Bilinear or bicubic interpolation would average surrounding pixels, destroying the message. The challenge name or description often hints at the interpolation method.

**Detection:** Open in image viewer and zoom to see repeating pixel patterns at regular intervals. Calculate GCD of image dimensions and suspected grid spacing.

---

## RGB Parity Steganography (Break In 2016)

Hidden image encoded in the parity of pixel RGB sums. Sum R+G+B per pixel -- even sum = white, odd sum = black. Renders a binary bitmap containing the hidden message.

```python
from PIL import Image
img = Image.open('image.png')
out = Image.new('1', img.size)
for x in range(img.width):
    for y in range(img.height):
        r, g, b = img.getpixel((x, y))[:3]
        out.putpixel((x, y), (r + g + b) % 2)
out.save('hidden.png')
```

**Key insight:** Unlike LSB (Least Significant Bit) stego (single channel, single bit), parity stego uses the combined sum of all channels. Look for challenge hints about "pairs", "couples", or "adding colors".

**Detection:** Image appears normal but pixel RGB sums show non-random parity distribution.

---

## Pixel Coordinate Chain Steganography (H4ckIT CTF 2016)

Each pixel encodes a data byte in the red channel and the coordinates of the next pixel to read in the green and blue channels, forming a linked-list traversal through the image.

```python
from PIL import Image

def extract_coordinate_chain(image_path, start_x=0, start_y=0):
    """Follow coordinate chain: R=data, G=next_x, B=next_y"""
    img = Image.open(image_path)
    flag = ""
    x, y = start_x, start_y
    visited = set()

    while (x, y) not in visited:
        visited.add((x, y))
        r, g, b = img.getpixel((x, y))[:3]

        if r == 0:  # null terminator
            break

        flag += chr(r)
        x, y = g, b  # next pixel coordinates from green and blue channels

    return flag

# Variants:
# - (R,G) = coordinates, B = data byte
# - Coordinates stored as (G*256+B) for images wider than 256px
# - Starting pixel indicated by metadata or known offset
```

**Key insight:** Linked-list pixel traversal hides both the message and the reading order. Standard LSB analysis misses this because only specific pixels carry data. Look for images where green/blue channels have suspiciously structured values (small numbers that could be coordinates).

---

## AVI Frame Differential Pixel Steganography (H4ckIT CTF 2016)

Compare consecutive video frames pixel-by-pixel. Pixels that increment by exactly 1 encode a "1" bit; unchanged pixels encode "0". Collect bits to form a Brainfuck program or binary message.

```python
from PIL import Image
import subprocess

def extract_frame_differential(frame_dir, num_frames):
    """Compare consecutive frames: incremented pixel = 1, same = 0"""
    bits = ""

    for i in range(num_frames - 1):
        img1 = Image.open(f"{frame_dir}/frame_{i:04d}.png")
        img2 = Image.open(f"{frame_dir}/frame_{i+1:04d}.png")

        pixels1 = list(img1.getdata())
        pixels2 = list(img2.getdata())

        for p1, p2 in zip(pixels1, pixels2):
            if p1 != p2:
                # Pixel changed (incremented by 1) = bit "1"
                bits += "1"
            else:
                bits += "0"

    # Convert bits to ASCII or interpret as Brainfuck
    message = ""
    for i in range(0, len(bits), 8):
        byte = int(bits[i:i+8], 2)
        if 32 <= byte < 127:
            message += chr(byte)

    return message

# Extract frames from AVI first:
# binwalk video.avi  (extracts embedded PNG/BMP frames)
# or: ffmpeg -i video.avi frame_%04d.png
```

**Key insight:** Frame differential steganography hides data in the temporal domain rather than spatial. Standard image stego tools analyze single frames and miss inter-frame changes. Extract all frames, then diff consecutive pairs looking for single-pixel-value increments.

---

### JPEG Single-Bit-Flip Brute Force with OCR (SECCON 2017)

Corrupted JPEG with a single bitflip. Generate all single-bit variants and scan with OCR:

```python
data = open('corrupted.jpg', 'rb').read()
for byte_pos in range(len(data)):
    for bit in range(8):
        candidate = data[:byte_pos] + bytes([data[byte_pos] ^ (1 << bit)]) + data[byte_pos+1:]
        with open(f'attempt_{byte_pos}_{bit}.jpg', 'wb') as f:
            f.write(candidate)
```

```bash
# Automated OCR scan for flag
for f in attempt_*.jpg; do
    result=$(tesseract "$f" stdout 2>/dev/null)
    if echo "$result" | grep -qi "flag\|ctf\|SECCON"; then
        echo "FOUND in $f: $result"
    fi
done
```

**Key insight:** For small files (< 10KB), the total search space for single-bit flips is `8 * file_size` — typically under 80,000 candidates, easily brute-forceable. Use thumbnail generation as a fast validity check (corrupt JPEGs fail to decode), then OCR on survivors. JPEG compressed data rule: `0xFF` is always followed by `0x00` (stuffed byte) or a marker — violations indicate the corruption location.

---

## GIF Frame PLTE Chunk Concatenation to ELF (IceCTF 2018)

**Pattern:** A GIF hides a Linux ELF binary by breaking it into indexed PNG frames. Each frame's `PLTE` (palette) chunk holds the next slice of the binary — the actual pixel data is irrelevant. Extract with Pillow: iterate frames, convert each to PNG, walk the PNG chunks, concatenate every `PLTE` body, and the result is a valid ELF file.

```python
from PIL import Image, ImagePalette
import struct

def read_png_plte(png_bytes):
    i = 8  # skip PNG magic
    while i < len(png_bytes):
        length = struct.unpack(">I", png_bytes[i:i+4])[0]
        ctype  = png_bytes[i+4:i+8]
        body   = png_bytes[i+8:i+8+length]
        if ctype == b"PLTE":
            return body
        i += 12 + length
    return b""

payload = bytearray()
with Image.open("carrier.gif") as gif:
    for frame in range(gif.n_frames):
        gif.seek(frame)
        png_buf = io.BytesIO()
        gif.save(png_buf, "PNG")
        payload += read_png_plte(png_buf.getvalue())

open("recovered.elf", "wb").write(payload)
```

**Key insight:** GIF frames are internally stored with their own palettes. When you re-encode each frame as a PNG, the palette survives as a `PLTE` chunk — an ignored but byte-accurate container. Any stego carrier that uses a multi-frame format with per-frame metadata (GIF palettes, APNG frame data, PDF page streams, MKV tracks) lets you embed data in the *metadata channel* instead of the pixel channel, bypassing most LSB-style detection. When a GIF looks like a harmless animation but contains extra frames or palette entries, dump chunk-by-chunk before touching the pixels.

**References:** IceCTF 2018 — ilovebees, writeup 11418

---

## Nested-Resize QR Overlay at Survivor Pixels (SECCON 2018)

**Pattern:** Challenge PNG decodes to two different QR codes depending on how many times it is scaled down with nearest-neighbor interpolation (500 → 250 → 100 → 50). Track which source pixels survive every reduction: for a 10× chain with `PIL.Image.resize(size, Image.NEAREST)`, survivors sit at indices `(10i+7, 10j+7)`. Overlay a second QR at exactly those positions so it only emerges after the chained resize.

```python
from PIL import Image
big = Image.open('qr1.png')              # 500x500 visible QR
small = Image.open('qr2.png')            # 50x50 hidden QR
px = big.load()
sx = small.load()
for i in range(50):
    for j in range(50):
        px[10*i+7, 10*j+7] = sx[i, j]
big.save('trap.png')
```

**Key insight:** Nearest-neighbor resize keeps exactly one pixel per source block; its offset depends on rounding (PIL picks `floor(original*scale)+0.5`). Compute the survivor index once per resize step, then compose the nested stego at those indices. Works for any number of cascaded resizes as long as the interpolation is nearest-neighbor.

**References:** SECCON 2018 — QRChecker, writeup 12014

---

## ImageMagick +append Puzzle Stitching + gaps Solver (X-MAS CTF 2018)

**Pattern:** Disk image contains N puzzle-piece PNGs carved out by `foremost` or `scalpel`. Stitch all pieces horizontally with ImageMagick `convert +append`, then feed the strip to the `gaps` jigsaw solver (https://github.com/nemanja-m/gaps) with the known piece size (often stored in EXIF) to auto-reassemble.

```bash
foremost -t png -i disk.img -o pieces
convert +append pieces/*.png strip.png
gaps --image=strip.png --size=273
```

**Key insight:** CTF jigsaw challenges rarely require manual work. Carve pieces, stitch, run `gaps` — it uses a genetic algorithm to reassemble in minutes. Read `exiftool` on each piece for the size hint.

**References:** X-MAS CTF 2018 — Message from Santa, writeup 12662

---

## Steghide Passphrase in JPEG Header Metadata (Saudi/Oman CTF 2019)

**Pattern:** JPEG file with `steghide`-embedded payload whose passphrase is hidden in plain ASCII inside the JPEG header/metadata region. Standard tools (`exiftool`, `strings`) may miss it if the byte range isn't flagged as a proper EXIF/comment tag, but `xxd` on the first few hundred bytes reveals the string.

```bash
# Scan header for suspicious ASCII
xxd info.jpg | head -20
# 00000010: ffdb 0043 0008 6261 6469 7362 6164 0008  ...C..badisbad..
#                      ^^^^^^^^^^^^^^^^^ passphrase at offset 0x18

# Confirm steghide payload with the passphrase
steghide --info info.jpg       # prompts for passphrase
steghide extract -sf info.jpg -p badisbad
```

**Key insight:** Always scan the first ~256 bytes of a JPEG with `xxd`/`hexdump -C` for ASCII runs — authors sometimes stuff passphrases into reserved areas of JFIF/APPn segments where `exiftool` doesn't surface them, but they're trivially visible in a hex view. Pair the leak with `steghide`, `outguess`, or `stegseek` wordlist seeding.

**References:** Quals Saudi and Oman National Cyber Security CTF 2019 — Hack a nice day, writeup 13232

---

## Corrupted PNG Magic and Lowercase Chunk Repair (Pragyan CTF 2019)

**Pattern:** PNG is unreadable because the 8-byte magic is tampered (e.g. `89 50 4E 47 2E 0A 2E 0A` instead of the correct `89 50 4E 47 0D 0A 1A 0A`) and critical chunk names are lowercased (`idat` instead of `IDAT`). PNG decoders treat lowercase chunk names as "ancillary" and skip them, so the image looks empty until the case is fixed. Metadata (e.g. `exiftool` Artist field) then yields the next step.

```bash
# Step 1: patch magic bytes
printf '\x89PNG\r\n\x1a\n' | dd of=broken.png conv=notrunc bs=1 count=8

# Step 2: re-capitalise critical chunk names (IHDR, IDAT, IEND, PLTE)
python3 -c "
d = open('broken.png','rb').read()
d = d.replace(b'idat', b'IDAT').replace(b'iend', b'IEND')
open('fixed.png','wb').write(d)
"

# Step 3: pull hidden metadata
exiftool fixed.png | grep -Ei 'artist|comment|desc'
# Artist : md5_MEf89jf4h9   -> use md5(...) as zip password
```

**Key insight:** PNG has two orthogonal parseability gates: the 8-byte signature and the case of each chunk name (first letter uppercase = critical). Fix both before concluding the file is empty. `pngcheck -v` flags exactly which byte/chunk is wrong. Once readable, treat EXIF `Artist`, `Description`, and `tEXt`/`iTXt` chunks as prime hiding spots.

**References:** Pragyan CTF 2019 — Magic PNGs, writeup 13833

---

## [来自实战] 物尽其用（ISCC 2026）

**技术模式**: 图像多通道LSB分别藏flag + model_state.npz藏解题提示（base64+gzip） + 通道重排后二次混洗组合最终答案

**关键操作**:
1. 压缩包体检：config.json中callback全关，说明答案不在训练流程里；model_state.npz中base_hint_bytes字段用base64+gzip解得ISCC{MD5(flag1R||flag2G)}
2. 对Input.png直接提取RGB三通道LSB各自打包为flag：R→ISCC{OgClRgOooQ}，G→ISCC{JGdJcASTrp}，B→ISCC{OZXozOrdzx}
3. flag1R直接取R通道花括号内容；flag2G不是原始G而是经过通道重排后落到逻辑G位的那个通道（逻辑(R,G,B)→(G,B,R)，故flag2G来源为原始B通道）
4. 原始B通道内容还需用对应seed对花括号内中段做一次洗牌（前缀ISCC{和}保持不动，仅打乱中间payload）
5. 最终：flag1R=OgClRgOooQ，flag2G=OXzdoxzZrO，答案=ISCC{MD5(flag1R||flag2G)}

**适用场景**: 下次遇到"模型训练附件+图片"时，先查npz字段名有无人类可读提示，再对图片做RGB三通道独立LSB提取，注意通道重排逻辑

---

## [来自实战] 神秘文件Plus（ISCC 2026）

**技术模式**: PNG尾插7z压缩包 + R通道LSB藏密码 + WAV音频左右声道差值二值载荷提取

**关键操作**:
1. PNG结构扫描：找IEND偏移（4723354）后还有5439201字节，头部37 7a bc af 27 1c=7z格式；7z带密码无法直接解
2. 返回PNG的R通道最低位按8bit还原，冒出32位十六进制口令（9f42d1364eee400aa7620c0400110223）
3. 用口令解7z，得1.wav~50.wav共50个音频切片（44100Hz/16bit PCM/双声道）
4. 横向对比全部wav的左右声道：只有3.wav左右声道不同，差异采样数2016，差值只有{1,2}两种值
5. 映射1→0，2→1，抽出2016 bit载荷，按正确维度解析得最终flag

**适用场景**: 下次遇到PNG+音频切片组合时，先检查PNG尾部是否有压缩包追加，再用位平面提取密码，然后对音频做横向差异比对而非逐文件分析

---

## [来自实战] everlasting_night — LSB列模式+md5密码+PNG宽度修改（长城杯2022）

**技术模式**: LSB隐写以"列"而非"行"存储（Stegsolve默认行模式会乱），隐藏数字作为md5隐写密码解压rar，rar内图片通过修改PNG宽度字段还原隐藏内容。

**关键操作**:
1. 010Editor检查PNG尾部：IEND之后有额外字节（先记下，可能是密码/辅助数据）
2. Stegsolve → Alpha2平面 → 发现右下角异常，但默认"Row"模式无内容；改为"Column"模式可读出隐藏数字串
3. 用读出的数字作为md5隐写工具（如stegdetect/专用脚本）的密码，解压得到rar
4. rar密码不是步骤2的原始数字，而是尾部附加字节经某种变换（广泛尝试：md5值本身作密码）
5. rar内有无后缀文件，010Editor查头部确认PNG，改后缀；GIMP改后缀为.data导入，调整宽度字段直到图像比例正常，读出flag

**适用场景**: LSB提取无果时检查Stegsolve的行/列模式切换；无后缀文件必用magic bytes确认格式；PNG图像显示异常（拉伸/截断）优先考虑宽高字段被篡改

---

## [来自实战] 盗版软件 — dmp→GIMP域名提取 + red通道隔字节LSB + base85（长城杯决赛2024）

**技术模式**: dmp浏览器内存文件改.data用GIMP调整位移读出域名，exe运行后red通道LSB隔字节存储压缩包，base85解码后微步沙箱分析得IP。

**关键操作**:
1. dmp改后缀为.data，GIMP打开为Raw Image Data，调整宽度/位移参数直到出现可读文本（域名winhack.com）
2. 访问域名下载exe，双击运行生成图片（或直接分析exe资源段）
3. Stegsolve查看red plane 0（R通道LSB），发现zip文件头7z但数据间隔分布
4. Python脚本隔字节提取：`infile.read(1); infile.seek(1,1); byte=infile.read(1)`循环
5. 得到zip内有.b后缀文件，base85解码（`base64.b85decode`）
6. 微步云沙箱/VirusTotal上传分析，联网行为记录得到C2 IP

**适用场景**: dmp内存文件用GIMP作为通用图像Raw查看器；LSB隐写若文件大小是预期2倍，必考虑隔字节存储；未知后缀文件先strings/binwalk，再试base85/base64/hex；恶意样本分析必用沙箱而非本地运行

---

## [来自实战] check — PNG RGB-LSB提取+HTML十六进制实体二次解码 (HW训练)

**技术模式**: PNG图片表面正常 → RGB各通道最低位(LSB)拼字节 → 得到`&#x66;&#x6c;...`HTML十六进制实体编码 → 再decode一次得到flag文本。**两步还原**：LSB提取→实体解码。

**关键操作**:
1. 题目名"check"暗示检查图片内部
2. 按像素顺序取R/G/B通道最低位，每8位组成1字节：
   ```python
   from PIL import Image
   img = Image.open('check.png').convert('RGBA')
   bits = [str(px[ch]&1) for px in img.getdata() for ch in (0,1,2)]
   raw = bytes(int(''.join(bits[i:i+8]),2) for i in range(0,len(bits)-7,8))
   ```
3. 发现`&#x66;&#x6c;&#x61;&#x67;...`→ HTML十六进制实体编码
4. `from html import unescape; flag = unescape(raw.decode('latin1'))`
5. 或用regex：`re.sub(r'&#x([0-9a-f]+);', lambda m: chr(int(m.group(1),16), text)`

**适用场景**: PNG+题目暗示检查→先RGB-LSB；LSB提取结果是编码而非明文→再看编码格式(HTML实体/base64/hex)；`&#x`开头是HTML十六进制实体；Python `html.unescape()`直接处理

---

## [来自实战] misc pdf — PDF不可见文本层藏flag (HW训练)

**技术模式**: PDF页面肉眼只看到图片，无明显flag → 提取PDF文本层（pypdf/pdfplumber/fitz）→ 大量`\t\r\xa0`空白字符中夹着明文flag。

**关键操作**:
1. 用阅读器渲染页面确认无可见flag（图片+空白）
2. 提取文本层：
   ```python
   import pypdf
   reader = pypdf.PdfReader('pdf.pdf')
   text = reader.pages[0].extract_text()
   import re
   flag = re.search(r'flag\{[^}]+\}', text).group()
   ```
3. 或用pdfplumber/PyMuPDF(fitz)：`page.get_text()`
4. 文本中flag被大量`\t\r\xa0`包围，正则`flag\{[^}]+\}`可直接提取

**适用场景**: PDF取证三步：渲染→提取文本→导出对象；肉眼无flag先提文本层，再查元数据，再导出内嵌对象；白色文字/透明文字/图片下方文字均可被程序提取；pdfplumber比pypdf更稳定处理特殊空白字符
