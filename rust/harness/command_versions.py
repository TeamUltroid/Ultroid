"""Replays the recorded cases of command recognition under the interpreter that runs this.

    python3.13 -W ignore rust/harness/command_versions.py

The cases in `rust/command-rs/cases.jsonl` were recorded from the original under one version of
Python. Its `re` is what decides them, and `re` is not the same in every version. This says how
many of the cases another interpreter answers differently, and shows the first of them.

Only the standard library is needed, so that an interpreter without Telethon can run it. The
price is a copy of `compile_pattern` below; run under the recording interpreter, it has to give
every case back, which is the check on the copy.
"""

import json
import os
import re
import sys

CASES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "command-rs", "cases.jsonl")


def compile_pattern(data, hndlr):
    if data.startswith("^"):
        data = data[1:]
    if data.startswith("."):
        data = data[1:]
    if hndlr in [" ", "NO_HNDLR"]:
        return re.compile("^" + data)
    return re.compile("\\" + hndlr + data)


def answer(function, args):
    *given, text = args
    if function != "inline" and not given[0]:
        return ["always"]
    try:
        if function == "command":
            compiled = compile_pattern(*given)
        else:
            compiled = re.compile(("^/" if function == "assistant" else "") + given[0])
    except re.error:
        return ["bad pattern"]
    found = compiled.match(text)
    if found is None:
        return ["no"]
    return ["match", found.end(), list(found.groups()), found.groupdict()]


def main():
    cases = differing = 0
    shown = []
    with open(CASES, encoding="utf-8") as recorded:
        for line in recorded:
            case = json.loads(line)
            cases += 1
            try:
                here = answer(case["fn"], case["args"])
            except Exception as error:  # noqa: BLE001
                here = ["raised", type(error).__name__]
            if here != case.get("ok"):
                differing += 1
                shown.append((case["fn"], case["args"], case.get("ok"), here))
    print(f"Python {sys.version.split()[0]}: {cases} recorded cases, {differing} answered differently")
    for function, args, recorded, here in shown[:10]:
        print(f"  {function}{tuple(args)!r}\n    recorded: {recorded}\n    here:     {here}")
    sys.exit(1 if differing else 0)


if __name__ == "__main__":
    main()
