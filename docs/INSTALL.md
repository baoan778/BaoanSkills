# Install BaoanSkills

BaoanSkills is a Python-based, file-level verified skill library for Codex and
other agents that discover `SKILL.md` directories. The installer copies only
skills on the reviewed public allowlist; it does not execute skill content or
install third-party tools.

[Back to README](../README.md) · [中文说明](../README.zh-CN.md) · [Routing guide](ROUTING.md) · [Authorization policy](AUTHORIZATION.md)

> [!IMPORTANT]
> **Authorized use only.** Install and use these skills only for CTF
> environments, owned labs, or systems for which you have explicit written
> permission. A public target or a discovered service is never authorization.

## Requirements

| Requirement | Supported |
|---|---|
| Python | 3.10, 3.11, or 3.12 |
| Operating system | Windows 10+, macOS 12+, and current mainstream Linux distributions |
| Git | Required for clone-and-update installation; not required to extract a release archive |
| Agent | Codex or another agent that discovers `SKILL.md` directories |

The installer has no runtime dependencies beyond the Python standard library.
Maintainer tooling is the only part that needs the packages in
`requirements-dev.txt`.

## Quick install

### macOS / Linux

```bash
git clone https://github.com/baoan778/BaoanSkills.git
cd BaoanSkills
python3 scripts/install_skills.py --list
python3 scripts/install_skills.py solve-challenge ctf-web ctf-crypto ctf-writeup
```

### Windows PowerShell

```powershell
git clone https://github.com/baoan778/BaoanSkills.git
Set-Location BaoanSkills
python scripts\install_skills.py --list
python scripts\install_skills.py solve-challenge ctf-web ctf-crypto ctf-writeup
```

Use `python3` instead of `python` on macOS or Linux when that is the available
interpreter name. On Windows, `py -3.12` is also suitable when the launcher is
installed.

The default destination is `$CODEX_HOME/skills` when `CODEX_HOME` is set,
otherwise `~/.codex/skills`. The installer expands the path and creates the
destination directory as needed.

## Choose a starter bundle

| Goal | Command |
|---|---|
| CTF fundamentals | `python scripts/install_skills.py solve-challenge ctf-web ctf-crypto ctf-forensics ctf-reverse ctf-pwn ctf-writeup` |
| Authorized web testing | `python scripts/install_skills.py ethical-hacking-methodology top-web-vulnerabilities sql-injection-testing xss-html-injection idor-testing pentest-checklist` |
| Cloud and host review | `python scripts/install_skills.py aws-penetration-testing linux-privilege-escalation windows-privilege-escalation ssh-penetration-testing` |
| Code and CI audit | `python scripts/install_skills.py agentic-actions-auditor semgrep-rule-creator burpsuite-project-parser` |
| Everything | `python scripts/install_skills.py --all` |

`--all` installs all 39 public skills. It does not install local staging skills
that are excluded from `release/public-skills.txt`.

## Installer options

| Option | Behavior |
|---|---|
| `--list` | Print the public skill names, one per line, and exit |
| `SKILL...` | Install the named public skills |
| `--all` | Install every public skill; cannot be combined with named skills |
| `--dest PATH` | Copy to a different skills directory |
| `--dry-run` | Print the planned operations without creating or replacing files |
| `--force` | Replace existing skill directories; without it, conflicts stop the install |
| `--help` | Show the complete command-line help |

The installer verifies every file in each requested skill against
`release/provenance.lock.json` before copying anything. Missing, extra,
symlinked, or changed files abort the operation and leave the destination
untouched for that request.

## Install from a release archive

Releases built after `v1.0.1` attach exactly two files to the
[GitHub release](https://github.com/baoan778/BaoanSkills/releases): a
`baoanskills-release.zip` archive and a `SHA256SUMS` checksum manifest. The
`v1.0.1` release predates this layout and keeps its legacy assets unchanged.
The examples below use `vX.Y.Z`; replace it with the version shown on the
release page.

### Windows PowerShell

```powershell
$version = "vX.Y.Z"
$archive = "baoanskills-release.zip"
Invoke-WebRequest "https://github.com/baoan778/BaoanSkills/releases/download/$version/$archive" -OutFile $archive
Invoke-WebRequest "https://github.com/baoan778/BaoanSkills/releases/download/$version/SHA256SUMS" -OutFile SHA256SUMS

$line = Get-Content .\SHA256SUMS | Where-Object { $_ -match '\s+baoanskills-release\.zip$' }
if (-not $line) { throw "SHA256SUMS does not list baoanskills-release.zip" }
$expected = ($line -split '\s+')[0].ToLowerInvariant()
$actual = (Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "Archive checksum mismatch" }

Expand-Archive $archive -DestinationPath .
Set-Location baoanskills-public
python scripts\install_skills.py ctf-writeup --dest "$HOME\.codex\skills"
```

### macOS / Linux

```bash
version=vX.Y.Z
archive=baoanskills-release.zip
curl -fLO "https://github.com/baoan778/BaoanSkills/releases/download/$version/$archive"
curl -fLO "https://github.com/baoan778/BaoanSkills/releases/download/$version/SHA256SUMS"

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c SHA256SUMS
else
  shasum -a 256 -c SHA256SUMS
fi

unzip -q "$archive"
cd baoanskills-public
python3 scripts/install_skills.py ctf-writeup
```

Download the archive and `SHA256SUMS` from the same release. A checksum
manifest from a different release is not valid for this archive.

## Update an installation

From a Git checkout:

```bash
git pull --ff-only
python3 scripts/install_skills.py --all --force
```

On Windows, use `python scripts\install_skills.py --all --force`. If you only
want selected skills, replace `--all` with the same skill names you installed:

```bash
python3 scripts/install_skills.py solve-challenge ctf-web ctf-crypto --force
```

`--force` replaces the entire skill directory with the verified version from
the updated checkout. It does not merge local edits or preserve files added
inside an installed skill directory. Restart or reload the agent after updating.

For a release archive, download the new version, verify its checksum, and run
the installer from the extracted `baoanskills-public` directory. Do not extract
the new archive over an existing installation; use the installer so the
provenance lock is checked.

## Manual installation

Manual copying is supported for inspection and air-gapped use, but it does not
provide the installer's provenance check. Copy the **whole skill directory**,
not only `SKILL.md`:

```text
skills/<skill-name>/
  SKILL.md
  references/
  scripts/
  agents/
```

Copying only the entrypoint loses references, scripts, and metadata. Do not copy
`release/`, `.git/`, caches, or the source checkout into the agent's skills
directory. If the installed agent supports a reload command, use it after the
copy.

## Verify the installation

```powershell
python scripts\install_skills.py --list
Test-Path "$HOME\.codex\skills\ctf-writeup\SKILL.md"
```

```bash
python3 scripts/install_skills.py --list
test -f "$HOME/.codex/skills/ctf-writeup/SKILL.md"
```

The exact destination may be different when `CODEX_HOME` or `--dest` is used.
The installer prints each copied skill and the final destination path.

## Troubleshooting

### `hash mismatch` or `size mismatch`

The checkout or extracted archive does not match
`release/provenance.lock.json`. Re-clone or re-download the release, then verify
the archive checksum. Do not edit the lock to make a modified file installable.

### `already installed (use --force to replace)`

The destination already contains one or more requested skill directories. Run
the same command with `--force`, or choose a new `--dest` for a side-by-side
installation. Review local edits before replacing a directory.

### `destination must be outside the source checkout`

Install into the agent's skills directory, not into the repository that contains
the source checkout. For example, use `--dest "$HOME/.codex/skills"`.

### Python version error

Use Python 3.10 or newer. Check the interpreter first:

```powershell
python --version
py -3.12 --version
```

```bash
python3 --version
```

If the virtual environment is active, install and run the same interpreter that
will execute the installer.

### A skill is missing or not listed

Run `python scripts/install_skills.py --list` from the release snapshot or
checkout. Names are case-sensitive, use lowercase hyphens, and must be present
in `release/public-skills.txt`. Raw local staging skills are not public and
cannot be installed by name.

### Unicode or path errors on Windows

Use a current PowerShell and a path without a trailing separator. Quote paths
containing spaces:

```powershell
python scripts\install_skills.py ctf-writeup --dest "C:\agent tools\skills"
```

The installer writes UTF-8 files and uses the standard Python path APIs. If the
agent reports a reload problem, restart the agent and confirm that the
destination contains `<skill-name>/SKILL.md`.

## Maintainer installation notes

The development environment and quality gates are documented in
[CONTRIBUTING.md](../CONTRIBUTING.md). Build a clean release snapshot with:

```bash
python scripts/build_public_bundle.py --output ../baoanskills-public --force
```

Never publish the source checkout directly. The generated snapshot excludes
ignored staging skills, caches, and transient build artifacts.

## License

The repository mixes MIT-licensed and CC BY-SA 4.0 material. See [NOTICE](../NOTICE)
and [licenses/](../licenses/) before redistributing or adapting a skill.
