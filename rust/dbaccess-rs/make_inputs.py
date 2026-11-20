"""Builds inputs.jsonl for the accessors of pyUltroid/dB.

    python3 make_inputs.py > inputs.jsonl

One scenario per line: a plain walk through each module, then generated scenarios that stay
inside one module, then KeyManager, the database itself, and mixes. The generator is
`rust/harness/scenarios.py`; it is seeded, so a rerun gives the same file.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "harness"))

import scenarios  # noqa: E402

for steps in scenarios.recorded(random.Random(20261120)):
    print(json.dumps({"fn": "run", "args": [scenarios.encoded(steps)]}, ensure_ascii=False))
