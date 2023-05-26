# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import base64
import ipaddress
import struct
import sys

from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession

from ..setup import LOGS

_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

# https://github.com/pyrogram/pyrogram/blob/master/docs/source/faq/what-are-the-ip-addresses-of-telegram-data-centers.rst


def _pyrogram_session(session):
    DC_IPV4 = {
        1: "149.154.175.53",
        2: "149.154.167.51",
        3: "149.154.175.100",
        4: "149.154.167.91",
        5: "91.108.56.130",
    }
    data_ = struct.unpack(
        _PYRO_FORM[len(session)],
        base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
    )
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


def validate_session(session, logger=LOGS, _exit=True):
    from localization import get_string

    if session:
        # Telethon Session
        if session.startswith(CURRENT_VERSION):
            if len(session.strip()) != 353:
                logger.exception(get_string("py_c1"))
                sys.exit()
            return StringSession(session)

        elif len(session) in _PYRO_FORM:
            return _pyrogram_session(session)
        else:
            logger.exception(get_string("py_c1"))
            if _exit:
                sys.exit()
    logger.exception(get_string("py_c2"))
    if _exit:
        exit()


def update_handlers(handlerType, newValue, oldValue):
    from core import ultroid_bot, asst
    from core.decorators._decorators import compile_pattern

    # TODO: DUAL/Asst going to be different
    # Check for old matches to be sure
    if handlerType == "DUAL_HNDLR":
        clients = [asst, ultroid_bot]
    else:
        clients = [ultroid_bot if handlerType == "HNDLR" else asst]

    def update(handler):
        pattern = handler._pattern
        if not pattern:
            return
        pattern = pattern.pattern
        oldPattern = pattern[len(oldValue) + 1 if oldValue != "NO_HNDLR" else 1 :]
        handler.pattern = compile_pattern(oldPattern, newValue).match

    for client in clients:
        for _, handler in client.list_event_handlers():
            update(handler)
