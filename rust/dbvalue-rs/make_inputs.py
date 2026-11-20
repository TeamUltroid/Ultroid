"""Builds inputs.jsonl for the database value format.

    python3 make_inputs.py > inputs.jsonl

Four kinds of stored text, in the order a reader would care about them: what Ultroid writes
(`str()` and `repr()` of nested values), setting values as people type them, Python literal
syntax at its edges, and random edits of all of those to find the near misses. Seeded, so a rerun
gives the same file.
"""

import json
import math
import random
import sys

rng = random.Random(20261120)

TEXTS = [
    "", "a", "hello world", "it's", 'say "hi"', "both ' and \"", "back\\slash", "new\nline",
    "tab\there", "cr\rhere", "ctrl \x01\x1f", "del\x7f", "nbsp\xa0here", "é à ü ñ", "日本語",
    "한국어", "emoji 😀", "family 👨‍👩‍👧", "shaking 🫨", "pink 🩷", "rtl ‏ mark",
    "combining é", "  line sep", "soft­hyphen", "bom ﻿", "private ",
    "{curly}", "[square]", "#hash", "@user", "https://t.me/TheUltroid", "$snip", "50% off",
    "a,b", "key: value", "'", '"', "\\", "\\n", "'''", '"""', "x" * 120, " lead", "trail ",
    "\t", "True", "None", "1", "-5", "1.5", "[1, 2]", "{'a': 1}", "Hello [Docs|ultroid.tech]",
    "**bold** `code` __italic__", "line1\nline2\nline3", "ß ǅ İ ı", "\x85 nel", "\x00 nul",
]
INTS = [0, 1, -1, 7, 42, 255, 1024, -1001234567890, 777000, 2**31, 2**53 + 1, 2**63, 2**64, 10**30, -(10**30)]
FLOATS = [0.0, -0.0, 1.5, -2.25, 0.1, 1e16, 1e-5, 1e300, 123456789.123, 5e-324, 1e22, 0.5,
          math.inf, -math.inf, math.nan]
BYTES = [b"", b"abc", b"\x00\xff", b"it's", b'q"q', b"both'\"", b"\n\t\r\\", bytes(range(0x7b, 0x84))]


def scalar():
    kind = rng.randrange(10)
    if kind == 0:
        return rng.choice([None, True, False])
    if kind in (1, 2):
        return rng.choice(INTS)
    if kind == 3:
        return rng.choice(FLOATS)
    if kind == 4:
        return rng.choice(BYTES)
    return rng.choice(TEXTS)


def key():
    kind = rng.randrange(6)
    if kind == 0:
        return rng.choice(INTS)
    if kind == 1:
        return (rng.choice(INTS), rng.choice(TEXTS))
    return rng.choice(TEXTS)


def value(depth=0):
    kind = rng.randrange(9) if depth < 4 else 0
    if kind <= 3:
        return scalar()
    size = rng.randrange(4)
    if kind == 4:
        return [value(depth + 1) for _ in range(size)]
    if kind == 5:
        return tuple(value(depth + 1) for _ in range(size))
    if kind == 6:
        return {key(): value(depth + 1) for _ in range(size)}
    if kind == 7:
        return {rng.choice(INTS[:8]) for _ in range(size)}
    return {"msg": rng.choice(TEXTS), "media": rng.choice([None, "BQACAgUAAx0CVhAAAQ"]),
            "button": rng.choice([None, [[["Docs", "ultroid.tech"]]]])}


# What the accessors store: chats mapped to words, notes, counters.
SHAPES = [
    {-1001234567890: ["spam", "scam"], -1009876543210: ["x"]},
    {-1001234567890: {"hello": {"msg": "Hi there!", "media": None, "button": None}}},
    {"greet": {"msg": "it's \"quoted\"", "media": "CAADAQADeAIAAm_BZBQ", "button": [[["A", "a.com"], ["B", "b.com"]]]}},
    [719195224, 1322549723, 1903729401], {"TAG": {5: [-100123, 777000]}, 12: 34},
    {-100123: {777000: [3, "flooding"]}}, ["afk msg", "pic", "https://graph.org/file/x.jpg", "Nov 20 2026 07:30:00PM"],
    {-100123: True}, {-100123: "ban"}, {"ASST": 5}, [], {}, (), [[]], [{}], {"a": {}}, {1: {2: {3: {4: [5]}}}},
]

SETTINGS = [
    ".", "!", "/", "$", "...", "?", "#", ";;", "~", "*", "-", "+", "_", ",", ":", "\\", "NO_HNDLR", " ",
    "5", "007", "+919876543210", "919876543210", "1e5", "0x10", "1_000", "1,000", "1.5", "-1001234567890",
    "True", "False", "None", "true", "false", "null", "yes", "on", "TRUE", "none", "en", "hi", "pt-br",
    "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ-1234567", "1BVtsOHwBu5", "1AZWarzQBu0" + "x" * 40 + "=",
    "https://graph.org/file/ec250c66268b62ee4ade6.jpg", "resources/extras/ultroid.jpg", "@TheUltroid",
    "Asia/Kolkata", "12:30", "2026-11-20", "20/11/2026", "#tag", "(text)", "[text]", "{text}", "'quoted'",
    '"quoted"', "1,2,3", "a,b", "1.2.3", "1.", ".5", "5.", "- 5", "5 # comment", "1 2", "0", "00", "01",
    "0.0", "-0", "--5", "+-5", "5-3", "5+3j", "3j", "1e", "e5", "0e0", "1E5", "inf", "nan", "-inf",
    "Infinity", '{"a": true, "b": null}', '{"a": 1, "b": [2, 3]}', '["x", "y"]', "[1, 2, 3]",
    "autocorrect autopic audiotools compressor", "Hello!\nWelcome to my PM.", "**PMSecurity**",
    "I'm AFK", "don't", 'He said "no"', "50%", "a=b", "x y z", "<b>bold</b>", "`code`", "user@example.com",
    # floats halfway between two shortest forms: `repr` must pick the even digit
    "900719925474099.25", "900719925474099.3", "900719925474099.75", "1844674407370955.1616",
    "-900719925474099.25", "[562949953421312.125, 562949953421312.375]", "{1125899906842624.25: 1125899906842624.75}",
    "0b101", "0o17", "0XFF", "1_0", "1__0", "_1", "1_", "9" * 25, "-" + "9" * 25, "1" * 4300, "1" * 4301,
    "0.1 + 0.2", "1 if True else 2", "lambda: 1", "__import__('os')", "set()", "dict()", "list()",
    "frozenset()", "set ( )", "set([1])", "b'bytes'", "u'text'", "r'raw\\n'", "f'x'", "rb'x'", "Rb'\\x'",
    "😀", "héllo", "🫨", "‍", "﻿", "﻿1", "\x0c1", "1\x0c", "\xa01", "1\xa0", "\x001", "1\x00",
]

SYNTAX = [
    # numbers
    "1", "-1", "+1", "- 1", "+ 1", "-(1)", "-(-1)", "- - 1", "(-1)", "((1))", "1_000_000", "0_0", "0__0",
    "0x1f", "0X1F", "0x_1f", "0x1_f", "0x", "0xg", "0o17", "0O17", "0o8", "0o_7", "0b101", "0B11", "0b2",
    "0b_1", "017", "08", "08.5", "08j", "0e0", "0.", ".0", ".", "1e5", "1E5", "1e+5", "1e-5", "1e 5",
    "1.e5", "1_0.0_1e1_0", "1e999", "-1e999", "1e-999", "1.5j", "1J", "1e3j", "0j", "-0j", "-1j", "+1j",
    "1+2j", "1-2j", "1 + 2j", "-1+2j", "-1-2j", "1+-2j", "1+2j+3j", "2j+1", "1+2", "1-2", "(1)+(2j)",
    "1.5+2.5j", "-1.5-2.5j", "True+1j", "1+True", "1e999+1j", "1+1e999j", "-0+0j", "0-0j", "-0.0+0j",
    "1*2j", "1/2", "2**3", "1//2", "1%2", "~1", "not 1", "-True", "+False", "-None", "1 < 2", "1 == 1",
    "1 and 2", "1 or 2", "1 if 1 else 2", "1j", "1jj", "1ee5", "1.2.3", "1..2", "1 .", "1 . 0", "1_", "_1",
    "1__2", "1e_5", "1_e5", "1._5", "1_.5", "0_x1", "00", "000", "0_0_0", "00.5", "1L", "1l", "1f", "0xfL",
    # names and calls
    "True", "False", "None", "true", "none", "TRUE", "Ellipsis", "...", ". . .", "....", "..", "NotImplemented",
    "set()", "set( )", "set (\n)", "set(())", "set(1)", "set([])", "frozenset()", "Set()", "dict()", "list()",
    "tuple()", "int()", "str()", "abc", "a.b", "a[0]", "a()", "print(1)", "ｓｅｔ()", "Ｔｒｕｅ", "ｎｏｎｅ",
    "sеt()", "(True)", "(None)", "(...)", "True,", "None,None", "True False",
    # strings
    "''", '""', "'a'", '"a"', "'''a'''", '"""a"""', "''''a''''", "'''a\nb'''", '"""a\nb"""', "'a\nb'",
    "'a\\\nb'", "'a' 'b'", "'a'\"b\"", "'a' \"b\" '''c'''", "'a''b'", "'a' b'b'", "b'a' 'b'", "b'a' b'b'",
    "'a' f'b'", "u'a'", "U'a'", "r'a\\nb'", "R'a\\nb'", "ur'a'", "ru'a'", "b'a'", "B'a'", "br'a\\n'",
    "rb'a\\n'", "bR'a'", "Rb'a'", "bu'a'", "f'a'", "F'a'", "f''", "fr'a'", "rf'a'", "f'{1}'", "'\\n'",
    "'\\t\\r\\a\\b\\f\\v'", "'\\\\'", "'\\''", "'\\\"'", '"\\\'"', "'\\0'", "'\\1'", "'\\12'", "'\\123'",
    "'\\1234'", "'\\8'", "'\\400'", "'\\777'", "b'\\400'", "b'\\777'", "'\\x41'", "'\\x4'", "'\\x'",
    "'\\xg0'", "'\\xFF'", "b'\\xff'", "b'\\x4'", "'\\u0041'", "'\\u004'", "'\\u00e9'", "'\\u20ac'",
    "'\\U0001f600'", "'\\U00110000'", "'\\U0001f60'", "'\\ud83d'", "'\\ud83d\\ude00'", "'\\udc80'",
    "b'\\u0041'", "b'\\N{DASH}'", "'\\N{DASH}'", "'\\N{EM DASH}'", "'\\N{em dash}'", "'\\N{LATIN SMALL LETTER A}'",
    "'\\N{NOPE}'", "'\\N{}'", "'\\N'", "'\\N{BELL}'", "'\\d'", "'\\ '", "'\\q\\w'", "b'\\d'", "'\\", "'a",
    'a\'', "'a\"", "'''a''", "'''a'''b", "'a'b", "'a' b", "b'é'", "b'\\xe9'", "'é'", "'😀'", "'\\'", "r'\\'",
    "r'\\''", "r'a\\'b'", "r'\\\\'", "rb'\\x41'", "'a\\\r\nb'", "'a\\\rb'", "'''a\\\nb'''", "'\x00'", "'\x7f'",
    "'\x01'", "'\x85'", "'\xa0'", "' '", "'﻿'", "''", "'\U0010ffff'", "'tab\there'",
    # containers
    "()", "(1,)", "(1)", "(1, 2)", "(1, 2,)", "(,)", "( )", "(1,,)", "((1,),)", "1,", "1, 2", "1, 2,", ",",
    "1,,", ",1", "[]", "[1]", "[1,]", "[1, 2]", "[,]", "[1,,2]", "[1 2]", "[ ]", "[[]]", "[[[]]]", "[1, [2, [3]]]",
    "{}", "{ }", "{1}", "{1,}", "{1, 2}", "{1: 2}", "{1: 2,}", "{1: 2, 3: 4}", "{,}", "{1:}", "{:1}", "{1: 2, 3}",
    "{1, 2: 3}", "{1: 2: 3}", "{**{}}", "{*[1]}", "[*[1]]", "(*[1],)", "{1: 'a', 1.0: 'b', True: 'c'}",
    "{0: 'a', False: 'b', 0.0: 'c', -0.0: 'd'}", "{1, 1.0, True}", "{'a', 'a'}", "{(1, 2): 3}", "{[1]: 2}",
    "{{}: 1}", "{{1}}", "{[1]}", "{{1: 2}}", "{(1, [2]): 3}", "{None: None}", "{...: ...}", "{b'a': 'a', 'a': b'a'}",
    "{1j: 2}", "{1.5: 2, 1e16: 3}", "[1, 'a', b'b', 2.5, None, True, ..., (), [], {}]",
    "[\n1,\n2\n]", "[1, # one\n2]", "(\n)", "{\n'a':\n1\n}", "[1,\r\n2]", "[1,\r2]", "[1\\\n,2]", "1\\\n", "\\\n1",
    "(1\n)", "1\n", "1\n\n", "\n1", "\n\n1\n", "1\n2", "1;", "1; 2", " 1", "\t1", " \t 1 \t ", "\n 1", "\n\t1",
    "1 \n ", "1\n  # c", "# c\n1", "#c", "", " ", "\n", "\t", "1 #", "1# c", "#1", "[1] # x", "\x0c1", "1 \x0c",
    "[\x0c1]", "[\v1]", "\v1", "[\xa01]", "[1 ]", "[1]\x00", "﻿[1]", "[1]﻿", "\r1", "1\r", "1\r\n",
    "[" * 5 + "]" * 5, "[" * 199 + "]" * 199, "[" * 200 + "]" * 200, "[" * 201 + "]" * 201, "(" * 199 + "1" + ")" * 199,
    "(" * 200 + "1" + ")" * 200, "[" * 100 + "(" * 99 + ")" * 99 + "]" * 100, "[" * 100 + "(" * 100 + ")" * 100 + "]" * 100,
    "[1" + ", 1" * 500 + "]", "{" + ", ".join(f"{i}: {i}" for i in range(200)) + "}",
    "'" + "a" * 5000 + "'", "9" * 4300, "9" * 4301, "-" + "9" * 4300, "[" + "9" * 4301 + "]", "0x" + "f" * 5000,
    "1e" + "9" * 30, "0." + "0" * 400 + "1", "1" + "0" * 400 + ".0",
    "[1, 2", "1, 2]", "(1, 2", "{1: 2", "[(1, 2])", "[}", "{]", "(]", ")", "]", "}", "[1)", "1 )", "'a', ]",
    "[1, 2] [3]", "[1, 2][0]", "(1)(2)", "{1: 2}[1]", "[1].append(2)", "[x for x in y]", "[1 for _ in ()]",
    "{x: x for x in y}", "(yield)", "await x", "x := 1", "(x := 1)", "*1", "**1", "@1", "1 @ 2", "$", "?", "!", "`1`",
    "1 <> 2", "1 != 2", "<1>", "a = 1", "import os", "pass", "return 1", "del x", "assert 1", "print 1",
]


def nest(open_, close, depth, inner=""):
    return open_ * depth + inner + close * depth


def tuples(depth):
    text = "1"
    for _ in range(depth):
        text = "(" + text + ",)"
    return text


# Where the expression may sit in the text, and how deep it may nest (CPython stops at 200).
LAYOUT = [
    "1\n \n", "1\n\t", "1\n\x0c", "1\n \x0c", "1\n\x0c ", "\n \x0c1", "\n\x0c 1", "1\n#c\n ", "1\n \n\n",
    "1 \\\n", "1\\\n\n", "(1\\\n)", "1,\\\n2", "\\\n\\\n1", "\\ \n1", "1 \\", "\\", "\\\n 1", "\\\n\t1",
    "1\n\\\n", "1\n\\\n\n", "1\n \\\n\n", "[\n\n]", "[#c\n]", "(\n1\n,\n)", "1\n\n\n#end", "#c\n 1",
    "#c\n#d\n1", "1#c\n#d", "1\r\n\r\n", "1\r \r", "\t\x0c1", "\x0c\x0c1", "\x0c 1", "1\n\x0c\x0c", "1 \x0c \n",
    nest("{1:", "}", 199, "1"), nest("{1:", "}", 200, "1"), nest("{1:", "}", 201, "1"), tuples(199), tuples(200),
    tuples(201), nest("[(", ",)]", 100, "1"), nest("[(", ",)]", 101, "1"), nest("({", "},)", 100, "1"),
    "+" * 5 + "1", "-" * 2 + "1", "-+1", "+-1", "+(+1)", "-(1j)", "-(1+2j)", "+(1)+2j", "(-1)+2j", "(1+2j)",
    "((1)+(2j))", "1+(2j)", "1 - - 2j", "1-(-2j)", "(1,)+2j", "'a'+2j", "9007199254740993+1j",
    "1" + "0" * 308 + "+1j", "1" + "0" * 309 + "+1j", "-1" + "0" * 309 + "-1j", "1e308+1e308j", "0x10+1j", "1_0+1_0j",
    # \N{...}: names are matched without regard to case; aliases exist too
    "'\\N{EM DASH}'", "'\\N{Em Dash}'", "'\\N{EMDASH}'", "'\\N{EM-DASH}'", "'\\N{EM  DASH}'", "'\\N{ EM DASH}'",
    "'\\N{SHAKING FACE}'", "'\\N{GRINNING FACE}'", "'\\N{CJK UNIFIED IDEOGRAPH-4E00}'",
    "'\\N{cjk unified ideograph-4e00}'", "'\\N{CJK UNIFIED IDEOGRAPH-4e00}'", "'\\N{HANGUL SYLLABLE GA}'",
    "'\\N{hangul syllable ga}'", "'\\N{LATIN CAPITAL LETTER A WITH GRAVE}'", "'\\N{NO-BREAK SPACE}'",
    "'\\N{ZERO WIDTH JOINER}'", "'\\N{DIGIT ONE}\\N{DIGIT TWO}'", "'\\N{LF}'", "'\\N{NULL}'", "'\\N{BEL}'",
    "'\\N{LINE FEED}'", "'x\\N{DASH'", "'\\N{EM DASH'", "'\\N{{EM DASH}}'", "'\\N{EM DASH}}'", "r'\\N{NOPE}'",
]


def marked(v):
    """A Python value in the JSON the recorder reads back as that value."""
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    if isinstance(v, int):
        return v if abs(v) <= 2**53 else {"$int": str(v)}
    if isinstance(v, float):
        if math.isnan(v):
            return {"$num": "NaN"}
        if math.isinf(v):
            return {"$num": "Infinity" if v > 0 else "-Infinity"}
        if v == 0 and math.copysign(1, v) < 0:
            return {"$num": "-0"}
        return {"$float": repr(v)} if v.is_integer() else v
    if isinstance(v, bytes):
        return {"$bytes": list(v)}
    if isinstance(v, list):
        return [marked(x) for x in v]
    if isinstance(v, tuple):
        return {"$tuple": [marked(x) for x in v]}
    if isinstance(v, set):
        return {"$set": [marked(x) for x in sorted(v)]}
    if all(isinstance(k, str) for k in v):
        return {k: marked(x) for k, x in v.items()}
    return {"$dict": [[marked(k), marked(x)] for k, x in v.items()]}


def mutate(text):
    alphabet = "'\"\\[](){}:,+-_.0123456789eEjJxXoObBrRuUfF \t\n#TrueFalsNonset=é😀"
    chars = list(text)
    for _ in range(rng.randrange(1, 4)):
        at = rng.randrange(len(chars) + 1)
        kind = rng.randrange(5)
        if kind == 0 and chars:
            del chars[min(at, len(chars) - 1)]
        elif kind == 1:
            chars.insert(at, rng.choice(alphabet))
        elif kind == 2 and chars:
            chars.insert(at, chars[min(at, len(chars) - 1)])
        elif kind == 3 and len(chars) > 1:
            at = min(at, len(chars) - 2)
            chars[at], chars[at + 1] = chars[at + 1], chars[at]
        else:
            chars = chars[:at]
    return "".join(chars)


def main():
    values = SHAPES + [value() for _ in range(520)] + [scalar() for _ in range(120)]
    written = []
    for v in values:
        written.append(str(v))
        written.append(repr(v))
    stored = list(dict.fromkeys(written + SETTINGS + SYNTAX + LAYOUT))
    short = [t for t in stored if len(t) <= 80]
    edits = list(dict.fromkeys(mutate(rng.choice(short)) for _ in range(2600)))
    stored += [t for t in edits if t not in set(stored)]
    out = sys.stdout
    for text in stored:
        out.write(json.dumps({"fn": "read_stored", "args": [text]}, ensure_ascii=False) + "\n")
    chaos = [None, True, False, 0, 1, -1, 2**53 + 1, 2**64, 0.0, -0.0, 1.5, math.nan, math.inf, "", "x", [], {},
             ["a", 1], {"a": "b"}, (), (1,), {1}, b"", b"abc", {1: 2}, {(1, 2): [3]}]
    texts = rng.sample(stored, 420)
    # Text that reads as a lone surrogate: Python holds it, though no backend could store it.
    texts += ["'\\ud83d'", "'a\\udc80b'", "['\\ud83d\\ude00']", "{'\\udfff': 1}"]
    args = [marked(v) for v in chaos + values + texts]
    # The largest int Python 3.11 still prints: 4300 digits. Written out, as `str()` refuses more.
    args.append({"$int": "1" + "0" * 4299})
    for arg in args:
        out.write(json.dumps({"fn": "write_value", "args": [arg]}, ensure_ascii=False) + "\n")


main()
