# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -
• `{i}google <query>`
    For doing google search.
• `{i}img <query>`
    For doing Images search.
• `{i}p <query>`
    Reply an Image or sticker to find its sauce.
"""

import os
from shutil import rmtree

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from search_engine_parser import *

from . import *

@ultroid_cmd(pattern="p")
async def reverse(event):
    reply = await event.get_reply_message()
    if not reply:
        return await eor(event, "`Reply to any Image`")
    ult = await eor(event, "`Processing...`")
    dl = await bot.download_media(reply)
    img = Image.open(dl)
    x, y = img.size
    file = {"encoded_image": (dl, open(dl, "rb"))}
    grs = requests.post(
        "https://www.google.com/searchbyimage/upload", files=file, allow_redirects=False
    )
    loc = grs.headers.get("Location")
    response = requests.get(
        loc,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
        },
    )
    xx = bs(response.text, "html.parser")
    div = xx.find("div", {"class": "r5a77d"})
    alls = div.find("a")
    link = alls["href"]
    text = alls.text
    await ult.edit(f"`Dimension ~ {x} : {y}`\nSauce ~ [{text}](google.com{link})")
    gi = googleimagesdownload()
    args = {
        "keywords": text,
        "limit": 2,
        "format": "jpg",
        "output_directory": "./resources/downloads/",
    }
    pth = gi.download(args)
    ok = pth[0][text]
    await event.client.send_file(
        event.chat_id, ok, album=True, caption="/protecc"
    )
    rmtree(f"./resources/downloads/{text}/")
    os.remove(dl)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=Var.HNDLR)}"})
