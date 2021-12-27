# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}yta <(youtube) link>`
   Download audio from the link.

• `{i}ytv <(youtube) link>`
   Download video  from the link.

• `{i}ytsa <(youtube) search query>`
   Search and download audio from youtube.

• `{i}ytsv <(youtube) search query>`
   Search and download video from youtube.
"""
from pyUltroid.functions.ytdl import download_yt, get_yt_link

from . import get_string, requests, ultroid_cmd


@ultroid_cmd(
    pattern="yt(a|v|sa|sv) ?(.*)",
)
async def download_from_youtube_(event):
    opt = event.pattern_match.group(1)
    xx = await event.eor(get_string("com_1"))
    if opt == "a":
        ytd = {
            "format": "bestaudio",
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True,
            "outtmpl": "%(id)s.m4a",
        }
        url = event.pattern_match.group(2)
        if not url:
            return await xx.eor(get_string("youtube_1"))
        try:
            requests.get(url)
        except BaseException:
            return await xx.eor(get_string("youtube_2"))
    elif opt == "v":
        ytd = {
            "format": "best",
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True,
            "outtmpl": "%(id)s.mp4",
        }
        url = event.pattern_match.group(2)
        if not url:
            return await xx.eor(get_string("youtube_3"))
        try:
            requests.get(url)
        except BaseException:
            return await xx.eor(get_string("youtube_4"))
    elif opt == "sa":
        ytd = {
            "format": "bestaudio",
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True,
            "outtmpl": "%(id)s.m4a",
        }
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await xx.eor(get_string("youtube_5"))
        url = get_yt_link(query)
        await xx.eor(get_string("youtube_6"))
    elif opt == "sv":
        ytd = {
            "format": "best",
            "addmetadata": True,
            "geo-bypass": True,
            "nocheckcertificate": True,
            "outtmpl": "%(id)s.mp4",
        }
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await xx.eor(get_string("youtube_7"))
        url = get_yt_link(query)
        await xx.eor(get_string("youtube_8"))
    else:
        return
    await download_yt(xx, url, ytd)
