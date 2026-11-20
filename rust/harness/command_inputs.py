"""Patterns and messages to try: for `rust/command-rs/make_inputs.py` and `fuzz_command.py`.

The patterns are the ones the code registers, read out of `plugins/`, `assistant/` and
`pyUltroid/` with `ast`, and made-up ones from the same grammar. The messages for a pattern are
built from the pattern itself, so that most of them are near a match: a text the pattern
accepts, the same with something added, dropped or changed, and a few that have nothing to do
with it.
"""

import ast
import os
import re
import re._parser as parser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
HANDLERS = [".", "!", "/", " ", "NO_HNDLR", "$", "?", "+", "^", "(", "\\", "..", ".!", "é", "😀", "#", "-", "~", "d", "w", "s", "a",
            "n", "b", "c", "1", "", ".*", "[", "|"]  # fmt: skip
LETTERS = "abcxyz019 _-/.#@!:,é٣²😀\n\t"
TAILS = ["", " ", "  ", "\n", "\n\n", " arg", " two args", " ünï 😀", "\nline", "x", "!", " \n", "\t", "\x1f", "\xa0x", " ٣٤"]
CLASSES = {"CATEGORY_DIGIT": "0159٣", "CATEGORY_NOT_DIGIT": "a _é", "CATEGORY_SPACE": " \t\n\x1f\xa0",
           "CATEGORY_NOT_SPACE": "a1_é", "CATEGORY_WORD": "a_Z9é٣²", "CATEGORY_NOT_WORD": " !-\ń"}  # fmt: skip
# What a made-up pattern is put together from. Most of it is what this port reads; the rest is
# there to see it refused the same way, or left alone.
ATOMS = ["a", "b", "c", "x", "1", " ", "_", "/", "-", "é", "😀", ".", ".", "\\d", "\\w", "\\s", "\\D", "\\W", "\\S", "\\n", "\\t", "\\1",
         "\\.", "\\\\", "\\$", "\\(", "\\[", "\\ ", "\\é", "[abc]", "[^abc]", "[a-z]", "[\\d_]", "[]x]", "[a-]", "[^\\s]", "[\\w.-]",
         "[\\]\\\\]", "[x-x]", "^", "$", "{", "}", "{}", "]", "#", ":", "=", "<", ">", ",", "!", "'", '"']  # fmt: skip
ODD = ["(", ")", "[", "[a", "[z-a]", "[\\d-a]", "\\", "\\c", "\\p", "\\1", "\\2", "\\1*", "\\b", "\\B", "\\A", "\\Z", "\\x41", "\\0",
       "{2}", "{2,}", "{,3}", "{2,3}", "{,}", "{a}", "{0}", "{2,1}", "{1000}", "{100001}", "{4294967295}", "{99999999999}", "*", "+",
       "?", "*+", "{2}+", "(?=a)", "(?!a)", "(?<=a)", "(?i)", "(?#c)", "(?>a)", "(?P=g0)", "(?P<n>a)(?P<n>b)", "(?P<é>a)", "(?P<1>a)",
       "(?P<>a)", "(?P<n", "(?", "(?:", "(a|)*", "(a*)+", "(a?)*", "()*", "(|a)+", "(?:a|)*", "(?:a*)*", "(a?){5}", "(a|){3,}",
       "(?:a??){2,}?", "(a)\\1", "(a|b)\\1+", "[]", "[^]", "|"]  # fmt: skip
# The counts are the same loop in `re` as `*`, `+` and `?`, with a least and a most.
QUANTIFIERS = ["", "", "", "", "", "", "*", "+", "?", "*?", "+?", "??", "*", "+", "?", "{2}", "{1,2}", "{0,2}?", "{,2}", "{2,}", "{1}?",
               "{2,3}?", "{0,1}", "{3}"]  # fmt: skip


def registered():
    """The patterns of every `ultroid_cmd`, `asst_cmd` and `in_pattern` in the code."""
    found = {"ultroid_cmd": set(), "asst_cmd": set(), "in_pattern": set()}
    for top in ("plugins", "assistant", "pyUltroid"):
        for folder, _, files in os.walk(os.path.join(ROOT, top)):
            for name in files:
                if not name.endswith(".py"):
                    continue
                with open(os.path.join(folder, name), encoding="utf-8") as source:
                    tree = ast.parse(source.read())
                for node in ast.walk(tree):
                    kind = isinstance(node, ast.Call) and getattr(node.func, "id", None)
                    if kind not in found:
                        continue
                    given = {keyword.arg: keyword.value for keyword in node.keywords}
                    pattern = given.get("pattern") or (node.args[0] if node.args else None)
                    # `in_pattern(re.compile("ip_(.*)"))`: the pattern is the argument of the call.
                    if isinstance(pattern, ast.Call) and pattern.args:
                        pattern = pattern.args[0]
                    if isinstance(pattern, ast.Constant) and isinstance(pattern.value, str):
                        found[kind].add(pattern.value)
    return {kind: sorted(patterns) for kind, patterns in found.items()}


def _member(rng, members):
    kinds = [str(kind) for kind, _ in members]
    if "NEGATE" in kinds:
        return rng.choice(LETTERS)
    kind, value = rng.choice(members)
    if str(kind) == "RANGE":
        return chr(rng.randint(*value))
    return rng.choice(CLASSES[str(value)]) if str(kind) == "CATEGORY" else chr(value)


def _example(rng, items, groups):
    out = []
    for kind, value in items:
        kind = str(kind)
        if kind == "LITERAL":
            out.append(chr(value))
        elif kind in ("ANY", "NOT_LITERAL"):
            out.append(rng.choice("ab 1é"))
        elif kind == "IN":
            out.append(_member(rng, value))
        elif kind == "CATEGORY":
            out.append(rng.choice(CLASSES[str(value)]))
        elif kind == "BRANCH":
            out.append(_example(rng, rng.choice(value[1]), groups))
        elif kind == "SUBPATTERN":
            out.append(_example(rng, value[3], groups))
            groups[value[0]] = out[-1]
        elif kind == "GROUPREF":
            out.append(groups.get(value, ""))
        elif kind.endswith("_REPEAT"):
            low, high, body = value
            low = min(low, 4)
            out.extend(_example(rng, body, groups) for _ in range(rng.randint(low, min(high, low + 2))))
    return "".join(out)


def example(rng, pattern):
    """A text the pattern is likely to match, or `None` for a pattern `re` refuses."""
    try:
        return _example(rng, parser.parse(pattern), {})
    except (re.error, RecursionError, OverflowError, ValueError):
        return None


def changed(rng, text):
    chars = list(text)
    for _ in range(rng.choice([1, 1, 2])):
        at = rng.randrange(len(chars) + 1)
        kind = rng.randrange(5)
        if kind == 0 and chars:
            del chars[min(at, len(chars) - 1)]
        elif kind == 1:
            chars.insert(at, rng.choice(LETTERS))
        elif kind == 2 and chars:
            chars[min(at, len(chars) - 1)] = rng.choice(LETTERS)
        elif kind == 3 and chars:
            chars[min(at, len(chars) - 1)] = chars[min(at, len(chars) - 1)].swapcase()
        else:
            chars = chars[:at]
    return "".join(chars)


def messages(rng, pattern, count):
    """`count` texts for a pattern as `re` gets it, most of them close to a match."""
    out = []
    for _ in range(count):
        text = example(rng, pattern)
        kind = rng.randrange(10)
        if text is None or kind == 0:
            text = "".join(rng.choice(LETTERS) for _ in range(rng.randrange(8)))
        elif kind < 5:
            text += rng.choice(TAILS)
        elif kind < 8:
            text = changed(rng, text) + rng.choice(TAILS[:6])
        out.append(text)
    return out


def made_up(rng, depth=0):
    """A pattern from the grammar the registered ones are written in, now and then with
    something in it that `re` refuses or that this port leaves alone."""
    branches = []
    for _ in range(rng.choice([1, 1, 1, 2, 3])):
        pieces = []
        for _ in range(rng.randrange(0 if depth else 1, 5)):
            kind = rng.random()
            if kind < 0.04:
                pieces.append(rng.choice(ODD))
                continue
            if kind < 0.24 and depth < 3:
                opening = rng.choice(["(", "(", "(", "(?:", "(?:", f"(?P<g{rng.randrange(3)}>"])
                piece = opening + made_up(rng, depth + 1) + ")"
            else:
                piece = rng.choice(ATOMS)
            pieces.append(piece + rng.choice(QUANTIFIERS))
        branches.append("".join(pieces))
    return "|".join(branches)
