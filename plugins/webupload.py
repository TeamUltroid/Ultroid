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

from . import *


@ultroid_cmd(
    pattern="webupload",
)
async def _(event):
    xx = await eor(event, "`Processing...`")
    vv = event.text.split(" ", maxsplit=1)
    try:
        file_name = vv[1]
    except IndexError:
        pass
    if event.reply_to_msg_id:
        bb = await event.get_reply_message()
        if bb.media:
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
        else:
            return await eod(xx, "`Reply to media file`")
    try:
        results = await event.client.inline_query(
            asst.me.username,
            f"fl2lnk {file_name}",
        )
    except rep:
        return await eor(
            xx,
            "`The bot did not respond to the inline query.\nConsider using {}restart`".format(
                HNDLR,
            ),
        )
    except dis:
        return await eor(
            xx,
            "`Please turn on inline mode for your bot from` @Botfather.",
        )
    await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
    await xx.delete()
    await event.delete()
