"""Loads the parts of Ultroid that refuse to import outside a running bot (ADR-007).

`pyUltroid.dB` raises unless Ultroid runs as a module, and the database classes read their
settings on import. This brings them up with nothing connected: no Telegram client, no network,
and a database that lives in a dict. The original modules are imported as they are.
"""

import logging
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Settings that would make the import reach for a real database driver.
for _name in ("REDIS_URI", "REDIS_URL", "REDISHOST", "MONGO_URI", "DATABASE_URL"):
    os.environ.pop(_name, None)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# `configs.Var` reads its settings from argv when there is more than one argument, and the
# package boots for real when its own name is in argv. Neither may happen here.
_argv = sys.argv
sys.argv = ["harness"]
try:
    import pyUltroid
    import pyUltroid.startup  # still a function library here: no log file, no prompts

    # The fallback store is `localdb`; the original pip-installs it on import when it is missing.
    sys.modules.setdefault("localdb", types.ModuleType("localdb")).Database = object
    # `startup` re-exports the flag it saw on import, so both copies are set. Its logger exists
    # only in a running bot, and the database classes name it in their signatures.
    pyUltroid.run_as_module = pyUltroid.startup.run_as_module = True
    pyUltroid.startup.LOGS = logging.getLogger("pyUltLogs")
    from pyUltroid.startup import _database
finally:
    sys.argv = _argv


class MemoryDB(_database._BaseDatabase):
    """The original's cache and value handling over a dict of text, which is what Redis holds."""

    name = "Memory"

    def __init__(self):
        self.raw = {}
        super().__init__()

    def get(self, key):
        return self.raw.get(key)

    def set(self, key, value):
        # A backend holds bytes. Text that cannot be encoded is refused by every driver, with
        # the error this raises.
        for text in (key, value):
            text.encode("utf-8")
        self.raw[key] = value
        return True

    def delete(self, key):
        return int(self.raw.pop(key, None) is not None)

    def keys(self):
        return list(self.raw)

    def restart(self):
        """What a restart leaves: the stored text, and an empty cache."""
        self._cache.clear()

    def wipe(self):
        self.raw.clear()
        self._cache.clear()


udB = MemoryDB()
pyUltroid.udB = udB


def canon(value):
    """`repr(value)`, except that a set lists its items sorted: CPython's own order follows
    its hash table, which a port cannot reproduce."""
    if isinstance(value, (set, frozenset)):
        return "{" + ", ".join(sorted(canon(x) for x in value)) + "}" if value else "set()"
    if isinstance(value, list):
        return "[" + ", ".join(canon(x) for x in value) + "]"
    if isinstance(value, tuple):
        return "(" + ", ".join(canon(x) for x in value) + ("," if len(value) == 1 else "") + ")"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{canon(k)}: {canon(x)}" for k, x in value.items()) + "}"
    return repr(value)


def describe(value):
    return [type(value).__name__, canon(value)]


def has_set_order(value):
    """Whether printing `value` depends on the order CPython happens to iterate a set in."""
    if isinstance(value, dict):
        return any(has_set_order(k) or has_set_order(x) for k, x in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return isinstance(value, (set, frozenset)) and len(value) > 1 or any(map(has_set_order, value))
    return False
