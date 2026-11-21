"""Builds inputs.jsonl for session strings.

    python3 make_inputs.py > inputs.jsonl

Made-up sessions in every layout Ultroid accepts, the near misses around them, and text that
is no session. The generator is `rust/harness/session_inputs.py`; it is seeded, so a rerun
gives the same file.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "harness"))

import session_inputs as made  # noqa: E402

rng = random.Random(20261120)


def emit(function, *args):
    print(json.dumps({"fn": function, "args": list(args)}, ensure_ascii=False))


# One of each kind first, then what is not text at all.
for text in [made.telethon(rng), *(made.pyrogram(rng, length) for length in made.PYROGRAM),
             made.telethon(rng, v6=True), made.telethon(rng, zero=True), *made.PLAIN]:  # fmt: skip
    for leave in (True, False):
        emit("check", text, leave)
    emit("parse", text)
for leave in (True, False, None, 0, 1, "", "x", [], [0]):
    emit("check", None, leave)
    emit("check", "hello", leave)
emit("parse", None)
for _ in range(700):
    emit("check", made.session(rng), rng.random() < 0.6)
for _ in range(500):
    emit("parse", made.session(rng))
