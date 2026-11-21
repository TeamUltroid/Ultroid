"""Builds inputs.jsonl for command recognition.

    rust-anything build . && python3 make_inputs.py > inputs.jsonl

Every pattern the code registers, under the usual handlers and a few unusual ones, on messages
built from the pattern; then made-up patterns from the same grammar. The generator is
`rust/harness/command_inputs.py`; it is seeded, so a rerun gives the same file as long as the
plugins register the same patterns.

The port reads a part of Python's `re` and declines the rest. A recorded case is a claim, so a
pattern the port declines is left out here, which is why the port has to be built first. How
many were left out, and why, is printed at the end. None of the registered patterns may be among
them under the handlers Ultroid uses: that stops the run.
"""

import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "harness"))
sys.path.insert(0, os.path.join(HERE, "python"))

import command_inputs as made  # noqa: E402
import command_rs  # noqa: E402

rng = random.Random(20261120)
found = made.registered()
written, declined = collections.Counter(), collections.Counter()


def emit(function, *args, must=False):
    try:
        getattr(command_rs, function)(*args)
    except NotImplementedError as left:
        if must:
            sys.exit(f"the port declines a registered pattern: {function}{args!r}: {left}")
        declined[str(left).partition(": ")[2]] += 1
        return
    written[function] += 1
    print(json.dumps({"fn": function, "args": list(args)}, ensure_ascii=False))


def prefixed(pattern, handler):
    """The pattern as `re` gets it for a userbot command, to build messages from."""
    pattern = pattern[1:] if pattern.startswith("^") else pattern
    pattern = pattern[1:] if pattern.startswith(".") else pattern
    return "^" + pattern if handler in (" ", "NO_HNDLR") else "\\" + handler + pattern


# Every registered command under the three handlers Ultroid uses by default and with none.
for pattern in found["ultroid_cmd"]:
    for handler in (".", "/", "!", " "):
        for text in made.messages(rng, prefixed(pattern, handler), 4):
            emit("command", pattern, handler, text, must=True)
# Under every other handler tried, a sample of them.
for handler in made.HANDLERS:
    for pattern in rng.sample(found["ultroid_cmd"], 12) + ["", "^.ping", "^^ping", "..ping", ".", "^"]:
        for text in made.messages(rng, prefixed(pattern, handler), 2):
            emit("command", pattern, handler, text)
for pattern in found["asst_cmd"] + [""]:
    for text in made.messages(rng, "^/" + pattern, 10):
        emit("assistant", pattern, text, must=True)
for pattern in found["in_pattern"] + [""]:
    for text in made.messages(rng, pattern, 10):
        emit("inline", pattern, text, must=True)
# Made-up patterns, as inline patterns (no prefix) and as commands.
for _ in range(900):
    pattern = made.made_up(rng)
    for text in made.messages(rng, pattern, 2):
        emit("inline", pattern, text)
for _ in range(300):
    pattern, handler = made.made_up(rng), rng.choice(made.HANDLERS)
    for text in made.messages(rng, prefixed(pattern, handler), 2):
        emit("command", pattern, handler, text)
for pattern in made.ODD:
    emit("inline", pattern, "a")
print(f"wrote {dict(written)}; left out {sum(declined.values())}: {dict(declined)}", file=sys.stderr)
