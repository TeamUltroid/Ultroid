# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
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


from pyUltroid.functions.antiflood_db import get_flood_limit, rem_flood, set_flood
from telethon.events import NewMessage as NewMsg

from . import *

_check_flood = {}


if Redis("ANTIFLOOD") is not (None or ""):

    @ultroid_bot.on(
        NewMsg(
            incoming=True,
        ),
    )
    async def flood_checm(event):
        if await check_if_admin(event):
            return
        limit = get_flood_limit(event.chat_id)
        if not limit:
            return
        count = 1
        if event.chat_id in _check_flood.keys():
            if event.sender_id == [x for x in _check_flood[event.chat_id].keys()][0]:
                count = _check_flood[event.chat_id][event.sender_id]
                _check_flood[event.chat_id] = {event.sender_id: count + 1}
            else:
                _check_flood[event.chat_id] = {event.sender_id: count}
        else:
            _check_flood[event.chat_id] = {event.sender_id: count}
        if _check_flood[event.chat_id][event.sender_id] >= int(limit):
            try:
                await event.client.edit_permissions(
                    event.chat_id, event.sender_id, send_messages=False
                )
                del _check_flood[event.chat_id]
                await event.reply("#AntiFlood\n\n`You have been muted.`")
            except BaseException:
                pass


@ultroid_cmd(
    pattern="setflood ?(\\d+)",
)
async def setflood(e):
    input = e.pattern_match.group(1)
    if not input:
        return await eod(e, "`What?`")
    if not input.isdigit():
        return await eod(e, "`Gwan Myad?`")
    m = set_flood(e.chat_id, input)
    if m:
        return await eod(
            e, f"`Successfully Updated Antiflood Settings to {input} in this chat.`"
        )


@ultroid_cmd(
    pattern="remflood$",
)
async def remove_flood(e):
    hmm = rem_flood(e.chat_id)
    try:
        del _check_flood[e.chat_id]
    except BaseException:
        pass
    if hmm is True:
        return await eod(e, "`Antiflood Settings Disabled`")
    else:
        await eod(e, "`No flood limits in this chat.`")


@ultroid_cmd(
    pattern="getflood$",
)
async def get_flood(e):
    ok = get_flood_limit(e.chat_id)
    if ok:
        return await eod(e, f"`Flood limit for this chat is {ok}.`")
    else:
        await eod(e, "`No flood limits in this chat.`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
