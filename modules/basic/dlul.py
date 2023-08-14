# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("downloadupload")

import asyncio
import contextlib
import glob
import os
import time
from datetime import datetime as dt

from requests.exceptions import InvalidSchema, InvalidURL
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from utilities.helper import time_formatter
from utilities.tools import get_chat_and_msgid, is_url_ok, set_attributes

from .. import (
    LOGS,
    eor,
    fast_download,
    get_all_files,
    get_string,
    progress,
    ultroid_cmd,
)


async def download_from_url(event):
    """Download from url"""
    queryed = link = event.pattern_match.group(1).strip()
    msg = await event.eor(get_string("udl_4"))
    if not queryed:
        return await eor(msg, get_string("udl_5"), time=5)
    try:
        link, filename = queryed.split(" | ")[:2]
    except ValueError:
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
    except (InvalidURL, InvalidSchema):
        return await msg.eor("`Invalid URL provided :(`", time=5)
    await msg.eor(f"`{filename}` `downloaded in {time_formatter(d*1000)}.`")


@ultroid_cmd(
    pattern="dl( (.*)|$)",
)
async def dl_cmd(event):
    query = event.pattern_match.group(1).strip()
    silent = "--silent" in query
    if silent:
        query = query.replace("--silent", "").strip()
    if query and "t.me/" in query:
        chat, msg = get_chat_and_msgid(query)
        if not (chat and msg):
            return await event.eor(get_string("gms_1"))
        ok = await event.client.get_messages(chat, ids=msg)
    elif event.reply_to_msg_id:
        ok = await event.get_reply_message()
    elif query and await is_url_ok(query):
        return await download_from_url(event)
    else:
        return await event.eor(get_string("cvt_3"), time=8)
    xx = await event.eor(get_string("com_1"))
    if not (ok and ok.media):
        return await xx.eor(get_string("udl_1"), time=5)
    s = dt.now()
    k = time.time()
    if hasattr(ok.media, "document"):
        file = ok.media.document
        filename = ok.file.name or query
        if not filename:
            mime_type = file.mime_type
            if "audio" in mime_type:
                filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
            elif "video" in mime_type:
                filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
        try:
            result = await event.client.fast_downloader(
                file,
                filename=f"resources/downloads/{filename}",
                show_progress=not silent,
                event=xx,
            )

        except MessageNotModifiedError as err:
            return await xx.edit(str(err))
        file_name = result[0].name
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


async def _upload_file(
    event, files, stream, msg, delete, thumb, force_doc, progress=True
):
    attributes = None
    if stream:
        try:
            attributes = await set_attributes(files)
        except KeyError as er:
            LOGS.exception(er)
    with contextlib.suppress(ValueError, IsADirectoryError):
        file, _ = await event.client.fast_uploader(
            files, show_progress=progress, event=msg, to_delete=delete
        )
        await event.client.send_file(
            event.chat_id,
            file=file,
            supports_streaming=stream,
            force_document=force_doc,
            attributes=attributes,
            thumb=thumb,
            caption=f"`Uploaded` `{files}` `in {time_formatter(_*1000)}`",
            reply_to=event.reply_to_msg_id or event,
        )


@ultroid_cmd(
    pattern="ul( (.*)|$)",
)
async def _(event):
    msg = await event.eor(get_string("com_1"))
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor("`Error: Provide Path.`")
    stream, force_doc, delete, thumb, parallel = (False, True, False, None, None)
    if "--stream" in query:
        stream = True
        force_doc = False
    delete = "--delete" in query
    parallel = "--parallel" in query
    if "--no-thumb" in query:
        thumb = False
    arguments = ["--stream", "--delete", "--no-thumb", "--parallel"]
    if any(item in query for item in arguments):
        query = (
            query.replace("--stream", "")
            .replace("--delete", "")
            .replace("--no-thumb", "")
            .replace("--parallel", "")
            .strip()
        )
    if not event.out and query == ".env":
        return await event.eor("`Error: Permission denied.`")
    if query.endswith("/"):
        query += "*"
    results = glob.glob(query)
    if not results and os.path.exists(query):
        results = [query]
    if not results:
        # Consider it as previewable link
        try:
            await event.reply(file=query)
            return await event.try_delete()
        except Exception as er:
            LOGS.exception(er)
        return await msg.eor(get_string("ls1"))
    for result in results:
        files = get_all_files(result) if os.path.isdir(result) else [result]
        if parallel:
            await asyncio.gather(
                *[
                    _upload_file(
                        event, file, stream, msg, delete, thumb, force_doc, False
                    )
                    for file in files
                ]
            )
        else:
            for file in files:
                await _upload_file(event, file, stream, msg, delete, thumb, force_doc)
    await msg.try_delete()
