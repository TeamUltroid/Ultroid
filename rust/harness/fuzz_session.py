"""Differential fuzz of session strings: the Python original against the Rust port.

    python3 rust/harness/fuzz_session.py [seed] [seconds]

Needs `rust-anything build rust/session-rs` first. Makes session strings and near misses with
`session_inputs.py`, runs `check` and `parse` on both sides, and prints every string they
disagree on. The recorded cases are the proof; this looks for what they missed.
"""

import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "session-rs", "python"))

import session  # noqa: E402
import session_inputs as made  # noqa: E402
import session_rs  # noqa: E402


def run(module, function, *args):
    try:
        return "ok", getattr(module, function)(*args)
    except Exception as error:  # noqa: BLE001
        return "error", type(error).__name__


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(seed)
    tried, differing, start = 0, [], time.time()
    while time.time() - start < budget:
        text = made.session(rng)
        if rng.random() < 0.3:
            text = made.edited(rng, text)
        tried += 1
        for function, args in (("check", (text, rng.random() < 0.5)), ("parse", (text,))):
            original, port = run(session, function, *args), run(session_rs, function, *args)
            if original != port:
                differing.append((function, args, original, port))
    print(f"seed {seed}: {tried} strings, {len(differing)} differences")
    for function, args, original, port in differing[:20]:
        print(f"  {function}{args!r}\n    original: {original}\n    port:     {port}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
