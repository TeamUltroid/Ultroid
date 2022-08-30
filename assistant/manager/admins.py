# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from telethon.errors.rpcerrorlist import UserNotParticipantError

from pyUltroid import _ult_cache

from . import *


@ultroid_cmd(pattern="d(kick|ban)", manager=True, require="ban_users")
async def dowj(e):
    replied = await e.get_reply_message()
    if replied:
        user = replied.sender_id
    else:
        return await e.eor("Reply to a message...")
    try:
        await replied.delete()
        if e.pattern_match.group(1).strip() == "kick":
            await e.client.kick_participant(e.chat_id, user)
            te = "Kicked"
        else:
            await e.client.edit_permissions(e.chat_id, user, view_messages=False)
            te = "Banned"
        await e.eor(f"{te} Successfully!")
    except Exception as E:
        await e.eor(str(E))


@callback(re.compile("cc_(.*)"), func=_ult_cache.get("admin_callback"))
async def callback_(event):
    data = event.data_match.group(1).decode("utf-8")
    if data not in _ult_cache.get("admin_callback", {}):
        return
    try:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
    except UserNotParticipantError:
        return await event.answer("Join the Group First!", alert=True)
    if not perm.is_admin:
        return await event.answer("You are not an Admin!", alert=True)
    _ult_cache["admin_callback"].update({data: (event.sender, perm)})
    await event.answer("Verification Done!")
    await event.delete()
