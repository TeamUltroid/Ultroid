# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import asyncio
import os
import re
import time

from pyUltroid.functions.all import *
from telethon import Button
from telethon.tl.types import DocumentAttributeAudio
from telethon.tl.types import InputWebDocument as wb
from youtube_dl import YoutubeDL
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
                        Button.inline("Audio", data=f"audio{link}"),
                        Button.inline("Video", data=f"video{link}"),
                    ],
                    [
                        Button.switch_inline(
                            "Sᴇᴀʀᴄʜ Aɢᴀɪɴ", query="yt ", same_peer=True
                        ),
                        Button.switch_inline(
                            "Sʜᴀʀᴇ", query=f"yt {string}", same_peer=False
                        ),
                    ],
                ],
            )
        )
    await event.answer(results)


@callback(re.compile("audio(.*)"))
@owner
async def _(sur):
    url = sur.pattern_match.group(1).decode("UTF-8")
    getter = sur.sender_id
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }
    song = True
    await dler(sur)
    with YoutubeDL(opts) as ytdl:
        ytdl_data = ytdl.extract_info(url)

    jpg = f"{ytdl_data['id']}.mp3.jpg"
    png = f"{ytdl_data['id']}.mp3.png"
    webp = f"{ytdl_data['id']}.mp3.webp"
    dir = os.listdir()

    if jpg in dir:
        thumb = jpg
    elif png in dir:
        thumb = png
    elif webp in dir:
        thumb = webp
    else:
        thumb = None

    c_time = time.time()
    if song:
        await sur.edit(
            f"`Preparing to upload song:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*"
        )
        await asst.send_file(
            getter,
            f"{ytdl_data['id']}.mp3",
            thumb=thumb,
            caption=f"**{ytdl_data['title']}\n{time_formatter((ytdl_data['duration'])*1000)}\n{ytdl_data['uploader']}**",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(ytdl_data["duration"]),
                    title=str(ytdl_data["title"]),
                    performer=str(ytdl_data["uploader"]),
                )
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, sur, c_time, "Uploading..", f"{ytdl_data['title']}.mp3")
            ),
        )
        os.system(f"rm {ytdl_data['id']}.mp*")
        await sur.edit(
            f"Get Your requested file **{ytdl_data['title']}** from here {Var.BOT_USERNAME} ",
            buttons=Button.switch_inline("Search More", query="yt ", same_peer=True),
        )


@callback(re.compile("video(.*)"))
@owner
async def _(fuk):
    url = fuk.pattern_match.group(1).decode("UTF-8")
    getter = fuk.sender_id
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    video = True
    await dler(fuk)
    with YoutubeDL(opts) as ytdl:
        ytdl_data = ytdl.extract_info(url)

    c_time = time.time()
    if video:
        await fuk.edit(
            f"`Preparing to upload video:`\
        \n**{ytdl_data['title']}**\
        \nby *{ytdl_data['uploader']}*"
        )
        await asst.send_file(
            getter,
            f"{ytdl_data['id']}.mp4",
            thumb=f"./resources/extras/ultroid.jpg",
            caption=f"**{ytdl_data['title']}\n{time_formatter((ytdl_data['duration'])*1000)}\n{ytdl_data['uploader']}**",
            supports_streaming=True,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, fuk, c_time, "Uploading..", f"{ytdl_data['title']}.mp4")
            ),
        )
        os.remove(f"{ytdl_data['id']}.mp4")
        await fuk.edit(
            f"Get Your requested file **{ytdl_data['title']}** from here {Var.BOT_USERNAME} ",
            buttons=Button.switch_inline("Search More", query="yt ", same_peer=True),
        )
