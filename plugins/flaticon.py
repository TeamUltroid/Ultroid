# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


"""
✘ Commands Available

• `{i}icon <query>`
    Icon search from flaticon.com and uploading as sticker.
"""

import os
import random

from bs4 import BeautifulSoup as bs

from . import LOGS, async_searcher, download_file, get_string, ultroid_cmd


@ultroid_cmd(pattern="icon ?(.*)")
async def www(e):
    a = e.pattern_match.group(1)
    if not a:
        return await e.eor("Give some Text to Get Icon from Flaticon.com")
    tt = await e.eor(get_string("com_1"))
    query = a.replace(" ", "%20")
    try:
        link = f"https://www.flaticon.com/search?word={query}"
        ge = await async_searcher(link)
        cl = bs(ge, "html.parser", from_encoding="utf-8")
        results = cl.find_all(
            "img", src="https://media.flaticon.com/dist/min/img/loader.gif"
        )
        dome = results[random.randrange(0, len(results) - 1)]["data-src"]
        await download_file(dome, "sticker.webp")
        await e.reply(file="sticker.webp")
        os.remove("sticker.webp")
        await tt.delete()
    except Exception as E:
        LOGS.info(E)
        await tt.edit("`No Results Found`")
