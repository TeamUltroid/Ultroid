# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_fakeaction")

import math
import time

from pyUltroid.fns.admins import ban_time

from . import asyncio, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="f(typing|audio|contact|document|game|location|sticker|photo|round|video)( (.*)|$)"
)
async def _(e):
    act = e.pattern_match.group(1).strip()
    t = e.pattern_match.group(2)
    if act in ["audio", "round", "video"]:
        act = f"record-{act}"
    if t.isdigit():
        t = int(t)
    elif t.endswith(("s", "h", "d", "m")):
        t = math.ceil((ban_time(t)) - time.time())
    else:
        t = 60
    await e.eor(get_string("fka_1").format(str(t)), time=5)
    async with e.client.action(e.chat_id, act):
        await asyncio.sleep(t)
