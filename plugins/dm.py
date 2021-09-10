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
    if not len(e.text.split()) > 1:
        return await eor(e, "`Give Chat username or id where to send.`", time=5)
    chat = e.text.split()[1]
    try:
        chat_id = await get_user_id(chat)
    except Exception as ex:
        return await eor(e, "`" + str(ex) + "`", time=5)
    if e.reply_to:
        msg = await e.get_reply_message()
    elif len(e.text.split()) > 2:
        msg = e.text.split(maxsplit=2)[2]
    else:
        return await eor(e, "`Give text to send or reply to msg`", time=5)
    try:
        await e.client.send_message(chat_id, msg)
        await eor(e, "`⚜️Message Delivered!⚜️`", time=5)
    except Exception as m:
        await eor(e, f"Error - {m}\nRead Usage : `{HNDLR}help dm`", time=5)


@ultroid_cmd(pattern="fwdreply ?(.*)", fullsudo=True)
async def _(e):
    message = e.pattern_match.group(1)
    if not e.reply_to_msg_id:
        return await eor(e, "`Reply to someone's msg.`", time=5)
    if not message:
        return await eor(e, "`No message found to deliver :(`", time=5)
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await eor(e, "`Check in Private.`", time=5)
