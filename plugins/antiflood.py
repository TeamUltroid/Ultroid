# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}setflood <integer>`
    Set flood limit in a chat.

• `{i}remflood`
    Remove flood limit from a chat.

• `{i}getflood`
    Get flood limit of a chat.
"""


import re

from pyUltroid.functions.antiflood_db import (
    get_flood,
    get_flood_limit,
    rem_flood,
    set_flood,
)
from telethon.events import NewMessage as NewMsg

from . import *

_check_flood = {}


if Redis("ANTIFLOOD") is not (None or ""):

    @ultroid_bot.on(
        NewMsg(
            chats=list(get_flood().keys()),
        ),
    )
    async def flood_checm(event):
        count = 1
        chat = (await event.get_chat()).title
        if event.chat_id in _check_flood.keys():
            if event.sender_id == [x for x in _check_flood[event.chat_id].keys()][0]:
                count = _check_flood[event.chat_id][event.sender_id]
                _check_flood[event.chat_id] = {event.sender_id: count + 1}
            else:
                _check_flood[event.chat_id] = {event.sender_id: count}
        else:
            _check_flood[event.chat_id] = {event.sender_id: count}
        if await check_if_admin(event) or event.sender.bot:
            return
        if event.sender_id in DEVLIST:
            return
        if _check_flood[event.chat_id][event.sender_id] >= int(
            get_flood_limit(event.chat_id)
        ):
            try:
                name = event.sender.first_name
                await event.client.edit_permissions(
                    event.chat_id, event.sender_id, send_messages=False
                )
                del _check_flood[event.chat_id]
                await event.reply("#AntiFlood\n\n`You have been muted.`")
                await asst.send_message(
                    int(Redis("LOG_CHANNEL")),
                    f"#Antiflood\n\n`Muted `[{name}](tg://user?id={event.sender_id})` in {chat}`",
                    buttons=Button.inline(
                        "Unmute", data=f"anti_{event.sender_id}_{event.chat_id}"
                    ),
                )
            except BaseException:
                pass


@callback(
    re.compile(
        "anti_(.*)",
    ),
)
async def unmuting(e):
    ino = (e.data_match.group(1)).decode("UTF-8").split("_")
    user = int(ino[0])
    chat = int(ino[1])
    user_name = (await ultroid_bot.get_entity(user)).first_name
    chat_title = (await ultroid_bot.get_entity(chat)).title
    await ultroid_bot.edit_permissions(chat, user, send_messages=True)
    await e.edit(
        f"#Antiflood\n\n`Unmuted `[{user_name}](tg://user?id={user})` in {chat_title}`"
    )


@ultroid_cmd(
    pattern="setflood ?(\\d+)",
    admins_only=True,
)
async def setflood(e):
    input = e.pattern_match.group(1)
    if not input:
        return await eor(e, "`What?`", time=5)
    if not input.isdigit():
        return await eor(e, "`Invalid Input`", time=5)
    m = set_flood(e.chat_id, input)
    if m:
        return await eod(
            e, f"`Successfully Updated Antiflood Settings to {input} in this chat.`"
        )


@ultroid_cmd(
    pattern="remflood$",
    admins_only=True,
)
async def remove_flood(e):
    hmm = rem_flood(e.chat_id)
    try:
        del _check_flood[e.chat_id]
    except BaseException:
        pass
    if hmm:
        return await eor(e, "`Antiflood Settings Disabled`", time=5)
    await eor(e, "`No flood limits in this chat.`", time=5)


@ultroid_cmd(
    pattern="getflood$",
    admins_only=True,
)
async def getflood(e):
    ok = get_flood_limit(e.chat_id)
    if ok:
        return await eor(e, f"`Flood limit for this chat is {ok}.`", time=5)
    await eor(e, "`No flood limits in this chat.`", time=5)
