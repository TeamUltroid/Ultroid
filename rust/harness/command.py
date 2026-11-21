"""How a command is recognised, as data in and data out (ADR-004, ADR-007).

A plugin registers a pattern for its command. Ultroid puts the handler in front
(`compile_pattern`) and Telethon matches the result against the start of every message with
`re.match`; `event.pattern_match` is that match. The three functions here are the three ways a
pattern gets compiled: for a userbot command, for a command of the assistant, and for an inline
query. Each says whether a text matches and what the groups hold.
"""

import re

import fixture

_compile_pattern = fixture.decorators().compile_pattern


def _report(found):
    if found is None:
        return ["no"]
    return ["match", found.end(), list(found.groups()), found.groupdict()]


def command(pattern: str, handler: str, text: str) -> list:
    """`ultroid_cmd(pattern=pattern)` under a handler, on a message. A plugin that gives no
    pattern gets every message."""
    pattern, handler, text = "" + pattern, "" + handler, "" + text
    if not pattern:
        return ["always"]
    try:
        compiled = _compile_pattern(pattern, handler)
    except re.error:
        return ["bad pattern"]
    return _report(compiled.match(text))


def assistant(pattern: str, text: str) -> list:
    """`asst_cmd(pattern=pattern)` on a message to the assistant bot."""
    pattern, text = "" + pattern, "" + text
    if not pattern:
        return ["always"]
    try:
        compiled = re.compile(f"^/{pattern}")
    except re.error:
        return ["bad pattern"]
    return _report(compiled.match(text))


def inline(pattern: str, text: str) -> list:
    """`in_pattern(pattern)` on the text of an inline query."""
    pattern, text = "" + pattern, "" + text
    try:
        compiled = re.compile(pattern)
    except re.error:
        return ["bad pattern"]
    return _report(compiled.match(text))
