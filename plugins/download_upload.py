# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}ul <path/to/file>`
    Upload file to telegram chat.
    You Can Upload Folders too.

• `{i}ul <path/to/file> (| stream)`
    Upload files as stream.

• `{i}dl <filename(optional)>`
    Reply to file to download.

• `{i}download <DDL> (| filename)`
    Download using DDL. Will autogenerate filename if not given.

"""
import asyncio
import glob
import os
import time
from datetime import datetime as dt

from aiohttp.client_exceptions import InvalidURL
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

from . import *


@ultroid_cmd(
    pattern="download ?(.*)",
)
async def down(event):
    matched = event.pattern_match.group(1)
    msg = await eor(event, "`Trying to download...`")
    if not matched:
        return await eor(msg, "`You forgot to give link :(`", time=5)
    try:
        splited = matched.split(" | ")
        link = splited[0]
        filename = splited[1]
    except IndexError:
        filename = None
    s_time = time.time()
    try:
        filename = await fast_download(
            link,
            filename,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    msg,
                    s_time,
                    f"Downloading from {link}",
                )
            ),
        )
    except InvalidURL:
        return await eor(msg, "`Invalid URL provided :(`", time=5)
    await eor(msg, f"`{filename} `downloaded.")


@ultroid_cmd(
    pattern="dl ?(.*)",
)
async def download(event):
    if not event.reply_to_msg_id:
        return await eor(event, "`Reply to a Media Message`")
    xx = await eor(event, get_string("com_1"))
    s = dt.now()
    k = time.time()
    if event.reply_to_msg_id:
        ok = await event.get_reply_message()
        if not ok.media:
            return await eor(xx, get_string("udl_1"), time=5)
        if hasattr(ok.media, "document"):
            file = ok.media.document
            mime_type = file.mime_type
            filename = event.pattern_match.group(1) or ok.file.name
            if not filename:
                if "audio" in mime_type:
                    filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
                elif "video" in mime_type:
                    filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
            try:
                result = await downloader(
                    "resources/downloads/" + filename,
                    file,
                    xx,
                    k,
                    "Downloading " + filename + "...",
                )
            except MessageNotModifiedError as err:
                return await xx.edit(str(err))
            file_name = result.name
        else:
            d = "resources/downloads/"
            file_name = await event.client.download_media(
                ok,
                d,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d,
                        t,
                        xx,
                        k,
                        "Downloading...",
                    ),
                ),
            )
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if t != "":
        await eor(xx, get_string("udl_2").format(file_name, t))
    else:
        await eor(xx, f"Downloaded `{file_name}` in `0 second(s)`")


@ultroid_cmd(
    pattern="ul ?(.*)",
)
async def download(event):
    if event.text[1:].startswith("ultroid"):
        return
    xx = await eor(event, get_string("com_1"))
    hmm = event.pattern_match.group(1)
    try:
        kk = hmm.split(" | stream")[0]
    except BaseException:
        pass
    try:
        title = kk.split("/")[-1]
    except BaseException:
        title = hmm
    s = dt.now()
    tt = time.time()
    if not kk:
        return await eor(xx, get_string("udl_3"), time=5)
    if os.path.isdir(kk):
        if not os.listdir(kk):
            return await eor(xx, "`This Directory is Empty.`", time=5)
        ok = glob.glob(f"{kk}/*")
        kk = [*sorted(ok)]
        for kk in kk:
            tt = time.time()
            try:
                try:
                    res = await uploader(kk, kk, tt, xx, f"Uploading {kk}...")
                except MessageNotModifiedError as err:
                    return await xx.edit(str(err))
                title = kk.split("/")[-1]
                if (
                    title.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac"))
                    and " | stream" in hmm
                ):
                    metadata = extractMetadata(createParser(res.name))
                    wi = 512
                    hi = 512
                    duration = 0
                    artist = ""
                    try:
                        if metadata.has("width"):
                            wi = metadata.get("width")
                        if metadata.has("height"):
                            hi = metadata.get("height")
                        if metadata.has("duration"):
                            duration = metadata.get("duration").seconds
                        if metadata.has("artist"):
                            artist = metadata.get("artist")
                        else:
                            artist = udB.get("artist") or ultroid_bot.first_name
                    except AttributeError:
                        return await event.client.send_file(
                            event.chat_id,
                            res,
                            caption=f"`{kk}/{title}`",
                            supports_streaming=True,
                        )
                    if res.name.endswith((".mkv", ".mp4", ".avi", "webm")):
                        attributes = [
                            DocumentAttributeVideo(
                                w=wi, h=hi, duration=duration, supports_streaming=True
                            )
                        ]
                    elif res.name.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                        attributes = [
                            DocumentAttributeAudio(
                                duration=duration,
                                title=title.split(".")[0],
                                performer=artist,
                            )
                        ]
                    else:
                        attributes = None
                    try:
                        await event.client.send_file(
                            event.chat_id,
                            res,
                            caption=f"`{kk}`",
                            attributes=attributes,
                            supports_streaming=True,
                            thumb="resources/extras/ultroid.jpg",
                        )
                    except BaseException:
                        await event.client.send_file(
                            event.chat_id,
                            res,
                            caption=f"`{kk}`",
                            thumb="resources/extras/ultroid.jpg",
                        )
                else:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{kk}`",
                        force_document=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
            except Exception as ve:
                return await eor(xx, str(ve))
    else:
        try:
            try:
                res = await uploader(kk, kk, tt, xx, f"Uploading {kk}...")
            except MessageNotModifiedError as err:
                return await xx.edit(str(err))
            if title.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                hmm = " | stream"
            if " | stream" in hmm:
                metadata = extractMetadata(createParser(res.name))
                wi = 512
                hi = 512
                duration = 0
                artist = ""
                try:
                    if metadata.has("width"):
                        wi = metadata.get("width")
                    if metadata.has("height"):
                        hi = metadata.get("height")
                    if metadata.has("duration"):
                        duration = metadata.get("duration").seconds
                    if metadata.has("artist"):
                        artist = metadata.get("artist")
                    else:
                        artist = udB.get("artist") or ultroid_bot.first_name
                except AttributeError:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        supports_streaming=True,
                    )
                if res.name.endswith((".mkv", ".mp4", ".avi", "webm")):
                    attributes = [
                        DocumentAttributeVideo(
                            w=wi, h=hi, duration=duration, supports_streaming=True
                        )
                    ]
                elif res.name.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                    attributes = [
                        DocumentAttributeAudio(
                            duration=duration,
                            title=title.split(".")[0],
                            performer=artist,
                        )
                    ]
                else:
                    attributes = None
                try:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        attributes=attributes,
                        supports_streaming=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
                except BaseException:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        force_document=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
            else:
                await event.client.send_file(
                    event.chat_id,
                    res,
                    caption=f"`{title}`",
                    force_document=True,
                    thumb="resources/extras/ultroid.jpg",
                )
        except Exception as ve:
            return await eor(xx, str(ve))
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if t == "":
        await eor(xx, f"Uploaded `{kk}` in `0 second(s)`")

    elif os.path.isdir(kk):
        size = 0
        for path, dirs, files in os.walk(kk):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        c = len(os.listdir(kk))
        await xx.delete()
        await event.client.send_message(
            event.chat_id,
            f"Uploaded Total - `{c}` files of `{humanbytes(size)}` in `{t}`",
        )
    else:
        await eor(xx, f"Uploaded `{kk}` in `{t}`")
