"""Differential fuzz of the language strings: `strings/__init__.py` against the Rust port.

    python3 -W ignore rust/harness/fuzz_strings.py [seed] [seconds]

Needs `rust-anything build rust/strings-rs` first. Runs random scenarios from
`language_scenarios.py` through both sides and compares the whole report: every result, every
call to the translator, every line logged, and what is loaded at the end.
"""

import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "strings-rs", "python"))

import language  # noqa: E402
import language_scenarios as made  # noqa: E402
import strings_rs  # noqa: E402


def ask(side, setup, steps):
    try:
        return side(setup, steps)
    except Exception as error:  # noqa: BLE001  (the failure is the result)
        return ["raised", type(error).__name__]


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(seed)
    tried = steps_run = translated = 0
    differing, start = [], time.time()
    while time.time() - start < budget:
        setup, steps = made.scenario(rng)
        theirs, ours = ask(language.run, setup, steps), ask(strings_rs.run, setup, steps)
        tried += 1
        steps_run += len(steps)
        translated += sum(1 for row in theirs if row[0] == "translate")
        if theirs != ours:
            differing.append((setup, steps, theirs, ours))
    print(f"seed {seed}: {tried} scenarios, {steps_run} steps, {translated} calls to the translator, "
          f"{len(differing)} differences")  # fmt: skip
    for setup, steps, theirs, ours in differing[:3]:
        print(f"  {setup!r}\n  {steps!r}")
        for row, (a, b) in enumerate(zip(theirs, ours)):
            if a != b:
                print(f"    row {row}\n      original: {a}\n      port:     {b}")
                break
        else:
            print(f"    lengths {len(theirs)} and {len(ours)}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
