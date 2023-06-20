# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import os
import re

from core.remote import rm
from PIL import Image
from telethon import Button
from telethon.errors.rpcerrorlist import (FilePartLengthInvalidError,
                                          MediaEmptyError)
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telethon.tl.types import InputWebDocument as wb
from utilities.helper import (bash, fast_download, humanbytes, numerize,
                              time_formatter)
from youtubesearchpython import VideosSearch

from . import LOGS, asst, callback, in_pattern, udB

ytt = "https://graph.org/file/afd04510c13914a06dd03.jpg"
_yt_base_url = "https://www.youtube.com/watch?v="
BACK_BUTTON = {}


@in_pattern("yt", owner=True, button={"Youtube": "yt"})
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
    search = VideosSearch(string, limit=50)
    nub = search.result()
    nibba = nub["result"]
    for v in nibba:
        ids = v["id"]
        link = _yt_base_url + ids
        title = v["title"]
        duration = v["duration"]
        views = v["viewCount"]["short"]
        publisher = v["channel"]["name"]
        published_on = v["publishedTime"]
        description = (
            v["descriptionSnippet"][0]["text"]
            if v.get("descriptionSnippet")
            and len(v["descriptionSnippet"][0]["text"]) < 500
            else "None"
        )
        thumb = f"https://i.ytimg.com/vi/{ids}/hqdefault.jpg"
        text = f"**Title: [{title}]({link})**\n\n"
        text += f"`Description: {description}\n\n"
        text += f"「 Duration: {duration} 」\n"
        text += f"「 Views: {views} 」\n"
        text += f"「 Publisher: {publisher} 」\n"
        text += f"「 Published on: {published_on} 」`"
        desc = f"{title}\n{duration}"
        file = wb(thumb, 0, "image/jpeg", [])
        buttons = [
            [
                Button.inline("Audio", data=f"ytdl:audio:{ids}"),
                Button.inline("Video", data=f"ytdl:video:{ids}"),
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
        ]
        BACK_BUTTON.update({ids: {"text": text, "buttons": buttons}})
        results.append(
            await event.builder.article(
                type="photo",
                title=title,
                description=desc,
                thumb=file,
                content=file,
                text=text,
                include_media=True,
                buttons=buttons,
            ),
        )
    await event.answer(results[:50])


@callback(
    re.compile(
        "ytdl:(.*)",
    ),
    owner=True,
)
async def _(e):
    with rm.get("ytdl", helper=True, dispose=True) as mod:
        dler, get_buttons, get_formats = mod.dler, mod.get_buttons, mod.get_formats
    _e = e.pattern_match.group(1).strip().decode("UTF-8")
    _lets_split = _e.split(":")
    _ytdl_data = await dler(e, _yt_base_url + _lets_split[1])
    _data = get_formats(_lets_split[0], _lets_split[1], _ytdl_data)
    _buttons = get_buttons(_data)
    _text = (
        "`Select Your Format.`"
        if _buttons
        else "`Error downloading from YouTube.\nTry Restarting your bot.`"
    )

    await e.edit(_text, buttons=_buttons)


@callback(
    re.compile(
        "ytdownload:(.*)",
    ),
    owner=True,
)
async def _(event):
    with rm.get("ytdl", helper=True, dispose=True) as mod:
        dler = mod.dler
    url = event.pattern_match.group(1).strip().decode("UTF-8")
    lets_split = url.split(":")
    vid_id = lets_split[2]
    artist = description = views = likes = duration = size = title = None
    link = _yt_base_url + vid_id
    format = lets_split[1]
    try:
        ext = lets_split[3]
    except IndexError:
        ext = "mp3"
    if lets_split[0] == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "outtmpl": f"%(id)s.{ext}",
            "logtostderr": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": ext,
                    "preferredquality": format,
                },
                {"key": "FFmpegMetadata"},
            ],
        }

        ytdl_data = await dler(event, link, opts, True)
        title = ytdl_data["title"]
        if ytdl_data.get("artist"):
            artist = ytdl_data["artist"]
        elif ytdl_data.get("creator"):
            artist = ytdl_data["creator"]
        elif ytdl_data.get("channel"):
            artist = ytdl_data["channel"]
        views = numerize(ytdl_data.get("view_count")) or 0
        thumb, _ = await fast_download(ytdl_data["thumbnail"], filename=f"{vid_id}.jpg")

        likes = numerize(ytdl_data.get("like_count")) or 0
        duration = ytdl_data.get("duration") or 0
        description = (
            ytdl_data["description"]
            if len(ytdl_data["description"]) < 100
            else ytdl_data["description"][:100]
        )
        description = description or "None"
        filepath = f"{vid_id}.{ext}"
        if not os.path.exists(filepath):
            filepath = f"{filepath}.{ext}"
        size = os.path.getsize(filepath)
        file, _ = await event.client.fast_uploader(
            filepath,
            filename=f"{title}.{ext}",
            show_progress=True,
            event=event,
            to_delete=True,
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
            "outtmpl": f"%(id)s.{ext}",
            "logtostderr": False,
            "postprocessors": [{"key": "FFmpegMetadata"}],
        }

        ytdl_data = await dler(event, link, opts, True)
        title = ytdl_data["title"]
        if ytdl_data.get("artist"):
            artist = ytdl_data["artist"]
        elif ytdl_data.get("creator"):
            artist = ytdl_data["creator"]
        elif ytdl_data.get("channel"):
            artist = ytdl_data["channel"]
        views = numerize(ytdl_data.get("view_count")) or 0
        thumb, _ = await fast_download(ytdl_data["thumbnail"], filename=f"{vid_id}.jpg")

        try:
            Image.open(thumb).save(thumb, "JPEG")
        except Exception as er:
            LOGS.exception(er)
            thumb = None
        description = (
            ytdl_data["description"]
            if len(ytdl_data["description"]) < 100
            else ytdl_data["description"][:100]
        )
        likes = numerize(ytdl_data.get("like_count")) or 0
        hi, wi = ytdl_data.get("height") or 720, ytdl_data.get("width") or 1280
        duration = ytdl_data.get("duration") or 0
        filepath = f"{vid_id}.mkv"
        if not os.path.exists(filepath):
            filepath = f"{filepath}.webm"
        size = os.path.getsize(filepath)
        file, _ = await event.client.fast_uploader(
            filepath,
            filename=f"{title}.mkv",
            show_progress=True,
            event=event,
            to_delete=True,
        )

        attributes = [
            DocumentAttributeVideo(
                duration=int(duration),
                w=wi,
                h=hi,
                supports_streaming=True,
            ),
        ]
    if not description:
        description = "None"
    text = f"**Title: [{title}]({_yt_base_url}{vid_id})**\n\n"
    text += f"`📝 Description: {description}\n\n"
    text += f"「 Duration: {time_formatter(int(duration)*1000)} 」\n"
    text += f"「 Artist: {artist} 」\n"
    text += f"「 Views: {views} 」\n"
    text += f"「 Likes: {likes} 」\n"
    text += f"「 Size: {humanbytes(size)} 」`"
    button = Button.switch_inline("Search More", query="yt ", same_peer=True)
    try:
        await event.edit(
            text,
            file=file,
            buttons=button,
            attributes=attributes,
            thumb=thumb,
        )
    except (FilePartLengthInvalidError, MediaEmptyError):
        file = await asst.send_message(
            udB.get_key("LOG_CHANNEL"),
            text,
            file=file,
            buttons=button,
            attributes=attributes,
            thumb=thumb,
        )
        await event.edit(text, file=file.media, buttons=button)
    await bash(f"rm {vid_id}.jpg")


@callback(re.compile("ytdl_back:(.*)"), owner=True)
async def ytdl_back(event):
    id_ = event.data_match.group(1).decode("utf-8")
    if not BACK_BUTTON.get(id_):
        return await event.answer("Query Expired! Search again 🔍")
    await event.edit(**BACK_BUTTON[id_])
