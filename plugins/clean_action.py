# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

•`{i}addclean`
    Clean all Upcoming action msg in added chat like someone joined/left/pin etc.

•`{i}remclean`
    Remove chat from database.

•`{i}listclean`
   To get list of all chats where its activated.

"""

from pyUltroid.functions.clean_db import *

from . import *


@ultroid_cmd(pattern="addclean$", admins_only=True)
async def _(e):
    add_clean(e.chat_id)
    await eod(e, "Added Clean Action Setting For this Chat")
    async for x in ultroid_bot.iter_messages(e.chat_id, limit=3000):
        if x.action:
            await x.delete()


@ultroid_cmd(pattern="remclean$")
async def _(e):
    rem_clean(e.chat_id)
    await eod(e, "Removed Clean Action Setting For this Chat")


@ultroid_cmd(pattern="listclean$")
async def _(e):
    k = udB.get("CLEANCHAT")
    if k:
        k = k.split(" ")
        o = ""
        for x in k:
            try:
                title = (await ultroid_bot.get_entity(int(x))).title
            except BaseException:
                title = "`Invalid ID`"
            o += x + " " + title + "\n"
        await eor(e, o)
    else:
        await eod(e, "`No Chat Added`")


@ultroid_bot.on(events.ChatAction())
async def _(event):
    if is_clean_added(event.chat_id):
        try:
            await event.delete()
        except BaseException:
            pass
