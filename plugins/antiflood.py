# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_antiflood")


import re

from telethon.events import NewMessage as NewMsg

from pyUltroid.dB import DEVLIST
from pyUltroid.dB.antiflood_db import get_flood, get_flood_limit, rem_flood, set_flood
from pyUltroid.fns.admins import admin_check

from . import Button, Redis, asst, callback, eod, get_string, ultroid_bot, ultroid_cmd

_check_flood = {}

if Redis("ANTIFLOOD"):

    @ultroid_bot.on(
        NewMsg(
            chats=list(get_flood().keys()),
        ),
    )
    async def flood_checm(event):
        count = 1
        chat = (await event.get_chat()).title
        if event.chat_id in _check_flood.keys():
            if event.sender_id == list(_check_flood[event.chat_id].keys())[0]:
                count = _check_flood[event.chat_id][event.sender_id]
                _check_flood[event.chat_id] = {event.sender_id: count + 1}
            else:
                _check_flood[event.chat_id] = {event.sender_id: count}
        else:
            _check_flood[event.chat_id] = {event.sender_id: count}
        if await admin_check(event, silent=True) or getattr(event.sender, "bot", None):
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
                await event.reply(f"#AntiFlood\n\n{get_string('antiflood_3')}")
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
    input_ = e.pattern_match.group(1).strip()
    if not input_:
        return await e.eor("`What?`", time=5)
    if not input_.isdigit():
        return await e.eor(get_string("com_3"), time=5)
    if m := set_flood(e.chat_id, input_):
        return await eod(e, get_string("antiflood_4").format(input_))


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
        return await e.eor(get_string("antiflood_1"), time=5)
    await e.eor(get_string("antiflood_2"), time=5)


@ultroid_cmd(
    pattern="getflood$",
    admins_only=True,
)
async def getflood(e):
    if ok := get_flood_limit(e.chat_id):
        return await e.eor(get_string("antiflood_5").format(ok), time=5)
    await e.eor(get_string("antiflood_2"), time=5)
