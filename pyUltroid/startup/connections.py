# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import base64
import ipaddress
import struct
import sys
from typing import Optional

from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession

from ..configs import Var
from . import *  # noqa: F401,F403
from .BaseClient import UltroidClient

# Pyrogram session formats keyed by length, with the corresponding struct
# layout. (Same numbers Pyrogram itself uses.)
_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

# https://github.com/pyrogram/pyrogram/blob/master/docs/source/faq/what-are-the-ip-addresses-of-telegram-data-centers.rst
DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def _fail(logger, code: str, _exit: bool) -> None:
    """Log a localised error and optionally terminate the process."""
    try:
        from strings import get_string

        msg = get_string(code)
    except Exception:
        msg = code
    logger.critical(msg)
    if _exit:
        sys.exit(1)


def validate_session(session: Optional[str], logger=LOGS, _exit: bool = True):  # noqa: F405
    """Validate a string session, converting Pyrogram sessions to Telethon."""
    if not session:
        _fail(logger, "py_c2", _exit)
        return None

    # Native Telethon string session.
    if session.startswith(CURRENT_VERSION):
        if len(session.strip()) != 353:
            _fail(logger, "py_c1", _exit)
            return None
        return StringSession(session)

    # Pyrogram session – translate it to a Telethon one.
    if len(session) in _PYRO_FORM:
        try:
            data_ = struct.unpack(
                _PYRO_FORM[len(session)],
                base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
            )
        except Exception as err:
            logger.error(f"Could not decode Pyrogram session: {err}")
            _fail(logger, "py_c1", _exit)
            return None

        auth_id = 2 if len(session) in {351, 356} else 3
        dc_id, auth_key = data_[0], data_[auth_id]
        return StringSession(
            CURRENT_VERSION
            + base64.urlsafe_b64encode(
                struct.pack(
                    _STRUCT_PREFORMAT.format(4),
                    dc_id,
                    ipaddress.ip_address(DC_IPV4[dc_id]).packed,
                    443,
                    auth_key,
                )
            ).decode("ascii")
        )

    _fail(logger, "py_c1", _exit)
    return None


def vc_connection(udB, ultroid_bot):
    """Return a Telethon client for Voice/Video Chat operations.

    Falls back to the main userbot client if no dedicated VC session was
    configured (or if the session is bad).
    """
    try:
        from strings import get_string
    except Exception:
        def get_string(code):
            return code

    VC_SESSION = Var.VC_SESSION or udB.get_key("VC_SESSION")
    if not VC_SESSION or VC_SESSION == Var.SESSION:
        return ultroid_bot

    LOGS.info("Starting up VcClient.")  # noqa: F405
    try:
        return UltroidClient(
            validate_session(VC_SESSION, _exit=False),
            log_attempt=False,
            exit_on_error=False,
        )
    except (AuthKeyDuplicatedError, EOFError):
        LOGS.info(get_string("py_c3"))  # noqa: F405
        udB.del_key("VC_SESSION")
    except Exception as err:
        LOGS.error("Failed to create a VC client.")  # noqa: F405
        LOGS.exception(err)  # noqa: F405
    return ultroid_bot
