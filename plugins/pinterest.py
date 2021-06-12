# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}pntrst <link/id>`
    Download and send pinterest pins.
"""


import os
from urllib.request import urlretrieve as donl

from bs4 import BeautifulSoup as bs
from requests import get

from . import *

_base = "https://pinterestdownloader.com/download?url="


def gib_link(link):
    colon = "%3A"
    slash = "%2F"
    if link.startswith("https"):
        return _base + link.replace(":", colon).replace("/", slash)
    else:
        return _base + f"https{colon}{slash}{slash}pin.it{slash}{link}"


@ultroid_cmd(
    pattern="pntrst ?(.*)",
)
async def pinterest(e):
    m = e.pattern_match.group(1)
    get_link = get(gib_link(m)).text
    hehe = bs(get_link, "html.parser")
    hulu = hehe.find_all("a", {"class": "download_button"})
    if len(hulu) < 1:
        return await eod(e, "`Wrong link or private pin.`")
    elif len(hulu) > 1:
        donl(hulu[0]["href"], "pinterest.mp4")
        donl(hulu[1]["href"], "pinterest.jpg")
        await e.delete()
        await e.client.send_file(
            e.chat_id, "pinterest.mp4", thumb="pinterest.jpg", caption=f"Pin:- {m}"
        )
        os.remove("pinterest.mp4")
        os.remove("pinterest.jpg")
    else:
        await e.delete()
        await e.client.send_file(e.chat_id, hulu[0]["href"], caption=f"Pin:- {m}")
