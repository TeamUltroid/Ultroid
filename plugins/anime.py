# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}airing`
   Get details about currently airing anime.
   
• `{i}anime <anime name>` 
   Get anime details from anilist.
"""

from os import remove
import json
import re
import requests
from . import *


@ultroid_cmd(pattern="airing")
async def airing_anime(event):
    try:
        await eor(event, airing_eps())
    except BaseException:
        info = airing_eps()
        t = info.replace("*", "").replace("`", "")
        f = open("animes.txt", "w")
        f.write(t)
        f.close()
        await event.reply(file="animes.txt")
        remove("anime.txt")
        await event.delete()


@ultroid_cmd(pattern="anime ?(.*)")
async def anilist(event):
    name = event.pattern_match.group(1)
    x = await eor(event, get_string("com_1"))
    if not name:
        return await eod(x, "`Enter a anime name!`", time=5)
    banner, title, year, episodes, info = get_anime_src_res(name)
    msg = f"**{title}**\n{year} | {episodes} Episodes.\n\n{info}"
    await event.reply(msg, file=banner, link_preview=True)
    await x.delete()
