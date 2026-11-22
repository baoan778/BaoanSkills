# Corpus index and search vocabulary

This card is the map for the curated CTF knowledge-base skill. It describes the local corpus by category and vocabulary without redistributing the source documents.

## Corpus at a glance

| Category | Files | Primary location | What it is useful for |
|---|---:|---|---|
| `topic-note` | 23 | repository root | Topic notes and rendered HTML copies covering web, stego, archives, and tooling |
| `writeup` | 81 | `WP汇总/` | Challenge families, notes, helper scripts, and supporting images |
| `script` | 437 | `CTF常用脚本及工具/` | Small solvers and bundled utility trees collected during CTF practice |
| `tool-guide` | 8 | `工具使用/` | Dirsearch, ffuf, SQLMap, Wireshark, and tshark references |
| `toolset` | 14,286 | `CTF工具集/` | Packaged Windows tools, dictionaries, rules, and supporting files |

Current manifest total: **14,835 files, 3,656,564,703 bytes**. The manifest is metadata only; it does not contain document bodies or bundled binaries.

## High-value starting points

| Need | Relative path |
|---|---|
| Web technique overview | `命令执行.md`, `文件包含.md`, `文件上传漏洞.md`, `SQL.md`, `SSRF漏洞.md`, `SSTI.md`, `JWTmd.md`, `php代码审计.md` |
| PHP object attacks | `PHP反序列化漏洞总结.md` |
| Image and audio stego | `图片隐写.md`, `音频隐写.md` |
| Archive puzzles | `压缩包总结.md` |
| ctfshow web families | `WP汇总/ctfshow-命令执行wp.md`, `WP汇总/ctfshow-文件上传wp.md`, `WP汇总/ctfshow-php特性.md`, `WP汇总/CTfshow-反序序列化wp.md`, `WP汇总/ctfshow-SSTI.md` |
| Node prototype notes | `WP汇总/Nodejs/Nodejs原型链污染.md` |
| Lab walkthrough collections | `WP汇总/各大靶场WP汇总.md` |
| Tool handbooks | `工具使用/Dirsearch.md`, `工具使用/ffuf的使用.md`, `工具使用/tshark使用.md`, `工具使用/Wireshark使用.md` |

The HTML files at the repository root are mostly rendered copies of the Markdown topic notes. Prefer the Markdown file when both exist because it is easier to search and diff.

## Search vocabulary

Search both English terms and Chinese aliases. Useful pairs include:

| English | Chinese or corpus term |
|---|---|
| command execution, RCE | 命令执行, 命令拼接, 无回显 |
| file inclusion, LFI, RFI | 文件包含, 伪协议 |
| file upload | 文件上传, 上传绕过 |
| SQL injection | SQL 注入, 联合注入, 盲注 |
| server-side request forgery | SSRF, 内网探测 |
| server-side template injection | SSTI, 模板注入 |
| deserialization | 反序列化, 魔术方法, POP 链 |
| prototype pollution | 原型链污染 |
| weak comparison, type juggling | PHP 特性, 弱类型 |
| image steganography | 图片隐写, LSB, 盲水印 |
| audio steganography | 音频隐写, 频谱, 波形 |
| archive analysis | 压缩包, 伪加密, CRC |
| traffic analysis | 流量分析, 取证 |

## Retrieval sequence

1. Classify the question as topic, writeup family, script family, tool guide, or packaged tool.
2. Choose a curated card from `SKILL.md` or a case from [the case index](cases/index.md).
3. Use `scripts/search_kb.py` for a literal, case-insensitive search when the local corpus is installed.
4. Verify the exact path in [file-manifest.csv](archive/file-manifest.csv) before opening or running anything.
5. Read the original source only in an authorized environment and record the path, line, and observed behavior as evidence.
6. Route execution to the specialized skill once the technical category is clear.

## Manifest fields

| Field | Meaning |
|---|---|
| `relative_path` | POSIX-style path relative to the corpus root; never an absolute host path |
| `category` | One of the five reviewed corpus categories |
| `extension` | Lowercase suffix, or an empty value when there is no suffix |
| `bytes` | Exact file size at manifest generation |
| `sha256` | Content identity for integrity checks and duplicate analysis |

A hash proves byte identity only. It does not prove safety, correctness, authorship, or redistribution rights.

## Quality warnings

- The corpus contains historical notes, scripts, screenshots, and tool archives with mixed provenance.
- Tool versions and flags may have changed; consult `--help` or the bundled version before relying on syntax.
- Some notes reference unavailable images or remote resources. Known local
  gaps include missing `../images/Less-1.jpg` from `SQL.md` and
  `.figureqr*.jpg` from `图片隐写.md`; those notes are not self-contained.
  See [known corpus gaps](archive/known-gaps.md) for authorized synthetic
  reconstruction steps.
- A script name is not evidence that the script is safe to run. Inspect imports, file paths, network calls, and destructive operations first.
- Do not infer that a path exists in the public package. Only the curated cards and manifest are shipped.

See [provenance.md](provenance.md), [the archive guide](archive/README.md), [the tool catalog](archive/tool-catalog.md), and [the archive exclusions](archive/exclusions.md) before extracting, running, or publishing corpus material.
