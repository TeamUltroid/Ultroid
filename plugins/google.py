# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}google <query>`
    For doing google search.

• `{i}img <query>`
  `{i}img <query> ; <no of results>`
    For doing Images search.

• `{i}reverse <query>`
    Reply an Image or sticker to find its sauce.
"""
import os
from shutil import rmtree

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from pyUltroid.functions.google_image import googleimagesdownload
from pyUltroid.functions.misc import google_search

from strings import get_string

from . import *


@ultroid_cmd(
    pattern="google ?(.*)",
    type=["official", "manager"],
)
async def google(event):
    inp = event.pattern_match.group(1)
    if not inp:
        return await eod(event, "`Give something to search..`")
    x = await eor(event, get_string("com_2"))
    gs = await google_search(inp)
    if len(gs) == 0:
        return await eod(x, f"`Can't find anything about {inp}`")
    out = ""
    for res in gs:
        text = res["title"]
        url = res["link"]
        des = res["description"]
        out += f" 👉🏻  [{text}]({url})\n`{des}`\n\n"
    omk = f"**Google Search Query:**\n`{inp}`\n\n**Results:**\n{out}"
    await eor(x, omk, link_preview=False)


@ultroid_cmd(pattern="img ?(.*)")
async def goimg(event):
    query = event.pattern_match.group(1)
    if not query:
        return await eor(event, "`Give something to search...`")
    nn = await eor(event, "`Processing Keep Patience...`")
    lmt = 5
    if ";" in query:
        try:
            lmt = int(query.split(";")[1])
            query = query.split(";")[0]
        except BaseException:
            pass
    try:
        gi = googleimagesdownload()
        args = {
            "keywords": query,
            "limit": lmt,
            "format": "jpg",
            "output_directory": "./resources/downloads/",
        }
        pth = gi.download(args)
        ok = pth[0][query]
    except BaseException:
        return await nn.edit("No Results Found :(")
    await event.reply(file=ok, message=query)
    rmtree(f"./resources/downloads/{query}/")
    await nn.delete()


@ultroid_cmd(pattern="reverse$")
async def reverse(event):
    reply = await event.get_reply_message()
    if not reply:
        return await eor(event, "`Reply to an Image`")
    ult = await eor(event, "`Processing...`")
    dl = await reply.download_media()
    img = Image.open(dl)
    x, y = img.size
    file = {"encoded_image": (dl, open(dl, "rb"))}
    grs = requests.post(
        "https://www.google.com/searchbyimage/upload",
        files=file,
        allow_redirects=False,
    )
    loc = grs.headers.get("Location")
    response = requests.get(
        loc,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
        },
    )
    xx = bs(response.text, "html.parser")
    div = xx.find_all("div", {"class": "r5a77d"})[0]
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
        event.chat_id,
        ok,
        album=True,
        caption="Similar Images Realted to Search",
    )
    rmtree(f"./resources/downloads/{text}/")
    os.remove(dl)
