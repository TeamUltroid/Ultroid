# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_downloadupload")

import asyncio
import glob
import os
import time
from datetime import datetime as dt

from aiohttp.client_exceptions import InvalidURL
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from pyUltroid.fns.helper import time_formatter
from pyUltroid.fns.tools import get_chat_and_msgid, set_attributes

from . import (
    LOGS,
    ULTConfig,
    downloader,
    eor,
    fast_download,
    get_all_files,
    get_string,
    progress,
    time_formatter,
    ultroid_cmd,
)


@ultroid_cmd(
    pattern="download( (.*)|$)",
)
async def down(event):
    matched = event.pattern_match.group(1).strip()
    msg = await event.eor(get_string("udl_4"))
    if not matched:
        return await eor(msg, get_string("udl_5"), time=5)
    try:
        splited = matched.split(" | ")
        link = splited[0]
        filename = splited[1]
    except IndexError:
        filename = None
    s_time = time.time()
    try:
        filename, d = await fast_download(
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
        return await msg.eor("`Invalid URL provided :(`", time=5)
    await msg.eor(f"`{filename}` `downloaded in {time_formatter(d*1000)}.`")


@ultroid_cmd(
    pattern="dl( (.*)|$)",
)
async def download(event):
    match = event.pattern_match.group(1).strip()
    if match and "t.me/" in match:
        chat, msg = get_chat_and_msgid(match)
        if not (chat and msg):
            return await event.eor(get_string("gms_1"))
        match = ""
        ok = await event.client.get_messages(chat, ids=msg)
    elif event.reply_to_msg_id:
        ok = await event.get_reply_message()
    else:
        return await event.eor(get_string("cvt_3"), time=8)
    xx = await event.eor(get_string("com_1"))
    if not (ok and ok.media):
        return await xx.eor(get_string("udl_1"), time=5)
    s = dt.now()
    k = time.time()
    if hasattr(ok.media, "document"):
        file = ok.media.document
        mime_type = file.mime_type
        filename = match or ok.file.name
        if not filename:
            if "audio" in mime_type:
                filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
            elif "video" in mime_type:
                filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        try:
            result = await downloader(
                f"resources/downloads/{filename}",
                file,
                xx,
                k,
                f"Downloading {filename}...",
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
                    get_string("com_5"),
                ),
            ),
        )
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    await xx.eor(get_string("udl_2").format(file_name, t))


@ultroid_cmd(
    pattern="ul( (.*)|$)",
)
async def _(event):
    msg = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1)
    if match:
        match = match.strip()
    if not event.out and match == ".env":
        return await event.reply("`You can't do this...`")
    stream, force_doc, delete, thumb = (
        False,
        True,
        False,
        ULTConfig.thumb,
    )
    if "--stream" in match:
        stream = True
        force_doc = False
    if "--delete" in match:
        delete = True
    if "--no-thumb" in match:
        thumb = None
    arguments = ["--stream", "--delete", "--no-thumb"]
    if any(item in match for item in arguments):
        match = (
            match.replace("--stream", "")
            .replace("--delete", "")
            .replace("--no-thumb", "")
            .strip()
        )
    if match.endswith("/"):
        match += "*"
    results = glob.glob(match)
    if not results and os.path.exists(match):
        results = [match]
    if not results:
        try:
            await event.reply(file=match)
            return await event.try_delete()
        except Exception as er:
            LOGS.exception(er)
        return await msg.eor(get_string("ls1"))
    for result in results:
        if os.path.isdir(result):
            c, s = 0, 0
            for files in get_all_files(result):
                attributes = None
                if stream:
                    try:
                        attributes = await set_attributes(files)
                    except KeyError as er:
                        LOGS.exception(er)
                try:
                    file, _ = await event.client.fast_uploader(
                        files, show_progress=True, event=msg, to_delete=delete
                    )
                    await event.client.send_file(
                        event.chat_id,
                        file,
                        supports_streaming=stream,
                        force_document=force_doc,
                        thumb=thumb,
                        attributes=attributes,
                        caption=f"`Uploaded` `{files}` `in {time_formatter(_*1000)}`",
                        reply_to=event.reply_to_msg_id or event,
                    )
                    s += 1
                except (ValueError, IsADirectoryError):
                    c += 1
            break
        attributes = None
        if stream:
            try:
                attributes = await set_attributes(result)
            except KeyError as er:
                LOGS.exception(er)
        file, _ = await event.client.fast_uploader(
            result, show_progress=True, event=msg, to_delete=delete
        )
        await event.client.send_file(
            event.chat_id,
            file,
            supports_streaming=stream,
            force_document=force_doc,
            thumb=thumb,
            attributes=attributes,
            caption=f"`Uploaded` `{result}` `in {time_formatter(_*1000)}`",
        )
    await msg.try_delete()
