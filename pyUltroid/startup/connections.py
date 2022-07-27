# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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

from ..configs import Var
from . import *
from .BaseClient import UltroidClient

_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

# https://github.com/pyrogram/pyrogram/blob/master/docs/source/faq/what-are-the-ip-addresses-of-telegram-data-centers.rst

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def validate_session(session, logger=LOGS):
    if session:
        # Telethon Session
        if session.startswith(CURRENT_VERSION):
            if len(session.strip()) != 353:
                logger.exception("Wrong string session. Copy paste correctly!")
                sys.exit()
            return StringSession(session)
        # Pyrogram Session
        elif len(session) in _PYRO_FORM.keys():
            if len(session) in [351, 356]:
                dc_id, _, auth_key, _, _ = struct.unpack(
                    _PYRO_FORM[len(session)],
                    base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
                )
            else:
                dc_id, _, _, auth_key, _, _ = struct.unpack(
                    _PYRO_FORM[len(session)],
                    base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
                )
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
    logger.exception("No String Session found. Quitting...")
    sys.exit()


def vc_connection(udB, ultroid_bot):
    VC_SESSION = Var.VC_SESSION or udB.get_key("VC_SESSION")
    if VC_SESSION and VC_SESSION != Var.SESSION:
        try:
            return UltroidClient(
                validate_session(VC_SESSION, LOGS),
                log_attempt=False,
                handle_auth_error=False,
            )
        except (AuthKeyDuplicatedError, EOFError):
            LOGS.info(
                "Your VC_SESSION Expired. Deleting VC_SESSION from redis..."
                + "\nRenew/Change it to Use Voice/Video Chat from VC Account..."
            )
            udB.del_key("VC_SESSION")
        except Exception as er:
            LOGS.info("While creating Client for VC.")
            LOGS.exception(er)
    return ultroid_bot
