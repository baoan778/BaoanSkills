---
name: ctf-misc
description: Solve cross-category CTF puzzles such as encodings, pyjails, bash jails, RF/SDR, esoteric languages, games, and unusual sandboxes. Prefer a more specific CTF skill when the dominant category is clear.
license: MIT
allowed-tools:
- Bash
- Read
- Write
- Edit
- Glob
- Grep
- Task
- WebFetch
- WebSearch
- Skill
metadata:
  user-invocable: 'false'
  compatibility: Requires filesystem-based agent (Claude Code or similar) with bash, Python 3, and internet access for tool installation.
  author: BaoanSkills contributors
  source: original
  category: ctf
  risk: offensive
  tags:
  - ctf
  - jail
  - encoding
  - rf
  - misc
  license_status: verified
  provenance_status: verified
  retrieved_at: '2026-11-22'
  modifications: 'Original BaoanSkills content; metadata normalized; authorization boundary preserved or added for public release. Public quality normalization: concise discovery description, reviewed risk and tags, explicit tool scope, and skill-specific UI presentation. Reorganized detailed field notes into a directly linked references/field-notes.md.'
  license_evidence: LICENSE
---

> **Authorized use only.** Use this skill only in environments you own or are explicitly authorized to assess.

# CTF Miscellaneous

Quick reference for miscellaneous CTF challenges. Each technique has a one-liner here; see supporting files for full details.

## Prerequisites

**Python packages (all platforms):**
```bash
pip install z3-solver pwntools Pillow numpy requests dnslib
```

**Linux (apt):**
```bash
apt install ffmpeg qrencode
```

**macOS (Homebrew):**
```bash
brew install ffmpeg qrencode
```

**Manual install:**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`

## Additional Resources

- [pyjails.md](./references/pyjails.md) - Python jail/sandbox escape techniques, quine context detection, restricted character repunit decomposition, func_globals module chain traversal, restricted charset number generation, class attribute persistence, f-string config injection via stored eval
- [bashjails.md](./references/bashjails.md) - Bash jail/restricted shell escape techniques, HISTFILE file read trick, bash -v verbose mode, ctypes.sh direct C library calls
- [encodings.md](./references/encodings.md) - Encodings, QR codes, esolangs, UTF-16 tricks, BCD encoding, multi-layer auto-decoding, indexed directory QR reassembly, multi-stage URL encoding chains
- [encodings-advanced.md](./references/encodings-advanced.md) - Verilog/HDL, Gray code cyclic encoding, RTF custom tag extraction, SMS PDU decoding, multi-encoding sequential solvers, UTF-9, pixel binary encoding, hexadecimal Sudoku + QR assembly, TOPKEK, MaxiCode
- [rf-sdr.md](./references/rf-sdr.md) - RF/SDR/IQ signal processing (QAM-16, carrier recovery, timing sync)
- [dns.md](./references/dns.md) - DNS exploitation (ECS spoofing, NSEC walking, IXFR, rebinding, tunneling)
- [games-and-vms.md](./references/games-and-vms.md) - WASM patching, Roblox place file reversing, PyInstaller, marshal analysis, Python env RCE, Z3 (including boolean logic gate network SAT solving), K8s RBAC, floating-point precision exploitation, custom assembly language sandbox escape via Python MRO chain
- [games-and-vms-2.md](./references/games-and-vms-2.md) - Cookie checkpoint game brute-forcing, Flask cookie game state leakage, WebSocket game manipulation, server time-only validation bypass, De Bruijn sequence, Brainfuck instrumentation, WASM linear memory manipulation
- [games-and-vms-3.md](./references/games-and-vms-3.md) - memfd_create packed binaries, multi-phase crypto games with HMAC commitment-reveal and GF(256) Nim, emulator ROM-switching state preservation, Python marshal code injection, Benford's Law bypass, parallel connection oracle relay, nonogram solver pipelines, 100 prisoners problem, C code jail escape via emoji identifiers, BuildKit daemon build secret exploitation, Docker container escape, Levenshtein distance oracle attack, taint analysis bypass via type coercion, shredded document pixel-edge reassembly
- [games-and-vms-4.md](./references/games-and-vms-4.md) - Part 4 (2018-era): XSLT as Turing-complete VM, JavaScript MAX_SAFE_INTEGER successor equality, binary search oracle in comparison-only DSL, blind SQLi via script-engine timeout error, OEIS sequence lookup automation, QR code reassembly from format-string constraints, matrix exponentiation for Fibonacci recurrence, Tribonacci for frog-jump counting, Selenium + Tesseract dynamic CAPTCHA, Brainfuck→Piet multi-layer polyglot, bytebeat synth code recognition
- [linux-privesc.md](./references/linux-privesc.md) - Sudo wildcard parameter injection (fnmatch), crafted pcap for sudoers.d, monit confcheck process injection, Apache -d override, backup cronjob SUID, PostgreSQL COPY TO PROGRAM RCE, PostgreSQL backup credential extraction, NFS share exploitation, SSH Unix socket tunneling, PaperCut Print Deploy privesc, Squid proxy pivoting, Zabbix admin password reset via MySQL, WinSSHTerm credential decryption
- [ctfd-navigation.md](./references/ctfd-navigation.md) - CTFd platform API navigation without browser: detection, token auth, challenge listing, file download, flag submission, scoreboard, hints, notifications, Python client class

---

## When to Pivot

- If the puzzle is actually centered on cryptography or number theory, switch to `/ctf-crypto`.
- If the challenge is a real binary exploit instead of a jail, toy VM, or encoding problem, switch to `/ctf-pwn` or `/ctf-reverse`.
- If the input is mostly files, images, audio, or packet captures that need recovery work first, switch to `/ctf-forensics`.
- For ML/AI techniques (model attacks, adversarial examples, LLM jailbreaking), see `/ctf-ai-ml`.

## Quick Start Commands

```bash
# File identification
file mystery_file
xxd mystery_file | head -5
python3 -c "import magic; print(magic.from_file('mystery_file'))"

# Encoding detection
python3 -c "import base64; print(base64.b64decode('<data>'))"
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR code
zbarimg qr.png
python3 -c "from pyzbar.pyzbar import decode; from PIL import Image; print(decode(Image.open('qr.png')))"

# Z3 constraint solving
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python jail test
python3 -c "__import__('os').system('id')"
```

## General Tips

- Read all provided files carefully
- Check file metadata, hidden content, encoding
- Power Automate scripts may hide API calls
- Use binary search when guessing multiple answers

## Detailed Field Notes

Read [the field notes](references/field-notes.md) for encoding recipes, challenge patterns, case studies, and command one-liners. Use the topic cards above when a focused technique reference is more appropriate.
