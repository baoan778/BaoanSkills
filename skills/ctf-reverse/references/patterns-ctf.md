# CTF Reverse - Competition-Specific Patterns (Part 1)

## Table of Contents
- [Hidden Emulator Opcodes + LD_PRELOAD Key Extraction (0xFun 2026)](#hidden-emulator-opcodes--ld_preload-key-extraction-0xfun-2026)
- [Spectre-RSB SPN Cipher — Static Parameter Extraction (0xFun 2026)](#spectre-rsb-spn-cipher--static-parameter-extraction-0xfun-2026)
- [Image XOR Mask Recovery via Smoothness (VuwCTF 2025)](#image-xor-mask-recovery-via-smoothness-vuwctf-2025)
- [Shellcode in Data Section via mmap RWX (VuwCTF 2025)](#shellcode-in-data-section-via-mmap-rwx-vuwctf-2025)
- [Recursive execve Subtraction (VuwCTF 2025)](#recursive-execve-subtraction-vuwctf-2025)
- [Byte-at-a-Time Block Cipher Attack (UTCTF 2024)](#byte-at-a-time-block-cipher-attack-utctf-2024)
- [Mathematical Convergence Bitmap (EHAX 2026)](#mathematical-convergence-bitmap-ehax-2026)
- [Windows PE XOR Bitmap Extraction + OCR (srdnlenCTF 2026)](#windows-pe-xor-bitmap-extraction--ocr-srdnlenctf-2026)
- [Two-Stage Loader: RC4 Gate + VM Constraints (srdnlenCTF 2026)](#two-stage-loader-rc4-gate--vm-constraints-srdnlenctf-2026)
- [GBA ROM VM Hash Inversion via Meet-in-the-Middle (srdnlenCTF 2026)](#gba-rom-vm-hash-inversion-via-meet-in-the-middle-srdnlenctf-2026)
- [Sprague-Grundy Game Theory Binary (DiceCTF 2026)](#sprague-grundy-game-theory-binary-dicectf-2026)
- [Kernel Module Maze Solving (DiceCTF 2026)](#kernel-module-maze-solving-dicectf-2026)
- [Multi-Threaded VM with Channel Synchronization (DiceCTF 2026)](#multi-threaded-vm-with-channel-synchronization-dicectf-2026)
- [Backdoored Shared Library Detection via String Diffing (Hack.lu CTF 2012)](#backdoored-shared-library-detection-via-string-diffing-hacklu-ctf-2012)
- [Custom binfmt Kernel Module with RC4 Flat Binaries (BSidesSF 2026)](#custom-binfmt-kernel-module-with-rc4-flat-binaries-bsidessf-2026)
- [Hash-Resolved Imports / No-Import Ransomware (BSidesSF 2026)](#hash-resolved-imports--no-import-ransomware-bsidessf-2026)
- [ELF Section Header Corruption for Anti-Analysis (BSidesSF 2026)](#elf-section-header-corruption-for-anti-analysis-bsidessf-2026)
- [VM Trace Diffing Instead of Full Disassembly (CONFidence CTF 2019 Teaser)](#vm-trace-diffing-instead-of-full-disassembly-confidence-ctf-2019-teaser)

---

## Hidden Emulator Opcodes + LD_PRELOAD Key Extraction (0xFun 2026)

**Pattern (CHIP-8):** Non-standard opcode `FxFF` triggers hidden `superChipRendrer()` → AES-256-CBC decryption. Key derived from binary constants.

**Technique:**
1. Check all instruction dispatch branches for non-standard opcodes
2. Hidden opcode may trigger crypto functions (OpenSSL)
3. Use `LD_PRELOAD` hook on `EVP_DecryptInit_ex` to capture AES key at runtime:

```c
#include <openssl/evp.h>
int EVP_DecryptInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                       ENGINE *impl, const unsigned char *key,
                       const unsigned char *iv) {
    // Log key
    for (int i = 0; i < 32; i++) printf("%02x", key[i]);
    printf("\n");
    // Call original
    return ((typeof(EVP_DecryptInit_ex)*)dlsym(RTLD_NEXT, "EVP_DecryptInit_ex"))
           (ctx, type, impl, key, iv);
}
```

```bash
gcc -shared -fPIC -ldl -lssl hook.c -o hook.so
LD_PRELOAD=./hook.so ./emulator rom.ch8
```

---

## Spectre-RSB SPN Cipher — Static Parameter Extraction (0xFun 2026)

**Pattern:** Binary uses cache side channels to implement S-boxes, but ALL cipher parameters (round keys, S-box tables, permutation) are in the binary's data section.

**Key insight:** Don't try to run on special hardware. Extract parameters statically:
- 8 S-boxes × 8 output bits, 256 entries each
- Values `0x340` = bit 1, `0x100` = bit 0
- 64-byte permutation table, 8 round keys

```python
# Extract from binary data section
import struct
sbox = [[0]*256 for _ in range(8)]
for i in range(8):
    for j in range(256):
        val = struct.unpack('<I', data[sbox_offset + (i*256+j)*4 : ...])[0]
        sbox[i][j] = 1 if val == 0x340 else 0
```

**Lesson:** Side-channel implementations embed lookup tables in memory. Extract statically.

---

## Image XOR Mask Recovery via Smoothness (VuwCTF 2025)

**Pattern (Trianglification):** Image divided into triangle regions, each XOR-encrypted with `key = (mask * x - y) & 0xFF` where mask is unknown (0-255).

**Recovery:** Natural images have smooth gradients. Brute-force mask (256 values per region), score by neighbor pixel differences:

```python
import numpy as np
from PIL import Image

img = np.array(Image.open('encrypted.png'))

def score_smoothness(region_pixels, mask, positions):
    decrypted = []
    for (x, y), pixel in zip(positions, region_pixels):
        key = (mask * x - y) & 0xFF
        decrypted.append(pixel ^ key)
    # Score: sum of absolute differences between adjacent pixels
    return -sum(abs(decrypted[i] - decrypted[i+1]) for i in range(len(decrypted)-1))

for region in regions:
    best_mask = max(range(256), key=lambda m: score_smoothness(region, m, positions))
```

**Search space:** 256 candidates × N regions = trivial. Smoothness is a reliable scoring metric for natural images.

---

## Shellcode in Data Section via mmap RWX (VuwCTF 2025)

**Pattern (Missing Function):** Binary relocates data to RWX memory (mmap with PROT_READ|PROT_WRITE|PROT_EXEC) and jumps to it.

**Detection:** Look for `mmap` with PROT_EXEC flag. Embedded shellcode often uses XOR with rotating key.

**Analysis:** Extract data section, apply XOR key (try 3-byte rotating), disassemble result.

---

## Recursive execve Subtraction (VuwCTF 2025)

**Pattern (String Inspector):** Binary recursively calls itself via `execve`, subtracting constants each time.

**Solution:** Find base case and work backward. Often a mathematical relationship like `N * M + remainder`.

---

## Byte-at-a-Time Block Cipher Attack (UTCTF 2024)

**Pattern (PES-128):** First output byte depends only on first input byte (no diffusion).

**Attack:** For each position, try all 256 byte values, compare output byte with target ciphertext. One match per byte = full plaintext recovery without knowing the key.

**Detection:** Change one input byte → only corresponding output byte changes. This means zero cross-byte diffusion = trivially breakable.

---

## Mathematical Convergence Bitmap (EHAX 2026)

**Pattern (Compute It):** Binary classifies complex-plane coordinates by Newton's method convergence. The classification results, arranged as a grid, spell out the flag in ASCII art.

**Recognition:**
- Input file with coordinate pairs (x, y)
- Binary iterates a mathematical function (e.g., z^3 - 1 = 0) and outputs pass/fail
- Grid dimensions hinted by point count (e.g., 2600 = 130×20)
- 5-pixel-high ASCII art font common in CTFs

**Newton's method for z^3 - 1:**
```python
def newton_converges_to_one(px, py, max_iter=50, target_count=12):
    """Returns True if Newton's method converges to z=1 in exactly target_count steps."""
    x, y = px, py
    count = 0
    for _ in range(max_iter):
        f_real = x**3 - 3*x*y**2 - 1.0
        f_imag = 3*x**2*y - y**3
        J_rr = 3.0 * (x**2 - y**2)
        J_ri = 6.0 * x * y
        det = J_rr**2 + J_ri**2
        if det < 1e-9:
            break
        x -= (f_real * J_rr + f_imag * J_ri) / det
        y -= (f_imag * J_rr - f_real * J_ri) / det
        count += 1
        if abs(x - 1.0) < 1e-6 and abs(y) < 1e-6:
            break
    return count == target_count

# Read coordinates and render bitmap
points = [(float(x), float(y)) for x, y in ...]
bits = [1 if newton_converges_to_one(px, py) else 0 for px, py in points]
WIDTH = 130  # 2600 / 20 rows
for r in range(len(bits) // WIDTH):
    print(''.join('#' if bits[r*WIDTH+c] else '.' for c in range(WIDTH)))
```

**Key insight:** The binary is a mathematical classifier, not a flag checker. The flag is in the visual pattern of classifications, not in the binary's output. Reverse-engineer the math, apply to all coordinates, and visualize as bitmap.

---

## Windows PE XOR Bitmap Extraction + OCR (srdnlenCTF 2026)

**Pattern (Artistic Warmup):** Binary renders input text, compares rendered bitmap against expected pixel data stored XOR'd with constant in `.rdata`. No need to compute — extract expected pixels directly.

**Attack:**
1. Reverse the core check function to identify rendering and comparison logic
2. Find the expected pixel blob in `.rdata` (look for large data block referenced near comparison)
3. XOR with constant (e.g., 0xAA) to recover expected rendered DIB
4. Save as image and OCR to recover flag text

```python
import numpy as np
from PIL import Image

with open("binary.exe", "rb") as f:
    data = f.read()

# Extract from .rdata section (offsets from reversing)
blob_offset = 0xC3620  # .rdata offset to XOR'd blob
blob_size = 0x15F90     # 450 * 50 * 4 (BGRA)
blob = np.frombuffer(data[blob_offset:blob_offset + blob_size], dtype=np.uint8)
expected = blob ^ 0xAA  # XOR with constant key

# Reshape as BGRA image (dimensions from reversing)
img = expected.reshape(50, 450, 4)
channel = img[:, :, 0]  # Take one channel (grayscale text)
Image.fromarray(channel, "L").save("target.png")

# OCR with charset whitelist
import subprocess
result = subprocess.run(
    ["tesseract", "target.png", "stdout", "-c",
     "tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"],
    capture_output=True, text=True)
print(result.stdout)
```

**Key insight:** When a binary renders text and compares pixels, the expected pixel data is the flag rendered as an image. Extract it directly from the binary data section without needing to understand the rendering logic. OCR with charset whitelist improves accuracy for CTF flag characters.

---

## Two-Stage Loader: RC4 Gate + VM Constraints (srdnlenCTF 2026)

**Pattern (Cornflake v3.5):** Two-stage malware loader — stage 1 uses RC4 username gate, stage 2 downloaded from C2 contains VM-based password validation.

**Stage 1 — RC4 username recovery:**
```python
def rc4(key, data):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(b ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)

# Key from binary strings, ciphertext from stored hex
username = rc4(b"s3cr3t_k3y_v1", bytes.fromhex("46f5289437bc009c17817e997ae82bfbd065545d"))
```

**Stage 2 — VM constraint extraction:**
1. Download stage 2 from C2 endpoint (e.g., `/updates/check.php`)
2. Reverse VM bytecode interpreter (typically 15-20 opcodes)
3. Extract linear equality constraints over flag characters
4. Solve constraint system (Z3 or manual)

**Key insight:** Multi-stage loaders often use simple crypto (RC4) for the first gate and more complex validation (custom VM) for the second. The VM memory may be uninitialized (all zeros), drastically simplifying constraint extraction since memory-dependent operations become constants.

---

## GBA ROM VM Hash Inversion via Meet-in-the-Middle (srdnlenCTF 2026)

**Pattern (Dante's Trial):** Game Boy Advance ROM implements a custom VM. Hash function uses FNV-1a variant with uninitialized memory (stays all zeros). Meet-in-the-middle attack splits the search space.

**Hash function structure:**
```python
# FNV-1a variant with XOR/multiply
P = 0x100000001b3        # FNV prime
CUP = 0x9e3779b185ebca87  # Golden ratio constant
MASK64 = (1 << 64) - 1

def fmix64(h):
    """Finalization mixer."""
    h ^= h >> 33; h = (h * 0xff51afd7ed558ccd) & MASK64
    h ^= h >> 33; h = (h * 0xc4ceb9fe1a85ec53) & MASK64
    h ^= h >> 33
    return h

def hash_input(chars, seed_lo=0x84222325, seed_hi=0xcbf29ce4):
    hlo, hhi, ptr = seed_lo, seed_hi, 0
    for c in chars:
        # tri_mix(c, mem[ptr]) — mem is always 0
        delta = ((ord(c) * CUP) ^ (0 * P)) & MASK64
        hlo = ((hlo ^ (delta & 0xFFFFFFFF)) * (P & 0xFFFFFFFF)) & 0xFFFFFFFF
        hhi = ((hhi ^ (delta >> 32)) * (P >> 32)) & 0xFFFFFFFF
        ptr = (ptr + 1) & 0xFF
    combined = ((hhi << 32) | (hlo ^ ptr)) & MASK64
    return fmix64((combined * P) & MASK64)
```

**Meet-in-the-middle attack:**
```python
import string

TARGET = 0x73f3ebcbd9b4cd93
LENGTH = 6
SPLIT = 3
charset = [c for c in string.printable if 32 <= ord(c) < 127]

# Forward pass: enumerate first 3 characters from seed state
forward = {}
for c1 in charset:
    for c2 in charset:
        for c3 in charset:
            state = hash_forward(seed, [c1, c2, c3])
            forward[state] = c1 + c2 + c3

# Backward pass: invert fmix64 and final multiply, enumerate last 3 chars
inv_target = invert_fmix64(TARGET)
for c4 in charset:
    for c5 in charset:
        for c6 in charset:
            state = hash_backward(inv_target, [c4, c5, c6])
            if state in forward:
                print(f"Found: {forward[state]}{c4}{c5}{c6}")
```

**Key insight:** Meet-in-the-middle reduces search from `95^6 ≈ 7.4×10^11` to `2×95^3 ≈ 1.7×10^6` — a factor of ~430,000x speedup. Critical when the hash function is invertible from the output side (i.e., `fmix64` and the final multiply can be undone). Also: uninitialized VM memory that stays zero simplifies the hash function by removing a variable.

---

## Sprague-Grundy Game Theory Binary (DiceCTF 2026)

**Pattern (Bedtime):** Stripped Rust binary plays N rounds of bounded Nim. Each round has piles and max-move parameter k. Binary uses a PRNG for moves when in a losing position; user must respond optimally so the PRNG eventually generates an invalid move (returns 1). Sum of return values must equal a target.

**Game theory identification:**
- Bounded Nim: remove 1 to k items from any pile per turn
- **Grundy value** per pile: `pile_value % (k+1)`
- **XOR** of all Grundy values: non-zero = winning (N-position), zero = losing (P-position)
- N-positions: computer wins automatically (returns 0)
- P-positions: computer uses PRNG, may make invalid move (returns 1)

**PRNG state tracking through user feedback:**
```python
MASK64 = (1 << 64) - 1

def prng_step(state, pile_count, k):
    """Computer's PRNG move. Returns (pile_idx, amount, new_state)."""
    r12 = state[2] ^ 0x28027f28b04ccfa7
    rax = (state[1] + r12) & MASK64
    s0_new = ROL64((state[0] ** 2 + rax) & MASK64, 32)
    r12_upd = (r12 + rax) & MASK64
    s0_final = ROL64((s0_new ** 2 + r12_upd) & MASK64, 32)

    pile_idx = rax % pile_count
    amount = (r12_upd % k) + 1
    return pile_idx, amount, [s0_final, r12_upd, state[2]]

# Critical: state[2] updated ONLY by user moves (XOR of pile_idx, amount, new_value)
# PRNG moves do NOT affect state[2] — creates feedback loop
```

**Solving approach:**
1. Dump game data from GDB (all entries with pile values and parameters)
2. Classify: count P-positions (return 1) vs N-positions (return 0)
3. Simulate each P-position: PRNG moves → user responds optimally → track state[2]
4. Encode user moves as input format (4-digit decimal pairs, reversed order)

**Key insight:** When a game binary's PRNG state depends on user input, you must simulate the full feedback loop — not just solve the game theory. Use GDB hardware watchpoints to discover which state variables are affected by user vs computer moves.

---

## Kernel Module Maze Solving (DiceCTF 2026)

**Pattern (Explorer):** Rust kernel module implements a 3D maze via `/dev/challenge` ioctls. Navigate the maze, avoid decoy exits (status=2), find the real exit (status=1), read the flag.

**Ioctl enumeration:**
| Command | Description |
|---------|-------------|
| `0x80046481-83` | Get maze dimensions (3 axes, 8-16 each) |
| `0x80046485` | Get status: 0=playing, 1=WIN, 2=decoy |
| `0x80046486` | Get wall bitfield (6 directions) |
| `0x80406487` | Get flag (64 bytes, only when status=1) |
| `0x40046488` | Move in direction (0-5) |
| `0x6489` | Reset position |

**DFS solver with decoy avoidance:**
```c
// Minimal static binary using raw syscalls (no libc) for small upload size
// gcc -nostdlib -static -Os -fno-builtin -o solve solve.c -Wl,--gc-sections && strip solve

int visited[16][16][16];
int bad[16][16][16];   // decoy positions across resets

void dfs(int fd, int x, int y, int z) {
    if (visited[x][y][z] || bad[x][y][z]) return;
    visited[x][y][z] = 1;

    int status = ioctl_get_status(fd);
    if (status == 1) { read_flag(fd); exit(0); }
    if (status == 2) { bad[x][y][z] = 1; return; }  // decoy — mark bad

    int walls = ioctl_get_walls(fd);
    int dx[] = {1,-1,0,0,0,0}, dy[] = {0,0,1,-1,0,0}, dz[] = {0,0,0,0,1,-1};
    int opp[] = {2,3,0,1,5,4};  // opposite directions for backtracking

    for (int dir = 0; dir < 6; dir++) {
        if (!(walls & (1 << dir))) continue;  // wall present
        ioctl_move(fd, dir);
        dfs(fd, x+dx[dir], y+dy[dir], z+dz[dir]);
        ioctl_move(fd, opp[dir]);  // backtrack
    }
}
// After decoy hit: reset via ioctl 0x6489, clear visited, re-run DFS
```

**Remote deployment:** Upload binary via base64 chunks over netcat shell, decode, execute.

**Key insight:** For kernel module challenges, injecting test binaries into initramfs and probing ioctls dynamically is faster than static RE of stripped kernel modules. Keep solver binary minimal (raw syscalls, no libc) for fast upload.

---

## Multi-Threaded VM with Channel Synchronization (DiceCTF 2026)

**Pattern (locked-in):** Custom stack-based VM runs 16 concurrent threads verifying a 30-char flag. Threads communicate via futex-based channels. Pipeline: input → XOR scramble → transformation → base-4 state machine → final check.

**Analysis approach:**
1. **Identify thread roles** by tracing channel read/write patterns in GDB
2. **Extract constants** (XOR scramble values, lookup tables) via breakpoints on specific opcodes
3. **Watch for inverted logic:** validity check returns 0 for valid, non-zero for blocked (opposite of intuition)
4. **Detect futex quirks:** `unlock_pi` on unowned mutex returns EPERM=1, which can change all computations

**BFS state space search for constrained state machines:**
```python
from collections import deque

def solve_flag(scramble_vals, lookup_table, initial_state, target_state):
    """BFS through state machine to find valid flag bytes."""
    flag = [None] * 30
    # Known prefix/suffix from flag format
    flag[0:5] = list(b'dice{')
    flag[29] = ord('}')

    # For each unknown position, try all printable ASCII
    states = {initial_state}
    for pos in range(28, 4, -1):  # processed in reverse
        next_states = {}
        for state in states:
            for ch in range(32, 127):
                transformed = transform(ch, scramble_vals[pos])
                digits = to_base4(transformed)
                new_state = apply_digits(state, digits, lookup_table)
                if new_state is not None:  # valid path exists
                    next_states.setdefault(new_state, []).append((state, ch))
        states = set(next_states.keys())

    # Trace back from target_state to recover flag
```

**Key insight:** Multi-threaded VMs require tracing data flow across thread boundaries. Channel-based communication creates a pipeline — identify each thread's role (input, transform, validate, output) by watching which channels it reads/writes. Constants that affect computation may come from unexpected sources (futex return values, thread IDs).

---

## Backdoored Shared Library Detection via String Diffing (Hack.lu CTF 2012)

**Pattern (Zombie Lockbox):** A setuid binary uses `strcmp` for password validation. The expected password is visible via `strings` and works under GDB (which drops suid), but fails when run normally. The binary links against a non-standard libc that patches function behavior based on suid status.

**Detection steps:**
1. Check for non-standard library paths with `ldd`:
```bash
ldd ./binary
# Suspicious: libc.so.6 => /lib/libc/libc.so.6  (non-standard path)
# Normal:    libc.so.6 => /lib32/libc.so.6
```

2. Diff strings between the suspicious and system libc:
```bash
strings /lib/libc/libc.so.6 > suspicious_strings
strings /lib32/libc-2.15.so > normal_strings
diff suspicious_strings normal_strings
```

3. Disassemble the patched function (e.g., `puts`) to find injected code:
```bash
gdb /lib/libc/libc.so.6
(gdb) disas puts
# Look for unexpected calls or branches
# Injected code may check suid status (getuid/geteuid syscalls)
# and swap the expected password at runtime
```

**Key insight:** When a binary behaves differently under GDB vs. normal execution, check `ldd` for non-standard library paths. Suid binaries drop privileges under debuggers, so a backdoored libc can detect this via `getuid`/`geteuid` syscalls and change program behavior accordingly. The `strings | diff` approach quickly reveals injected data without full disassembly.

---

---

## Custom binfmt Kernel Module with RC4 Flat Binaries (BSidesSF 2026)

**Pattern (Private Binary):** A custom Linux kernel module (`.ko`) registers a `binfmt` handler for non-standard binary formats. When a file with a specific magic number is executed, the kernel module intercepts it, decrypts the contents in memory, and jumps to the entry point.

**Reverse engineering approach:**
1. **Analyze the `.ko`:** Look for `register_binfmt()` call — it registers a `struct linux_binfmt` with a `load_binary` callback
2. **Find the magic number:** The `load_binary` function checks the file's first bytes against a specific magic number to identify its format
3. **Extract the encryption key:** Look for `movabs` instructions loading 8-byte constants — these are often RC4 key bytes
4. **Identify the encryption scheme:** Common choices are RC4, XOR, or AES-ECB. RC4 is identifiable by the S-box initialization loop (256-byte array, swap pattern)
5. **Decrypt the flat binary:** Apply the recovered key to the encrypted file contents, skipping any header

```python
from Crypto.Cipher import ARC4

# Extract RC4 key from kernel module (found via movabs instructions)
key = bytes([0x41, 0x42, 0x43, ...])  # Key bytes from .ko disassembly

with open('encrypted.bin', 'rb') as f:
    header = f.read(HEADER_SIZE)  # Skip binfmt header
    encrypted = f.read()

cipher = ARC4.new(key)
decrypted = cipher.decrypt(encrypted)

# The decrypted output is a flat binary (no ELF headers)
# Load at the fixed virtual address specified in the kernel module
# Disassemble with: objdump -b binary -m i386:x86-64 -D decrypted.bin
# Or in Ghidra: import as "Raw Binary", set base address from .ko
```

**Detection in kernel module:**
- `register_binfmt` / `unregister_binfmt` calls
- `vm_mmap()` or `vm_brk()` for memory allocation at fixed addresses
- Direct jump to mapped memory (entry point execution)
- S-box initialization pattern (RC4): loop 0-255, swap `S[i]` with `S[j]`

**Key insight:** The flat binary has no ELF headers, so standard tools won't recognize it. You must extract the load address from the kernel module (look for the `vm_mmap` call's address argument) and import the decrypted blob at that address in your disassembler. RC4 keys in kernel modules are often stored as immediate values in `mov` or `movabs` instructions rather than in data sections.

**References:** BSidesSF 2026 "Private Binary"

---

## Hash-Resolved Imports / No-Import Ransomware (BSidesSF 2026)

**Pattern (Ran Somewhere):** Malware binary has zero visible imports — all API calls are resolved at runtime by hashing symbol names and comparing against pre-computed hash values. The binary uses `dlopen` + a custom hash table to find libc and libcrypto functions.

**Identification:**
- `readelf -d` shows no dynamic symbols or very few (just `dlopen`/`dlsym`)
- Strings reveal no standard API names
- Disassembly shows hash computation loops followed by indirect calls
- RC4-encrypted embedded strings (RSA public key, file paths, passphrases)

**Analysis shortcut — LD_PRELOAD key extraction:**

Rather than reversing the full hash resolution and key derivation, hook the crypto functions that the malware ultimately calls:

```c
// hook_crypto.c — captures AES key used by the ransomware
#define _GNU_SOURCE
#include <dlfcn.h>
#include <openssl/evp.h>
#include <stdio.h>

int EVP_CipherInit_ex(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *type,
                       ENGINE *impl, const unsigned char *key,
                       const unsigned char *iv) {
    if (key) {
        FILE *f = fopen("/tmp/aes_key.bin", "wb");
        fwrite(key, 1, 32, f);  // AES-256
        fclose(f);
        fprintf(stderr, "[HOOK] AES key captured\n");
    }
    typedef int (*orig_t)(EVP_CIPHER_CTX*, const EVP_CIPHER*, ENGINE*,
                          const unsigned char*, const unsigned char*);
    orig_t orig = (orig_t)dlsym(RTLD_NEXT, "EVP_CipherInit_ex");
    return orig(ctx, type, impl, key, iv);
}
```

```bash
# Compile and run
gcc -shared -fPIC -o hook.so hook_crypto.c -ldl
# Run in Docker container (ransomware may be destructive!)
docker run --rm -v $(pwd):/work -w /work ubuntu:22.04 \
  bash -c "LD_PRELOAD=./hook.so ./ransomware; xxd /tmp/aes_key.bin"
```

**Hash resolution patterns:**
- **SipHash variant:** Two 64-bit seeds, iterative mixing with symbol name bytes
- **DJB2/FNV variants:** Simpler hash functions with recognizable constants (`5381`, `0xcbf29ce484222325`)
- **ROR13-based:** Windows malware favorite: `hash = (hash >> 13) | (hash << 19); hash += c`

**Decryption after key capture:**
```python
from Crypto.Cipher import AES

key = open('/tmp/aes_key.bin', 'rb').read()
iv = open('/tmp/aes_iv.bin', 'rb').read()  # Also hookable
cipher = AES.new(key, AES.MODE_CBC, iv)

with open('flag.txt.enc', 'rb') as f:
    ct = f.read()
pt = cipher.decrypt(ct)
# Remove PKCS7 padding
pt = pt[:-pt[-1]]
print(pt.decode())
```

**Key insight:** When a binary resolves all imports via hashing, don't waste time reversing the hash function and building a rainbow table. Instead, let the malware resolve everything itself by running it in a sandboxed environment with `LD_PRELOAD` hooks on the functions you care about (OpenSSL crypto functions, file I/O, network calls). The AES key is deterministic across runs — if it works once, it works always.

**Safety:** Always run suspected ransomware in a Docker container or VM. Mount only copies of the encrypted files, never originals.

**References:** BSidesSF 2026 "Ran Somewhere"

---

## ELF Section Header Corruption for Anti-Analysis (BSidesSF 2026)

**Pattern (stubborn-elf):** An ELF binary has deliberately corrupted section header table entries, causing standard analysis tools (`readelf`, `objdump`, IDA, Ghidra) to crash or produce errors. However, the **program headers** (which the OS loader uses) are intact, so the binary executes normally. The flag is appended after the corrupted sections, marked with magic bytes.

```python
import sys

# Standard tools fail on corrupted section headers
# Manual parsing bypasses section headers entirely

with open("stubborn_elf", "rb") as f:
    data = f.read()

# Search for magic marker appended after ELF sections
magic = b"\xDE\xAD\xBE\xEF\xCA\xFE\xBA\xBE"
idx = data.find(magic)
if idx >= 0:
    # Data after magic is XOR-encrypted
    encrypted = data[idx + len(magic):]
    decrypted = bytes(b ^ 0x42 for b in encrypted)
    print(decrypted.decode(errors='ignore'))
```

**Key insight:** ELF execution requires **program headers** (PT_LOAD segments), NOT section headers. Section headers are metadata for debuggers and analysis tools — they're optional at runtime. Corrupting `e_shoff`, `e_shnum`, or `e_shstrndx` in the ELF header breaks tools but not execution. When tools fail, parse the binary manually or patch the ELF header to zero out section header references before loading in a disassembler.

**Recovery approach:**
```bash
# Patch section header offset to 0 (removes section table)
printf '\x00\x00\x00\x00\x00\x00\x00\x00' | dd of=binary bs=1 seek=40 conv=notrunc
# Now Ghidra/IDA can load it using program headers only

# Or use readelf -l (program headers only, ignores sections)
readelf -l stubborn_elf
```

**When to recognize:** `readelf -S` crashes or shows garbage. `file` command identifies it as ELF. `readelf -l` (lowercase L, program headers) works fine. The binary runs normally despite tool failures.

**References:** BSidesSF 2026 "stubborn-elf"

---

## VM Trace Diffing Instead of Full Disassembly (CONFidence CTF 2019 Teaser)

**Pattern (Go Machine):** Go binary runs a 15-handler stack-VM (`0123456789OEQLCI` dispatch string) whose opcode meanings are rotated by an LCG-driven `shuffle` handler after every tick. Rewriting the interpreter faithfully is painful; the VM actually computes a simple 32-bit hash over 4-character input groups.

Instead, attach a debugger-driven tracer to the dispatch routine and dump `(opcode, stack)` per step — then compare traces for two nearly identical inputs:

```python
# Pseudo-code for an IDAPython / gdb conditional-breakpoint tracer
def on_dispatch():
    op  = read_byte(bytecode + pc)
    top = stack[:sp+1]
    print(f"{decode(op)}\t({'|'.join(hex(x) for x in top)})")

# Replay the dumped trace in plain Python; no bytecode parsing, no shuffle logic:
elif line.startswith('save at (0x51)'):
    return stack[top] == expected_hash   # calculated hash lands at mem[0x51]

# Diff trace("abcd") vs trace("dcba") -> the same mul/mod sequence shows up,
# revealing the real algorithm:
def calc_hash(x, mod):
    for _ in range(8):
        x = x * x % mod
    return x * x_original % mod
```

Dump the per-group moduli (`[0x88ca6b51, 0x8405b751, 0xbfa08c87, 0x82013f23, 0x4666751b, 0x5271083f]`) and expected hashes from the trace, then brute-force 4-character permutations of `string.printable` against `calc_hash`.

**Key insight:** Custom VMs with self-modifying dispatch (shuffle, rotor, LCG-keyed opcode table) are designed to punish naive reimplementation. Recording the executed instruction stream bypasses the trick entirely — the trace is deterministic for a given input, and diffing two traces with a single-bit difference localises the "real" algorithm hiding under the VM overhead.

**References:** CONFidence CTF 2019 Teaser — Go Machine, writeup 13947

---

## [来自实战] Box（ISCC 2026）

**技术模式**: 无文件头高熵二进制逆向：16字节块同位字节相似度分析 → 发现特殊块规律 → 异或模板块推key → 语义辅助补全flag

**关键操作**:
1. 文件体检：统计信息熵（约7.995，接近密文）、按16字节分块、确认无常见文件头
2. 不看整块是否重复，改为看两块在相同偏移上有多少字节相等，筛出17个"同位12字节相同"的异常块
3. 差分异常块索引（5,9,13,17,21...二阶差分恒为4），确认为规律埋放而非随机，按连边关系分成4组
4. 0号块是模板块；用已知flag前缀"ISCC{"前5字节异或密文得前5字节key，再结合题目名/题面"Six Six Six"语义（SipHash, AES-128）补全16字节key
5. 用16字节key异或全文还原明文

**适用场景**: 下次遇到高熵无头二进制时，先做16字节块同位相似度热图，规律性分组暴露异或key结构

---

## [来自实战] Conway's trap（ISCC 2026）

**技术模式**: PE逆向：运行期内存读取全局串绕过静态分析 + INT3陷阱+VEH改道隐藏真实校验逻辑 + 小端序常量展开

**关键操作**:
1. 程序卡在首次输入时直接用ReadProcessMemory读运行期全局std::string，拿到seed_target MD5和flag相关大串
2. seed变换函数(0x401990)：每2字节混合+rol1+整体左移1字节，重复5次→可逆；逆过程：右移1字节+逐字节反推，得原始seed
3. 第二关真实逻辑不在表面函数(0x401cb0)，而在INT3触发VEH后跳转到0x401d00
4. 0x401d00的23字节校验常量以dword/word入栈，必须按小端序展开，不能直接抄立即数顺序
5. 逐字节逆：flag_inner[i] = ror8(target[i] ^ 0xaa, 3) - (0x17*i) ^ seed[i & 0xf]

**适用场景**: 下次遇到Windows PE + INT3陷阱 + 函数首字节0xcc时，先找VEH/SEH改道目标地址，再做常量小端序展开

---

## [来自实战] l11nk（ISCC 2026）

**技术模式**: MIPS ELF relocatable object逆向：从外部未定义符号（SHN_UNDEF）和R_MIPS_32重定位表提取26个字符槽位结构，区分"结构证明"与"字符值还原"的边界

**关键操作**:
1. 先拉ELF摘要、.comment/.ai.guard（故意误导内容：假CRC32/TEA提示、假flag）、.symtab、.lm.auth.rel重定位表
2. 从.symtab找26个连续编号SHN_UNDEF全局符号__lm_cacheline_00~25（数量=flag总长）
3. 从.lm.auth.rel的507065条重定位中统计R_MIPS_32：780条，打到27个唯一偏移，26个非零偏移步长固定为0x24
4. 关键反证：把26个符号全置0和置入参考flag两次重建二进制diff=0，说明.o只暴露槽位结构而非字符值（后续半字重定位会覆盖）
5. 正确复现边界：只靠.o能证明"有26个外部槽位+顺序"，字符值需结合参考答案做兼容性验证

**适用场景**: 下次遇到stripped MIPS/其他架构.o文件时，优先分析SHN_UNDEF符号数量和R_MIPS_32重定位表结构，判断是"完整校验器"还是"链接模板"

---

## [来自实战] QuorumGlyph（ISCC 2026）

**技术模式**: stripped ELF逆向：.init_array构造器预计算目标块 + 37轮可逆对称变换逆推 + 三条互补证词定位 + 24bit穷举隐藏5字符

**关键操作**:
1. .init_array中0x401080构造器：splitmix64风格扰动+.rodata末64字节常量→生成64字节目标块，必须先还原此步才能逆主链
2. 37轮主变换（每轮4步：xor+rol，左传播，右传播，5次交换），全部可逆；工作块=42字节flag（第10~14位清零）+8字节h1+14字节h2
3. 逆主链后前42字节出ISCC{QRM_\x00\x00\x00\x00\x00_3_w1tness_no_single_path!!}，中间5位被清零，主链不能单独还原
4. 第三条证词（隐藏glyph校验）专门验第10~14位，字符集为32字符字母表ABCDEFGHJKLMNPQRSTUVWXYZ23456789，24bit（2^24=16M）穷举用numba加速
5. witness证词管"清零版flag"，可做侧证验正确性但不能当主要来源

**适用场景**: 下次遇到"三条证词/多路校验+中间某段被故意清零"结构时，先逆主变换拿框架，再对隐藏段做有限字符集穷举

---

## [来自实战] 手忙脚乱（ISCC 2026）

**技术模式**: Windows PE两层串行门（UAF+自定义流加密），.rdata明文布局6个加密材料块，无调试器纯静态复刻

**关键操作**:
1. 先解决DLL依赖（MinGW运行库libstdc++/libgcc/libwinpthread），观察交互：第一层错→静默重来，第一层对+第二层错→打印FAIL
2. .rdata中PASS\n\0FAIL\n\0后紧跟6块材料（MASK2/MASK1/TARGET_T/TARGET/K3/K6），按16字节对齐切出，目标是两条24字节明文
3. decrypt_blob核心：r9=seed^0xA3B1C2D3，每字节x=(r9+r8)&0xff后更新r9和r8，做混合流加密
4. 有符号名可直接查看decrypt_blob/encryptPart2/decrypt_K3/decrypt_K6等函数，按调用顺序复刻两条解密链
5. 程序本身不吐flag，只给PASS/FAIL；答案是两条能让程序输出PASS的24字节明文

**适用场景**: 下次遇到"两段输入+.rdata中有规律排列的加密材料块+自定义流加密"时，先切出材料块，再对decrypt函数做最小化静态复刻

---

## [来自实战] baby_tree — AST自定义块密码逆向（长城杯2022）

**技术模式**: 程序以自定义AST格式存储加密逻辑（非标准可执行代码），直接分析AST节点类型还原算法，再写C/Python解密脚本反向执行。

**关键操作**:
1. `assign_expr`=赋值语句，`binary_expr`的`decl`后跟运算符，`argument_list`中两个`argument`参与运算 → 手工/脚本还原算法逻辑
2. 识别密钥调度：初始key="345y"经39次左循环移位后用于解密；解密时每轮key反向右移一位
3. 每轮解密4字节：先用k[2]/k[3]异或还原，再用k[0]/k[1]配合上一步结果反算剩余两字节
4. 写C解密脚本（或Python等价），逆序遍历密文数组（从i=38到0）完成整体解密

**适用场景**: 遇到"程序主体是AST/IR格式而非常规汇编"时，先枚举所有节点类型（assign/binary/call），再按数据流顺序还原等效代码，最后写逆运算脚本

---

## [来自实战] asm_re — 算术加密公式逆推（长城杯决赛2024）

**技术模式**: 二进制对输入进行`(x*80+20)^0x4d+30`形式的算术加密，直接找数据存储位置提取密文hex，写逆公式脚本`((y-30)^0x4d-20)/80`解密。

**关键操作**:
1. 逆向识别加密公式：变量经过"乘80→加20→异或0x4d→加30"四步变换
2. 找密文存储段（.data/.rodata），按Little-Endian每4字节一组提取int32密文
3. 逆运算顺序：减30 → 异或0x4d → 减20 → 除80
4. Python脚本按4字节分组解析，每组还原为chr输出

**适用场景**: 静态分析找到简单算术加密（无循环依赖）时，直接提数据写逆公式脚本，无需动调；注意Little-Endian拼接顺序`int(x[1]+x[0],16)`

---

## [来自实战] whereThel1b/gdb_debug — 黑盒单字节oracle爆破（长城杯决赛2024）

**技术模式**: .so/.pyd文件只有校验函数无源码，输出密文与目标密文逐字节比对；单字节独立影响密文1-2字节，用字符集遍历+进程爆破逐位还原。

**关键操作**:
1. 多次测试确认"单个明文字节只影响固定位置的1-2个密文字节"（黑盒oracle性质）
2. 枚举字符集（alphanumeric+符号），对每个候选字符发起新进程调用校验函数
3. 比对输出密文前N字节是否匹配目标；匹配则锁定该字符，now计数器+1，继续下一位
4. whereThel1b：调用`trytry(flag.encode())`获取密文；gdb_debug：需patch二进制将strcmp改为puts输出密文
5. 部分位置可能多个字符满足，手动调大now阈值逐一试过

**适用场景**: 遇到黑盒校验函数+密文已知+单字节oracle特征时，直接爆破字符集；注意控制并发进程数，分多轮跑避免资源耗尽；patch技巧：strcmp plt偏移→puts plt偏移

---

## [来自实战] S1mpleVM — 链表栈VM逆向 + init_array反调试（强网杯S8决赛2024）

**技术模式**: VM用链表模拟栈（每节点0x10字节，前8字节数据后8字节next指针），opcodes-0x10偏移，字节码存储于quest文件；init_array中IsDebuggerPresent检测触发时修改quest文件，需绕过反调试才能正确分析。

**关键操作**:
1. IDA重定义结构体`struct LinkEntry { signed val; LinkEntry *next; }`，将所有malloc返回值改为LinkEntry*类型，伪代码立刻清晰
2. 13个opcode（-0x10偏移）：0=mod, 1=push_imm, 2=pop_to_reg, 3=mul, 4=add, 5=print, 6=push_input, 7=(x>>y)&1, 8=xor, 9=input_ptr++, A=return, B=sub, C=div
3. 自实现VM（C++/Python用std::stack）并加debug输出，重定向stderr到文件快速提取：XOR目标值（乘法前的值）和每字节每位的权重数组
4. 每个字节8个权重，枚举printable字符计算`sum(bit[j]*weight[j*8+i])`，匹配target即为答案
5. 反调试绕过：用xdbg插件，或直接重命名文件（反调试以文件名查找），确认quest文件未被修改

**适用场景**: 下次遇到Windows VM二进制+字节码文件分开存放时，先检查init_array反调试是否会修改字节码文件；VM用malloc模拟栈时，IDA定义链表结构体是首要步骤；单字节权重累加校验用脚本爆破

---

---

## [来自实战] tradere — ptrace父子进程树形VM + AES ECB逆向（强网杯2025预赛）

**技术模式**: 父进程通过ptrace追踪子进程int 3断点；每次触发读取结构体节点，节点含lchild/rchild/func/RIP；func返回值决定控制流走向，整体构成二叉树形VM；加密为AES ECB/NoPadding，密钥由固定seed随机数生成。

**关键操作**:
1. 结构体定义：`struct data { data* lchild; data* rchild; long long(*func)(user_regs_struct*); long long reg2; }`；func返回0→goto lchild，1→goto rchild，2→ret(pop栈)，3→call rchild@API，4→push lchild+goto rchild
2. 断fork，dump结构体数组为 .h 文件；写C++脚本扫描所有节点去重func，找出PLT地址集合
3. 写dot图生成脚本（printdot+printedge）用BFS遍历，输出可视化控制流图（但节点多时需脚本辅助）
4. 写BFS模拟脚本vmrun2：case 2→pop stack输出jump，case 3→print `call API@plt + jmp lidx`，case 4→push lidx跳ridx，条件跳→je/jne/jl/jle/jg/jns ridx+jmp lidx
5. IDA Python脚本按基本块RIP逐指令反汇编（print_until_int3），结合func类型在末尾插入跳转指令，重构完整汇编指令流
6. 加密流程：`srand(0x10000)` → 16次rand()生成buf1[] → `srand(rand())` → 32次rand()生成XOR数组 → `input → AES_ECB_NoPadding → XOR rand_array → XOR key2_hardcoded → cmp target`
7. 解密：提取target字节序列，与rand_array和key2逐字节XOR还原AES密文，再用AES ECB解密得flag

**适用场景**: 下次遇到ptrace父子进程 + 结构体中含func指针 + int 3频繁触发时，优先考虑树形VM；dump结构体后BFS重建控制流是核心；AES SBOX初始化异或固定key可直接确认AES变体；/proc/pid/mem动态dump内存验证加密中间状态

---

See also: [patterns-ctf-2.md](./patterns-ctf-2.md) for Part 2 (multi-layer self-decrypting binary, embedded ZIP+XOR license, stack string deobfuscation, prefix hash brute-force, CVP/LLL lattice, decision tree obfuscation, GF(2^8) Gaussian elimination), [patterns-ctf-3.md](./patterns-ctf-3.md) for Part 3 (Z3 boolean circuit, sliding window popcount, keyboard LED Morse code, C++ destructor-hidden validation, VM sequential key-chain brute-force, BWT inversion, OpenType font ligature exploitation, GLSL shader VM with self-modifying code).

---

## [来自实战] re01 — ARM SO花指令 + 修改AES (网鼎杯2024白虎组)

**技术模式**: Android SO逆向遇到无法F5的ARM64函数，根因是花指令(间接跳转BR X8 + 无效MOV对)；AES被修改为交换MixColumns/ShiftRows顺序 + 自定义Sbox，需重建解密逻辑。

**关键操作**:
1. IDA无法F5 → 在函数附近搜索`BR X8`指令：`BR X8`实际跳转到下一条指令 = 花指令，全部NOP掉
2. 另一类花指令：`MOV X0, X0`等无效指令对，同样NOP
3. `init_array`中hook了`JNI_OnLoad`，并hook了`RegisterNative`使真实native函数为`sub_1A9A8`
4. 找到函数后识别修改AES特征：Sbox表不同于标准AES，`KeyExpansion`流程正常但Cipher函数中**MixColumns在ShiftRows前**（标准顺序相反）
5. 解密时对应修改InvCipher：顺序改为`InvShiftRows → InvSubBytes → AddRoundKey → InvShiftRows → InvMixColumns → InvSubBytes`
6. 提取自定义rsbox（逆Sbox）：`for i in range(256): rsbox[sbox[i]] = i`
7. 密钥：已知key前8字节正常，后8字节**反转**；模式：AES-CBC，IV=key

**适用场景**: ARM64 SO花指令首查`BR X8`(间接跳转到下条)；JNI hook链：init_array→hook JNI_OnLoad→hook RegisterNative→替换真实函数；魔改AES先比对标准Sbox(0x63开头)，再确认Cipher轮次操作顺序

---

## [来自实战] reverse02 — Rust Web服务器路径遍历 (网鼎杯2024白虎组)

**技术模式**: Rust实现的web服务将`../`替换为`/`来防路径遍历，用`....//`绕过（替换后剩余`../`）。

**关键操作**:
1. 服务开启8080端口，只处理GET请求
2. 过滤规则：`../` → `/`（单次替换）
3. 绕过：`....//` → 替换`../`后得到`../` → 可遍历到父目录
4. payload: `GET /....//....//....//etc/passwd HTTP/1.1`

**适用场景**: 路径遍历过滤器用字符串替换（非递归）时，双写目标pattern即可绕过：`....//` → `../`，`..%2f` URL编码绕过也常用

---

## [来自实战] 眼见为虚_1 — 虚表调用+TEA变换+目标数组XOR解密 (DASCTF)

**技术模式**: 找不到直接验证逻辑时从"right flag"/"wrong flag"字符串定位，发现通过虚表调用的处理函数，提取TEA风格变换生成key，用key XOR解密目标数组。

**关键操作**:
1. 搜索"right flag"/"wrong flag"字符串 → 定位验证函数`sub_401522`
2. 找到最终比较函数`sub_402B68`：将处理后的输入与40字节目标数组逐字节比较
3. 目标数组小端序存储，展开还原真实字节顺序
4. 处理函数`sub_4014F0`通过虚表调用真实处理逻辑 → 分析虚表找真实函数
5. 发现TEA风格变换：用hardcoded初始值经过32轮计算生成8字节key
   - `a1[2..7]` = 六个hardcoded常量，经过32轮TEA生成 `5C FC A0 27 20 A7 84 7A`
6. 解密：`flag[i] = target[i] ^ ((key[i%8] + 0x1B) & 0xFF)`
   ```python
   target = bytes.fromhex("3356e8016f84e4a3...e8")
   k1, k2 = 0x27A0FC5C, 0x7A84A720
   key = struct.pack("<II", k1, k2)
   flag = bytes([target[i] ^ ((key[i%8] + 0x1B) & 0xFF) for i in range(40)])
   ```

**适用场景**: 虚表调用先找vtable指针 → 逐个分析虚函数；TEA类变换特征是循环32/16轮、delta=0x9E3779B9；目标数组小端序先转换字节顺序再分析

---

## [来自实战] eazy_code-new — PowerShell变量名混淆 + 隐藏Python XXTEA逆向 (DASCTF)

**技术模式**: 文件看似乱码但是PowerShell脚本，变量名代替数字0-9，拼出`[char]`流，动态执行第二层Python代码；第二层用自定义XXTEA加密，逆向解密得flag。

**关键操作 — 第一层（PowerShell混淆解混淆）**:
1. 识别特征：大量`${特殊字符}`形式的变量名 → PowerShell混淆
2. 建立映射表（变量名→数字0-9）：
   ```python
   mp = {'${\]}': '0', '${!;}': '1', '${ @ }': '2', '${= }': '3',
         '${ \]}': '4', '${!}': '5', '${#.}': '6', '${(}': '7',
         '${) }': '8', '${```*%}': '9', '{%}': '[char]'}
   ```
3. 替换后还原出`[char]99+[char]108+...`形式 → 提取数字 → chr()得到第二层代码

**关键操作 — 第二层（XXTEA/Block TEA逆向）**:
1. 第二层是Python class `chiper`，使用Block TEA（XXTEA变种）加密
2. key = `[0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]`（MD5初始值！）
3. delta = `0x87654321`（非标准delta，注意与标准0x9E3779B9区分）
4. 目标数组：`ans = [1374278842, 2136006540, 4191056815, 3248881376]`（4个uint32 = 16字节flag）
5. XXTEA解密：
   ```python
   def decrypt(v, key, delta):
       n = len(v)
       rounds = 6 + 52//n
       total = c_uint32((rounds * delta) & 0xffffffff)
       # 标准XXTEA逆向流程...
   plain = decrypt(ans, key, 0x87654321)
   flag = struct.pack('<4I', *plain).decode()
   ```

**适用场景**: PowerShell混淆`${特殊字符}`变量名 → 先建字符到数字映射表；隐藏层通常是Python/C#/JS；Block TEA/XXTEA的delta可以不是标准值，必须从代码中提取；key用MD5初始值是常见混淆手法

---

## [来自实战] tt3441810 — x64 push+write syscall模式直接静态提取flag (HW训练)

**技术模式**: 机器码转储文件，每轮固定模式：`68 xx xx 00 00`(push imm32，高2字节为0) + 设置rdi=1/rsi=rsp/rdx=2/rax=1 + `0F 05`(syscall write) → 每次打印2字节；无条件跳转，直接从push立即数提取字符对即可。

**关键操作**:
1. 识别文件：小体积，含十六进制dump，地址前缀`00400080`样式
2. 识别模式：`68 xx xx 00 00` → `push imm32`，真正数据是前2字节；后跟`48 BF 01...`设rdi=1，`0F 05` syscall
3. 不需要组装执行，直接提取所有`68 XX XX 00 00`中的`XX XX`：
   ```python
   import re
   pairs = re.findall(r'68 ([0-9A-F]{2}) ([0-9A-F]{2}) 00 00', text)
   flag = ''.join(bytes.fromhex(a+b).decode('latin1') for a,b in pairs)
   ```
4. 按序拼接字符对得到`flag{poppopret}`

**适用场景**: 静态程序输出(无复杂计算/条件跳转) → 不需运行直接读数据；x64 write(1,rsp,2)模式识别；16进制dump中找`68`开头+`00 00`结尾的4字节push；能静态提取就不上调试器

---

## [来自实战] hacklu-triangle — JS前端Unicorn ARM模拟器逆向+Z3约束求解 (Hack.lu 2017)

**技术模式**: 前端JS校验，`enc_pw()`和`test_pw()`从图片字节中抽取ARM机器码，交给Unicorn.js执行；不手逆unicorn胶水代码，而是还原等价字节约束关系，再交Z3求解32字节密码。

**关键操作**:
1. 页面源码找`login()`调用链：`enc_pw` → `get_pw` → `test_pw`
2. `get_pw()`从图片字节按偏移表抽取32字节密码；`enc_pw`/`test_pw`把另一批图片字节当ARM指令执行
3. 不逆Unicorn本体，而是化简`enc_pw`/`test_pw`的等价逻辑成字节约束：
   - 阶段1：每字节根据flag状态加偏移，flag由上一字节奇偶决定
   - 阶段2：每字节再加常量（奇数位+2，偶数位+5）
4. 目标输出`XYzaSAAX_PBssisodjsal_sSUVWZYYYb`固定
5. Z3建32个BitVec(8)约束，按逆序求解：
   ```python
   s = z3.Solver()
   chars = [z3.BitVec(f'c{i}', 8) for i in range(32)]
   # add phase1/phase2 constraints for each byte
   ```
6. 得密码`MPmVH94PTH7hhafgYahYaVfKJNLRNQLZ`，flag为`flag{...}`

**适用场景**: 前端含`Unicorn`/wasm时不手逆，找"输入到输出"等价关系；Z3适合逐字节固定方程；找关键JS文件：页面源码→login()→关联js；图片可以是数据载体而非装饰
