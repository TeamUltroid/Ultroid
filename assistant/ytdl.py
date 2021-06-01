# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import os
import re
import time
from urllib.request import urlretrieve

from pyUltroid.functions.all import *
from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telethon.tl.types import InputWebDocument as wb
from youtubesearchpython import VideosSearch

ytt = "https://telegra.ph/file/afd04510c13914a06dd03.jpg"


@in_pattern("yt")
@in_owner
async def _(event):
    try:
        string = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        fuk = event.builder.article(
            title="Search Something",
            thumb=wb(ytt, 0, "image/jpeg", []),
            text="**YᴏᴜTᴜʙᴇ Sᴇᴀʀᴄʜ**\n\nYou didn't search anything",
            buttons=Button.switch_inline(
                "Sᴇᴀʀᴄʜ Aɢᴀɪɴ",
                query="yt ",
                same_peer=True,
            ),
        )
        await event.answer([fuk])
        return
    results = []
    search = VideosSearch(string, limit=10)
    nub = search.result()
    nibba = nub["result"]
    for v in nibba:
        link = v["link"]
        title = v["title"]
        ids = v["id"]
        duration = v["duration"]
        thumb = f"https://img.youtube.com/vi/{ids}/hqdefault.jpg"
        text = f"**•Tɪᴛʟᴇ•** `{title}`\n\n**••[Lɪɴᴋ]({link})••**\n\n**••Dᴜʀᴀᴛɪᴏɴ••** `{duration}`\n\n\n"
        desc = f"Title : {title}\nDuration : {duration}"
        results.append(
            await event.builder.document(
                file=thumb,
                title=title,
                description=desc,
                text=text,
                include_media=True,
                buttons=[
                    [
                        Button.inline("Audio", data=f"ytdl_audio_{link}"),
                        Button.inline("Video", data=f"ytdl_video_{link}"),
                    ],
                    [
                        Button.switch_inline(
                            "Sᴇᴀʀᴄʜ Aɢᴀɪɴ",
                            query="yt ",
                            same_peer=True,
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ",
                            query=f"yt {string}",
                            same_peer=False,
                        ),
                    ],
                ],
            ),
        )
    await event.answer(results)


@callback(re.compile("yt_(.*)"))
@owner
async def _(event):
    url = event.pattern_match.group(1).decode("UTF-8")
    lets_split = url.split("_", maxsplit=1)
    if lets_split[0] == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                },
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        ytdl_data = await dler(event, opts, lets_split[1])
        title = ytdl_data["title"]
        artist = ytdl_data["uploader"]
        urlretrieve(
            f"https://i.ytimg.com/vi/{ytdl_data['id']}/hqdefault.jpg", f"{title}.jpg"
        )
        thumb = f"{title}.jpg"
        duration = ytdl_data["duration"]
        os.rename(f"{ytdl_data['id']}.mp3", f"{title}.mp3")
        c_time = time.time()
        file = await uploader(
            f"{title}.mp3", f"{title}.mp3", c_time, event, "Uploading " + title + "..."
        )
        attributes, file, thumb = await event.client._file_to_media(
            file,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(duration),
                    title=title,
                    performer=artist,
                ),
            ],
            thumb=thumb,
        )

    elif lets_split[0] == "video":
        opts = {
            "format": "bestvideo+bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        ytdl_data = await dler(event, opts, lets_split[1])
        title = ytdl_data["title"]
        artist = ytdl_data["uploader"]
        urlretrieve(
            f"https://i.ytimg.com/vi/{ytdl_data['id']}/hqdefault.jpg", f"{title}.jpg"
        )
        thumb = f"{title}.jpg"
        duration = ytdl_data["duration"]
        os.rename(f"{ytdl_data['id']}.mp4", f"{title}.mp4")
        wi, _ = await bash(f'mediainfo "{title}.mp4" | grep "Width"')
        hi, _ = await bash(f'mediainfo "{title}.mp4" | grep "Height"')
        c_time = time.time()
        file = await uploader(
            f"{title}.mp4", f"{title}.mp4", c_time, event, "Uploading " + title + "..."
        )
        attributes, file, thumb = await event.client._file_to_media(
            file,
            attributes=[
                DocumentAttributeVideo(
                    duration=int(duration),
                    w=wi,
                    h=hi,
                    supports_streaming=True,
                ),
            ],
            thumb=thumb,
        )
    await event.edit(
        f"**{title}\n{time_formatter(int(duration)*1000)}\n{artist}**",
        file=file,
        buttons=Button.switch_inline("Search More", query="yt ", same_peer=True),
    )
    os.system(f"rm {title}*")
