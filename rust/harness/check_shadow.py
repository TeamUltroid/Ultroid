"""Replay a crate's recorded cases through its shadow drop-in, in every mode.

    python3 rust/harness/check_shadow.py rust/helper-rs

Needs `rust-anything build <crate>` and `rust-anything shadow <crate>` first. `old` and `shadow`
must return what the original returned when it was recorded; `new` must return it from Rust;
`shadow` must also report no mismatch between the two.
"""

import glob
import importlib.util
import json
import math
import os
import subprocess
import sys

MODES = ("old", "shadow", "new")


def dec(v):
    """A recorded argument back as the Python value it stands for."""
    if isinstance(v, list):
        return [dec(x) for x in v]
    if not isinstance(v, dict):
        return v
    if len(v) == 1:
        ((key, inner),) = v.items()
        if key == "$num":
            return {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf, "-0": -0.0}[inner]
        if key == "$float":
            return float(inner)
        if key == "$int":
            return int(inner)
        if key == "$tuple":
            return tuple(dec(x) for x in inner)
        if key == "$set":
            return {dec(x) for x in inner}
        if key == "$bytes":
            return bytes(inner)
        if key == "$dict":
            return {dec(k): dec(x) for k, x in inner}
    return {k: dec(x) for k, x in v.items()}


def replay(crate, mode):
    (path,) = glob.glob(os.path.join(crate, "shadow", "*_shadow.py"))
    spec = importlib.util.spec_from_file_location("shadow_under_check", path)
    shadow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shadow)
    cases = [json.loads(line) for line in open(os.path.join(crate, "cases.jsonl"), encoding="utf-8")]
    failed = []
    for case in cases:
        args = [dec(a) for a in case["args"] if a != {"$undefined": True}]
        try:
            got = {"ok": shadow.enc(getattr(shadow, case["fn"])(*args))}
        except Exception as error:  # noqa: BLE001
            got = {"error": type(error).__name__}
        if "error" in case:
            # The bindings answer a bad argument with TypeError, whatever the original raised.
            kinds = {case["error"].split(":", 1)[0]} | ({"TypeError"} if mode == "new" else set())
            same = got.get("error") in kinds
        else:
            same = shadow.canon(got.get("ok"), False) == shadow.canon(case["ok"], False) and "ok" in got
        if not same:
            failed.append((case["fn"], case["args"], got))
    mismatches = shadow.stats["mismatches"]
    print(f"{mode:6} {len(cases) - len(failed)}/{len(cases)} cases, {mismatches} shadow mismatches")
    for fn, args, got in failed[:10]:
        print(f"  {fn}{args}: {got}")
    return not failed and mismatches == 0


def main():
    crate = os.path.abspath(sys.argv[1])
    if len(sys.argv) > 2:
        sys.exit(0 if replay(crate, sys.argv[2]) else 1)
    ok = True
    for mode in MODES:
        env = dict(os.environ, RUST_ANYTHING_MODE=mode)
        run = subprocess.run([sys.executable, __file__, crate, mode], env=env, stdout=subprocess.PIPE, text=True)
        # The original prints a banner when imported outside a running bot.
        print("".join(line for line in run.stdout.splitlines(True) if "TeamUltroid" not in line), end="")
        ok = ok and run.returncode == 0
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
