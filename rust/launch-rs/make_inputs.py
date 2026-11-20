"""Builds inputs.jsonl for the launch logic of `multi_client.py`.

    python3 make_inputs.py > inputs.jsonl

Environments by hand for each rule, then random ones: each of the 25 variables the script can
read is there or not, empty or not, among variables it does not read. Seeded, so a rerun gives
the same file.
"""

import json
import random

NAMES = ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]
SUFFIXES = ["", "1", "2", "3", "4"]
VALUES = ["1", "12345", "abc", "0", " ", "-m", "--help", "a b", "ünï", "😀", "redis://h:1", "'q'", '"', "\n", "x" * 300]
# Names the script does not read, some of them close to ones it does.
OTHER = ["API_ID5", "API_ID0", "API_ID01", "api_id", "API_ID ", " API_ID", "API_ID_1", "SESSION11", "REDIS_URL", "PATH",
         "BOT_TOKEN", "", "API_HASH٢", "1API_ID", "REDIS_PASSWORD5"]  # fmt: skip

rng = random.Random(20261120)


def emit(environment):
    print(json.dumps({"fn": "plan", "args": [environment]}, ensure_ascii=False))


def client(suffix, tag=""):
    return {name + suffix: f"{name.lower()}{suffix}{tag}" for name in NAMES}


emit({})
for suffix in SUFFIXES:
    emit(client(suffix))
    for name in NAMES:
        # One variable missing, and one there but empty.
        emit({key: value for key, value in client(suffix).items() if key != name + suffix})
        emit({**client(suffix), name + suffix: ""})
# Every set of clients, the first to the fifth.
for which in range(1, 32):
    environment = {}
    for at, suffix in enumerate(SUFFIXES):
        if which >> at & 1:
            environment.update(client(suffix))
    emit(environment)
    emit(dict(reversed(list(environment.items()))))
for name in OTHER:
    emit({name: "x"})
    emit({**client(""), name: "x"})
    emit({**{key: value for key, value in client("").items() if key != "API_ID"}, name: "x"})
for value in VALUES:
    emit({**client("2"), "SESSION2": value})
    emit({name: value for name in NAMES})
for _ in range(1500):
    environment = {}
    for suffix in SUFFIXES:
        present = rng.random()
        for name in NAMES:
            roll = rng.random()
            if roll < present * 0.9 + 0.1:
                environment[name + suffix] = "" if rng.random() < 0.06 else rng.choice(VALUES)
    for name in rng.sample(OTHER, rng.randrange(4)):
        environment[name] = rng.choice(VALUES + [""])
    items = list(environment.items())
    rng.shuffle(items)
    emit(dict(items))
# What is no environment at all.
for junk in ([], None, "API_ID", 5, 1.5, True, [["API_ID", "1"]], {"API_ID": 1}, {"API_ID": None}, {"x": ["y"]},
             {**client(""), "SESSION": 5}, {**client(""), "OTHER": None}):  # fmt: skip
    emit(junk)
