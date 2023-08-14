# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import string

from utilities.tools import atranslate

from . import (HNDLR, LOGS, get_string, udB, ultroid_bot,  # ignore: pylint
               ultroid_cmd)

try:
    from gingerit.gingerit import GingerIt
except ImportError:
    LOGS.info("GingerIt not found")
    GingerIt = None

from telethon import events


@ultroid_cmd(pattern="autocorrect", fullsudo=True)
async def acc(e):
    if not udB.get_key("AUTOCORRECT"):
        udB.set_key("AUTOCORRECT", "True")
        ultroid_bot.add_handler(
            gramme, events.NewMessage(outgoing=True, func=lambda x: x.text)
        )
        return await e.eor(get_string("act_1"), time=5)
    udB.del_key("AUTOCORRECT")
    await e.eor(get_string("act_2"), time=5)


async def gramme(event):
    if not udB.get_key("AUTOCORRECT"):
        return
    t = event.text
    if t[0] == HNDLR or t[0].lower(
    ) not in string.ascii_lowercase or t.endswith(".."):
        return
    tt = await atranslate(t, "en", detect=True)
    if tt and tt[1] != "en":
        return
    xx = GingerIt()
    x = xx.parse(t)
    res = x["result"]
    try:
        await event.edit(res)
    except BaseException:
        pass


if GingerIt and udB.get_key("AUTOCORRECT"):
    ultroid_bot.add_handler(
        gramme, events.NewMessage(outgoing=True, func=lambda x: x.text)
    )
