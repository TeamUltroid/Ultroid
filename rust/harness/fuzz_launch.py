"""Differential fuzz of the launch logic: `multi_client.py` against the Rust port.

    python3 rust/harness/fuzz_launch.py [seed] [seconds]

Needs `rust-anything build rust/launch-rs` first. Builds random environments out of the
variables the script reads, variables it does not, and values of every kind, and compares what
each side would start.
"""

import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "launch-rs", "python"))

import launch  # noqa: E402
import launch_rs  # noqa: E402

NAMES = ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]
PIECES = ["", "", "", "1", "2", "3", "4", "5", "0", "01", " ", "_", "١", "a"]
LETTERS = "ab01 -=\n'\"é😀\\"


def environment(rng):
    out = {}
    for _ in range(rng.randrange(40)):
        name = rng.choice(NAMES) + rng.choice(PIECES)
        if rng.random() < 0.05:
            name = rng.choice([name.lower(), " " + name, name[1:], name + name[-1], ""])
        out[name] = "".join(rng.choice(LETTERS) for _ in range(rng.choice([0, 1, 1, 2, 5, 30])))
    return out


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 20
    rng = random.Random(seed)
    tried = started = 0
    differing, start = [], time.time()
    while time.time() - start < budget:
        given = environment(rng)
        theirs, ours = launch.plan(given), launch_rs.plan(given)
        tried += 1
        started += theirs[0] == "start"
        if theirs != ours:
            differing.append((given, theirs, ours))
    print(f"seed {seed}: {tried} environments ({started} with a client to start), {len(differing)} differences")
    for given, theirs, ours in differing[:5]:
        print(f"  {given!r}\n    original: {theirs}\n    port:     {ours}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
