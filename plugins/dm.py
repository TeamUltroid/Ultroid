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


@ultroid_cmd(pattern="dm ?(.*)", fullsudo=True)
async def dm(e):
    if len(e.text) > 3 and e.text[3] != " ":  # weird fix
        return
    d = e.pattern_match.group(1)
    c = d.split(" ")
    try:
        chat_id = await get_user_id(c[0])
    except Exception as ex:
        return await eor(e, "`" + str(ex) + "`", time=5)
    masg = await e.get_reply_message()
    if e.reply_to_msg_id:
        await e.client.send_message(chat_id, masg)
        await eor(e, "`⚜️Message Delivered!`", time=5)
    msg = "".join(i + " " for i in c[1:])
    if msg == "":
        return
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
