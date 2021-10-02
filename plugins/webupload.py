# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}webupload`
    Upload files on another server.
"""

import time

from telethon.errors.rpcerrorlist import BotInlineDisabledError as dis
from telethon.errors.rpcerrorlist import BotResponseTimeoutError as rep

from . import HNDLR, asst, downloader, eor, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="webupload",
)
async def _(event):
    xx = await eor(event, get_string("com_1"))
    vv = event.text.split(" ", maxsplit=1)
    try:
        file_name = vv[1]
    except IndexError:
        return await eor(xx, get_string("wbl_1"))
    bb = await event.get_reply_message()
    if not (bb and bb.media):
        return await eor(xx, get_string("cvt_3"))
    ccc = time.time()
    try:
        naam = await downloader(
            bb.file.name,
            bb.media.document,
            xx,
            ccc,
            "Downloading " + bb.file.name + "...",
        )
        file_name = naam.name
    except BaseException:
        file_name = await event.client.download_media(bb)
    try:
        results = await event.client.inline_query(
            asst.me.username,
            f"fl2lnk {file_name}",
        )
    except rep:
        return await eor(
            xx,
            get_string("help_2").format(
                HNDLR,
            ),
        )
    except dis:
        return await eor(
            xx,
            get_string("help_3"),
        )
    await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
    await xx.delete()
    await event.delete()
