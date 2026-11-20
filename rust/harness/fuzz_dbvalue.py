"""Differential fuzz of the database value format: the Python original against the Rust port.

    python3 -W ignore rust/harness/fuzz_dbvalue.py [seed] [seconds]

Needs `rust-anything build rust/dbvalue-rs` first. Generates stored text (edits of the recorded
inputs, token soup, random characters) and nested values, runs both sides on each, and prints
every input they disagree on. The recorded cases are the proof; this looks for what they missed.
`-W ignore` silences CPython's own warnings about the odd literals.
"""

import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "dbvalue-rs", "python"))

import dbvalue  # noqa: E402
import dbvalue_rs  # noqa: E402

TOKENS = [
    "1", "0", "00", "07", "1_0", "0x1f", "0o7", "0b1", "1.5", ".5", "1.", "1e5", "1e-5", "2j", "1.5J", "0j",
    "True", "False", "None", "...", "set", "set()", "'a'", '"b"', "'''c'''", "b'x'", "r'\\n'", "u'u'", "f'f'",
    "rb'q'", "'\\n'", "'\\x41'", "'\\u00e9'", "'\\N{DASH}'", "'\\N{EM DASH}'", "'\\N{LF}'", "'it\\'s'", "(", ")",
    "[", "]", "{", "}", ",", ":", "+", "-", " ", "\t", "\n", "\r", "\x0c", "#c", "\\\n", "\\", ".", "_", "e", "j",
    "x", "*", "=", "é", "'", '"', "'\\", "''", '""', "9" * 20, "1e999", "-0.0", "(1,)", "[]", "{}", "{1}",
    "{1:2}", "()", "'é'", "'😀'", "b''", "\\x", "\\u", "0_", "__", "0e0", "1E+1", "0X_F",
]
ALPHABET = "'\"\\[](){}:,+-_.0123456789eEjJxXoObBrRuUfF \t\n\r\x0c#TrueFalsNonset=*é😀\x00\x0b\xa0"
TEXTS = ["", "a", "it's", 'say "hi"', "both ' and \"", "back\\slash", "new\nline", "é 日本 😀", "🫨", "\x01\x7f\xa0",
         "‍ ", "True", "1", "[1, 2]", "+919876543210", "x" * 70]
INTS = [0, 1, -1, 255, -1001234567890, 2**53 + 1, 2**64, -(10**30)]
FLOATS = [0.0, -0.0, 1.5, 0.1, 1e16, 1e-5, 1e300, 5e-324, math.inf, -math.inf, math.nan]
BYTES = [b"", b"abc", b"\x00\xff", b"it's", b'q"q', b"\n\\"]


def edit(rng, text):
    chars = list(text)
    for _ in range(rng.randrange(1, 5)):
        at = rng.randrange(len(chars) + 1)
        kind = rng.randrange(6)
        if kind == 0 and chars:
            del chars[min(at, len(chars) - 1)]
        elif kind == 1:
            chars.insert(at, rng.choice(ALPHABET))
        elif kind == 2 and chars:
            chars.insert(at, chars[min(at, len(chars) - 1)])
        elif kind == 3 and len(chars) > 1:
            at = min(at, len(chars) - 2)
            chars[at], chars[at + 1] = chars[at + 1], chars[at]
        elif kind == 4:
            chars[at:at] = list(rng.choice(TOKENS))
        else:
            chars = chars[:at]
    return "".join(chars)


def value(rng, depth=0):
    kind = rng.randrange(10) if depth < 4 else 0
    if kind <= 4:
        return rng.choice([None, True, False] + INTS + FLOATS + BYTES + TEXTS * 2)
    size = rng.randrange(4)
    if kind == 5:
        return [value(rng, depth + 1) for _ in range(size)]
    if kind == 6:
        return tuple(value(rng, depth + 1) for _ in range(size))
    if kind == 7:
        return {rng.choice(INTS[:5]) for _ in range(size)}
    keys = INTS + TEXTS + [(1, "a"), b"k", 1.5, None, True]
    return {rng.choice(keys): value(rng, depth + 1) for _ in range(size)}


def run(module, function, argument):
    try:
        return "ok", getattr(module, function)(argument)
    except Exception as error:  # noqa: BLE001
        return "error", type(error).__name__


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(seed)
    inputs = os.path.join(HERE, "..", "dbvalue-rs", "inputs.jsonl")
    corpus = [json.loads(line)["args"][0] for line in open(inputs, encoding="utf-8") if '"read_stored"' in line]
    corpus = [text for text in corpus if len(text) <= 60]
    tried, differing, seen, start = 0, [], set(), time.time()
    while time.time() - start < budget:
        kind = rng.randrange(6)
        if kind == 5:
            checks = [("write_value", value(rng))]
        else:
            text = (edit(rng, rng.choice(corpus)) if kind < 3
                    else "".join(rng.choice(TOKENS) for _ in range(rng.randrange(1, 9))) if kind == 3
                    else "".join(rng.choice(ALPHABET) for _ in range(rng.randrange(1, 12))))
            if text in seen:
                continue
            seen.add(text)
            checks = [("read_stored", text), ("write_value", text)]
        tried += 1
        for function, argument in checks:
            original, port = run(dbvalue, function, argument), run(dbvalue_rs, function, argument)
            if original != port:
                differing.append((function, argument, original, port))
    print(f"seed {seed}: {tried} inputs, {len(differing)} differences")
    for function, argument, original, port in differing[:40]:
        print(f"  {function}({argument!r})\n    original: {original}\n    port:     {port}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
