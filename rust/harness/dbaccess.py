"""The accessors of `pyUltroid/dB`, run as scenarios over a database in memory (ADR-007).

The accessors keep their state in the database, so one call proves little: what matters is what
a later call sees, and what is left after a restart. A scenario is a list of steps, run in order
on an empty database. A step is a list: a name, then the arguments.

    ["blacklist_db.add_blacklist", -1001, "spam"]    any function of a `pyUltroid/dB` module
    ["KeyManager.add", "PMPERMIT", "list", 777]      a method; key and cast (None or "list") first
    ["udB.get_key", "LANGUAGE"]                      get_key, set_key, del_key, rename, keys, re_cache
    ["$restart"]                                     the cache is lost, the stored text stays
    ["$raw", "NOTE", "{1: 2}"]                       stored text changed behind the cache's back
    ["$clock", 86400]                                the time is that many seconds after 2000-01-01

Database keys are text here. Nothing in this file raises on purpose: a step that makes no sense
fails the way Python fails on it, and that failure is its result.
"""

import inspect
import operator
from datetime import datetime, timedelta

from fixture import canon, has_set_order, udB

from pyUltroid.dB import (  # noqa: E402  (the fixture has to load first)
    afk_db,
    antiflood_db,
    asstcmd_db,
    blacklist_chat_db,
    blacklist_db,
    botchat_db,
    echo_db,
    filestore_db,
    filter_db,
    forcesub_db,
    gban_mute_db,
    greetings_db,
    mute_db,
    notes_db,
    nsfw_db,
    snips_db,
    vc_sudos,
    warn_db,
)
from pyUltroid.dB.base import KeyManager

BASE = datetime(2000, 1, 1)
CASTS = {None: None, "list": list}


class _Clock(datetime):
    """`datetime` whose `now()` is whatever the scenario last set."""

    moment = BASE

    @classmethod
    def now(cls, tz=None):
        return cls.moment


afk_db.dt = _Clock


def _restart():
    udB.restart()


def _raw(key, text):
    udB.raw["" + key] = "" + text
    udB._cache.pop(key, None)


def _clock(seconds):
    _Clock.moment = BASE + timedelta(seconds=operator.index(seconds))


def _method(name):
    return lambda key, cast, *rest: getattr(KeyManager("" + key, cast=CASTS[cast]), name)(*rest)


STEPS = {"$restart": {"": _restart}, "$raw": {"": _raw}, "$clock": {"": _clock}}
STEPS["udB"] = {
    "get_key": lambda key: udB.get_key("" + key),
    "set_key": lambda key, value: udB.set_key("" + key, value),
    "del_key": lambda key: udB.del_key("" + key),
    "rename": lambda old, new: udB.rename("" + old, "" + new),
    "keys": lambda: udB.keys(),
    "re_cache": lambda: udB.re_cache(),
}
STEPS["KeyManager"] = {name: _method(name) for name in ("get", "get_child", "count", "add", "remove", "contains")}
for module in (afk_db, antiflood_db, asstcmd_db, blacklist_chat_db, blacklist_db, botchat_db, echo_db,
               filestore_db, filter_db, forcesub_db, gban_mute_db, greetings_db, mute_db, notes_db, nsfw_db,
               snips_db, vc_sudos, warn_db):  # fmt: skip
    name = module.__name__.rpartition(".")[2]
    STEPS[name] = {
        function: found
        for function, found in vars(module).items()
        if inspect.isfunction(found) and found.__module__ == module.__name__
    }
# A view of the keys cannot cross the bridge; a list of them can.
STEPS["asstcmd_db"]["list_cmds"] = lambda: list(asstcmd_db.list_cmds())
# These two may be given the name of the key to read.
STEPS["greetings_db"]["get_stuff"] = lambda *key: greetings_db.get_stuff(*["" + name for name in key])
STEPS["nsfw_db"]["get_stuff"] = lambda *key: nsfw_db.get_stuff(*["" + name for name in key])


def _step(one):
    try:
        name, *args = one + []
        owner, _, function = ("" + name).partition(".")
        value = STEPS[owner][function](*args)
        return ["ok", type(value).__name__, canon(value)]
    except Exception as error:
        return ["error", type(error).__name__]


def _stored(text):
    """Stored text as it is, unless it holds a set whose order CPython does not fix (ADR-013)."""
    value = udB._get_data(data=text)
    return canon(value) if has_set_order(value) else text


def run(steps: list) -> list:
    """The result of every step, then the text the database holds at the end."""
    udB.wipe()
    _Clock.moment = BASE
    results = [_step(one) for one in steps + []]
    return results + [["stored"] + [[key, _stored(text)] for key, text in udB.raw.items()]]
