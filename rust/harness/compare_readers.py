"""What Ultroid's two readers make of the language files in `strings/strings`.

    python3 -W ignore rust/harness/compare_readers.py [code ...]

`strings/__init__.py` reads a language file with PyYAML when PyYAML is installed, and with
`safe_load` of `pyUltroid/fns/tools.py` when it is not. PyYAML is in no requirements file. This
reads every file with both and counts the keys that come out differently; with codes given, it
prints each differing key of those languages. It needs PyYAML to compare against.

The second reader passes every value to `eval`. The count at the end says what `eval` made of
the values in the files: text in quotes, something it could not evaluate (kept as it stands), or
anything else, which would be a value of whatever Python makes of the words in the file.
"""

import ast
import collections
import glob
import os
import sys

import yaml
from fixture import ROOT, stub_strings

stub_strings()

from pyUltroid.fns import tools  # noqa: E402

MISSING = "<no such key>"


def main():
    wanted = sys.argv[1:]
    total = differing = 0
    evaluated = collections.Counter()
    for path in sorted(glob.glob(os.path.join(ROOT, "strings", "strings", "*.yml"))):
        code = os.path.basename(path)[:-4]
        with open(path, encoding="UTF-8") as file:
            text = file.read()
        with open(path, encoding="UTF-8") as file:
            own = tools.safe_load(file)
        theirs = yaml.safe_load(text)
        keys = list(dict.fromkeys([*theirs, *own]))
        odd = [key for key in keys if own.get(key, MISSING) != theirs.get(key, MISSING)]
        total += len(keys)
        differing += len(odd)
        print(f"{code}: {len(theirs)} keys with PyYAML, {len(own)} with the fallback, {len(odd)} differ")
        for key in odd if code in wanted else []:
            print(f"  {key!r}\n    PyYAML:   {theirs.get(key, MISSING)!r}\n    fallback: {own.get(key, MISSING)!r}")
        for line in text.split("\n"):
            if ":" not in line and "-" not in line:
                continue
            value = line.split(":" if ":" in line else "-", 1)[1].strip()
            try:
                # This is what the reader does with every value; it is what is being measured.
                made = eval(value, vars(tools))  # noqa: S307  # nosec B307
            except Exception as error:  # noqa: BLE001
                evaluated[f"not evaluated ({type(error).__name__})"] += 1
                continue
            try:
                literal = ast.literal_eval(value) == made
            except Exception:  # noqa: BLE001
                literal = False
            evaluated[f"a literal ({type(made).__name__})" if literal else "evaluated to something else"] += 1
    print(f"all files: {differing} of {total} keys differ")
    print("what eval made of the values:", dict(evaluated))


if __name__ == "__main__":
    main()
