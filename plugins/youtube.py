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

from youtube_dl import YoutubeDL

from . import *


@ultroid_cmd(pattern="yt(a|v|sa|sv) ?(.*)")
async def download_from_youtube_(event):
    opt = event.pattern_match.group(1)
    if opt == "a":
        ytd = YoutubeDL(
            {
                "format": "bestaudio",
                "writethumbnail": True,
                "addmetadata": True,
                "geo-bypass": True,
                "nocheckcertificate": True,
                "outtmpl": "%(id)s.mp3",
            }
        )
        url = event.pattern_match.group(2)
        if not url:
            return await eor(event, "Give me a (youtube) URL to download audio from!")
        try:
            request.get(url)
        except BaseException:
            return await eor(event, "`Give A Direct Audio Link To Download`")
        xx = await eor(event, get_string("com_1"))
    elif opt == "v":
        ytd = YoutubeDL(
            {
                "format": "best",
                "writethumbnail": True,
                "addmetadata": True,
                "geo-bypass": True,
                "nocheckcertificate": True,
                "outtmpl": "%(id)s.mp4",
            }
        )
        url = event.pattern_match.group(2)
        if not url:
            return await eor(event, "Give me a (youtube) URL to download video from!")
        try:
            request.get(url)
        except BaseException:
            return await eor(event, "`Give A Direct Video Link To Download`")
        xx = await eor(event, get_string("com_1"))
    elif opt == "sa":
        ytd = YoutubeDL(
            {
                "format": "bestaudio",
                "writethumbnail": True,
                "addmetadata": True,
                "geo-bypass": True,
                "nocheckcertificate": True,
                "outtmpl": "%(id)s.mp3",
            }
        )
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await eor(
                event, "Give me a (youtube) search query to download audio from!"
            )
        xx = await eor(event, "`Searching on YouTube...`")
        url = await get_yt_link(query)
        await xx.edit("`Downloading audio song...`")
    elif opt == "sv":
        ytd = YoutubeDL(
            {
                "format": "best",
                "writethumbnail": True,
                "addmetadata": True,
                "geo-bypass": True,
                "nocheckcertificate": True,
                "outtmpl": "%(id)s.mp4",
            }
        )
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await eor(
                event, "Give me a (youtube) search query to download video from!"
            )
        xx = await eor(event, "`Searching YouTube...`")
        url = await get_yt_link(query)
        await xx.edit("`Downloading video song...`")
    else:
        return
    await download_yt(xx, event, url, ytd)
