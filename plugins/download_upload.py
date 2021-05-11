# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ul <path/to/file>`
    Upload file to telegram chat.

• `{i}ul <path/to/file> | stream`
    Upload files as stream.

• `{i}dl <filename(optional)>`
    Reply to file to download.

"""

import time
from datetime import datetime as dt

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

from . import *


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
            return await eod(xx, get_string("udl_1"), time=5)
        if hasattr(ok.media, "document"):
            file = ok.media.document
            mime_type = file.mime_type
            if event.pattern_match.group(1):
                filename = event.pattern_match.group(1)
            else:
                filename = ok.file.name
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
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if t != "":
        await eor(xx, get_string("udl_2").format(file_name, t))
    else:
        await eor(xx, f"Downloaded `{file_name}` in `0 second(s)`")


@ultroid_cmd(
    pattern="ul ?(.*)",
)
async def download(event):
    xx = await eor(event, get_string("com_1"))
    hmm = event.pattern_match.group(1)
    try:
        kk = hmm.split(" | ")[0]
    except BaseException:
        pass
    try:
        title = kk.split("/")[-1]
    except BaseException:
        title = hmm
    s = dt.now()
    tt = time.time()
    if not kk:
        return await eod(xx, get_string("udl_3"))
    else:
        try:
            if Redis("CUSTOM_THUMBNAIL"):
                await bash(
                    f"wget {Redis('CUSTOM_THUMBNAIL')} -O resources/extras/ultroid.jpg"
                )
            try:
                res = await uploader(kk, kk, tt, xx, "Uploading...")
            except MessageNotModifiedError as err:
                return await xx.edit(str(err))
            if " | stream" in hmm and res.name.endswith(
                tuple([".mkv", ".mp4", ".mp3", ".opus", ".m4a", ".ogg"])
            ):
                metadata = extractMetadata(createParser(res.name))
                wi = 512
                hi = 512
                duration = 0
                if metadata.has("width"):
                    wi = metadata.get("width")
                if metadata.has("height"):
                    hi = metadata.get("height")
                if metadata.has("duration"):
                    duration = metadata.get("duration").seconds
                if metadata.has("artist"):
                    metadata.get("artist")
                if res.name.endswith(tuple([".mkv", ".mp4"])):
                    attributes = [
                        DocumentAttributeVideo(
                            w=wi, h=hi, duration=duration, supports_streaming=True
                        )
                    ]
                if res.name.endswith(tuple([".mp3", ".m4a", ".opus", ".ogg"])):
                    attributes = [
                        DocumentAttributeAudio(duration=duration, title=title)
                    ]
                try:
                    x = await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=title,
                        attributes=attributes,
                        supports_streaming=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
                except BaseException:
                    x = await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=title,
                        force_document=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
            else:
                x = await event.client.send_file(
                    event.chat_id,
                    res,
                    caption=title,
                    force_document=True,
                    thumb="resources/extras/ultroid.jpg",
                )
        except Exception as ve:
            return await eor(xx, str(ve))
    e = datetime.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if t != "":
        await eor(xx, f"Uploaded `{kk}` in `{t}`")
    else:
        await eor(xx, f"Uploaded `{kk}` in `0 second(s)`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
