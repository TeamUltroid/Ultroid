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

from numerize import numerize
from pyUltroid.functions.all import *
from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telethon.tl.types import InputWebDocument as wb
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

ytt = "https://telegra.ph/file/afd04510c13914a06dd03.jpg"
_yt_base_url = "https://www.youtube.com/watch?v="


@in_pattern("yt")
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
        ids = v["id"]
        link = _yt_base_url + ids
        title = v["title"]
        duration = v["duration"]
        thumb = f"https://i.ytimg.com/vi/{ids}/hqdefault.jpg"
        text = f"**•Tɪᴛʟᴇ•** `{title}`\n\n**••[Lɪɴᴋ]({link})••**\n\n**••Dᴜʀᴀᴛɪᴏɴ••** `{duration}`\n\n\n"
        desc = f"Title : {title}\nDuration : {duration}"
        file = wb(thumb, 0, "image/jpeg", [])
        results.append(
            await event.builder.article(
                type="photo",
                title=title,
                description=desc,
                thumb=file,
                content=file,
                text=text,
                include_media=True,
                buttons=[
                    [
                        Button.inline("Audio", data=f"ytdl_audio_{ids}"),
                        Button.inline("Video", data=f"ytdl_video_{ids}"),
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
    await event.answer(results[:50])


@callback(
    re.compile(
        "ytdl_(.*)",
    ),
)
@owner
async def _(e):
    _e = e.pattern_match.group(1).decode("UTF-8")
    _lets_split = _e.split("_", maxsplit=1)
    _ytdl_data = await dler(e, _yt_base_url + _lets_split[1])
    _data = get_data(_lets_split[0], _ytdl_data)
    _buttons = get_buttons(
        "ytdownload_" + _lets_split[0] + "_" + _lets_split[1] + ":", _data
    )
    _text = "`Select Your Format.`"
    if not _buttons:
        _text = "`Error downloading from YouTube.\nTry Restarting your bot.`"
    await e.edit(_text, buttons=_buttons)


@callback(
    re.compile(
        "ytdownload_(.*)",
    ),
)
@owner
async def _(event):
    url = event.pattern_match.group(1).decode("UTF-8")
    lets_split = url.split("_", maxsplit=1)
    vid_id = lets_split[1].split(":")[0]
    link = _yt_base_url + vid_id
    format = url.split(":")[1]
    if lets_split[0] == "audio":
        opts = {
            "format": str(format),
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        ytdl_data = await dler(event, link)
        YoutubeDL(opts).download([link])
        title = ytdl_data["title"]
        artist = ytdl_data["uploader"]
        views = numerize.numerize(ytdl_data["view_count"])
        urlretrieve(f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg", f"{title}.jpg")
        thumb = f"{title}.jpg"
        duration = ytdl_data["duration"]
        os.rename(f"{ytdl_data['id']}.mp3", f"{title}.mp3")
        c_time = time.time()
        file = await uploader(
            f"{title}.mp3", f"{title}.mp3", c_time, event, "Uploading " + title + "..."
        )
        attributes = [
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=artist,
            ),
        ]
    elif lets_split[0] == "video":
        opts = {
            "format": str(format),
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        ytdl_data = await dler(event, link)
        YoutubeDL(opts).download([link])
        title = ytdl_data["title"]
        artist = ytdl_data["uploader"]
        views = numerize.numerize(ytdl_data["view_count"])
        urlretrieve(f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg", f"{title}.jpg")
        thumb = f"{title}.jpg"
        duration = ytdl_data["duration"]
        try:
            os.rename(f"{ytdl_data['id']}.mp4", f"{title}.mp4")
        except FileNotFoundError:
            try:
                os.rename(f"{ytdl_data['id']}.mkv", f"{title}.mp4")
            except FileNotFoundError:
                os.rename(f"{ytdl_data['id']}.webm", f"{title}.mp4")
        except Exception as ex:
            return await event.edit(str(ex))
        wi, _ = await bash(f'mediainfo "{title}.mp4" | grep "Width"')
        hi, _ = await bash(f'mediainfo "{title}.mp4" | grep "Height"')
        c_time = time.time()
        file = await uploader(
            f"{title}.mp4", f"{title}.mp4", c_time, event, "Uploading " + title + "..."
        )
        attributes = [
            DocumentAttributeVideo(
                duration=int(duration),
                w=int(wi.split(":")[1].split()[0]),
                h=int(hi.split(":")[1].split()[0]),
                supports_streaming=True,
            ),
        ]
    text = f"**Title:** `{title}`\n"
    text += f"**Duration:** `{time_formatter(int(duration)*1000)}`\n"
    text += f"**Views:** `{views}`\n"
    text += f"**Artist:** `{artist}`\n\n"
    await event.edit(
        text,
        file=file,
        buttons=Button.switch_inline("Search More", query="yt ", same_peer=True),
        attributes=attributes,
        thumb=thumb,
    )
    os.system(f'rm "{title}"*')
