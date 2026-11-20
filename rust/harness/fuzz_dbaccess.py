"""Differential fuzz of the accessors of pyUltroid/dB: the Python original against the Rust port.

    python3 -W ignore rust/harness/fuzz_dbaccess.py [seed] [seconds]

Needs `rust-anything build rust/dbaccess-rs` first. Makes scenarios with `scenarios.py`, runs
each on both sides, and prints the first step they disagree on. The recorded cases are the
proof; this looks for what they missed.
"""

import copy
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "dbaccess-rs", "python"))

import dbaccess  # noqa: E402
import dbaccess_rs  # noqa: E402
import scenarios  # noqa: E402


def run(module, steps):
    try:
        return module.run(steps)
    except Exception as error:  # noqa: BLE001
        return ["raised", type(error).__name__]


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(seed)
    tried, steps_run, differing, start = 0, 0, [], time.time()
    while time.time() - start < budget:
        kind = rng.randrange(10)
        if kind < 6:
            modules = [rng.choice(scenarios.MODULES)]
        elif kind < 8:
            modules = rng.sample(scenarios.MODULES, 2) + ["KeyManager"]
        else:
            modules = [rng.choice(["KeyManager", "udB"])]
        steps = scenarios.scenario(rng, modules, odd=rng.choice([0.05, 0.15, 0.4]))
        # Each side gets values of its own, as two processes would.
        original, port = run(dbaccess, copy.deepcopy(steps)), run(dbaccess_rs, steps)
        tried, steps_run = tried + 1, steps_run + len(steps)
        if original != port:
            differing.append((steps, original, port))
    print(f"seed {seed}: {tried} scenarios, {steps_run} steps, {len(differing)} differences")
    for steps, original, port in differing[:12]:
        at = next((i for i, pair in enumerate(zip(original, port)) if pair[0] != pair[1]), 0)
        for step in steps[: at + 1]:
            print(f"  {step!r}")
        print(f"    original: {original[at] if at < len(original) else original}")
        print(f"    port:     {port[at] if at < len(port) else port}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
