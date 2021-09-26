# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}dm <username/id> <reply/type>`
    Direct Message the User.

• `{i}fwdreply <reply to msg>`
    Reply to someone's msg by forwarding it in private.
"""
from . import *


@ultroid_cmd(pattern="dm", fullsudo=True)
async def dm(e):
    if len(e.text) > 3 and e.text[3] != " ":  # weird fix
        return
    if len(e.text.split()) <= 1:
        return await eor(e, get_strings('dm_1'), time=5)
    chat = e.text.split()[1]
    try:
        chat_id = await get_user_id(chat)
    except Exception as ex:
        return await eor(e, f"`{ex}`", time=5)
    if e.reply_to:
        msg = await e.get_reply_message()
    elif len(e.text.split()) > 2:
        msg = e.text.split(maxsplit=2)[2]
    else:
        return await eor(e, get_strings('dm_2'), time=5)
    try:
        await e.client.send_message(chat_id, msg)
        await eor(e, get_strings('dm_3'), time=5)
    except Exception as m:
        await eor(e, get_string("dm_4").format(m, HNDLR), time=5)


@ultroid_cmd(pattern="fwdreply ?(.*)", fullsudo=True)
async def _(e):
    message = e.pattern_match.group(1)
    if not e.reply_to_msg_id:
        return await eor(e, get_string("ex_1"), time=5)
    if not message:
        return await eor(e, get_strings('dm_6'), time=5)
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await eor(e, get_strings('dm_5'), time=5)
