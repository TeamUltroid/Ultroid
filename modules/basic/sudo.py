# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}addsudo`
    Add Sudo Users by replying to user or using <space> separated userid(s)

• `{i}delsudo`
    Remove Sudo Users by replying to user or using <space> separated userid(s)

• `{i}listsudo`
    List all sudo users.
"""

from telethon.tl.types import User

from core import ultroid_bot
from core.decorators import get_sudos, is_sudo
from utilities.helper import inline_mention

from .. import get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="addsudo( (.*)|$)", fullsudo=True)
async def addsudo_func(ult):
    inputs = ult.pattern_match.group(1).strip()
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id_ = replied_to.sender_id
        name = await replied_to.get_sender()
    elif inputs:
        id_ = inputs
        try:
            name = await ult.client.get_entity(inputs)
        except BaseException:
            name = None
    elif ult.is_private:
        id_ = ult.chat_id
        name = await ult.get_chat()
    else:
        return await ult.eor(get_string("sudo_1"), time=5)
    if name and isinstance(name, User) and (name.bot or name.verified):
        return await ult.eor(get_string("sudo_4"))
    name = inline_mention(name) if name else f"`{id_}`"
    if id_ == ultroid_bot.uid:
        mmm = get_string("sudo_2")
    elif is_sudo(id_):
        mmm = f"{name} `is already a SUDO User ...`"
    else:
        udB.set_key("SUDO", "True")
        key = get_sudos()
        key.append(id_)
        udB.set_key("SUDOS", key)
        mmm = f"**Added** {name} **as SUDO User**"
    await ult.eor(mmm, time=5)


@ultroid_cmd(pattern="delsudo( (.*)|$)", fullsudo=True)
async def delsudo_func(ult):
    inputs = ult.pattern_match.group(1).strip()
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id_ = replied_to.sender_id
        name = await replied_to.get_sender()
    elif inputs:
        id_ = inputs
        try:
            name = await ult.client.get_entity(id_)
        except BaseException:
            name = None
    elif ult.is_private:
        id_ = ult.chat_id
        name = await ult.get_chat()
    else:
        return await ult.eor(get_string("sudo_1"), time=5)
    name = inline_mention(name) if name else f"`{id_}`"
    if not is_sudo(id_):
        mmm = f"{name} `wasn't a SUDO User ...`"
    else:
        key = get_sudos()
        key.remove(id_)
        udB.set_key("SUDOS", key)
        mmm = f"**Removed** {name} **from SUDO User(s)**"
    await ult.eor(mmm, time=5)


@ultroid_cmd(
    pattern="listsudo$",
)
async def listsudo_func(ult):
    sudos = get_sudos()
    if not sudos:
        return await ult.eor(get_string("sudo_3"), time=5)
    msg = ""
    for i in sudos:
        try:
            name = await ult.client.get_entity(i)
        except BaseException:
            name = None
        if name:
            msg += f"• {inline_mention(name)} ( `{i}` )\n"
        else:
            msg += f"• `{i}` -> Invalid User\n"
    m = udB.get_key("SUDO")
    if m is not True:
        m = "[False](https://graph.org/Ultroid-04-06)"
    return await ult.eor(
        f"**SUDO MODE : {m}\n\nList of SUDO Users :**\n{msg}", link_preview=False
    )
