# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}html <reply image>`
    Convert replied image into html.
"""


import os

from img2html.converter import Img2HTMLConverter

from . import *


@ultroid_cmd(
    pattern="html$",
)
async def _(e):
    if not e.reply_to_msg_id:
        return await eor(e, "`Reply to image.`")
    m = await eor(e, "`Converting to html...`")
    img = await (await e.get_reply_message()).download_media()
    converter = Img2HTMLConverter(char="■")
    html = converter.convert(img)
    with open("html.html", "w") as t:
        t.write(html)
    await e.client.send_file(e.chat_id, "html.html", reply_to=e.reply_to_msg_id)
    await m.delete()
    os.remove(img)
    os.remove("html.html")
