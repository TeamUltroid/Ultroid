"""Which lines of `strings/__init__.py` the recorded scenarios run.

    python3 -W ignore rust/harness/coverage_strings.py

Replays the inputs of `rust/strings-rs` through `language.py` with a trace on the original
module, and lists the lines that hold code and were never run.
"""

import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import language  # noqa: E402

seen = set()


def watch(frame, event, _):
    if frame.f_code.co_filename != language.SOURCE:
        return None
    if event == "line":
        seen.add(frame.f_lineno)
    return watch


def main():
    with open(language.SOURCE, encoding="utf-8") as source:
        tree = ast.parse(source.read())
    # Every statement but imports and the bodies of `try: import` at the top, which run once.
    code = {node.lineno for node in ast.walk(tree) if isinstance(node, ast.stmt)}
    with open(os.path.join(HERE, "..", "strings-rs", "inputs.jsonl"), encoding="utf-8") as inputs:
        cases = [json.loads(line)["args"] for line in inputs]
    sys.settrace(watch)
    for setup, steps in cases:
        try:
            language.run(setup, steps)
        except Exception:  # noqa: BLE001  (a setting that is none fails before the module runs)
            pass
    sys.settrace(None)
    missed = sorted(code - seen)
    print(f"{len(cases)} scenarios run {len(code & seen)} of {len(code)} statements of strings/__init__.py")
    with open(language.SOURCE, encoding="utf-8") as source:
        lines = source.read().split("\n")
    for number in missed:
        print(f"  never run: line {number}: {lines[number - 1].strip()}")


if __name__ == "__main__":
    main()
