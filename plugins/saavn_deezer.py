# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}saavn <search query>`
    Download songs from Saavn

• `{i}deez <search query>`
    Download songs from Deezer
"""

import os
import time
from urllib.request import urlretrieve

import requests as r
from telethon.tl.types import DocumentAttributeAudio

from . import *


@ultroid_cmd(pattern="deez ?(.*)")
async def siesace(e):
    song = e.pattern_match.group(1)
    if not song:
        return await eod(e, "`Give me Something to Search")
    hmm = time.time()
    lol = await eor(e, "`Searching on Deezer...`")
    sung = song.replace(" ", "%20")
    url = f"https://thearq.tech/deezer?query={sung}&count=1"
    try:
        k = (r.get(url)).json()[0]
    except IndexError:
        return await eod(lol, "`Song Not Found.. `")
    title = k["title"]
    urrl = k["url"]
    img = k["thumbnail"]
    duration = k["duration"]
    singers = k["artist"]
    urlretrieve(urrl, title + ".mp3")
    urlretrieve(img, title + ".jpg")
    okk = await uploader(
        title + ".mp3", title + ".mp3", hmm, lol, "Uploading " + title + "..."
    )
    await ultroid_bot.send_file(
        e.chat_id,
        okk,
        caption="`" + title + "`" + "\n`From Deezer`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=singers,
            )
        ],
        supports_streaming=True,
        thumb=title + ".jpg",
    )
    await lol.delete()
    os.remove(title + ".mp3")
    os.remove(title + ".jpg")


@ultroid_cmd(pattern="saavn ?(.*)")
async def siesace(e):
    song = e.pattern_match.group(1)
    if not song:
        return await eod(e, "`Give me Something to Search")
    hmm = time.time()
    lol = await eor(e, "`Searching on Saavn...`")
    sung = song.replace(" ", "%20")
    url = f"https://jostapi.herokuapp.com/saavn?query={sung}"
    try:
        k = (r.get(url)).json()[0]
    except IndexError:
        return await eod(lol, "`Song Not Found.. `")
    title = k["song"]
    urrl = k["media_url"]
    img = k["image"]
    duration = k["duration"]
    singers = k["singers"]
    urlretrieve(urrl, title + ".mp3")
    urlretrieve(img, title + ".jpg")
    okk = await uploader(
        title + ".mp3", title + ".mp3", hmm, lol, "Uploading " + title + "..."
    )
    await ultroid_bot.send_file(
        e.chat_id,
        okk,
        caption="`" + title + "`" + "\n`From Saavn`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=singers,
            )
        ],
        supports_streaming=True,
        thumb=title + ".jpg",
    )
    await lol.delete()
    os.remove(title + ".mp3")
    os.remove(title + ".jpg")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
