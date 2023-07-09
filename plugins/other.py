# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}send <username/id> <reply/type>`
    send message to User/Chat.

• `{i}fwdreply <reply to msg>`
    Reply to someone's msg by forwarding it in private.

• `{i}save <reply message>`
    Save that replied msg to ur saved messages box.

• `{i}fsave <reply message>`
    Forward that replied msg to ur saved messages.
"""

from . import HNDLR, eod, get_string, ultroid_cmd


@ultroid_cmd(pattern="(send|dm)( (.*)|$)", fullsudo=True)
async def dm(e):
    if len(e.text.split()) <= 1:
        return await e.eor(get_string("dm_1"), time=5)
    chat = e.text.split()[1]
    try:
        chat_id = await e.client.parse_id(chat)
    except Exception as ex:
        return await e.eor(f"`{ex}`", time=5)
    if len(e.text.split()) > 2:
        msg = e.text.split(maxsplit=2)[2]
    elif e.reply_to:
        msg = await e.get_reply_message()
    else:
        return await e.eor(get_string("dm_2"), time=5)
    try:
        _ = await e.client.send_message(chat_id, msg)
        n_, time = get_string("dm_3"), None
        if not _.is_private:
            n_ = f"[{n_}]({_.message_link})"
        await e.eor(n_, time=time)
    except Exception as m:
        await e.eor(get_string("dm_4").format(m, HNDLR), time=5)


@ultroid_cmd(pattern="fwdreply( (.*)|$)", fullsudo=True)
async def _(e):
    message = e.pattern_match.group(1).strip()
    if not e.reply_to_msg_id:
        return await e.eor(get_string("ex_1"), time=5)
    if not message:
        return await e.eor(get_string("dm_6"), time=5)
    msg = await e.get_reply_message()
    fwd = await msg.forward_to(msg.sender_id)
    await fwd.reply(message)
    await e.eor(get_string("dm_5"), time=5)


@ultroid_cmd(pattern="(f|)save$")
async def saf(e):
    x = await e.get_reply_message()
    if not x:
        return await eod(
            e, "Reply to Any Message to save it to ur saved messages", time=5
        )
    if e.pattern_match.group(1).strip() == "f":
        await x.forward_to(e.sender_id)
    else:
        await e.client.send_message(e.sender_id, x)
    await e.eor("Message saved to Your Pm/Saved Messages.", time=5)
