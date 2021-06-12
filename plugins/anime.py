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
"""

from os import remove

from . import *


@ultroid_cmd(pattern="airing")
async def airing_anime(event):
    try:
        await eor(event, airing_eps())
    except BaseException:
        msg = airing_eps()
        t = msg.replace("*", "").replace("`", "")
        f = open("animes.txt", "w")
        f.write(t)
        f.close()
        await event.reply(file="animes.txt")
        remove("anime.txt")
        await event.delete()
