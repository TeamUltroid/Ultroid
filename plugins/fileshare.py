# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}store <reply_to_message>`
   Store the replied message/media and generate a shareable link to that file, to be accessed via your assistant bot!

• `{i}liststored`
   Get all stored messages.
"""

import os

from pyUltroid.dB.filestore_db import get_stored_msg, list_all_stored_msgs
from pyUltroid.functions.tools import get_file_link

from . import asst, eor, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="store$")
async def filestoreplg(event):
    msg = await event.get_reply_message()
    if not msg:
        return await event.eor(get_string("fsh_3"), time=10)
    # allow storing both messages and media.
    filehash = await get_file_link(msg)
    link_to_file = "https://t.me/{}?start={}".format(asst.me.username, filehash)
    await eor(
        event,
        get_string("fsh_2").format(link_to_file),
        link_preview=False,
    )


@ultroid_cmd("delstore ?(.*)")
async def _(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.eor("`Give stored film's link to delete.`", time=5)
    match = match.split("?start=")
    botusername = match[0].split("/")[-1]
    if botusername != asst.me.username:
        return await event.eor(
            "`Message/Media of provided link was not stored by this bot.`", time=5
        )
    msg_id = get_stored_msg(match[1])
    if not msg_id:
        return await event.eor(
            "`Message/Media of provided link was already deleted.`", time=5
        )
    del_stored(match[1])
    msg = await asst.get_messages(udB.get_key("LOG_CHANNEL"), ids=int(msg_id))
    await msg.delete()
    await event.eor("__Deleted__")


@ultroid_cmd("liststored$")
async def liststored(event):
    files = list_all_stored_msgs()
    if not files:
        return await event.eor(get_string("fsh_4"), time=5)
    msg = "**Stored files:**\n"
    for c, i in enumerate(files, start=1):
        msg += f"`{c}`. https://t.me/{asst.me.username}?start={i}\n"
    if len(msg) > 4095:
        with open("liststored.txt", "w") as f:
            f.write(msg.replace("**", "").replace("`", ""))
        await event.reply(get_string("fsh_1"), file="liststored.txt")
        os.remove("liststored.txt")
        return
    await event.eor(msg, link_preview=False)
