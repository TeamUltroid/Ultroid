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


@ultroid_cmd(pattern="dm ?(.*)")
async def dm(e):
    if not e.out and not is_fullsudo(e.sender_id):
        return await eor(e, "`This Command is Full Sudo Restricted..`")
    if len(e.text) > 3:
        if not e.text[3] == " ":  # weird fix
            return
    d = e.pattern_match.group(1)
    c = d.split(" ")
    try:
        chat_id = await get_user_id(c[0])
    except Exception as ex:
        return await eod(e, "`" + str(ex) + "`")
    msg = ""
    masg = await e.get_reply_message()
    if e.reply_to_msg_id:
        await e.client.send_message(chat_id, masg)
        await eod(e, "`⚜️Message Delivered!`")
    for i in c[1:]:
        msg += i + " "
    if msg == "":
        return
    try:
        await e.client.send_message(chat_id, msg)
        await eod(e, "`⚜️Message Delivered!⚜️`")
    except BaseException:
        await eod(e, f"Read Usage : `{HNDLR}help dm`")


@ultroid_cmd(pattern="fwdreply ?(.*)")
async def _(e):
    message = e.pattern_match.group(1)
    if not e.reply_to_msg_id:
        return await eod(e, "`Reply to someone's msg.`")
    if not message:
        return await eod(e, "`No message found to deliver :(`")
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await eod(e, "`Check in Private.`")
