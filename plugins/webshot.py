# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}webshot <url>`
    Get a screenshot of the webpage.

"""
import os

from htmlwebshot import WebShot

from . import *


@ultroid_cmd(pattern="webshot ?(.*)")
async def webss(event):
    xx = await eor(event, get_string("com_1"))
    xurl = e.pattern_match.group(1)
    if not xurl:
        return await eor(xx, "`Give a URL please!`", time=5)
    elif not is_url_ok(xurl):
        return await eor(xx, "Invalid URL!", time=5)
    shot = WebShot(quality=88, flags=["--enable-javascript", "--no-stop-slow-scripts"])
    pic = await shot.create_pic_async(url=xurl)
    await xx.reply(
        f"**WebShot Generated**\n**URL**: {xurl}",
        file=pic,
        link_preview=False,
        force_document=True,
    )
    os.remove(pic)
    await xx.delete()
