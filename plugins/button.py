# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_button")

import os

from . import upload_file as uf
from telethon.utils import pack_bot_file_id

from pyUltroid.fns.tools import create_tl_btn, get_msg_button

from . import HNDLR, get_string, mediainfo, ultroid_cmd
from ._inline import something


@ultroid_cmd(pattern="button")
async def butt(event):
    media, wut, text = None, None, None
    if event.reply_to:
        wt = await event.get_reply_message()
        if wt.text:
            text = wt.text
        if wt.media:
            wut = mediainfo(wt.media)
        if wut and wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            media = uf(dl)
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await event.eor(get_string("com_4"), time=5)
            dl = await wt.download_media()
            media = uf(dl)
            os.remove(dl)
        else:
            media = pack_bot_file_id(wt.media)
    try:
        text = event.text.split(maxsplit=1)[1]
    except IndexError:
        if not text:
            return await event.eor(
                f"**Please give some text in correct format.**\n\n`{HNDLR}help button`",
            )
    text, buttons = get_msg_button(text)
    if buttons:
        buttons = create_tl_btn(buttons)
    await something(event, text, media, buttons)
    await event.delete()
