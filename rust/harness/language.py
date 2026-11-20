"""Language strings, run as scenarios (ADR-004, ADR-007).

`strings/__init__.py` loads the language files and answers `get_string`. On import it reads the
language from `udB` or the environment and loads that file; a string the language lacks is
taken from English and sent to Google to be translated. `run` gives the module all of that for
one scenario and reports what it did.

    setup = {
        "stored": "hi",                 the text under `language` in the database, or None
        "env": "en_US:en",              the LANGUAGE variable, or None
        "files": {"en.yml": {...}},     what is in strings/strings: a name, and what reading
                                        the file gives, whatever that is
        "broken": ["xx.yml"],           names that are there and cannot be read
        "translate": ["tag", "type"],   what each call to `translate` does, in turn
    }
    steps = [["get_string", "py_c1"], ["get_help", "ping"], ["get_languages"], ["language", "hi"]]

The files are real, in a directory of their own, and the module's `open`, `os.path.exists` and
`glob` see them. Reading a file is the one thing replaced: instead of parsing YAML, the reader
hands over what the scenario says the file holds. Which YAML reader Ultroid uses, and what the
two it can use make of the same file, is a question of its own.

Nothing in this file raises on purpose: what makes no sense fails the way Python fails on it.
"""

import copy
import glob
import importlib.util
import os
import sys
import tempfile
import types

from fixture import ROOT, canon, stub_strings, udB

stub_strings()

import pyUltroid  # noqa: E402  (the fixture has to load first)
from pyUltroid.fns import tools  # noqa: E402

SOURCE = os.path.join(ROOT, "strings", "__init__.py")
# A file name has to be one the directory can hold, whatever the machine.
_PLAIN = {True: None}


def _tag(text, lang):
    return f"[{lang}] {text}"


# What a call to `translate` can do. Google gives text back, gives nothing, or the call fails.
_TRANSLATE = {
    "same": lambda text, lang: text,
    "tag": _tag,
    "empty": lambda text, lang: "",
    "drop": lambda text, lang: text.replace("{}", "", 1),
    "extra": lambda text, lang: text + " {}",
    "break": lambda text, lang: text + "\\ Nx",
    "none": lambda text, lang: None,
    "type": lambda text, lang: "" + 1,
    "key": lambda text, lang: {}["nothing"],
    "value": lambda text, lang: int("x"),
}


class _Log:
    def __init__(self, events):
        self.events = events

    def info(self, message):
        self.events.append(["log", "info", "" + message])

    def exception(self, error):
        self.events.append(["log", "exception", type(error).__name__])


def _language(value):
    pyUltroid.ULTConfig.lang = value


def run(setup: dict, steps: list) -> list:
    """Runs the steps on a freshly imported `strings`. Returns, in order: what the import and
    each step logged and asked to have translated, each step's result as `["ok", type, text]` or
    `["error", exception]`, and at the end the language and everything loaded."""
    # A dict, two lists, and text or None twice: anything else fails here, as Python fails on it.
    files, broken, script = {**setup["files"]}, setup["broken"] + [], setup["translate"] + []
    stored, env = setup["stored"], setup["env"]
    for name in [*broken, *files]:
        plain = "/" not in name and "\0" not in name and name not in ("", ".", "..")
        _PLAIN[plain and len(name.encode()) <= 200]
    if stored is not None:
        stored = "" + stored
    if env is not None:
        env = "" + env
        _PLAIN["\0" not in env]
    events = []

    def translate(text, lang_tgt="en"):
        events.append(["translate", canon(text), canon(lang_tgt)])
        return _TRANSLATE[script.pop(0) if script else "tag"](text, lang_tgt)

    def read(stream):
        return copy.deepcopy(files[os.path.basename(stream.name)])

    def listed(pattern):
        # The order a directory lists its files in is the machine's. Here it is the scenario's.
        order = [*broken, *files]
        return sorted(glob.glob(pattern), key=lambda path: order.index(os.path.basename(path)))

    udB.wipe()
    if stored is not None:
        udB.raw["language"] = stored
    real = pyUltroid.LOGS, tools.translate, sys.modules.get("yaml"), os.environ.get("LANGUAGE"), os.getcwd()
    spec = importlib.util.spec_from_file_location("ultroid_strings", SOURCE)
    strings = importlib.util.module_from_spec(spec)
    with tempfile.TemporaryDirectory() as folder:
        try:
            os.makedirs(os.path.join(folder, "strings", "strings"))
            for name in broken:
                os.makedirs(os.path.join(folder, "strings", "strings", name), exist_ok=True)
            for name in files:
                if name not in broken:
                    open(os.path.join(folder, "strings", "strings", name), "w").close()
            os.environ.pop("LANGUAGE", None)
            if env is not None:
                os.environ["LANGUAGE"] = env
            pyUltroid.ULTConfig.lang = "en"
            pyUltroid.LOGS, tools.translate = _Log(events), translate
            sys.modules["yaml"] = types.SimpleNamespace(safe_load=read)
            os.chdir(folder)
            spec.loader.exec_module(strings)
            strings.glob = listed
            calls = {
                "get_string": strings.get_string,
                "get_help": strings.get_help,
                "get_languages": strings.get_languages,
                "language": _language,
            }
            report = [*events]
            events.clear()
            for step in steps + []:
                name, *arguments = step + []
                call = calls[name]
                try:
                    value = call(*arguments)
                    outcome = ["ok", type(value).__name__, canon(value)]
                except Exception as error:  # noqa: BLE001  (the failure is the result)
                    outcome = ["error", type(error).__name__]
                report += events + [outcome]
                events.clear()
            loaded = [[canon(code), canon(value)] for code, value in strings.languages.items()]
            return report + [["state", canon(pyUltroid.ULTConfig.lang), loaded]]
        finally:
            os.chdir(real[4])
            pyUltroid.LOGS, tools.translate = real[:2]
            sys.modules.pop("yaml", None)
            if real[2] is not None:
                sys.modules["yaml"] = real[2]
            os.environ.pop("LANGUAGE", None)
            if real[3] is not None:
                os.environ["LANGUAGE"] = real[3]
            pyUltroid.ULTConfig.lang = "en"
