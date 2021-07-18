# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}deez <search query (| flac)>`
    Download songs from Deezer
"""
import os
import time
from json.decoder import JSONDecodeError

import requests as r
from telethon.tl.types import DocumentAttributeAudio

from . import *


@ultroid_cmd(
    pattern="deez ?(.*)",
)
async def siesace(e):
    song = e.pattern_match.group(1)
    if not song:
        return await eod(e, "Give me Something to Search")
    quality = "mp3"
    if "| flac" in song:
        try:
            song = song.split("|")[0]
            quality = "flac"
        except Exception as ex:
            await eod(e, f"`{str(ex)}`")
    hmm = time.time()
    lol = await eor(e, "`Searching on Deezer...`")
    sung = song.replace(" ", "%20")
    url = f"https://jostapi.herokuapp.com/deezer?query={sung}&quality={quality}&count=1"
    try:
        k = (r.get(url)).json()[0]
    except IndexError:
        return await eod(lol, "`Song Not Found.. `")
    except JSONDecodeError:
        return await eod(
            lol, f"`Tell `[sɪᴘᴀᴋ](tg://user?id=1303895686)`to turn on API.`"
        )
    try:
        title = k["title"]
        urrl = k["raw_link"]
        img = k["album"]["cover_xl"]
        duration = k["duration"]
        singers = k["artist"]["name"]
    except Exception as ex:
        return await eod(lol, f"`{str(ex)}`")
    await download_file(urrl, title + "." + quality)
    await download_file(img, title + ".jpg")
    okk = await uploader(
        title + "." + quality,
        title + "." + quality,
        hmm,
        lol,
        "Uploading " + title + "...",
    )
    await e.reply(
        "`" + title + "`" + "\n`From Deezer`",
        file=okk,
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
    os.remove(title + "." + quality)
    os.remove(title + ".jpg")
