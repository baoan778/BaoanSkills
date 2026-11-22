# Tool catalog

Authorized CTF and owned-lab use only.

The local corpus contains **55 top-level directories** under `CTF工具集/`. This
catalog is a navigation aid only: it names tool families and suggests when a
category is worth reviewing. It does not reproduce binaries, installers,
licenses, configuration files, dictionaries, screenshots, or tool source.

## How to use the catalog

1. Pick the narrowest domain that matches the challenge evidence.
2. Check the relevant manifest paths with `rg` or `scripts/search_kb.py`.
3. Confirm the tool's provenance, license, version, and checksum before running
   anything.
4. Prefer a maintained, independently installed tool over an untrusted bundled
   copy.
5. Run only in the isolated challenge environment and record the observed
   version and flags.

The names below are exact top-level directory names. Several include version
strings or vendor spellings; those are inventory labels, not endorsements.

## Recon, web, and infrastructure

| Top-level directories | Typical review question |
|---|---|
| `端口扫描`, `漏洞扫描`, `网站爬虫`, `web`, `Yapi`, `服务器架设`, `在线工具`, `科学上网`, `训练平台`, `无线安全`, `注入工具` | What is exposed, what does the target expect, and is the tool suitable for the current authorized lab? |

## Reverse, memory, and binary analysis

| Top-level directories | Typical review question |
|---|---|
| `安卓逆向`, `逆向综合`, `内存分析`, `取证`, `硬件安全`, `png-debugger-master`, `winhex20.6` | What format or runtime is involved, and which static or dynamic observation can be reproduced safely? |

## Crypto, encoding, and cracking

| Top-level directories | Typical review question |
|---|---|
| `编码解码`, `密码学`, `密码工具`, `密码爆破`, `暴力破解`, `CRC爆破`, `base一把梭`, `base隐写`, `bpg-0.9.8-win64`, `npiet-1.3a-win32` | Is the challenge asking for a reversible transform, a cryptanalytic weakness, a format repair, or a controlled search? |

## Steganography, media, archives, and miscellaneous

| Top-level directories | Typical review question |
|---|---|
| `二维码工具`, `截图恢复`, `流量分析`, `音频工具`, `隐形水印提取`, `信息隐藏`, `文本处理`, `文件比对`, `资源提取`, `综合工具`, `APNG Disassembler`, `BT种子编辑`, `exiftool-12.52`, `Jphswin`, `MISC做题思路`, `MP3Stego`, `NTFS文件流`, `openstego-master`, `OurSecret`, `Shiro rememberMe 在线解密_files`, `SSTV`, `SSuitePicsel`, `tweakpng-1.4.6`, `wbs43open-win32`, `zip伪加密` | Which carrier, metadata layer, encoding, or archive invariant is most likely to hide the clue? |

## Scripts and general toolboxes

| Top-level directories | Typical review question |
|---|---|
| `CTF常用脚本`, `CTF工具箱` | Is there a small reviewed helper that clarifies the workflow, or should the technique be reimplemented with a maintained tool? |

## Coverage check

The five groups above cover every top-level directory in the current toolset
inventory:

- 11 directories in the recon, web, and infrastructure group;
- 7 in reverse, memory, and binary analysis;
- 10 in crypto, encoding, and cracking;
- 25 in steganography, media, archives, and miscellaneous;
- 2 in scripts and general toolboxes.

That is **55 top-level directories** in total. Nested files are intentionally
not expanded here; use the [file manifest](file-manifest.csv) and the
[search helper](../../scripts/search_kb.py) when a narrower path is needed.

## Safety and provenance

- A directory name is not a license review or a malware scan.
- Some bundled tools may be commercial, shareware, abandoned, patched, or of
  unknown origin.
- Do not execute a bundled binary merely because it appears in a CTF corpus.
- Treat generated files, save states, sample outputs, and dictionaries as
  untrusted input.
- If provenance is unclear, keep the material local and use the technique card
  instead of redistributing or running the tool.

See [the archive guide](README.md) and [the exclusion rules](exclusions.md).
