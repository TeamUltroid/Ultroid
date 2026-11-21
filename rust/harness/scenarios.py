"""Scenarios for the accessors of `pyUltroid/dB`: lists of steps for `dbaccess.run`.

`rust/dbaccess-rs/make_inputs.py` records a fixed set of them, `fuzz_dbaccess.py` keeps making
new ones. A scenario stays inside one or two modules and a handful of chats, users and words, so
that its steps meet: something is added, found, removed, read after a restart. Most arguments
are what the plugins pass (ids, words, replies); some are of the wrong type, to see how each
function fails.

Three kinds of value are left out because CPython itself gives no fixed answer for them: a set
of more than one member (its order follows the hash table, ADR-013), NaN (found by identity, not
by value) and text with a lone surrogate (it cannot cross the bridge).
"""

import copy

# Every function with the kind of each argument.
REPLY = ["msg", "media", "button"]
FUNCTIONS = {
    "afk_db": {"get_stuff": [], "add_afk": ["msg", "any", "media"], "is_afk": [], "del_afk": []},
    "antiflood_db": {"get_flood": [], "set_flood": ["chat", "any"], "get_flood_limit": ["chat"], "rem_flood": ["chat"]},
    "asstcmd_db": {"get_stuff": [], "add_cmd": ["word", *REPLY], "rem_cmd": ["word"], "cmd_reply": ["word"],
                   "list_cmds": []},
    "blacklist_chat_db": {"add_black_chat": ["chat"], "rem_black_chat": ["chat"]},
    "blacklist_db": {"get_stuff": [], "add_blacklist": ["chat", "word"], "rem_blacklist": ["chat", "word"],
                     "list_blacklist": ["chat"], "get_blacklist": ["chat"]},
    "botchat_db": {"get_stuff": [], "add_stuff": ["message", "any"], "get_who": ["message"],
                   "tag_add": ["message", "chat", "user"], "who_tag": ["message"]},
    "echo_db": {"get_stuff": [], "add_echo": ["chat", "user"], "rem_echo": ["chat", "user"],
                "check_echo": ["chat", "user"], "list_echo": ["chat"]},
    "filestore_db": {"get_stored": [], "store_msg": ["word", "any"], "list_all_stored_msgs": [],
                     "get_stored_msg": ["word"], "del_stored": ["word"]},
    "filter_db": {"get_stuff": [], "add_filter": ["chat", "word", *REPLY], "rem_filter": ["chat", "word"],
                  "rem_all_filter": ["chat"], "get_filter": ["chat"], "list_filter": ["chat"]},
    "forcesub_db": {"get_chats": [], "add_forcesub": ["chat", "any"], "get_forcesetting": ["chat"],
                    "rem_forcesub": ["chat"]},
    "gban_mute_db": {"list_gbanned": [], "gban": ["user", "msg"], "ungban": ["user"], "is_gbanned": ["user"],
                     "gmute": ["user"], "ungmute": ["user"], "is_gmuted": ["user"], "list_gmuted": []},
    "greetings_db": {"get_stuff": ["key"], "add_welcome": ["chat", *REPLY], "get_welcome": ["chat"],
                     "delete_welcome": ["chat"], "add_goodbye": ["chat", *REPLY], "get_goodbye": ["chat"],
                     "delete_goodbye": ["chat"], "add_thanks": ["chat"], "remove_thanks": ["chat"],
                     "must_thank": ["chat"]},
    "mute_db": {"get_muted": [], "mute": ["chat", "user"], "unmute": ["chat", "user"], "is_muted": ["chat", "user"]},
    "notes_db": {"get_stuff": [], "add_note": ["chat", "word", *REPLY], "rem_note": ["chat", "word"],
                 "rem_all_note": ["chat"], "get_notes": ["chat", "word"], "list_note": ["chat"]},
    "nsfw_db": {"get_stuff": ["key"], "nsfw_chat": ["chat", "any"], "rem_nsfw": ["chat"], "is_nsfw": ["chat"],
                "profan_chat": ["chat", "any"], "rem_profan": ["chat"], "is_profan": ["chat"]},
    "snips_db": {"get_all_snips": [], "add_snip": ["word", *REPLY], "rem_snip": ["word"], "get_snips": ["word"],
                 "list_snip": []},
    "vc_sudos": {"get_vcsudos": [], "is_vcsudo": ["user"], "add_vcsudo": ["user"], "del_vcsudo": ["user"]},
    "warn_db": {"get_stuff": [], "add_warn": ["chat", "user", "any", "msg"], "warns": ["chat", "user"],
                "reset_warn": ["chat", "user"]},
    "KeyManager": {"get": ["key", "cast"], "count": ["key", "cast"], "get_child": ["key", "cast", "index"],
                   "add": ["key", "cast", "item"], "remove": ["key", "cast", "item"],
                   "contains": ["key", "cast", "item"]},
    "udB": {"get_key": ["key"], "set_key": ["key", "stored"], "del_key": ["key"], "rename": ["key", "key"],
            "keys": [], "re_cache": []},
}
# The database keys each module keeps its state under.
KEYS = {
    "afk_db": ["AFK_DB"], "antiflood_db": ["ANTIFLOOD"], "asstcmd_db": ["ASST_CMDS"],
    "blacklist_chat_db": ["BLACKLIST_CHATS"], "blacklist_db": ["BLACKLIST_DB"], "botchat_db": ["BOTCHAT"],
    "echo_db": ["ECHO"], "filestore_db": ["FILE_STORE"], "filter_db": ["FILTERS"], "forcesub_db": ["FORCESUB"],
    "gban_mute_db": ["GBAN", "GMUTE"], "greetings_db": ["WELCOME", "GOODBYE", "THANK_MEMBERS"], "mute_db": ["MUTE"],
    "notes_db": ["NOTE"], "nsfw_db": ["NSFW", "PROFANITY"], "snips_db": ["SNIP"], "vc_sudos": ["VC_SUDOS"],
    "warn_db": ["WARNS"], "KeyManager": ["PMPERMIT", "BOT_USERS", "NIGHT_CHATS"], "udB": ["LANGUAGE", "HNDLR", "K"],
}
MODULES = [name for name in FUNCTIONS if name not in ("KeyManager", "udB")]
# The functions that put something in: a scenario often starts with a few of them.
ADDING = ("add", "set_", "store_", "mute", "gban", "gmute", "nsfw_chat", "profan_chat", "tag_add")
ADDERS = {module: [name for name in functions if name.startswith(ADDING)] for module, functions in FUNCTIONS.items()}

CHATS = [-1001234567890, -100123, 777, 12345]
USERS = [111, 222, 333, 1]
ODD_IDS = [
    "-100123", "777", "111", " 42 ", "4_2", "١٢٣", "chat", "", "0x10", "+5", "5\x1f", "\xa0222", "1__1", "9" * 30,
    777.0, 111.0, 1.5, -0.0, 1e300, float("inf"), True, False, None, 0, 2**64, -(2**70), (1, 2), (), [1], {"a": 1},
    b"12", b" 111 ", b"x", b"",
]  # fmt: skip
WORDS = ["spam", "eggs", "ham", "hello world", "TAG", "button", "msg", "hi"]
ODD_WORDS = [
    "", "  two  words ", "é", "😀 ok", "a\nb", "t\tb", "fs\x1csep", "nbsp\xa0x", "ideo　sp", "#tag", "$snip",
    "it's", 'q"q', "`tick`", "\\back", "\x01ctl", "🫨", "x" * 80, 5, 0, None, 1.5, True, b"by tes", b"", ["l"],
    ("t",), {"d": 1},
]  # fmt: skip
MESSAGES = [1001, 1002, "TAG"]
MSGS = ["hi", "", None, "multi\nline", "it's", 'say "hi"', "back\\slash", "é 日本 😀", "**bold** `code`", 0, 5]
MEDIA = [None, "BQACAgUAAx0CVqQ", ""]
BUTTONS = [None, [[["Docs", "https://ultroid.tech"]]], [], [[["a", "b"], ["c", "d"]], [["e", "f"]]], "x"]
ANY = [
    None, True, False, 0, 1, -3, 5, 2**64, 1.5, -0.0, float("inf"), "", "text", "ban", "5", "[1, 2]", b"ab",
    [], [1, 2], ["a", [1]], (), (1, "a"), {}, {"a": 1}, {1: [2]}, {(1, 2): "t"}, set(), {1}, {"x"},
]  # fmt: skip
# What `udB.set_key` is given: no sets, since a set at the top of a key can grow and be listed.
STORED = [value for value in ANY if not isinstance(value, set)] + [
    "+919876543210", "007", "'5'", "{'a': 1}", "1,2", "hello", "True", "en", ".", "1e5", "[inf]",
]
ODD_KEYS = ["", "weird key", "ключ", 5, None, 1.5, ["K"], b"K"]
CASTS = ["list", "list", "list", "list", None, None, "dict", "LIST", "", 5, False, []]
INDEXES = [0, 1, -1, 2, 5, -9, True, "a", "0", 1.0, None, 2**70, [0]]
# Stored text as another program, another version or a careless `.setdb` could leave it.
RAW = [
    "", "0", "5", "1.5", "True", "None", "hello", "007", "+5", "'text'", "'ab'", "'abcd'", "b'bytes'", "b'abcd'",
    "[]", "{}", "()", "set()", "...", "[inf]", "{1: nan}", "[1, 2, 3]", "(1, 2)", "((1, 2),)", "{1: 2}",
    "[[1, 2]]", "[[[1, 2]]]", "[[], {}]", "{'TAG': 5}", "{'TAG': {}}", "{'TAG': [1]}", "{'TAG': {1001: [777, 111]}}",
    "{1001: 111, 1002: 0}", "{777: 5}", "{777: 0}", "{777: []}", "{777: [111]}", "{777: [111, '111', 111.0]}",
    "{777: (111, 222)}", "{777: 'spam eggs'}", "{777: b'spam'}", "{777: {111: [3, 'r']}}", "{777: {111: 'xy'}}",
    "{777: {111: [3]}}", "{777: [[3, 'r']]}", "{'777': ['spam']}", "{777.0: ['spam', 'a b']}", "{True: ['x']}",
    "{777: {'spam': {'msg': 'm', 'media': None, 'button': None}}}", "{777: {'spam': 5, 'eggs': 0}}",
    "{777: ['spam', 5, None, ('t',), b'b', 1.5]}", "{-100123: 'ban', 777: 0, 12345: True}",
    "[111, 222]", "[111, '111', 111.0, True]", "[[111], (222,)]", "'111'", "(111, 222)", "{111: 'reason'}",
    "{111: ''}", "{111: 0, 222: None}",
    "{'hi': {'msg': 'm', 'media': None, 'button': [[['a', 'b']]]}, 'button': {'msg': 1}}",
    "{'hi': {'msg': 'm', 'media': 5}}", "{'hi': 'abc'}", "{'hi': ['m', 'x', 'b']}", "{'hi': 7}",
    "{'spam': {'msg': 'm', 'media': None, 'button': None}}", "{'spam': 5, 'eggs': 'x', 5: 5, None: 1, (1, 2): 3}",
    "{777: {'welcome': 'w', 'media': None, 'button': None}}", "{777: True, -100123: False}",
    # Text with a lone surrogate: Python can hold it, no backend can store it.
    "'\\ud83d'", "{777: ['\\ud83d', 'spam']}", "{'\\ud83d': {'msg': '\\udc00', 'media': None, 'button': None}}",
    "['\\ud83d']",
]  # fmt: skip
AFK_TIMES = [
    "Jan 01 2000 12:00:00AM", "Dec 31 1999 11:59:59PM", "Jan 02 2000 01:01:01AM", "Feb 29 2000 12:30:00PM",
    "jan 1 2000 1:2:3am", "JAN  5\t2000 08:01:04Pm", "Jan 05 2٠٠٠ 08:0١:٤AM", "Nov 2٥ 2026 08:51:44PM",
    "Jan 01 0001 12:00:00AM", "Dec 31 9999 11:59:59PM", "", "Jan 01 2000", "Jan 01 2000 12:00:00", "Jan 01 2000 12:00:00 AM",
    " Jan 01 2000 12:00:00AM", "Jan 01 2000 12:00:00AM ", "Jan 32 2000 12:00:00AM", "Feb 30 2000 12:00:00AM",
    "Feb 29 2001 12:00:00AM", "Jan 00 2000 12:00:00AM", "Jan 01 0000 12:00:00AM", "Jan 01 00 12:00:00AM",
    "Jan 01 20000 12:00:00AM", "Jan 01 2000 13:00:00AM", "Jan 01 2000 00:00:00AM", "Jan 01 2000 12:60:00AM",
    "Jan 01 2000 12:00:61AM", "Jan 01 2000 12:00:60AM", "January 01 2000 12:00:00AM", "01 Jan 2000 12:00:00AM",
    "Jan ٥ 2000 12:00:00AM", "Jan 0٥ 2000 12:00:00AM", "Jan 01 2000 0٨:00:00AM", "ſep 01 2000 12:00:00AM",
    "Sep 01 2000 12:00:00ＡM", "Jan\x1c1\x1f2000\x1d1:1:1pm", "Jan 01 2000 12:00:00XM", "Jan 01 2000 12-00-00AM",
]  # fmt: skip
# Seconds after 2000-01-01: ordinary moments, the first and last second a `datetime` can hold, and one past each.
FIRST, LAST = -63082281600, 252455615999
CLOCKS = [0, 1, 59, 3600, 86399, 86400, 90061, 31622400, 10**9, 4 * 10**9, -1, -86400, -31536000000, FIRST, LAST,
          FIRST - 1, LAST + 1, True, 1.5, "5", None, 2**70]  # fmt: skip
CASTS_USED = ["list", "list", "list", None]
POOLS = {"item": (USERS + CHATS, ANY), "msg": (MSGS, ODD_WORDS), "media": (MEDIA, ANY), "button": (BUTTONS, ANY), "any": (ANY, ANY),
         "chat": (CHATS, ODD_IDS), "user": (USERS, ODD_IDS), "message": (MESSAGES, ODD_IDS),
         "word": (WORDS, ODD_WORDS), "stored": (STORED, STORED), "index": (INDEXES, INDEXES), "cast": (CASTS_USED, CASTS)}


def pick(rng, pool):
    return copy.deepcopy(rng.choice(pool))


def argument(rng, kind, module, odd, few):
    if kind == "key":
        return pick(rng, ODD_KEYS + sum(KEYS.values(), [])) if rng.random() < odd else pick(rng, KEYS[module])
    usual, unusual = POOLS[kind]
    return pick(rng, unusual if rng.random() < odd else few.get(kind, usual))


def call(rng, module, odd=0.15, few=None, function=None):
    """One call into `module`, now and then with an argument too few or too many. `few` narrows
    the usual chats, users and words to the handful a scenario is about."""
    function = function or rng.choice(list(FUNCTIONS[module]))
    args = [argument(rng, kind, module, odd, few or {}) for kind in FUNCTIONS[module][function]]
    if module == "botchat_db" and function == "add_stuff" and isinstance(args[1], set):
        # A set stored under `TAG` grows with every `tag_add`, and then has no order to compare.
        args[1] = set()
    if rng.random() < 0.02:
        args = args[:-1] if args and rng.random() < 0.5 else args + [pick(rng, ANY)]
    return [f"{module}.{function}", *args]


def afk_text(rng):
    time = rng.choice(AFK_TIMES)
    shape = rng.randrange(8)
    if shape == 0:
        return repr(["m", None, None])
    if shape == 1:
        return repr(rng.choice([time, {3: time, 0: "a", 1: "b"}, ("m", "t", None, time), ["m", "t", None, 5]]))
    return repr(["brb", rng.choice([None, "pic"]), None, time])


def scenario(rng, modules, length=None, odd=0.15):
    """Steps that stay inside `modules` and a few chats, users and words, with restarts, a moving
    clock and text changed in the store. Two in three start by putting something in."""
    # Two of each, the first twice as likely as the second.
    few = {kind: [first, first, second] for kind, (first, second) in {
        "chat": rng.sample(CHATS, 2), "user": rng.sample(USERS, 2), "word": rng.sample(WORDS, 2),
        "message": rng.sample(MESSAGES, 2), "item": rng.sample(USERS, 2)}.items()}  # fmt: skip
    few.update(index=[0, 1, -1], cast=[rng.choice(CASTS_USED)])
    steps = []
    if rng.random() < 0.67:
        for _ in range(rng.randrange(2, 5)):
            module = rng.choice(modules)
            steps.append(call(rng, module, odd / 5, few, rng.choice(ADDERS[module])))
    for _ in range(length or rng.randrange(4, 13)):
        module = rng.choice(modules)
        chance = rng.random()
        if chance < 0.08:
            steps.append(["$restart"])
        elif chance < 0.13:
            key = rng.choice(KEYS[module])
            steps.append(["$raw", key, afk_text(rng) if key == "AFK_DB" and rng.random() < 0.8 else rng.choice(RAW)])
        elif chance < 0.18:
            steps.append(call(rng, "udB" if rng.random() < 0.7 else "KeyManager", odd, few))
            if steps[-1][1:] and rng.random() < 0.8:
                steps[-1][1] = rng.choice(KEYS[module])
        elif chance < 0.22 or (module == "afk_db" and chance < 0.40):
            steps.append(["$clock", pick(rng, CLOCKS)])
        else:
            steps.append(call(rng, module, odd, few))
    return steps


# One plain walk through each module: what the plugins do with it, in order.
STORIES = [
    [["afk_db.is_afk"], ["afk_db.add_afk", "brb", None, None], ["$clock", 90061], ["afk_db.is_afk"], ["$restart"],
     ["afk_db.get_stuff"], ["afk_db.is_afk"], ["afk_db.del_afk"], ["afk_db.is_afk"], ["afk_db.get_stuff"]],
    [["antiflood_db.set_flood", -100123, 5], ["antiflood_db.get_flood_limit", -100123], ["$restart"],
     ["antiflood_db.get_flood"], ["antiflood_db.rem_flood", -100123], ["antiflood_db.rem_flood", -100123],
     ["antiflood_db.get_flood_limit", -100123]],
    [["asstcmd_db.add_cmd", "hi", "hello", None, None], ["asstcmd_db.cmd_reply", "hi"],
     ["asstcmd_db.add_cmd", "button", "b", "m", [[["a", "b"]]]], ["asstcmd_db.cmd_reply", "hi"],
     ["asstcmd_db.cmd_reply", "button"], ["asstcmd_db.list_cmds"], ["$restart"], ["asstcmd_db.rem_cmd", "hi"],
     ["asstcmd_db.rem_cmd", "hi"], ["asstcmd_db.cmd_reply", "hi"], ["asstcmd_db.get_stuff"]],
    [["blacklist_chat_db.add_black_chat", -100123], ["blacklist_chat_db.add_black_chat", -100123],
     ["blacklist_chat_db.add_black_chat", 777], ["$restart"], ["blacklist_chat_db.rem_black_chat", -100123],
     ["blacklist_chat_db.rem_black_chat", -100123], ["udB.get_key", "BLACKLIST_CHATS"]],
    [["blacklist_db.add_blacklist", 777, "spam eggs"], ["blacklist_db.add_blacklist", 777, "eggs  ham spam"],
     ["blacklist_db.list_blacklist", 777], ["blacklist_db.get_blacklist", 777], ["$restart"],
     ["blacklist_db.rem_blacklist", 777, "ham"], ["blacklist_db.rem_blacklist", 777, "ham"],
     ["blacklist_db.rem_blacklist", 777, "spam eggs"], ["blacklist_db.rem_blacklist", 777, "eggs"],
     ["blacklist_db.list_blacklist", 777], ["blacklist_db.get_blacklist", 777], ["blacklist_db.get_stuff"]],
    [["botchat_db.add_stuff", 1001, 111], ["botchat_db.get_who", 1001], ["botchat_db.who_tag", 1001],
     ["botchat_db.tag_add", 1001, 777, 111], ["botchat_db.tag_add", 1002, 777, 222], ["botchat_db.who_tag", 1002],
     ["$restart"], ["botchat_db.get_who", 1002], ["botchat_db.who_tag", 1001], ["botchat_db.get_stuff"]],
    [["echo_db.add_echo", 777, 111], ["echo_db.add_echo", "777", "222"], ["echo_db.add_echo", 777, 111],
     ["echo_db.check_echo", 777, "222"], ["echo_db.check_echo", 777, 333], ["echo_db.list_echo", 777], ["$restart"],
     ["echo_db.rem_echo", 777, 111], ["echo_db.rem_echo", 777, "222"], ["echo_db.rem_echo", 12345, 111],
     ["echo_db.list_echo", 777], ["echo_db.get_stuff"]],
    [["filestore_db.store_msg", "abc", 1001], ["filestore_db.store_msg", "def", 1002],
     ["filestore_db.list_all_stored_msgs"], ["filestore_db.get_stored_msg", "abc"], ["$restart"],
     ["filestore_db.del_stored", "abc"], ["filestore_db.del_stored", "abc"], ["filestore_db.get_stored_msg", "abc"],
     ["filestore_db.get_stored"]],
    [["filter_db.add_filter", 777, "spam", "no spam", None, None], ["filter_db.add_filter", 777, "hi", "hello", "m", []],
     ["filter_db.list_filter", 777], ["filter_db.get_filter", 777], ["$restart"], ["filter_db.rem_filter", 777, "hi"],
     ["filter_db.rem_filter", 777, "hi"], ["filter_db.rem_all_filter", 777], ["filter_db.rem_all_filter", 777],
     ["filter_db.list_filter", 777], ["filter_db.get_stuff"]],
    [["forcesub_db.add_forcesub", 777, -100123], ["forcesub_db.get_forcesetting", 777], ["$restart"],
     ["forcesub_db.get_chats"], ["forcesub_db.rem_forcesub", 777], ["forcesub_db.rem_forcesub", 777],
     ["forcesub_db.get_forcesetting", 777]],
    [["gban_mute_db.gban", 111, "spam"], ["gban_mute_db.gban", "222", ""], ["gban_mute_db.is_gbanned", 111],
     ["gban_mute_db.is_gbanned", "222"], ["gban_mute_db.list_gbanned"], ["$restart"], ["gban_mute_db.ungban", 111],
     ["gban_mute_db.ungban", 111], ["gban_mute_db.is_gbanned", 111], ["gban_mute_db.gmute", 111],
     ["gban_mute_db.gmute", "111"], ["gban_mute_db.is_gmuted", 111], ["gban_mute_db.list_gmuted"],
     ["gban_mute_db.ungmute", "111"], ["gban_mute_db.ungmute", 111], ["gban_mute_db.ungmute", 111],
     ["gban_mute_db.ungmute", 111], ["gban_mute_db.is_gmuted", "111"]],
    [["greetings_db.add_welcome", 777, "welcome", None, None], ["greetings_db.get_welcome", 777],
     ["greetings_db.add_goodbye", 777, "bye", "m", [[["a", "b"]]]], ["greetings_db.get_goodbye", 777],
     ["greetings_db.add_thanks", 777], ["greetings_db.must_thank", 777], ["$restart"],
     ["greetings_db.get_stuff", "WELCOME"], ["greetings_db.get_stuff"], ["greetings_db.delete_welcome", 777],
     ["greetings_db.delete_welcome", 777], ["greetings_db.delete_goodbye", 777], ["greetings_db.remove_thanks", 777],
     ["greetings_db.remove_thanks", 777], ["greetings_db.get_welcome", 777], ["greetings_db.must_thank", 777]],
    [["mute_db.mute", 777, 111], ["mute_db.mute", 777, 111], ["mute_db.mute", 777, 222], ["mute_db.is_muted", 777, 111],
     ["$restart"], ["mute_db.unmute", 777, 111], ["mute_db.unmute", 777, 111], ["mute_db.unmute", 12345, 111],
     ["mute_db.is_muted", 777, 111], ["mute_db.is_muted", 12345, 111], ["mute_db.get_muted"]],
    [["notes_db.add_note", 777, "rules", "be kind", None, None], ["notes_db.add_note", "777", "faq", "read", "m", []],
     ["notes_db.get_notes", 777, "rules"], ["notes_db.list_note", 777], ["notes_db.list_note", "777"], ["$restart"],
     ["notes_db.rem_note", "777", "faq"], ["notes_db.rem_note", 777, "faq"], ["notes_db.get_notes", 777, "faq"],
     ["notes_db.rem_all_note", 777], ["notes_db.rem_all_note", 777], ["notes_db.list_note", 777],
     ["notes_db.get_stuff"]],
    [["nsfw_db.nsfw_chat", 777, "ban"], ["nsfw_db.is_nsfw", 777], ["nsfw_db.profan_chat", 777, "mute"],
     ["nsfw_db.is_profan", 777], ["$restart"], ["nsfw_db.get_stuff"], ["nsfw_db.get_stuff", "PROFANITY"],
     ["nsfw_db.rem_nsfw", 777], ["nsfw_db.rem_nsfw", 777], ["nsfw_db.rem_profan", 777], ["nsfw_db.is_nsfw", 777],
     ["nsfw_db.is_profan", 777]],
    [["snips_db.add_snip", "hi", "hello", None, None], ["snips_db.add_snip", "bye", "ciao", "m", [[["a", "b"]]]],
     ["snips_db.get_snips", "hi"], ["snips_db.list_snip"], ["$restart"], ["snips_db.rem_snip", "hi"],
     ["snips_db.rem_snip", "hi"], ["snips_db.get_snips", "hi"], ["snips_db.list_snip"], ["snips_db.get_all_snips"]],
    [["vc_sudos.add_vcsudo", 111], ["vc_sudos.add_vcsudo", 111], ["vc_sudos.is_vcsudo", 111], ["$restart"],
     ["vc_sudos.del_vcsudo", 111], ["vc_sudos.is_vcsudo", 111], ["vc_sudos.del_vcsudo", 111],
     ["vc_sudos.del_vcsudo", 111], ["vc_sudos.get_vcsudos"]],
    [["warn_db.warns", 777, 111], ["warn_db.add_warn", 777, 111, 1, "spam"], ["warn_db.add_warn", 777, 222, 1, None],
     ["warn_db.add_warn", 777, 111, 2, "again"], ["warn_db.warns", 777, 111], ["$restart"],
     ["warn_db.reset_warn", 777, 111], ["warn_db.reset_warn", 777, 111], ["warn_db.warns", 777, 111],
     ["warn_db.warns", 777, 222], ["warn_db.get_stuff"]],
    [["KeyManager.get", "PMPERMIT", "list"], ["KeyManager.add", "PMPERMIT", "list", 111],
     ["KeyManager.add", "PMPERMIT", "list", 111], ["KeyManager.add", "PMPERMIT", "list", 222],
     ["KeyManager.contains", "PMPERMIT", "list", 222], ["KeyManager.count", "PMPERMIT", "list"],
     ["KeyManager.get_child", "PMPERMIT", "list", -1], ["$restart"], ["KeyManager.remove", "PMPERMIT", "list", 111],
     ["KeyManager.remove", "PMPERMIT", "list", 111], ["KeyManager.get", "PMPERMIT", "list"],
     ["KeyManager.get", "PMPERMIT", None], ["KeyManager.add", "K", None, {"a": 1}], ["KeyManager.add", "K", None, {"b": 2}],
     ["KeyManager.add", "K", None, 5], ["KeyManager.remove", "K", None, "a"], ["KeyManager.get_child", "K", None, "b"],
     ["udB.set_key", "LONE", 5], ["KeyManager.add", "LONE", "list", 6], ["KeyManager.get", "LONE", "list"]],
    [["udB.set_key", "PHONE", "+919876543210"], ["udB.get_key", "PHONE"], ["udB.set_key", "HNDLR", "."],
     ["udB.set_key", "IDS", [1, "a", None]], ["udB.keys"], ["$restart"], ["udB.get_key", "IDS"],
     ["udB.rename", "IDS", "NEW"], ["udB.rename", "IDS", "NEW"], ["udB.get_key", "NEW"], ["$raw", "Q", "'5'"],
     ["udB.get_key", "Q"], ["udB.rename", "Q", "R"], ["udB.get_key", "R"], ["udB.del_key", "PHONE"],
     ["udB.del_key", "PHONE"], ["udB.get_key", "PHONE"], ["udB.re_cache"], ["udB.keys"], ["udB.get_key", ""],
     ["udB.set_key", "", 1], ["udB.get_key", ""], ["$raw", "LONE", "'\\ud83d'"], ["udB.get_key", "LONE"],
     ["udB.rename", "LONE", "MOVED"], ["udB.get_key", "MOVED"], ["udB.keys"], ["$restart"], ["udB.get_key", "MOVED"]],
    # A scenario that makes no sense, step by step.
    [[], 5, None, "udB.keys", [5], [None, 1], ["nope"], ["nope.nothing"], ["udB"], ["udB.nothing"], ["udB.keys", 1],
     ["udB.get_key"], ["$restart", 1], ["$restart."], ["$restart.x"], ["$raw", "K"], ["$raw", "K", 5], ["$raw", 5, "x"],
     ["$clock"], ["$clock", "x"], ["$clock", 10**30], ["KeyManager.get", "K"], ["KeyManager.get", 5, "list"],
     ["KeyManager.get", "K", "set"], ["KeyManager.get", "K", []], ["KeyManager.add", "K", "list"],
     ["KeyManager.nothing", "K", "list"], ["afk_db.dt"], ["afk_db.udB"], ["greetings_db.get_stuff", 5],
     ["greetings_db.get_stuff", "A", "B"], ["nsfw_db.get_stuff", None], {"a": 1}, ["udB.keys."], [["udB.keys"]]],
]


def recorded(rng):
    """The fixed set of scenarios whose results are recorded."""
    yield from copy.deepcopy(STORIES)
    for module in MODULES:
        for _ in range(26):
            yield scenario(rng, [module])
    for _ in range(40):
        yield scenario(rng, ["afk_db"], odd=0.1)
    for _ in range(70):
        yield scenario(rng, ["KeyManager"])
    for _ in range(60):
        yield scenario(rng, ["udB"], odd=0.3)
    for _ in range(90):
        yield scenario(rng, rng.sample(MODULES, 2) + ["KeyManager"])


def encoded(value):
    """A value as the recorder's input file writes it: JSON, with marks for what JSON lacks."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return value if abs(value) <= 2**53 else {"$int": str(value)}
    if isinstance(value, float):
        if value in (float("inf"), float("-inf")):
            return {"$num": "Infinity" if value > 0 else "-Infinity"}
        if value == 0 and str(value) == "-0.0":
            return {"$num": "-0"}
        return {"$float": repr(value)} if value.is_integer() else value
    if isinstance(value, bytes):
        return {"$bytes": list(value)}
    if isinstance(value, list):
        return [encoded(member) for member in value]
    if isinstance(value, tuple):
        return {"$tuple": [encoded(member) for member in value]}
    if isinstance(value, set):
        return {"$set": [encoded(member) for member in value]}
    if all(isinstance(key, str) and not key.startswith("$") for key in value):
        return {key: encoded(member) for key, member in value.items()}
    return {"$dict": [[encoded(key), encoded(member)] for key, member in value.items()]}
