# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}autocorrect`
    To on/off Autocorrect Feature.

"""

import string

from gingerit.gingerit import GingerIt
from google_trans_new import google_translator
from telethon import events

from . import HNDLR, Redis, eor, get_string, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="autocorrect", fullsudo=True)
async def acc(e):
    if Redis("AUTOCORRECT") != "True":
        udB.set("AUTOCORRECT", "True")
        return await eor(e, get_string("act_1"), time=5)
    udB.delete("AUTOCORRECT")
    await eor(e, get_string("act_2"), time=5)


@ultroid_bot.on(events.NewMessage(outgoing=True, func=lambda x: x.text))
async def gramme(event):
    if Redis("AUTOCORRECT") != "True":
        return
    t = event.text
    if t[0] == HNDLR or t[0].lower() not in string.ascii_lowercase or t.endswith(".."):
        return
    tt = google_translator().detect(t)
    if tt[0] != "en":
        return
    xx = GingerIt()
    x = xx.parse(t)
    res = x["result"]
    try:
        await event.edit(res)
    except BaseException:
        pass
