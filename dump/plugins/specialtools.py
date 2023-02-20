# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}wspr <username>`
    Send secret message..

• `{i}q <color-optional>`
• `{i}q @username`
• `{i}q r <color-optional>`
• `{i}q count` : `multiple quotes`
    Create quotes..

• `{i}sticker <query>`
    Search Stickers as Per ur Wish..

• `{i}getaudio <reply to an audio>`
    Download Audio To put in ur Desired Video/Gif.

• `{i}addaudio <reply to Video/gif>`
    It will put the above audio to the replied video/gif.

• `{i}dob <date of birth>`
    Put in dd/mm/yy Format only(eg .dob 01/01/1999).

• `{i}wall <query>`
    Search Hd Wallpaper as Per ur Wish..
"""
import os
import time
from datetime import datetime as dt
from random import choice

import pytz
from bs4 import BeautifulSoup as bs
from telethon.tl.types import DocumentAttributeVideo

from pyUltroid.fns.tools import get_google_images, metadata

from . import (
    HNDLR,
    ULTConfig,
    async_searcher,
    bash,
    downloader,
    eod,
    get_string,
    mediainfo,
    quotly,
    ultroid_bot,
    ultroid_cmd,
    uploader,
)
from .beautify import all_col

File = []


import contextlib
@ultroid_cmd(
    pattern="getaudio$",
)
async def daudtoid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_1"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, get_string("spcltool_1"))
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Downloading {dl}...",
    )

    File.append(file.name)
    await xxx.edit(get_string("spcltool_2"))


@ultroid_cmd(
    pattern="addaudio$",
)
async def adaudroid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_3"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith("video"):
        return await eod(e, get_string("spcltool_3"))
    if not (File and os.path.exists(File[0])):
        return await e.edit(f"`First reply an audio with {HNDLR}addaudio`")
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Downloading {dl}...",
    )

    await xxx.edit(get_string("spcltool_5"))
    await bash(
        f'ffmpeg -i "{file.name}" -i "{File[0]}" -shortest -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4'
    )
    out = "output.mp4"
    mmmm = await uploader(out, out, time.time(), xxx, f"Uploading {out}...")
    data = await metadata(out)
    width = data["width"]
    height = data["height"]
    duration = data["duration"]
    attributes = [
        DocumentAttributeVideo(
            duration=duration, w=width, h=height, supports_streaming=True
        )
    ]
    await e.client.send_file(
        e.chat_id,
        mmmm,
        thumb=ULTConfig.thumb,
        attributes=attributes,
        force_document=False,
        reply_to=e.reply_to_msg_id,
    )
    await xxx.delete()
    os.remove(out)
    os.remove(file.name)
    File.clear()
    os.remove(File[0])



@ultroid_cmd(pattern="wall( (.*)|$)")
async def wall(event):
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await event.eor("`Give me something to search..`")
    nn = await event.eor(get_string("com_1"))
    query = f"hd {inp}"
    images = await get_google_images(query)
    for z in range(5):
        await event.client.send_file(event.chat_id, file=images[z]["original"])
    await nn.delete()

