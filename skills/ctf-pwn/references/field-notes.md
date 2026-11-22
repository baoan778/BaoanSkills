# Pwn Field Notes

Detailed pwn notes that support [`../SKILL.md`](../SKILL.md). Read this file after confirming the challenge really needs exploitation.

## Table of Contents

- [Heap Exploitation](#heap-exploitation)
- [Additional Exploit Notes](#additional-exploit-notes)
  - [talloc Pool Header Forgery](#talloc-pool-header-forgery)
  - [JIT Compilation Exploits](#jit-compilation-exploits)
  - [Type Confusion in Interpreters](#type-confusion-in-interpreters)
  - [Off-by-One Index / Size Corruption](#off-by-one-index--size-corruption)
  - [Double win() Call](#double-win-call)
  - [Arbitrary Read/Write to Shell via GOT Overwrite](#arbitrary-readwrite-to-shell-via-got-overwrite)
  - [Stack Leak via __environ and memcpy Overflow](#stack-leak-via-__environ-and-memcpy-overflow)
  - [JIT Sandbox Escape via uint16 Jump Truncation](#jit-sandbox-escape-via-uint16-jump-truncation)
  - [DNS Compression Pointer Stack Overflow](#dns-compression-pointer-stack-overflow)
  - [ELF Code Signing Bypass via Program Headers](#elf-code-signing-bypass-via-program-headers)
  - [Game Level Format Signed/Unsigned Coordinate Mismatch](#game-level-format-signedunsigned-coordinate-mismatch)
  - [File Descriptor Inheritance via Missing O_CLOEXEC](#file-descriptor-inheritance-via-missing-o_cloexec)
  - [Sign Extension Integer Underflow in Metadata Parsing](#sign-extension-integer-underflow-in-metadata-parsing)
  - [ROP Chain Construction with Read-Only Primitive](#rop-chain-construction-with-read-only-primitive)
  - [Esoteric Language GOT Overwrite](#esoteric-language-got-overwrite)
  - [Protocol Stack Bleeding](#protocol-stack-bleeding)
  - [Timing Attack Flag Recovery](#timing-attack-flag-recovery)
  - [DNS Record Buffer Overflow](#dns-record-buffer-overflow)
  - [ASAN Shadow Memory Exploitation](#asan-shadow-memory-exploitation)
  - [Format String .fini_array Loop for Multi-Stage Exploitation](#format-string-fini_array-loop-for-multi-stage-exploitation)
  - [Format String with RWX .fini_array Hijack](#format-string-with-rwx-fini_array-hijack)
  - [Custom Canary Preservation](#custom-canary-preservation)
  - [MD5 Preimage Gadget Construction](#md5-preimage-gadget-construction)
  - [Python Sandbox Escape](#python-sandbox-escape)
  - [VM GC-Triggered UAF (Slab Reuse)](#vm-gc-triggered-uaf-slab-reuse)
  - [GC Null-Reference Cascading Corruption](#gc-null-reference-cascading-corruption)
  - [OOB Read via Stride/Rate Leak](#oob-read-via-striderate-leak)
  - [SROP with UTF-8 Constraints](#srop-with-utf-8-constraints)
  - [VM Exploitation (Custom Bytecode)](#vm-exploitation-custom-bytecode)
  - [FUSE/CUSE Character Device Exploitation](#fusecuse-character-device-exploitation)
  - [Busybox/Restricted Shell Escalation](#busyboxrestricted-shell-escalation)
  - [process_vm_readv Sandbox Bypass](#process_vm_readv-sandbox-bypass)
  - [Named Pipe (mkfifo) File Size Bypass](#named-pipe-mkfifo-file-size-bypass)
  - [Shell Tricks](#shell-tricks)
  - [Double Stack Pivot to BSS via leave;ret](#double-stack-pivot-to-bss-via-leaveret)
  - [RETF Architecture Switch for Seccomp Bypass](#retf-architecture-switch-for-seccomp-bypass)
  - [Leakless Libc via Multi-fgets stdout FILE Overwrite](#leakless-libc-via-multi-fgets-stdout-file-overwrite)
  - [Signed/Unsigned Char Underflow to Heap Overflow](#signedunsigned-char-underflow-to-heap-overflow)
  - [TLS Destructor Hijack via `__call_tls_dtors`](#tls-destructor-hijack-via-__call_tls_dtors)
  - [Signed Int Overflow to Negative OOB Heap Write](#signed-int-overflow-to-negative-oob-heap-write)
  - [Custom Shadow Stack Bypass via Pointer Overflow](#custom-shadow-stack-bypass-via-pointer-overflow)
  - [Windows SEH Overwrite + VirtualAlloc ROP](#windows-seh-overwrite--virtualalloc-rop)
  - [SeDebugPrivilege to SYSTEM](#sedebugprivilege-to-system)
  - [mmap/munmap Size Mismatch UAF](#mmapmunmap-size-mismatch-uaf)
  - [strcspn Indirect Null Byte Injection](#strcspn-indirect-null-byte-injection)
  - [Windows CFG Bypass Using system() as Valid Call Target](#windows-cfg-bypass-using-system-as-valid-call-target)
  - [4-Byte Shellcode with Timing Side-Channel](#4-byte-shellcode-with-timing-side-channel)
  - [CRC Oracle as Arbitrary Read Primitive](#crc-oracle-as-arbitrary-read-primitive)
  - [UTF-8 Case Conversion Buffer Overflow](#utf-8-case-conversion-buffer-overflow)
- [Useful Commands](#useful-commands)

## Heap Exploitation

- tcache poisoning (glibc 2.26+), fastbin dup / double free
- House of Force (old glibc), unsorted bin attack
- **House of Apple 2** (glibc 2.34+): FSOP (File Stream Oriented Programming) via `_IO_wfile_jumps` when `__free_hook`/`__malloc_hook` removed. Fake FILE with `_flags = " sh"`, vtable chain → `system(fp)`. For SUID binaries: use `setcontext()` variant to stack pivot → `setuid(0)` → `system()` (dash drops privs when uid != euid). See [heap-techniques.md](./heap-techniques.md#setcontext-variant-for-suid-binaries-midnight-flag-2026).
- **Classic unlink**: Corrupt adjacent chunk metadata, trigger backward consolidation for write-what-where primitive. Pre-2.26 glibc only. See [heap-techniques.md](./heap-techniques.md#classic-heap-unlink-attack-crypto-cat).
- **House of Force:** Corrupt top chunk size to `0xffffffffffffffff`, next `malloc(target - top - 2*SIZE_SZ)` returns arbitrary address. Pre-2.29 glibc only. See [heap-techniques.md](./heap-techniques.md#house-of-force-csaw-ctf-2016).
- **House of Einherjar**: Off-by-one null clears PREV_INUSE, backward consolidation with self-pointing unlink.
- **Safe-linking** (glibc 2.32+): tcache fd mangled as `ptr ^ (chunk_addr >> 12)`.
- Check glibc version: `strings libc.so.6 | grep GLIBC`
- Freed chunks contain libc pointers (fd/bk) -> leak via error messages or missing null-termination
- Heap feng shui: control alloc order/sizes, create holes, place targets adjacent to overflow source
- **Unsafe unlink + top chunk consolidation**: After unlink writes self-pointer to BSS, craft fake BSS chunk spanning to top chunk. `free()` consolidates, relocating heap base to BSS. Subsequent mallocs return BSS memory. See [heap-techniques.md](./heap-techniques.md#unsafe-unlink-to-bss--top-chunk-consolidation-seccon-2016).

**House of Orange:** Corrupt top chunk size → large malloc forces sysmalloc → old top freed without calling `free()`. Chain with FSOP. See [heap-techniques.md](./heap-techniques.md#house-of-orange).

**House of Spirit:** Forge fake chunk in target area, `free()` it, reallocate to get write access. Requires valid size + next chunk size. See [heap-techniques.md](./heap-techniques.md#house-of-spirit).

**House of Lore:** Corrupt smallbin `bk` → link fake chunk → second malloc returns attacker-controlled address. See [heap-techniques.md](./heap-techniques.md#house-of-lore).

**ret2dlresolve:** Forge Elf64_Sym/Rela to resolve arbitrary libc function without leak. `Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])`. Requires Partial RELRO. See [advanced.md](./advanced.md#ret2dlresolve).

**tcache stashing unlink (glibc 2.29+):** Corrupt smallbin chunk's `bk` during tcache stashing → arbitrary address linked into tcache → write primitive. See [heap-techniques.md](./heap-techniques.md#tcache-stashing-unlink-attack).

**UAF vtable pointer encoding shell argument:** After UAF, heap spray places `system()` at offset +3. Object address containing `0x6873` ("sh") in low bytes doubles as the command string argument when `system(this)` is called through the hijacked vtable. See [heap-techniques-2.md](./heap-techniques-2.md#uaf-vtable-pointer-encoding-shell-argument-bctf-2017).

**Fastbin stdout vtable two-stage hijack (PIE + Full RELRO):** Use 0x7f byte in libc's stdout region as fake fastbin chunk size. Two-stage: first vtable redirect to `gets()` (rdi=stdout), then `gets()` overwrites vtable again to `system()` with command string. See [heap-techniques.md](./heap-fsop.md#fastbin-stdout-vtable-two-stage-hijack-for-pie--full-relro-asis-ctf-2017).

See [heap-techniques.md](./heap-techniques.md) for House of Apple 2 FSOP chain (+ setcontext SUID variant), House of Orange/Spirit/Lore/Force, tcache stashing unlink, custom allocator exploitation (nginx pools, talloc), classic unlink, musl libc heap. See [advanced.md](./advanced.md) for ret2dlresolve, heap overlap via base conversion, tree data structure stack underallocation.

**GF(2) Gaussian elimination for tcache poisoning:** When a deterministic XOR cipher corrupts heap metadata as a side effect, model the corruption as linear algebra over GF(2). Find a subset of cipher seeds whose combined XOR transforms tcache `fd` from current value to target address. See [advanced-exploits-4.md](./advanced-exploits-4.md#gf2-gaussian-elimination-for-multi-pass-tcache-poisoning-midnight-flag-2026).

## Additional Exploit Notes

### talloc Pool Header Forgery
**Pattern:** talloc (hierarchical allocator in Samba/CUPS) pool header forgery. Forge fake pool header with controlled `end`/`object_count` fields to redirect next `talloc()` to arbitrary address. Leak GOT for libc, write `__free_hook` with `system()`. See [heap-techniques.md](./heap-techniques.md#talloc-pool-header-forgery-for-arbitrary-readwrite-boston-key-party-2016).

### JIT Compilation Exploits
**Pattern:** Off-by-one in instruction encoding -> misaligned machine code. Embed shellcode as operand bytes of subtraction operations, chain with 2-byte `jmp` instructions. See [advanced.md](./advanced.md).

**BF JIT unbalanced bracket:** Unbalanced `]` pops tape address (RWX) from stack → write shellcode to tape with `+`/`-`, trigger `]` to jump to it. See [advanced.md](./advanced.md).

### Type Confusion in Interpreters
**Pattern:** Interpreter sets wrong type tag → struct fields reinterpreted. Unused padding bytes in one variant become active pointers/data in another. Flag bytes as type value trigger UNKNOWN_DATA dump. See [advanced.md](./advanced.md).

### Off-by-One Index / Size Corruption
**Pattern:** Array index 0 maps to `entries[-1]`, overlapping struct metadata (size field). Corrupted size → OOB read leaks canary/libc, then OOB write places ROP chain. See [advanced.md](./advanced.md).

### Double win() Call
**Pattern:** `win()` checks `if (attempts++ > 0)` — needs two calls. Stack two return addresses: `p64(win) + p64(win)`. See [advanced.md](./advanced.md).

### Arbitrary Read/Write to Shell via GOT Overwrite
**Pattern:** Binary provides explicit read/write primitives. Leak libc via GOT read, overwrite `strtoll@GOT` with `system`, next call becomes `system(user_input)`. Choose GOT targets where the function takes a user-controlled string as first arg. See [advanced-exploits-3.md](./advanced-exploits-3.md#arbitrary-readwrite-to-shell-via-got-overwrite-bsidessf-2026).

### Stack Leak via __environ and memcpy Overflow
**Pattern:** Binary with read-only primitive and `memcpy(stack_buf, user_addr, user_len)`. Leak libc via GOT, leak stack via `__environ`, plant ROP addresses in input buffer, overflow memcpy to copy them over return address, send EOF to trigger return. See [advanced-exploits-3.md](./advanced-exploits-3.md#stack-leak-via-__environ-and-memcpy-overflow-bsidessf-2026).

### JIT Sandbox Escape via uint16 Jump Truncation
**Pattern:** JIT compiler truncates conditional jump offset to uint16, causing misalignment when code exceeds 64KB. Embed 2-byte shellcode fragments in `add` immediates, thread with `jmp $+3` to chain execution. See [advanced-exploits-3.md](./advanced-exploits-3.md#jit-sandbox-escape-via-conditional-jump-uint16-truncation-bsidessf-2026).

### DNS Compression Pointer Stack Overflow
**Pattern:** Custom DNS server doesn't track decompressed name length. Compression pointer chains revisit data, overflowing stack buffer. Split ROP chain across multiple DNS question entries. See [advanced-exploits-3.md](./advanced-exploits-3.md#dns-compression-pointer-stack-overflow-with-multi-question-rop-bsidessf-2026).

### ELF Code Signing Bypass via Program Headers
**Pattern:** Signing scheme hashes section headers/content but not program headers. Append shellcode, modify LOAD segment's `p_offset` to point to appended data — signature still valid, loader executes attacker code. See [advanced-exploits-3.md](./advanced-exploits-3.md#elf-code-signing-bypass-via-program-header-manipulation-bsidessf-2026).

### Game Level Format Signed/Unsigned Coordinate Mismatch
**Pattern:** Level editor parses signed integer coordinates but bounds-checks via unsigned comparison — negative coordinates pass the check and write block IDs (arbitrary bytes) before the level array, enabling stack return address overwrite. Leak stack address via hidden developer mode, encode shellcode as block IDs. See [advanced-exploits-3.md](./advanced-exploits-3.md#game-level-format-signedunsigned-coordinate-mismatch-bsidessf-2026).

### File Descriptor Inheritance via Missing O_CLOEXEC
**Pattern:** Service reads secret into `memfd_create()` FD without `MFD_CLOEXEC`, then calls `system()` for user commands — child inherits the FD. Bypass `strstr()` keyword filters with shell quote splitting (`p'r'oc` instead of `proc`) to read `/proc/self/fd/N`. See [advanced-exploits-3.md](./advanced-exploits-3.md#file-descriptor-inheritance-via-missing-o_cloexec-bsidessf-2026).

### Sign Extension Integer Underflow in Metadata Parsing
**Pattern:** Metadata parser's `to_int32` converts unsigned values >= 0x80000000 to negative signed integers. Used as array index/offset, this causes OOB memory access. Iterate byte-by-byte to leak flag from memory. See [advanced-exploits-3.md](./advanced-exploits-3.md#sign-extension-integer-underflow-in-metadata-parsing-bsidessf-2026).

### ROP Chain Construction with Read-Only Primitive
**Pattern:** Binary with only `read()` primitive — no write, no win function. Leak libc via GOT, then "import" arbitrary byte values onto the stack by reading from libc offsets whose content matches desired ROP gadget addresses. Read primitive doubles as write primitive. See [advanced-exploits-3.md](./advanced-exploits-3.md#rop-chain-construction-with-read-only-primitive-bsidessf-2026).

### Esoteric Language GOT Overwrite
**Pattern:** Brainfuck/Pikalang interpreter with unbounded tape = arbitrary read/write relative to buffer base. Move pointer to GOT, overwrite byte-by-byte with `system()`. See [advanced.md](./advanced.md).

### Protocol Stack Bleeding
Custom network protocols echoing data based on length field leak stack memory when length exceeds actual data (Heartbleed-style). See [overflow-basics.md](./overflow-basics.md#protocol-length-field-stack-bleeding-ekoparty-ctf-2016).

### Timing Attack Flag Recovery
Validation time varies per correct character; measure elapsed time per candidate byte to recover flag character-by-character. See [advanced-exploits.md](./advanced-exploits.md#timing-attack-for-character-by-character-flag-recovery-rc3-ctf-2016).

### DNS Record Buffer Overflow
**Pattern:** Many AAAA records overflow stack buffer in DNS response parser. Set up DNS server with excessive records, overwrite return address. See [advanced.md](./advanced.md).

### ASAN Shadow Memory Exploitation
**Pattern:** Binary with AddressSanitizer has format string + OOB write. ASAN may use "fake stack" (50% chance). Leak PIE, detect real vs fake stack, calculate OOB write offset to overwrite return address. See [advanced.md](./advanced.md).

### Format String .fini_array Loop for Multi-Stage Exploitation
**Pattern:** No GOT function called after `printf()`. Overwrite `.fini_array[0]` with `main()` for re-execution loop. Stage 1: leak libc/stack. Stage 2: `printf@GOT` to `system()`, `__stack_chk_fail@GOT` to `main()`. Stage 3: corrupt canary to trigger `__stack_chk_fail` re-entry, now `printf(input)` is `system(input)`. See [format-string.md](./format-string.md#format-string-fini_array-loop-for-multi-stage-exploitation-codegate-2016).

### Format String with RWX .fini_array Hijack
**Pattern (Encodinator):** Base85-encoded input in RWX memory passed to `printf()`. Write shellcode to RWX region, overwrite `.fini_array[0]` via format string `%hn` writes. Use convergence loop for base85 argument numbering. See [advanced.md](./advanced.md).

### Custom Canary Preservation
**Pattern:** Buffer overflow must preserve known canary value. Write exact canary bytes at correct offset: `b'A' * 64 + b'BIRD' + b'X'`. See [advanced.md](./advanced.md).

### MD5 Preimage Gadget Construction
**Pattern (Hashchain):** Brute-force MD5 preimages with `eb 0c` prefix (jmp +12) to skip middle bytes; bytes 14-15 become 2-byte i386 instructions. Build syscall chains from gadgets like `31c0` (xor eax), `cd80` (int 0x80). See [advanced.md](./advanced.md) for C code and v2 technique.

### Python Sandbox Escape
AST bypass via f-strings, audit hook bypass with `b'flag.txt'` (bytes vs str), MRO-based `__builtins__` recovery. See [sandbox-escape.md](./sandbox-escape.md).

### VM GC-Triggered UAF (Slab Reuse)
**Pattern:** Custom VM with NEWBUF/SLICE/GC opcodes. Slicing creates shared slab reference; dropping+GC'ing slice frees slab while parent still holds it. Allocate function object to reuse slab, leak code pointer via UAF read, overwrite with win() address. See [advanced.md](./advanced.md).

### GC Null-Reference Cascading Corruption
**Pattern:** Mark-compact GC follows null references to heap address 0, creating fake object. During compaction, memmove cascades corruption through adjacent object headers → OOB access → libc leak → FSOP. See [advanced.md](./advanced.md).

### OOB Read via Stride/Rate Leak
**Pattern:** String processing function with user-controlled stride skips past null terminator, leaking stack canary and return address one byte at a time. Then overflow with leaked values. See [overflow-basics.md](./overflow-basics.md).

### SROP with UTF-8 Constraints
**Pattern:** When payload must be valid UTF-8 (Rust binaries, JSON parsers), use SROP — only 3 gadgets needed. Multi-byte UTF-8 sequences spanning register field boundaries "fix" high bytes. See [rop-advanced.md](./rop-advanced.md).

### VM Exploitation (Custom Bytecode)
**Pattern:** Custom VM with OOB read/write in syscalls. Leak PIE via XOR-encoded function pointer, overflow to rewrite pointer with `win() ^ KEY`. See [sandbox-escape.md](./sandbox-escape.md).

### FUSE/CUSE Character Device Exploitation
Look for `cuse_lowlevel_main()` / `fuse_main()`, backdoor write handlers with command parsing. Exploit to `chmod /etc/passwd` then modify for root access. See [sandbox-escape.md](./sandbox-escape.md).

### Busybox/Restricted Shell Escalation
Find writable paths via character devices, target `/etc/passwd` or `/etc/sudoers`, modify permissions then content. See [sandbox-escape.md](./sandbox-escape.md).

### process_vm_readv Sandbox Bypass
**Pattern:** Sandbox validates file paths via `process_vm_readv()` + `realpath()`. Map memory with `PROT_READ` only at fixed address via `mmap(MAP_FIXED)` -- sandbox's `process_vm_readv` fails silently, bypassing path validation entirely. See [sandbox-escape.md](./sandbox-escape.md#process_vm_readv-failure-as-sandbox-escape-0ctf-2016).

### Named Pipe (mkfifo) File Size Bypass
**Pattern:** Binary checks `stat()` file size before reading. Named pipes report `st_size = 0` but deliver arbitrary data via `read()`. `mkfifo /tmp/pipe && cat payload > /tmp/pipe &` then pass pipe to binary. Combine with `ln -s /flag arena.c` for string reuse in ROP. See [sandbox-escape.md](./sandbox-escape.md#named-pipe-mkfifo-for-file-size-check-bypass-nuit-du-hack-2016).

### Shell Tricks
`exec<&3;sh>&3` for fd redirection, `$0` instead of `sh`, `ls -la /proc/self/fd` to find correct fd. See [sandbox-escape.md](./sandbox-escape.md).

### Double Stack Pivot to BSS via leave;ret
**Pattern:** Small overflow (only RBP + RIP). Overwrite RBP → BSS address, RIP → `leave; ret` gadget. `leave` sets RSP = RBP (BSS). Second stage at BSS calls `fgets(BSS+offset, large_size, stdin)` to load full ROP chain. See [rop-advanced.md](./rop-advanced.md#double-stack-pivot-to-bss-via-leaveret-midnightflag-2026).

### RETF Architecture Switch for Seccomp Bypass
**Pattern:** Seccomp blocks 64-bit syscalls (`open`, `execve`). Use `retf` gadget to load CS=0x23 (IA-32e compatibility mode). In 32-bit mode, `int 0x80` uses different syscall numbers (open=5, read=3, write=4) not covered by the filter. Requires `mprotect` to make BSS executable for 32-bit shellcode. See [rop-advanced.md](./rop-advanced.md#retf-architecture-switch-for-seccomp-bypass-midnightflag-2026).

### Leakless Libc via Multi-fgets stdout FILE Overwrite
**Pattern:** No libc leak available. Chain multiple `fgets(addr, 7, stdin)` calls via ROP to construct fake stdout FILE struct on BSS. Set `_IO_write_base` to GOT entry, call `fflush(stdout)` → leaks GOT content → libc base. The 7-byte writes avoid null byte corruption since libc pointer MSBs are already `\x00`. See [advanced-exploits-2.md](./advanced-exploits-2.md#leakless-libc-via-multi-fgets-stdout-file-overwrite-midnightflag-2026).

### Signed/Unsigned Char Underflow to Heap Overflow
**Pattern:** Size field stored as `signed char`, cast to `unsigned char` for use. `size = -112` → `(unsigned char)(-112) = 144`, overflowing a 127-byte buffer by 17 bytes. Combine with XOR keystream brute-force for byte-precise writes, forge chunk sizes for unsorted bin promotion (libc leak), FSOP stdout for TLS leak, and TLS destructor (`__call_tls_dtors`) overwrite for RCE. See [advanced-exploits-2.md](./advanced-exploits-2.md#signedunsigned-char-underflow-to-heap-overflow--tls-destructor-hijack-midnightflag-2026).

### TLS Destructor Hijack via `__call_tls_dtors`
**Pattern:** Alternative to House of Apple 2 on glibc 2.34+. Forge `__tls_dtor_list` entries with pointer-guard-mangled function pointers: `encoded = rol(target ^ pointer_guard, 0x11)`. Requires leaking pointer guard from TLS segment (via FSOP stdout redirection). Each node calls `PTR_DEMANGLE(func)(obj)` on exit. See [advanced-exploits-2.md](./advanced-exploits-2.md#tls-destructor-overwrite-for-rce-via-__call_tls_dtors).

### Signed Int Overflow to Negative OOB Heap Write
**Pattern (Canvas of Fear):** Index formula `y * width + x` in signed 32-bit int overflows to negative value, passing bounds check and writing backward into heap metadata. Use to corrupt adjacent chunk sizes/pointers, leak libc via unsorted bin, redirect a data pointer to `environ` for stack leak, then write ROP chain to main's return address. When binary is behind a web API, chain XSS → Fetch API → heap exploit, and inject `\n` in API parameters for command stacking via `sendline()`. See [advanced-exploits-2.md](./advanced-exploits-2.md#signed-int-overflow-to-negative-oob-heap-write--xss-to-binary-pwn-bridge-midnight-2026) for full exploit chain, XSS bridge pattern, and RGB pixel write primitive.

### Custom Shadow Stack Bypass via Pointer Overflow
**Pattern (Revenant):** Userland shadow stack in `.bss` with unbounded pointer. Recurse to advance `shadow_stack_ptr` past the array into user-controlled memory (e.g., `username` buffer), write `win()` there, then overflow the hardware stack return address to match. Both checks pass. See [advanced-exploits-2.md](./advanced-exploits-2.md#custom-shadow-stack-bypass-via-pointer-overflow-midnight-2026) for full exploit and `.bss` layout analysis.

### Windows SEH Overwrite + VirtualAlloc ROP
Format string leak defeats ASLR. SEH (Structured Exception Handler) overwrite with stack pivot to ROP chain. `pushad` builds VirtualAlloc call frame for DEP (Data Execution Prevention) bypass. Detached process launcher for shell stability on thread-based servers. See [advanced-exploits-4.md](./advanced-exploits-4.md#windows-seh-overwrite--pushad-virtualalloc-rop-rainbowtwo-htb).

### SeDebugPrivilege to SYSTEM
`SeDebugPrivilege` + Meterpreter `migrate -N winlogon.exe` -> SYSTEM. See [advanced-exploits-4.md](./advanced-exploits-4.md#sedebugprivilege-to-system-rainbowtwo-htb).

### mmap/munmap Size Mismatch UAF
Over-unmap via mmap(small)/munmap(large) destroys adjacent mappings. Thread stack fills gap, old buffer pointer becomes write-into-stack. Race-free UAF variant. See [advanced-exploits-4.md](./advanced-exploits-4.md#mmapmunmap-size-mismatch-uaf-for-thread-stack-overlap-0ctf-2017).

### strcspn Indirect Null Byte Injection
`strcspn(buf, "\r\n")` + null write truncates strings at injected newlines. Bypasses CGI null-byte filtering for path traversal. See [advanced-exploits-4.md](./advanced-exploits-4.md#strcspn-as-indirect-null-byte-injection-bsidessf-2017).

### Windows CFG Bypass Using system() as Valid Call Target
**Pattern:** Windows CFG validates indirect call targets but `system()` from msvcrt passes validation since it is a legitimate API entry point. Overwrite function pointer with `system()`, use comma instead of space in arguments to bypass input filters. See [advanced-exploits-4.md](./advanced-exploits-4.md#windows-cfg-bypass-using-system-as-valid-call-target-insomnihack-2017).

### 4-Byte Shellcode with Timing Side-Channel
**Pattern:** Binary executes only 4 bytes of user shellcode in a 4096-iteration loop. Callee-saved registers (r12-r15) persist across iterations, enabling incremental state building. The 4096x loop amplifies timing differences for reliable side-channel measurement. See [advanced-exploits-3.md](./advanced-exploits-3.md#4-byte-shellcode-with-timing-side-channel-via-persistent-registers-google-ctf-2017).

### CRC Oracle as Arbitrary Read Primitive
**Pattern:** CRC is bijective on single bytes. Overflow a pointer to control the CRC input address, precompute all 256 single-byte CRCs, and reverse-lookup each byte of arbitrary memory. Chain reads to leak GOT, libc, stack, and canary. See [advanced-exploits-3.md](./advanced-exploits-3.md#crc-oracle-as-arbitrary-read-primitive-asis-ctf-2017).

### UTF-8 Case Conversion Buffer Overflow
**Pattern:** Unicode case conversion can expand character byte length (e.g., 2-byte UTF-8 becomes 4 bytes when uppercased). If buffer is sized for input length, the longer output overflows. Affects GLib `g_utf8_strup()`, ICU, and similar functions. See [advanced-exploits-3.md](./advanced-exploits-3.md#utf-8-case-conversion-buffer-overflow-hitb-ctf-2017).

## Useful Commands

`checksec`, `one_gadget`, `ropper`, `ROPgadget`, `seccomp-tools dump`, `strings libc | grep GLIBC`. See [rop-advanced.md](./rop-advanced.md) for full command list and pwntools template.

## [来自实战] entrance（ISCC 2026）

**技术模式**: UAF前置绕过 + printf格式串泄canary + ret2libc两轮（先泄libc再getshell）

**关键操作**:
1. 前置UAF门：程序malloc("hack")后free，再按用户给的长度重新malloc，利用tcache复用旧chunk使旧指针strcmp比对通过（长度=72，内容="hack"）
2. 第一次hello输入：发25字节非零填充，让printf %s把canary非零7字节带出，左补\x00还原canary
3. 第一轮ROP：pop rdi + puts@GOT + puts@PLT + main，泄漏libc真实地址
4. 第二轮ROP：ret对齐 + pop rdi + /bin/sh + system，libc偏移以远端泄漏值为准而非附件
5. 附件libc偏移不可信，必须用远端泄漏值重算；puts=0x6f6a0, system=0x453a0, /bin/sh=0x18ce57

**适用场景**: 下次遇到"有UAF前置门 + printf(buf)回显 + 两段输入"结构时优先考虑此方向

---

## [来自实战] forest（ISCC 2026）

**技术模式**: UAF网格测试确定有效窗口 + printf格式串做canary边界探针 + ret2dlresolve收尾（无需两轮泄libc）

**关键操作**:
1. UAF门：测试不同长度（64/72/80/88/96/100/104/108/112），96~104进入下一阶段，选100+输入"magic"复用chunk
2. canary探针：扫描首轮read+printf回显偏移，0x19开始跨入canary区，0x21/0x22继续有非零回显，精确定位边界
3. 第二关直接被UAF灭掉（全局状态检查被绕过），无需单独处理
4. 第二波payload：修复canary + ret2dlresolve，利用No PIE + Partial RELRO + read gadget，省去第二轮libc泄漏
5. 发包节奏：wave和plan必须分两次发，等程序打印"warmth."后再发第二波，防止read一次吞掉全部输入

**适用场景**: 下次遇到No PIE+Partial RELRO+有read gadget的场景，优先考虑ret2dlresolve而非两轮ret2libc

---

## [来自实战] Ring factory（ISCC 2026）

**技术模式**: 格式串+UAF双线并行（fgets名字短payload泄canary，ring slot UAF泄libc unsorted bin），最终ret2libc

**关键操作**:
1. 名字输入仅6字节，只做单点观察：%7$p=canary（末尾固定\x00），%13$p=main返回点（PIE影子）
2. UAF泄libc：9槽全forge后连续discard 0~7，第8个chunk（同尺寸）落入unsorted bin；show时%s打印fd指针即main_arena+96
3. libc_base = leak_fd - (__malloc_hook + 0x70)，无需硬背神秘常数
4. cast输入：buf在rbp-0x40，canary在rbp-0x8，填充0x38字节+canary+占位+ret+pop_rdi+/bin/sh+system
5. gadget和/bin/sh字符串从附件libc直接搜，不依赖one_gadget

**适用场景**: 下次遇到"短格式串输入+菜单UAF+cast/write超长输入"三件套时优先考虑此方向

---

## [来自实战] Sea（ISCC 2026）

**技术模式**: 格式串写GOT（__stack_chk_fail改为后门函数）+ 故意撞canary触发跳转，两次机会内完成

**关键操作**:
1. 题目端口可能变化，先探测实际活跃端口（非题面给的1000，实为10009）
2. 第一次输入：格式串%31$p泄PIE基址（低12bit固定0x3cc=main），计算base = leak - 0x13cc
3. 构造格式串写__stack_chk_fail@GOT为win函数地址：拆成3段%hn写低6字节，格式串后补\x00对齐到8字节再追加3个目标地址p64
4. 同一个payload（105字节）超过buf大小0x68，自动撞坏canary触发__stack_chk_fail→跳入后门
5. 不需要知道canary值，不依赖GOT以外的gadget，适合"两次尝试"限制场景

**适用场景**: 下次遇到"PIE+有__stack_chk_fail+printf(buf)+两次机会"时，优先考虑"改GOT到后门+故意撞canary"而非直接ROP

---

## [来自实战] somebox — LCG流加密已知明文恢复 + 时间侧信道爆破（2025强网杯决赛）

**技术模式**: Rust二进制，自定义流加密（4路独立LCG + mix变换），菜单明文已知→恢复k/b参数；登录密码计时侧信道逐字节爆破。

**LCG参数恢复**:
- 递推公式：`key[n] = (k * key[n-1] + b) mod 2^64`
- 已知明文（菜单文本）→ 前几项已知 → 解线性同余方程组恢复k、b
- 关键：4路key轮转，前24个key项通过已知明文XOR反推，再用`inverse_mix()`还原LCG状态
- 多解时取第一组解即可（实测不影响加解密）

**时间侧信道爆破**:
```python
# 每匹配一个正确字节，程序sleep 5ms
# 逐字节枚举：T >= 5*(current+1) ms 说明该字节正确
T = int(result[pos+1:rpos])
if T >= 5 * current + 5:
    current += 1; found = True
```

**调试技巧**: 程序必须通过pwntools交互，用IDA dbg_server附加调试：
1. 启动dbg_server监听
2. pwntools运行程序
3. IDA → Debugger → Attach → 选对应进程

**关键操作**:
1. 初始KEYC = [0x9E3779B97F4A7C15, 0, 0x94D049BB133111EB, 0]（断点栈上读取）
2. 接收第一行密文，用已知菜单明文XOR得到KEYX序列，再inverse_mix()还原LCG状态
3. 调用find_k_b_from_sequence()解出各路k/b
4. 之后encrypt/decrypt共享同一密钥生成器（注意功能1不消耗密钥）

**适用场景**: 下次遇到"自定义流加密+服务端输出已知明文前缀"时，优先尝试已知明文攻击恢复密钥；遇到"登录有计时反馈"时尝试时间侧信道逐字节爆破

---

## [来自实战] TrustSQL — SQLite3 edit()函数RCE（2025强网杯决赛）

**技术模式**: SQLite3开启`trusted_schema=ON`后，`edit()`函数可执行任意系统命令；通过恶意.db文件中的VIEW在特定查询时触发。

**关键操作**:
1. 前提：`PRAGMA trusted_schema = ON`（题目已开启）
2. 直接RCE：`SELECT edit('gnome-calculator;','gnome-calculator;');`
3. 但题目只允许执行固定查询，需预埋VIEW：
```sql
CREATE VIEW qwbDB AS SELECT edit('gnome-calculator;','gnome-calculator;') AS users;
```
4. 当操作员执行 `SELECT users FROM qwbDB;` 时自动触发计算器

**适用场景**: 下次遇到SQLite3题目且有`trusted_schema=ON`权限时，优先检查`edit()`函数RCE；需要在特定查询触发payload时用VIEW包装

---

## [来自实战] orange_cat_diary — House of Orange + fastbin attack（长城杯决赛2024）

**技术模式**: 无free函数时用House of Orange强制topchunk进unsorted bin泄露libc，再用UAF触发fastbin attack劫持__malloc_hook写one_gadget。

**关键操作**:
1. edit溢出8字节修改topchunk.size为0x0f91（满足page对齐且PREV_INUSE置位）
2. 申请比topchunk更大的堆块，系统调用sysmalloc时旧topchunk被free进unsorted bin
3. show泄露fd指针，计算libc基址：`libc_base = leak - 1640 - 0x10 - libc.sym['__malloc_hook']`
4. 触发UAF：free一个0x68大小块，edit覆盖fd为`__malloc_hook - 0x23`（fake size 0x7f对齐fastbin）
5. 连续申请两次0x68，第二次填充0x13字节padding + one_gadget地址覆盖__malloc_hook
6. 再次malloc触发one_gadget getshell

**适用场景**: 遇到"有edit无free"堆题时，检查edit是否能溢出覆盖topchunk.size；glibc 2.23 fastbin attack首选`__malloc_hook-0x23`（fake size=0x7f），one_gadget选满足[rsp+0x50]==NULL类约束的偏移

---

## [来自实战] go_stack — Go二进制ROP链（长城杯决赛2024）

**技术模式**: Go静态链接二进制无ASLR时，cyclic确定溢出偏移，ROPgadget找gadget，直接构造syscall链(read→execve)无需泄露libc。

**关键操作**:
1. `cyclic 0x200`发送测试串，从Go崩溃输出的错误地址用`cyclic -l`反查偏移（本例464）
2. ROPgadget在静态链接Go二进制中找`syscall`/`pop rax`/`pop rdi_6`/`pop rsi`/`pop rdx`（Go gadget丰富）
3. 第一段ROP：`rax=0`+syscall = sys_read → 将"/bin/sh\0"读入bss+0x200
4. 第二段ROP：`rax=59`+`rdi=bss+0x200`+`rsi=0`+`rdx=0`+syscall = execve("/bin/sh",0,0)
5. `time.sleep(2)`等read完成后发送字符串；注意Go栈布局：溢出后先设新rsp再放ROP链

**适用场景**: Go pwn用cyclic定偏移；静态链接使ROPgadget搜索更容易；无PIE时直接硬编码地址；syscall号走Linux x86_64（read=0, execve=59）

---

## [来自实战] heap — AES加密堆+unsafe unlink+ORW（强网杯S8决赛2024）

**技术模式**: 堆内容AES-ECB加密（随机密钥），safe_malloc限制分配在第一个页；输入长度<16绕过加密；tcache bin attack清零密钥→密钥已知→unsafe unlink任意写→__environ泄露栈→栈迁移+ORW。

**关键操作**:
1. **绕过AES**：add/edit的内容长度<16时不加密，直接明文存堆；利用tcache bin attack将fd指向key堆块地址，分配两次后写入8字节0x00（glibc 2.31 tcache取出时清空bk指针，恰好覆盖密钥后8字节），密钥变为全0
2. **泄露地址**：解密函数将内容解密到栈后输出，add(b'a'*0x20)后show可在响应中找到code_base；free+show泄露heap；unsorted bin free后show再AES-ECB加密响应得libc
3. **unsafe unlink**：需要指向fake chunk头部的已知指针（在bss的BookList中）；伪造fd=&p-0x18, bk=&p-0x10；触发条件：相邻块prev_inuse=0且prev_size=fake_chunk_size；unlink后BookList[victim]指向自身-0x18，实现任意写
4. **最终利用**：arbitrary write改BookList[0]为`__environ`地址→show读stack地址→写heap布置ORW chain→用leave gadget做栈迁移到堆上的ROP链

**适用场景**: 遇到AES加密堆，先看加密条件（长度阈值）绕过；safe_malloc页约束时必须在现有堆指针上做文章；glibc 2.31 tcache双free后修改fd+两次add = 任意地址分配

---

## [来自实战] ez_heap — base64解码长度溢出 + 零字节strchr漏洞（强网杯S8决赛2024）

**技术模式**: base64解码分配大小`3*len/4`（截断），当len不是4的倍数时解码写出超过分配大小；base64表strchr遇到末尾`\0`时返回位置0x41，配合`=`造成额外1字节`\x41`溢出topchunk size。

**关键操作**:
1. **漏洞点**：解码malloc大小`3*len/4`（整除截断），但解码函数每次输出3字节；输入非4倍数长度的base64串触发越界
2. **零字节trick**：base64字符串末尾`=`等效0，`strchr(table, 0)`找到字符串末尾返回`&table[64]`，偏移恰好是0x41；这导致解码最后一组时多写1字节`\x41`（'A'），正好覆盖下一个chunk的size LSB
3. **堆重叠**：构造输入使溢出的`\x41`覆盖相邻chunk size，扩大该chunk → free后进unsorted bin → 再分配时覆盖tcache bin中的fd指针
4. **利用链**：unsorted bin泄露libc → tcache bin attack → __free_hook = system → free("/bin/sh") → shell
5. **注意**：tcache数量检测问题，必须free两个相同大小块，再edit后进入的那个块修改fd；最低2位为0的libc地址需多覆盖1字节才能泄露

**适用场景**: base64解码分配大小计算不精确时（非4对齐），控制输入长度触发1-2字节越界；`strchr`对`\x00`的边界行为是base64解码漏洞的常见根因；检查堆操作是否有tcache计数检查，绕过方式固定

---

## [来自实战] baby_heap — libc GOT劫持strncmp→puts泄露环境变量flag（强网杯2024预赛）

**技术模式**: glibc 2.35，任意写限制在libc _IO_2_1_stdin_之前的data段（即libc GOT区域）；把libc GOT中的`strncmp`改为`puts`，再调用`putenv`/`setenv`触发`__add_to_environ`遍历所有环境变量时调用`strncmp(ep, name, len)`→变为`puts(ep)`，打印全部环境变量中的flag。

**关键操作**:
1. 先free两个相同大小unsorted bin块（size≥0x500），show泄露libc地址（bk指针）和堆地址
2. 任意写选项的限制：不能写`&_IO_2_1_stdin_ + 0x1000`以后（libc data后半段），但libc GOT在stdin之前，可写
3. 计算`libc.sym['strncmp']`在GOT中的地址，用写选项改为`libc.sym['puts']`
4. 调用`putenv`或`setenv`（选项2或3），其内部`__add_to_environ`无条件遍历`__environ`数组，对每项调用`strncmp(ep, name, namelen)`→实际调用`puts(ep)`→打印所有环境变量
5. 远程flag存于环境变量，本地getenv仅匹配首两字符后才调用strncmp，而putenv/setenv路径无条件全遍历

**适用场景**: 遇到"向libc data段任意写"且有env操作选项时，优先看libc GOT中可劫持的字符串/比较函数；`__add_to_environ`遍历env的路径比`getenv`更激进（无前缀过滤），是更好的触发链

---

## [来自实战] expect_number — 固定rand种子+C++异常回溯ROP（强网杯2024预赛）

**技术模式**: `srand(1)`种子固定→rand序列可预测；计算结果溢出写struct末尾覆盖函数指针低字节→跳到含栈溢出的vtable函数→溢出触发C++异常→异常栈回溯时找到外层`try{cin}catch{system("/bin/sh")}`完成利用。

**关键操作**:
1. `srand(1)`产生固定序列，本地C程序输出`rand()%4+1`的前288项，完全预知每轮运算类型
2. 构造序列让计算结果等于0x60（目标函数指针偏移），遇加法给2，遇减法给0，遇乘除给1（保持无效），超过0x80的值需用`x/2`再`*2`的方式构造（否则符号扩展后变负数超范围）
3. show()泄露程序基地址（利用固定序列在正确轮次调用）
4. 最后send payload=`b'\x00'*0x20 + p64(writable_addr) + p64(target_ret_addr)`到选项4，栈溢出；RBP必须设为可写地址（后门代码有写栈操作）
5. 溢出触发C++运行时异常→异常处理回溯调用栈找`try`块→命中外层`try{cin}{catch{system("/bin/sh")}}`→getshell

**适用场景**: C++题先找`try/catch`包裹的高危代码（system/exec）；固定种子的rand可直接本地复现；异常回溯利用的核心是让ret addr指向可以触发异常且调用栈上有catch的函数

---

## [来自实战] baby-calc — off-by-null变量覆盖+z3求解+栈迁移ret2libc（西湖论剑2023）

**技术模式**: off-by-null覆盖循环变量i→修改返回地址为leave ret实现栈迁移→提前布置ROP链(puts泄露libc+返回main, system getshell)→z3求解输入验证方程组绕过检查。

**关键操作**:
1. 漏洞：输入0x18填充到返回地址，末尾`\x00`字节off-by-null覆盖循环变量i（相邻栈变量）→i被改成0x38，循环继续写入覆盖返回地址
2. 栈迁移：返回地址改为`leave; ret`指令地址(0x400c19)→rbp已布置为栈上ROP链基址→第二次ret执行ROP
3. ROP链：先填充25个`ret`增加栈对齐成功率（因栈地址随机化），再`pop_rdi; got[puts]; plt[puts]; main+1`泄露libc，第二轮返回时`pop_rdi; /bin/sh; system; main+1`
4. z3求解验证：16个输入变量v3-v18，22个等式约束，z3自动求解通过验证
   ```python
   from z3 import *
   s = Solver()
   v3,v4,...,v18 = Ints('v3 v4 ... v18')
   s.add(v3 == 19); s.add(v5*v4*v3 - v6 == 36182); ...
   print(s.model())
   ```
5. 最终payload：`str(x).ljust(0x8,b'\0') + p64(0x400c19)*25 + ROP_chain + z3_solution_bytes + padding + p32(offset)`
6. libc版本：glibc 2.23-0ubuntu11.3（根据泄露地址查）

**适用场景**: off-by-null覆盖相邻变量改循环计数器扩大写入范围；栈不确定时填充大量ret指令增加ROP成功率；输入验证有大量等式约束时直接z3求解；栈迁移首选`leave; ret`gadget

---

## [来自实战] Message — 格式化字符串泄露+栈迁移ORW（西湖论剑2023）

**技术模式**: 格式化字符串漏洞`printf(input)`泄露栈地址和libc基址→栈溢出写ROP链到已知栈地址→leave ret栈迁移→open/read/write ROP链读flag。

**关键操作**:
1. 格式化字符串泄露：`%p%24$p`泄露栈上第1和第24个qword→第1个偏移0xc0得rbp，第24个减0x1f42e8得libc基址
2. 栈迁移布置：payload放到栈上已知地址`stack_addr-0xb0`，最后8字节写`p64(stack_addr-0xb0) + p64(leave_ret)`劫持rbp和返回地址
3. ORW ROP链：
   ```python
   payload = b'/flag\0\0\0' +  # flag字符串放栈头
   p64(pop_rdi) + p64(flag_addr) + p64(pop_rsi) + p64(0) + p64(open) +  # open('/flag', 0)
   p64(pop_rdi) + p64(3) + p64(pop_rsi) + p64(buf) + p64(pop_rdx) + p64(0x30) + p64(read) +  # read(3, buf, 0x30)
   p64(pop_rdi) + p64(1) + p64(pop_rsi) + p64(buf) + p64(pop_rdx) + p64(0x30) + p64(write)  # write(1, buf, 0x30)
   ```
4. glibc 2.31，gadgets从libc提取：pop_rsi=libc+0x2601f, pop_rdx=libc+0x142c92
5. 关键：ORW时文件描述符从3开始（stdin/out/err占0/1/2），读到的buffer地址必须可写

**适用场景**: 格式化字符串题优先泄露栈地址（第1个参数通常是caller rbp）和libc地址（ret chain上的libc函数）；seccomp禁execve时用ORW；栈迁移到已知地址避免爆破ASLR

---

## [来自实战] note-service2 — 负数索引越界写GOT+堆内分段shellcode (CISCN 2018)

**技术模式**: add note时index无边界检查，负数可越界写GOT；notes[-17]恰好命中free@got；覆盖后delete(0)=`free(note[0])`跳执行shellcode，rdi自然指向note[0]存的`/bin/sh`；小chunk分段shellcode每段末尾`jmp 0x19`跳过metadata。

**关键操作**:
1. show/edit菜单显示"not implement"→漏洞只在add(index)/del
2. 计算：`(free@got_addr - notes_base_addr) / 8 = -17`
3. `add(0,8,'/bin/sh')` → note[0]存/bin/sh字符串地址
4. `add(-17,8,shellcode_chunk1)` → free@got = &chunk1（shellcode首段）
5. shellcode分段：每8字节用户区末尾`jmp 0x19`跳过chunk header落到下一chunk
6. shellcode完成：rsi=0, rdx=0, rax=59 → `syscall` → execve('/bin/sh',0,0)
7. `delete(0)` → `free(note[0])` → 跳shellcode → shell

**适用场景**: 指针数组index无下界→计算负数索引命中GOT/函数指针；Partial RELRO下free@got可写；小malloc chunk分段shellcode用`jmp 0x19`(跨0x20 chunk metadata)；rdi在free调用时天然等于被free的指针

---

## [来自实战] owo what's this — 简单ret2win(gets+pop rdi+栈对齐) (新西兰CTF)

**技术模式**: 64位ELF，no PIE no Canary NX on，`gets(buf)`无限度溢出；buf在rbp-0x10，偏移24字节覆盖返回地址；win函数需参数67416741通过rdi → `pop rdi; ret` + 额外`ret`栈对齐。

**关键操作**:
1. `checksec`确认：no PIE, no canary → ret2win
2. 偏移：`sub rsp,0x10` → buf在rbp-0x10 → 16+8(rbp)=24字节
3. 用ROPgadget找`pop rdi; ret`地址
4. payload：`b'A'*24 + p64(pop_rdi) + p64(67416741) + p64(ret) + p64(win_addr)`
5. 额外`ret`gadget确保栈16字节对齐（`movaps`指令要求）

**适用场景**: gets/read无限制→溢出；64位ret2win标配：pop rdi设参数+ret对齐+call win；偏移=buf_to_rbp+8；no PIE时地址静态，ROPgadget直接查---

## [来自实战] pwn01 — 堆tcache一次任意地址写\x00攻击free_hook (网鼎杯2024白虎组)

**技术模式**: glibc 2.35堆题，利用off-by-one漏洞修改tcache链表fd指针最后一字节为\x00，使fd指向目标地址（如`__free_hook`），tcache attack劫持free_hook为system。

**关键操作**:
1. 漏洞点：edit函数可向chunk写入size+1字节，off-by-one可将下一chunk的fd指针最后字节覆盖为\x00
2. 堆布局：分配多个chunk使tcache链表中的fd指针某字节恰好为目标地址（如`__free_hook`）的低字节
3. 修改fd最后字节为\x00 → fd指向`__free_hook` → 下次malloc从tcache返回`__free_hook`地址
4. 向返回的chunk写入`system`地址 → `__free_hook`被改写为`system`
5. 释放包含"/bin/sh"字符串的chunk → 触发`free(chunk)` → 实际执行`system("/bin/sh")`
6. glibc 2.35已移除`__malloc_hook`/`__free_hook`，但libc-2.35仍保留（2.36+才彻底移除）
7. 泄露libc：利用UAF或tcache attack泄露heap地址 → 再泄露libc

**适用场景**: glibc 2.31-2.35堆题优先考虑tcache attack（无size检查）；off-by-one修改fd最后字节是tcache attack经典技巧；glibc 2.35仍可用free_hook；泄露libc后计算system和free_hook偏移

---

## [来自实战] house_1 — 格式化字符串双次泄露PIE+canary + fmtstr修改变量 + ret2libc (DASCTF)

**技术模式**: 格式化字符串漏洞两次利用：第1次泄露PIE偏移，第2次泄露canary，再用fmtstr_payload修改全局变量解锁较长输入，最后通过puts泄露libc做ret2libc。

**关键操作**:
1. 第一次格式化字符串泄露PIE：`%8$p` → 栈上第8个地址，与PIE偏移0x14a0
   ```python
   pie = pie_leak - 0x14a0
   ```
2. 第二次格式化字符串泄露canary：`%13$p` → 栈上第13个是canary
3. 用fmtstr_payload修改全局变量（如size限制）为更大值，解锁更长payload输入：
   ```python
   fmtstr_payload(6, {pie + 0x4010: 0x100})  # 修改全局size为0x100
   ```
4. 触发选项3（长输入）→ 构造ROP：泄露puts地址 → 计算libc基址
5. 二次ROP：`rdi + "/bin/sh"` + ret对齐 + `system`
   ```python
   pay = b"a"*0x48 + p64(canary) + p64(0) + p64(rdi) + p64(pie+elf.got["puts"]) + p64(pie+elf.plt["puts"]) + p64(ret_addr)
   libc_base = u64(p.recvuntil(b"\x7f")[-6:].ljust(8, b"\x00")) - libc.sym["puts"]
   ```

**适用场景**: 格式化字符串题先确定PIE偏移（栈上特定偏移处会有text段地址），canary通常在main的rbp上方；fmtstr_payload自动计算覆写格式；全保护题用canary覆写+PIE基址计算ROP链
4. glibc 2.31，gadgets从libc提取：pop_rsi=libc+0x2601f, pop_rdx=libc+0x142c92
5. 关键：ORW时文件描述符从3开始（stdin/out/err占0/1/2），读到的buffer地址必须可写

**适用场景**: 格式化字符串题优先泄露栈地址（第1个参数通常是caller rbp）和libc地址（ret chain上的libc函数）；seccomp禁execve时用ORW；栈迁移到已知地址避免爆破ASLR
