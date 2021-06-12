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
from googletrans import Translator
from telethon import events

from . import *

tr = Translator()


@ultroid_cmd(pattern="autocorrect")
async def acc(e):
    if not is_fullsudo(e.sender_id):
        return await eod(ult, "`This Command Is Sudo Restricted.`")
    if Redis("AUTOCORRECT") != "True":
        udB.set("AUTOCORRECT", "True")
        await eod(e, "AUTOCORRECT Feature On")
    else:
        udB.delete("AUTOCORRECT")
        await eod(e, "AUTOCORRECT Feature Off")


@ultroid_bot.on(events.NewMessage(outgoing=True))
async def gramme(event):
    if Redis("AUTOCORRECT") != "True":
        return
    t = event.text
    tt = tr.translate(t)
    if t.startswith((HNDLR, ".", "?", "#", "_", "*", "'", "@", "[", "(", "+")):
        return
    if t.endswith(".."):
        return
    if tt.src != "en":
        return
    xx = GingerIt()
    x = xx.parse(t)
    res = x["result"]
    try:
        await event.edit(res)
    except BaseException:
        pass
