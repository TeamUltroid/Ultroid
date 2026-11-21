"""Session strings, as data in and data out (ADR-004, ADR-007).

Ultroid logs in with the `SESSION` variable: a Telethon string session, or a Pyrogram one that
`validate_session` converts on the way in. Whether a string is accepted, and which data centre,
address and key it stands for, has to stay the same or nobody can log in.

The messages `validate_session` logs come from `strings`, which is a unit of its own: here a
stand-in gives back the key of the message asked for.
"""

import fixture

fixture.stub_strings()

from telethon.sessions.string import StringSession  # noqa: E402

from pyUltroid.startup import connections  # noqa: E402


class _Log:
    def __init__(self):
        self.seen = []

    def exception(self, message):
        self.seen.append(message)


def _fields(made):
    key = made.auth_key.key.hex() if made.auth_key else None
    return [made.dc_id, made.server_address, made.port, key, made.save()]


def _named(error):
    return f"{type(error).__module__}.{type(error).__name__}"


def _text(value):
    """A session is text or nothing at all; anything else fails here as adding it to text fails."""
    return None if value is None else "" + value


def check(session, leave) -> list:
    """What `validate_session(session, _exit=leave)` does: the session it returns (data centre,
    address, port, key, and the string Telethon would save), that it returned nothing, that it
    left the program, or the exception it raised. Then the messages it logged."""
    session, log = _text(session), _Log()
    try:
        made = connections.validate_session(session, logger=log, _exit=bool(leave))
    except SystemExit:
        return ["exit", log.seen]
    except Exception as error:
        return ["raised", _named(error), log.seen]
    if made is None:
        return ["none", log.seen]
    return ["session", *_fields(made), log.seen]


def parse(text) -> list:
    """What Telethon's `StringSession(text)` holds, or the exception it raises."""
    text = _text(text)
    try:
        return ["session", *_fields(StringSession(text))]
    except Exception as error:
        return ["raised", _named(error)]
