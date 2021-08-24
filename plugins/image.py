# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os

from htmlwebshot import WebShot

from . import *


@ultroid_cmd(pattern="image ?(.*)")
async def f2i(e):
    txt = e.pattern_match.group(1)
    if txt:
        html = txt
    elif e.reply_to:
        r = await e.get_reply_message()
        html = await e.client.download_media(r.media)
    else:
        return await eod(e, "`Either reply to any file or give any text`")
    shot = WebShot(quality=85)
    css = "body {background: white;} p {color: red;}"
    pic = await shot.create_pic_async(html=html, css=css)
    try:
        await e.reply(file=pic)
    except BaseException:
        await e.reply(file=pic, force_document=True)
    os.remove(pic)
