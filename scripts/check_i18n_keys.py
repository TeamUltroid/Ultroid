#!/usr/bin/env python3
"""Warn/fail when non-English string files miss keys present in en.yml.

Usage:
  python scripts/check_i18n_keys.py           # warn, exit 0
  python scripts/check_i18n_keys.py --strict  # exit 1 on missing keys
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRINGS = ROOT / "strings" / "strings"
KEY_RE = re.compile(r"^([A-Za-z0-9_]+):", re.M)


def keys_in(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(KEY_RE.findall(text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 if any lang lags en.yml")
    args = ap.parse_args()

    en = STRINGS / "en.yml"
    if not en.exists():
        print("en.yml missing", file=sys.stderr)
        return 2
    en_keys = keys_in(en)
    print(f"en.yml keys: {len(en_keys)}")

    worst = 0
    for path in sorted(STRINGS.glob("*.yml")):
        if path.name == "en.yml":
            continue
        k = keys_in(path)
        missing = sorted(en_keys - k)
        extra = sorted(k - en_keys)
        worst = max(worst, len(missing))
        status = "OK" if not missing else f"MISSING {len(missing)}"
        print(f"  {path.name}: {status} (have {len(k)})")
        if missing and len(missing) <= 12:
            for m in missing:
                print(f"    - {m}")
        elif missing:
            for m in missing[:8]:
                print(f"    - {m}")
            print(f"    … +{len(missing) - 8} more")
        if extra and len(extra) <= 5:
            print(f"    extra: {', '.join(extra)}")

    if args.strict and worst:
        print(f"\nStrict mode: {worst} max missing keys — failing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
