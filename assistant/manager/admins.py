# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from pyUltroid import _ult_cache
from telethon.errors.rpcerrorlist import UserNotParticipantError

from . import *


@ultroid_cmd(pattern="d(kick|ban)", manager=True)
async def dowj(e):
    replied = await e.get_reply_message()
    if replied:
        user = replied.sender_id
    else:
        return await eor(e, "Reply to a message...")
    try:
        await replied.delete()
        if e.pattern_match.group(1) == "kick":
            await e.client.kick_participant(e.chat_id, user)
            te = "Kicked"
        else:
            await e.client.edit_permissions(e.chat_id, user, view_messages=False)
            te = "Banned"
        await eor(e, f"{te} Successfully!")
    except Exception as E:
        await eor(e, str(E))
