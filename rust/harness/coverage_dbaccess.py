"""Says which lines of the original the recorded scenarios never run.

    python3 rust/harness/coverage_dbaccess.py

Runs the scenarios of `rust/dbaccess-rs/inputs.jsonl` (rebuilt from the same seed) through
`dbaccess.run` and lists every line of the functions in `pyUltroid/dB/*.py` and in `_BaseDatabase`
that no step reached. A port proven on cases that skip a line is not proven for that line.
"""

import collections
import os
import random
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import dbaccess  # noqa: E402
import scenarios  # noqa: E402
from fixture import _database  # noqa: E402

from pyUltroid.dB import base  # noqa: E402


# Lines no scenario can reach, by their text, and why.
UNREACHABLE = {
    "pyUltroid/dB/forcesub_db.py": {
        "except KeyError:": "the key was just found, so deleting it cannot fail",
        "return False": "the same",
    },
    "pyUltroid/startup/_database.py": {
        "return": "set_key(cache_only=True): nothing in Ultroid passes it, and it is not ported",
    },
}


def function_lines(code):
    """The lines of every function body in a code object. A `def` line belongs to whatever holds
    the function: it ran when the module was imported."""
    found = set()
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            if const.co_flags & 0x02:  # CO_NEWLOCALS: a function, not a class body
                found |= {line for _, _, line in const.co_lines() if line} - {const.co_firstlineno}
            found |= function_lines(const)
    return found


def targets():
    modules = [sys.modules["pyUltroid.dB." + name] for name in scenarios.MODULES] + [base]
    wanted = {}
    for module in modules:
        source = open(module.__file__, encoding="utf-8").read()
        wanted[module.__file__] = function_lines(compile(source, module.__file__, "exec"))
    # Of the database class, what every backend shares. `keys`, `ping` and `usage` are replaced
    # by each backend, the one in the fixture included.
    wanted[_database.__file__] = set()
    for function in vars(_database._BaseDatabase).values():
        if isinstance(function, types.FunctionType) and function.__name__ not in ("__init__", "keys", "ping"):
            code = function.__code__
            wanted[_database.__file__] |= {line for _, _, line in code.co_lines() if line} - {code.co_firstlineno}
    return wanted


def main():
    wanted = targets()
    seen = collections.defaultdict(set)

    def tracer(frame, event, arg):
        if frame.f_code.co_filename not in wanted:
            return None
        if event == "line":
            seen[frame.f_code.co_filename].add(frame.f_lineno)
        return tracer

    count = 0
    sys.settrace(tracer)
    try:
        for steps in scenarios.recorded(random.Random(20261120)):
            dbaccess.run(steps)
            count += 1
    finally:
        sys.settrace(None)
    root = os.path.join(HERE, "..", "..")
    total = missed = 0
    for path, lines in sorted(wanted.items()):
        name = os.path.relpath(path, root)
        source = open(path, encoding="utf-8").read().splitlines()
        known = UNREACHABLE.get(name, {})
        never = sorted(lines - seen[path])
        total += len(lines)
        for line in never:
            text = source[line - 1].strip()
            if text in known:
                print(f"{name}:{line}: `{text}` cannot be reached: {known[text]}")
            else:
                missed += 1
                print(f"{name}:{line}: `{text}` was never run")
    print(f"{count} scenarios ran {total - sum(len(lines - seen[path]) for path, lines in wanted.items())} of {total} lines")
    sys.exit(1 if missed else 0)


if __name__ == "__main__":
    main()
