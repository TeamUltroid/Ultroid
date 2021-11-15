# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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
from pyUltroid.dB.sudos import add_sudo, del_sudo, is_sudo
from pyUltroid.misc import sudoers
from telethon.tl.types import User
from telethon.utils import get_peer_id

from . import (
    Redis,
    eor,
    get_string,
    get_user_id,
    inline_mention,
    udB,
    ultroid_bot,
    ultroid_cmd,
)


@ultroid_cmd(pattern="addsudo ?(.*)", fullsudo=True)
async def _(ult):
    inputs = ult.pattern_match.group(1)
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id = replied_to.sender_id
        name = await replied_to.get_sender()
    elif inputs:
        id = await get_user_id(inputs)
        try:
            name = await ult.client.get_entity(int(id))
            id = get_peer_id(name)
        except BaseException:
            name = None
    elif ult.is_private:
        id = ult.chat_id
        name = await ult.get_chat()
    else:
        return await eor(ult, get_string("sudo_1"), time=5)
    if name and isinstance(name, User) and (name.bot or name.verified):
        return await eor(ult, get_string("sudo_4"))
    if name:
        name = inline_mention(name)
    else:
        name = f"`{id}`"

    if id == ultroid_bot.uid:
        mmm = get_string("sudo_2")
    elif is_sudo(id):
        mmm = f"{name} `is already a SUDO User ...`"
    elif add_sudo(id):
        udB.set("SUDO", "True")
        sudoers().append(id)
        mmm = f"**Added {name} as SUDO User**"
    else:
        return
    await eor(ult, mmm, time=5)


@ultroid_cmd(pattern="delsudo ?(.*)", fullsudo=True)
async def _(ult):
    inputs = ult.pattern_match.group(1)
    if ult.reply_to_msg_id:
        replied_to = await ult.get_reply_message()
        id = replied_to.sender_id
        name = await replied_to.get_sender()
    elif inputs:
        id = await get_user_id(inputs)
        try:
            name = await ult.client.get_entity(int(id))
            id = get_peer_id(name)
        except BaseException:
            name = None
    elif ult.is_private:
        id = ult.chat_id
        name = await ult.get_chat()
    else:
        return await eor(ult, get_string("sudo_1"), time=5)
    if name:
        name = inline_mention(name)
    else:
        name = f"`{id}`"
    if not is_sudo(id):
        mmm = f"{name} `wasn't a SUDO User ...`"
    elif del_sudo(id):
        sudoers().remove(id)
        mmm = f"**Removed {name} from SUDO User(s)**"
    else:
        return
    await eor(ult, mmm, time=5)


@ultroid_cmd(
    pattern="listsudo$",
)
async def _(ult):
    sudos = Redis("SUDOS")
    if sudos == "" or sudos is None:
        return await eor(ult, get_string("sudo_3"), time=5)
    sumos = sudos.split(" ")
    msg = ""
    for i in sumos:
        try:
            name = await ult.client.get_entity(int(i))
        except BaseException:
            name = None
        if name:
            msg += f"• {inline_mention(name)} ( `{i}` )\n"
        else:
            msg += f"• `{i}` -> Invalid User\n"
    m = udB.get_key("SUDO") or "False"
    if m == "False":
        m = "[False](https://telegra.ph/Ultroid-04-06)"
    return await eor(
        ult, f"**SUDO MODE : {m}\n\nList of SUDO Users :**\n{msg}", link_preview=False
    )
