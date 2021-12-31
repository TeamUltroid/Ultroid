# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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

from telethon.utils import get_display_name

from . import get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="addclean$", admins_only=True)
async def _(e):
    key = udB.get_key("CLEANCHAT") or []
    if e.chat_id in key:
        return await eod(e, get_string("clan_5"))
    key.append(e.chat_id)
    udB.set_key("CLEANCHAT", key)
    await e.eor(get_string("clan_1"), time=5)


@ultroid_cmd(pattern="remclean$")
async def _(e):
    key = udB.get_key("CLEANCHAT") or []
    if e.chat_id in key:
        key.remove(e.chat_id)
        udB.set_key("CLEANCHAT", key)
    await e.eor(get_string("clan_2"), time=5)


@ultroid_cmd(pattern="listclean$")
async def _(e):
    k = udB.get_key("CLEANCHAT")
    if k:
        o = ""
        for x in k:
            try:
                title = get_display_name(await e.client.get_entity(x))
            except BaseException:
                title = get_string("clan_3")
            o += f"{x} {title}\n"
        await e.eor(o)
    else:
        await e.eor(get_string("clan_4"), time=5)
