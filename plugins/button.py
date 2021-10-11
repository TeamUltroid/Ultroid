# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}button <text with button format`
   create button u can reply to pic also

Format:- `{i}button Hey There! @UseUltroid 😎.
[Ultroid | t.me/theUltroid][Support | t.me/UltroidSupport | same]
[TeamUltroid | t.me/TeamUltroid]`
"""

from pyUltroid.functions.tools import create_tl_btn, get_msg_button
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *
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
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            variable = uf(dl)
            media = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eor(event, get_string("com_4"), time=5)
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            media = "https://telegra.ph" + variable[0]
        else:
            pack_bot_file_id(wt.media)
    if not text:
        text = event.text.split(maxsplit=1)
        if len(text) <= 1:
            return await eor(
                event,
                f"**Please give some text in correct format.**\n\n`{HNDLR}help button`",
            )
        text = text[1]
    text, buttons = get_msg_button(text)
    if buttons:
        buttons = create_tl_btn(buttons)
    return await something(event, text, None, buttons)
