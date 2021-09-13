# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

`{i}image <text or reply to html or any doc file>`
   Creates image from html and any text.

"""

import os

from htmlwebshot import WebShot

from . import *


@ultroid_cmd(pattern="image ?(.*)")
async def f2i(e):
    txt = e.pattern_match.group(1)
    if txt:
        html = e.text.split(maxsplit=1)[1]
    elif e.reply_to:
        r = await e.get_reply_message()
        if r.media:
            html = await e.client.download_media(r.media)
        elif r.text:
            html = r.text
    else:
        return await eod(e, "`Either reply to any file or give any text`")
    html = html.replace("\n", "<br>")
    shot = WebShot(quality=85)
    css = "body {background: white;} p {color: red;}"
    pic = await shot.create_pic_async(html=html, css=css)
    try:
        await e.reply(file=pic)
    except BaseException:
        await e.reply(file=pic, force_document=True)
    os.remove(pic)
    if os.path.exists(html):
        os.remove(html)
