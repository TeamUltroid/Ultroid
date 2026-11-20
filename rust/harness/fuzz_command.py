"""Differential fuzz of command recognition: Python's `re` against the Rust port.

    python3 -W ignore rust/harness/fuzz_command.py [seed] [seconds]

Needs `rust-anything build rust/command-rs` first. Takes the registered patterns under odd
handlers and made-up patterns (`command_inputs.py`), builds messages from each, and compares
both sides. A pattern the port declines to read is counted and skipped: the port makes no
claim for it. So is a case either side cannot finish in a few seconds. Everything else has to
agree, a pattern `re` refuses included.
`-W ignore` silences CPython's own warnings about the odd patterns.
"""

import multiprocessing
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "command-rs", "python"))

import command_inputs as made  # noqa: E402

# A pattern with repeats inside repeats can keep `re` busy for longer than the universe will
# last, and the port with it, since it matches the same way. Each side therefore runs in a
# process of its own, and one that does not answer in this many seconds is stopped and counted
# as slow. When only one side was slow it is asked once more with five times the patience: the
# two take about as long as each other, so a case near the limit often falls on both sides of
# it.
PATIENCE = 4


def _serve(side, calls, answers):
    module = __import__("command" if side == "original" else "command_rs")
    for function, args in iter(calls.get, None):
        try:
            answers.put(getattr(module, function)(*args))
        except NotImplementedError:
            answers.put("declined")
        except Exception as error:  # noqa: BLE001
            answers.put(["raised", type(error).__name__, str(error)[:80]])


class Side:
    """One side in its own process, started again whenever it had to be stopped."""

    def __init__(self, name):
        self.name, self.worker = name, None

    def ask(self, function, args, patience=PATIENCE):
        fresh = self.worker is None
        if fresh:
            self.calls, self.answers = multiprocessing.Queue(), multiprocessing.Queue()
            self.worker = multiprocessing.Process(target=_serve, args=(self.name, self.calls, self.answers))
            self.worker.daemon = True
            self.worker.start()
        self.calls.put((function, args))
        try:
            # A new process has the original to import before it can answer.
            return self.answers.get(timeout=patience + (15 if fresh else 0))
        except Exception:  # noqa: BLE001  (queue.Empty: no answer in time)
            self.worker.kill()
            self.worker = None
            return "slow"


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(seed)
    registered = made.registered()
    original, port = Side("original"), Side("port")
    tried = declined = 0
    slow, differing, start = [], [], time.time()
    while time.time() - start < budget:
        kind = rng.randrange(10)
        if kind < 3:
            pattern, handler = rng.choice(registered["ultroid_cmd"]), rng.choice(made.HANDLERS)
        else:
            pattern, handler = made.made_up(rng), rng.choice(made.HANDLERS + [".", ".", "/"])
        if kind % 2:
            function, args, seen = "command", (pattern, handler), "\\" + handler + pattern
        elif kind == 0:
            function, args, seen = "assistant", (pattern,), "^/" + pattern
        else:
            function, args, seen = "inline", (pattern,), pattern
        for text in made.messages(rng, seen, 3):
            tried += 1
            theirs = original.ask(function, (*args, text))
            ours = port.ask(function, (*args, text))
            if ours == "declined":
                declined += 1
                break
            if theirs == "slow" and ours != "slow":
                theirs = original.ask(function, (*args, text), PATIENCE * 5)
            elif ours == "slow" and theirs != "slow":
                ours = port.ask(function, (*args, text), PATIENCE * 5)
            if "slow" in (theirs, ours):
                slow.append((function, args, text, theirs, ours))
                break
            if theirs != ours:
                differing.append((function, args, text, theirs, ours))
    # Slow on one side only, after the second try, is a finding too: the two match the same
    # way, so they should tire of the same patterns.
    lopsided = [case for case in slow if case[3] != case[4]]
    print(f"seed {seed}: {tried} cases, {declined} patterns declined, {len(slow)} too slow "
          f"({len(lopsided)} of them on one side only), {len(differing)} differences")  # fmt: skip
    for function, args, text, theirs, ours in lopsided[:10] + [case for case in slow if case[3] == case[4]][:2]:
        which = "both" if theirs == ours else "the original" if theirs == "slow" else "the port"
        print(f"  slow in {which}: {function}{args!r} on {text!r}")
    for function, args, text, theirs, ours in differing[:15]:
        print(f"  {function}{args!r} on {text!r}\n    original: {theirs}\n    port:     {ours}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
