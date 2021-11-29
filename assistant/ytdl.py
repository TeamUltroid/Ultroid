# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import os
import re

from pyUltroid.functions.helper import bash, fast_download, numerize, time_formatter
from pyUltroid.functions.ytdl import dler, get_buttons, get_formats
from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telethon.tl.types import InputWebDocument as wb
from youtubesearchpython import VideosSearch

from . import callback, in_pattern

ytt = "https://telegra.ph/file/afd04510c13914a06dd03.jpg"
_yt_base_url = "https://www.youtube.com/watch?v="


@in_pattern("yt", owner=True)
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
        text = f"<strong>Title:- <a href={link}>{title}</a></strong>\n"
        text += f"<strong>⏳:-</strong> <code>{duration}</code>\n"
        text += f"<strong>👀:- </strong> <code>{views}</code>\n"
        text += f"<strong>Publisher:- </strong> <code>{publisher}</code>\n"
        text += f"<strong>Published:- </strong> <code>{published_on}</code>\n"
        text += f"<strong>Description:- </strong> <code>{description}</code>"
        desc = f"{title}\n{duration}"
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
                parse_mode="html",
                buttons=[
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
                ],
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
    _e = e.pattern_match.group(1).decode("UTF-8")
    _lets_split = _e.split(":")
    _ytdl_data = await dler(e, _yt_base_url + _lets_split[1])
    _data = get_formats(_lets_split[0], _lets_split[1], _ytdl_data)
    _buttons = get_buttons(_data)
    _text = "`Select Your Format.`"
    if not _buttons:
        _text = "`Error downloading from YouTube.\nTry Restarting your bot.`"
    await e.edit(_text, buttons=_buttons)


@callback(
    re.compile(
        "ytdownload:(.*)",
    ),
    owner=True,
)
async def _(event):
    url = event.pattern_match.group(1).decode("UTF-8")
    lets_split = url.split(":")
    vid_id = lets_split[2]
    link = _yt_base_url + vid_id
    format = lets_split[1]
    ext = lets_split[3]
    if lets_split[0] == "audio":
        opts = {
            "format": str(format),
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "outtmpl": "%(id)s." + ext,
            "logtostderr": False,
        }
        ytdl_data = await dler(event, link, opts, True)
        title = ytdl_data["title"]
        if ytdl_data.get("artist"):
            artist = ytdl_data["artist"]
        elif ytdl_data.get("creator"):
            artist = ytdl_data["creator"]
        elif ytdl_data.get("channel"):
            artist = ytdl_data["channel"]
        views = numerize(ytdl_data["view_count"])
        thumb, _ = await fast_download(ytdl_data["thumbnail"], filename=vid_id + ".jpg")
        likes = numerize(ytdl_data["like_count"])
        duration = ytdl_data["duration"]
        description = (
            ytdl_data["description"]
            if len(ytdl_data["description"]) < 100
            else ytdl_data["description"][:100]
        )
        file, _ = await event.client.fast_uploader(
            vid_id + "." + ext,
            filename=title + "." + ext,
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
            "outtmpl": "%(id)s." + ext,
            "logtostderr": False,
        }
        ytdl_data = await dler(event, link, opts, True)
        title = ytdl_data["title"]
        if ytdl_data.get("artist"):
            artist = ytdl_data["artist"]
        elif ytdl_data.get("creator"):
            artist = ytdl_data["creator"]
        elif ytdl_data.get("channel"):
            artist = ytdl_data["channel"]
        views = numerize(ytdl_data["view_count"])
        thumb, _ = await fast_download(ytdl_data["thumbnail"], filename=vid_id + ".jpg")
        description = (
            ytdl_data["description"]
            if len(ytdl_data["description"]) < 100
            else ytdl_data["description"][:100]
        )
        likes = numerize(ytdl_data["like_count"])
        hi, wi = ytdl_data["height"], ytdl_data["width"]
        duration = ytdl_data["duration"]
        filepath = vid_id + ".mkv"
        if not os.path.exists(filepath):
            filepath = filepath + ".webm"
        file, _ = await event.client.fast_uploader(
            filepath,
            filename=title + ".mkv",
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
    text = f"**Title:** `{title}`\n"
    text += f"**Description:** `{description}`\n\n"
    text += f"`⏳:` `{time_formatter(int(duration)*1000)}`\n"
    text += f"`🎤:` `{artist}`\n"
    text += f"`👀`: `{views}`\n"
    text += f"`👍`: `{likes}`\n"
    await event.edit(
        text,
        file=file,
        buttons=Button.switch_inline("Search More", query="yt ", same_peer=True),
        attributes=attributes,
        thumb=thumb,
    )
    await bash(f"rm {vid_id}.jpg")
