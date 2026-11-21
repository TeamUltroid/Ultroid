"""Builds inputs.jsonl for the language strings.

    python3 make_inputs.py > inputs.jsonl

A scenario by hand for each rule of `strings/__init__.py`, then random ones from
`rust/harness/language_scenarios.py`. Seeded, so a rerun gives the same file.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "harness"))

import language_scenarios as made  # noqa: E402

EN = {"name": "English", "natively": "English", "authors": ["xditya", "sppidy"], "py_c1": "Wrong string session.",
      "cmda": "✘ Commands Available", "help_ping": "\n\n• `{i}ping`", "fmt": "a {} b {}", "plain": "no places"}  # fmt: skip
HI = {"name": "Hindi", "natively": "हिन्दी", "authors": ["x"], "py_c1": "गलत स्ट्रिंग सेशन।"}
BOTH = {"en.yml": EN, "hi.yml": HI}
ASK = [["get_string", "py_c1"], ["get_string", "fmt"], ["get_string", "fmt"], ["get_string", "nope"], ["get_string", "nope", False],
       ["get_help", "ping"], ["get_help", "nope"]]  # fmt: skip


def emit(setup, steps):
    setup = {"stored": None, "env": None, "files": {}, "broken": [], "translate": [], **setup}
    print(json.dumps({"fn": "run", "args": [setup, steps]}, ensure_ascii=False))


# English, the language everything falls back to.
emit({"files": {"en.yml": EN}}, ASK + [["get_languages"]])
emit({"files": {"en.yml": EN}, "stored": "en"}, ASK)
emit({"files": {"en.yml": EN}, "env": "en"}, ASK)
# Another language: English is not loaded until the list of languages is asked for.
emit({"files": BOTH, "stored": "hi"}, ASK + [["get_languages"]] + ASK)
emit({"files": BOTH, "env": "hi"}, ASK + [["get_languages"]] + ASK)
emit({"files": BOTH, "stored": "hi", "env": "en"}, ASK)
# A language with no file is read as English, and every string goes to the translator.
for ways in (["tag"], ["same"], ["empty"], ["drop"], ["extra"], ["break"], ["none"], ["type"], ["key"], ["value"], ["what"], []):
    emit({"files": {"en.yml": EN}, "stored": "de", "translate": ways * 3}, ASK + [["get_string", "plain"], ["get_string", "plain"]])
# What a desktop Linux sets for its own messages lands in the same variable.
emit({"files": {"en.yml": EN}, "env": "en_US:en"}, ASK)
emit({"files": BOTH, "env": ""}, ASK)
# The language changed while running, as the language menu does it.
emit({"files": BOTH}, [["get_string", "py_c1"], ["language", "hi"], ["get_string", "py_c1"], ["get_languages"], ["get_string", "py_c1"]])
emit({"files": BOTH}, [["get_languages"], ["language", "hi"]] + ASK + [["language", None]] + ASK + [["language", "zz"]] + ASK)
# Files that cannot be read, or hold something else than a mapping.
emit({"files": BOTH, "broken": ["hi.yml"], "stored": "hi"}, ASK + [["get_languages"]])
emit({"files": {"hi.yml": HI}, "stored": "hi"}, ASK + [["get_languages"]] + ASK)
emit({"files": {}, "stored": "hi"}, ASK + [["get_languages"]])
for held in (None, [], ["a", "b"], "text", 5, {}, {"name": "only a name"}):
    emit({"files": {"en.yml": held}}, ASK + [["get_languages"]])
    emit({"files": {"en.yml": EN, "hi.yml": held}, "stored": "hi"}, ASK + [["get_languages"], ["get_string", 0], ["get_string", "fmt"]])
# Names in the folder that are no language file, and a language named like a path.
emit({"files": {**BOTH, "notes.txt": EN, "fooyml": EN, ".hidden.yml": EN, "x.yaml": EN, "a\\b.yml": HI, "yml": EN}}, [["get_languages"]])
for stored in made.STORED:
    emit({"files": {**BOTH, "5.yml": HI, "True.yml": HI, "a\\b.yml": HI}, "broken": ["zz.yml"], "stored": stored}, ASK[:4] + [["get_languages"]])
# Keys and values that are not text.
for key in made.ODD:
    emit({"files": {"en.yml": {**EN, "odd": key, "cmda": key}}, "stored": "de"}, [["get_string", "odd"], ["get_help", "ping"], ["get_string", key]])
    emit({"files": {"en.yml": EN}}, [["get_string", key], ["get_string", key, False], ["get_help", key]])
# Steps that make no sense, and settings that are none.
emit({"files": BOTH}, [["get_string"], ["get_string", "a", True, 1], ["get_help"], ["get_languages", 1], ["language"]])
for steps in ([["nope"]], [[]], ["get_string"], [None], [[["get_string"]]], [["get_string", "py_c1"], ["nope"]]):
    emit({"files": BOTH}, steps)
for setup in ({"files": []}, {"files": None}, {"broken": "hi.yml"}, {"broken": None}, {"translate": "tag"}, {"stored": 5}, {"env": 5},
              {"env": "a\x00b"}, {"broken": [5]}, {"broken": ["a/b"]}, {"broken": [""]}, {"broken": [".."]}, {"broken": [["x"]]},
              {"files": {"a/b.yml": EN}}, {"files": {"x" * 201: EN}}, {"broken": ["é" * 101]}, {"translate": [["tag"]]}, {"translate": [5]}):  # fmt: skip
    emit({"files": BOTH, **setup}, ASK[:3])
rng = random.Random(20261120)
for _ in range(1400):
    emit(*made.scenario(rng))
