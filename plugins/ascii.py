# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}ascii <reply image>`
    Convert replied image into html.
"""
import os

from htmlwebshot import WebShot
from img2html.converter import Img2HTMLConverter

from . import *


@ultroid_cmd(
    pattern="ascii ?(.*)",
)
async def _(e):
    if not e.reply_to_msg_id:
        return await eor(e, "`Reply to image.`")
    m = await eor(e, "`Converting to html...`")
    img = await (await e.get_reply_message()).download_media()
    char = "■" if not e.pattern_match.group(1) else e.pattern_match.group(1)
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    shot = WebShot(quality=85)
    pic = await shot.create_pic_async(html=html)
    await m.delete()
    await e.reply(file=pic)
    os.remove(pic)
    os.remove(img)
