#!/usr/bin/env bash
# Ultroid session generator launcher
# Prefers the in-repo ssgen.py; falls back to a fresh copy only if missing.

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

install_deps() {
  if command -v apt-get >/dev/null 2>&1 && [[ "$(id -u)" -eq 0 || -n "${TERMUX_VERSION:-}" ]]; then
    apt-get install -y python3 python3-pip >/dev/null 2>&1 || true
  fi
}

install_deps

if [[ ! -f ssgen.py ]]; then
  echo "ssgen.py missing locally — downloading from TeamUltroid/Ultroid…"
  curl -fsSL -o ssgen.py \
    "https://raw.githubusercontent.com/TeamUltroid/Ultroid/main/resources/session/ssgen.py" \
    || wget -q -O ssgen.py \
    "https://raw.githubusercontent.com/TeamUltroid/Ultroid/main/resources/session/ssgen.py"
fi

python3 ssgen.py
