"""Scenarios for the language strings: for `rust/strings-rs/make_inputs.py` and `fuzz_strings.py`.

A scenario is a setting (the files in `strings/strings`, the stored language, the `LANGUAGE`
variable, what the translator does) and a list of steps; `language.py` says what each part
means. The keys and codes come from small pools, so that lookups hit and miss in every way: in
the language, only in English, in neither, in a language that is not loaded.
"""

KEYS = ["py_c1", "cmda", "help_ping", "help_x", "name", "natively", "authors", "fmt", "x", "", "two words", "é"]
TEXTS = ["Hello", "Wrong string session. Copy paste correctly!", "a {} b {}", "{}", "{}{}", "", "✘ Commands Available",
         "\n\n• `{i}ping`", "x\\ Ny", "नमस्ते {}", " ", "{ }", "{{}}", "😀"]  # fmt: skip
CODES = ["en", "hi", "es", "pt-br", "xx"]
# What a file can hold where text is expected, and what a file can hold instead of a mapping.
ODD = [None, 5, 0, 1.5, True, False, [], ["a"], ["{}", "{}"], {}, {"k": "v"}, "text", [1, 2]]
# Names in the folder that are no language, or not quite one.
OTHER = ["notes.txt", "fooyml", ".hidden.yml", "x.yaml", "a\\b.yml", "EN.yml", " .yml", "yml", "5.yml", "True.yml", ".yml"]
# Stored text that is no plain code: what `get_key` reads as something else, and paths.
STORED = ["5", "None", "0", "[1, 2]", "{'a': 1}", "True", "1.5", "'en'", "(1,)", "", " ", "en ", "EN", "en.yml", "./en", "../strings/en",
          "x/../en", "en/../en", "zz.yml/../en", "../../x", "../../../no-such-language-file", "a\\b", "x/y", "hi\x00", "e" * 300]  # fmt: skip
VARIABLES = ["en_US:en", "en", "hi", "", "C", "xx", "de_DE.UTF-8"]
WAYS = ["same", "tag", "tag", "empty", "drop", "extra", "break", "none", "type", "key", "value", "what"]
HELP = ["ping", "x", "", 5, None, "two words"]


def language(rng, code):
    """What a language file holds: mostly a mapping of keys to text."""
    if rng.random() < 0.08:
        return rng.choice(ODD)
    held = {}
    if rng.random() < 0.9:
        held.update(name=code.upper(), natively=f"<{code}>", authors=[f"{code}-author"] * rng.randrange(1, 3))
    for key in rng.sample(KEYS, rng.randrange(len(KEYS))):
        held[key] = rng.choice(ODD) if rng.random() < 0.08 else rng.choice(TEXTS)
    if held and rng.random() < 0.1:
        del held[rng.choice(list(held))]
    return held


def setting(rng):
    files = {}
    if rng.random() < 0.85:
        files["en.yml"] = language(rng, "en")
    for code in rng.sample(CODES[1:], rng.choice([0, 1, 1, 2, 3])):
        files[code + ".yml"] = language(rng, code)
    for name in rng.sample(OTHER, rng.choice([0, 0, 1, 2])):
        files[name] = language(rng, name[:2])
    names = list(files)
    rng.shuffle(names)
    files = {name: files[name] for name in names}
    broken = [rng.choice(names + ["zz.yml"])] if rng.random() < 0.12 else []
    roll = rng.random()
    stored = None if roll < 0.4 else rng.choice(CODES) if roll < 0.85 else rng.choice(STORED)
    roll = rng.random()
    variable = None if roll < 0.6 else rng.choice(VARIABLES)
    ways = [rng.choice(WAYS) for _ in range(rng.choice([0, 0, 1, 2, 4, 8]))]
    return {"stored": stored, "env": variable, "files": files, "broken": broken, "translate": ways}


def steps(rng):
    out = []
    for _ in range(rng.randrange(1, 9)):
        roll = rng.random()
        key = rng.choice(ODD) if rng.random() < 0.05 else rng.choice(KEYS)
        if roll < 0.55:
            out.append(["get_string", key])
        elif roll < 0.68:
            out.append(["get_string", key, rng.choice([True, False, False, 0, 1, "", None])])
        elif roll < 0.82:
            out.append(["get_help", rng.choice(HELP)])
        elif roll < 0.92:
            out.append(["get_languages"])
        else:
            out.append(["language", rng.choice(CODES + CODES + STORED[:9] + [None, 5, "", ["en"]])])
    return out


def scenario(rng):
    return setting(rng), steps(rng)
