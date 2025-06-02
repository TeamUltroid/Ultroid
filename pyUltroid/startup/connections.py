# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import base64
import ipaddress
import struct
import sys

from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession
from logging import getLogger

from ..configs import Var
from .BaseClient import UltroidClient

_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

logger = getLogger(__name__)

# https://github.com/pyrogram/pyrogram/blob/master/docs/source/faq/what-are-the-ip-addresses-of-telegram-data-centers.rst

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def validate_session(session, logger=logger, _exit=True):
    from strings import get_string

    if session:
        # Telethon Session
        if session.startswith(CURRENT_VERSION):
            if len(session.strip()) != 353:
                logger.exception(get_string("py_c1"))
                sys.exit()
            return StringSession(session)

        # Pyrogram Session
        elif len(session) in _PYRO_FORM.keys():
            data_ = struct.unpack(
                _PYRO_FORM[len(session)],
                base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
            )
            if len(session) in [351, 356]:
                auth_id = 2
            else:
                auth_id = 3
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
        else:
            logger.exception(get_string("py_c1"))
            if _exit:
                sys.exit()
    logger.exception(get_string("py_c2"))
    if _exit:
        sys.exit()


def vc_connection(udB, ultroid_bot):
    from strings import get_string

    VC_SESSION = Var.VC_SESSION or udB.get_key("VC_SESSION")
    if VC_SESSION and VC_SESSION != Var.SESSION:
        logger.info("Starting up VcClient.")
        try:
            return UltroidClient(
                validate_session(VC_SESSION, _exit=False),
                log_attempt=False,
                exit_on_error=False,
            )
        except (AuthKeyDuplicatedError, EOFError):
            logger.info(get_string("py_c3"))
            udB.del_key("VC_SESSION")
        except Exception as er:
            logger.info("While creating Client for VC.")
            logger.exception(er)
    return ultroid_bot
