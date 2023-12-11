# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import *

import contextlib
import os
import sys
import time

from utilities.helper import bash, time_formatter, check_update
from .utils.funcs import process_main, load_plugins
from telethon.errors import SessionRevokedError

# Option to Auto Update On Restarts..
# TODO: UPDATE_ON_RESTART

ultroid_bot.me.phone = None

if not ultroid_bot.me.bot:
    udB.set_key("OWNER_ID", ultroid_bot.me.id)

LOGS.info("Initialising...")

if not udB.get_config("BOT_TOKEN"):
    with rm.get("autobot", helper=True) as mod:
        ultroid_bot.run_in_loop(mod.autopilot())


if HOSTED_ON == "heroku":
    rm._http_import("heroku", "core/heroku.py", helper=True)

ultroid_bot.run_in_loop(load_plugins())
ultroid_bot.loop.create_task(process_main())

with contextlib.suppress(BaseException):
    cleanup_cache()

LOGS.info(
    f"Took {time_formatter((time.time() - start_time) * 1000)} to start •ULTROID•"
)
LOGS.info(
    """
            ----------------------------------------------------------------------
                Ultroid has been deployed! Visit @TheUltroid for updates!!
            ----------------------------------------------------------------------
"""
)
try:
    asst.run()
except SessionRevokedError:
    LOGS.info(f"Assistant [@{asst.me.username}]'s session was revoked!")

    # shift loop to bot
    ultroid_bot.run()
