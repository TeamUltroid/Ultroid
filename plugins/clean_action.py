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
    await eor(e, "Added Clean Action Setting For this Chat", time=5)


@ultroid_cmd(pattern="remclean$")
async def _(e):
    rem_clean(e.chat_id)
    await eor(e, "Removed Clean Action Setting For this Chat", time=5)


@ultroid_cmd(pattern="listclean$")
async def _(e):
    k = udB.get("CLEANCHAT")
    if k:
        k = k.split(" ")
        o = ""
        for x in k:
            try:
                title = e.chat.title
            except BaseException:
                title = "`Invalid ID`"
            o += x + " " + title + "\n"
        await eor(e, o)
    else:
        await eor(e, "`No Chat Added`", time=5)
