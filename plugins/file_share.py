# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

from pyUltroid.functions.tools import get_file_link

from . import asst, eor, udB, ultroid_cmd


@ultroid_cmd(pattern="store")
async def filestoreplg(event):
    msg = await event.get_reply_message()
    if msg is None:
        await eor(event, "`Reply to a message to make a shareable link!`", time=10)
        return
    # allow storing both messages and media.
    filehash = await get_file_link(msg)
    link_to_file = "https://t.me/{}?start={}".format(asst.me.username, filehash)
    await eor(
        event,
        "**File has been stored!**\n\n**Shareable link:** {}".format(link_to_file),
        link_preview=False,
    )


@ultroid_cmd("liststored$")
async def liststored(event):
    get = udB.get_key("FILE_STORE") or {}
    if not get:
        await eor(event, "**No files stored!**", time=5)
        return
    msg = "**Stored files:**\n"
    for c, i in enumerate(list(get.keys())):
        c += 1
        msg += f"`{c}`. https://t.me/{asst.me.username}?start={i}\n"
    if len(msg) > 4095:
        with open("liststored.txt", "w") as f:
            f.write(msg.replace("**", "").replace("`", ""))
        await event.reply("**List of files stored.:**", file="liststored.txt")
        os.remove("liststored.txt")
        return
    await eor(event, msg, link_preview=False)
