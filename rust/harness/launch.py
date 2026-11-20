"""Which clients `multi_client.py` starts, as data in and data out (ADR-002, ADR-007).

`multi_client.py` is a script, not a module of functions: it reads the environment, starts
`python3 -m pyUltroid ...` once for every configured client and waits for them all. `plan` runs
the script itself, with the environment it is given in place of the real one and with a
`subprocess.Popen` that notes what it was asked to start and starts nothing.
"""

import os
import runpy
import subprocess
import sys

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "multi_client.py")


class _Noted:
    """Stands in for a started process."""

    started = []

    def __init__(self, command):
        self.waited = False
        _Noted.started.append((list(command), self))

    def wait(self):
        self.waited = True


def plan(environment: dict) -> list:
    """What the script does with these environment variables: `["start", arguments, ...]` with
    the arguments of each client it starts, in order and without the interpreter in front, or
    `["exit", message]`."""
    environment = {"" + name: "" + value for name, value in environment.items()}
    real = os.environ, subprocess.Popen
    os.environ, subprocess.Popen, _Noted.started = environment, _Noted, []
    try:
        runpy.run_path(SCRIPT, run_name="__main__")
    except SystemExit as left:
        return ["exit", left.code]
    finally:
        os.environ, subprocess.Popen = real
    # The interpreter is this machine's; every client must have been started with it and waited
    # for, or the report says so.
    report = ["start"]
    for command, process in _Noted.started:
        fine = command[0] == sys.executable and process.waited
        report.append(command[1:] if fine else ["not as expected", command, process.waited])
    return report
