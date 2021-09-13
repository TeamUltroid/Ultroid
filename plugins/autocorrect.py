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

from gingerit.gingerit import GingerIt
from google_trans_new import google_translator
from telethon import events

from . import *


@ultroid_cmd(pattern="autocorrect", fullsudo=True)
async def acc(e):
    if Redis("AUTOCORRECT") != "True":
        udB.set("AUTOCORRECT", "True")
        await eor(e, "AUTOCORRECT Feature On", time=5)
    else:
        udB.delete("AUTOCORRECT")
        await eor(e, "AUTOCORRECT Feature Off", time=5)


@ultroid_bot.on(events.NewMessage(outgoing=True))
async def gramme(event):
    if Redis("AUTOCORRECT") != "True":
        return
    t = event.text
    if t.startswith((HNDLR, ".", "?", "#", "_", "*", "'", "@", "[", "(", "+")):
        return
    if t.endswith(".."):
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
