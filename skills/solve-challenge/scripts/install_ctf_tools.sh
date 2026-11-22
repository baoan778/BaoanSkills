#!/usr/bin/env bash
# Guided CTF tool installer. Run only in an environment you control.
# The script never pipes remote content into a shell and is safe to inspect.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install_ctf_tools.sh [all|python|apt|brew|gems|go|manual] [--dry-run]

Groups:
  python  Python packages used by the CTF skills
  apt     Debian/Ubuntu packages
  brew    Homebrew packages
  gems    Ruby gems
  go      Go command-line tools
  manual  Print source links for tools that need manual installation
  all     Run every available package-manager group (not manual)

Environment:
  CTF_PIP_BREAK_SYSTEM_PACKAGES=1  Add the matching pip flag when required by
                                   an externally managed Python installation.

Always review package names and commands before running on a shared system.
USAGE
}

DRY_RUN=0
GROUP=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    all|python|apt|brew|gems|go|manual)
      if [ -n "$GROUP" ]; then
        echo "error: choose one group" >&2
        usage >&2
        exit 2
      fi
      GROUP="$arg"
      ;;
    *) echo "error: unknown argument: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$GROUP" ]; then
  usage >&2
  exit 2
fi

run() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  if [ "$DRY_RUN" -eq 0 ]; then
    "$@"
  fi
}

require_command() {
  command -v "$1" >/dev/null 2>&1
}

as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    run "$@"
  elif require_command sudo; then
    run sudo "$@"
  else
    echo "warning: sudo is unavailable; skipping: $*" >&2
    return 0
  fi
}

install_python() {
  if require_command python3; then
    local -a flags=(--user --upgrade)
    if [ "${CTF_PIP_BREAK_SYSTEM_PACKAGES:-0}" = "1" ]; then
      flags+=(--break-system-packages)
    fi
    run python3 -m pip install "${flags[@]}" \
      pwntools requests pycryptodome z3-solver flask-unsign \
      sqlmap frida-tools
  else
    echo "warning: python3 is unavailable; skipping Python group" >&2
  fi
}

install_apt() {
  if ! require_command apt-get; then
    echo "warning: apt-get is unavailable; skipping apt group" >&2
    return 0
  fi
  as_root apt-get update
  as_root apt-get install -y \
    binutils file gdb jq curl netcat-openbsd nmap \
    binwalk foremost exiftool steghide tshark \
    john hashcat sleuthkit python3-pip ruby ruby-dev \
    build-essential zlib1g-dev libssl-dev
}

install_brew() {
  if ! require_command brew; then
    echo "warning: Homebrew is unavailable; skipping brew group" >&2
    return 0
  fi
  run brew install nmap netcat jq curl hashcat john binwalk \
    foremost exiftool tshark steghide radare2 gdb
}

install_gems() {
  if ! require_command gem; then
    echo "warning: gem is unavailable; skipping gems group" >&2
    return 0
  fi
  run gem install --user-install zsteg one_gadget seccomp-tools
}

install_go() {
  if ! require_command go; then
    echo "warning: go is unavailable; skipping go group" >&2
    return 0
  fi
  run go install github.com/ffuf/ffuf/v2@latest
  run go install github.com/OJ/gobuster/v3@latest
  run go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
  run go install github.com/projectdiscovery/httpx/cmd/httpx@latest
}

install_manual() {
  cat <<'MANUAL'
The following tools are deliberately manual because their distribution and
license terms vary. Download only from the source below and verify the release:

- ysoserial:       https://github.com/frohoff/ysoserial
- Il2CppDumper:    https://github.com/Perfare/Il2CppDumper
- pwndbg:          https://github.com/pwndbg/pwndbg
- RsaCtfTool:      https://github.com/RsaCtfTool/RsaCtfTool
- Ghidra:          https://github.com/NationalSecurityAgency/ghidra
- CyberChef:       https://github.com/gchq/CyberChef

Use a pinned release or commit when reproducing a challenge, and keep tool
outputs outside the repository.
MANUAL
}

case "$GROUP" in
  python) install_python ;;
  apt) install_apt ;;
  brew) install_brew ;;
  gems) install_gems ;;
  go) install_go ;;
  manual) install_manual ;;
  all)
    install_python
    install_apt
    install_brew
    install_gems
    install_go
    ;;
esac

echo "installer group complete: $GROUP"
