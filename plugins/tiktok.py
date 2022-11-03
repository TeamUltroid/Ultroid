"""
✘ Perintah Tersedia -

•`{i}tt <tiktok url>`
    Download Video Tiktok Tanpa Watermark
"""



import glob
import io
import os
from asyncio.exceptions import TimeoutError as AsyncTimeout

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None
from telethon.errors.rpcerrorlist import MessageTooLongError, YouBlockedUserError
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantsBots,
    DocumentAttributeVideo,
)

from pyUltroid.fns.tools import metadata, translate

from . import (
    HNDLR,
    LOGS,
    ULTConfig,
    async_searcher,
    bash,
    check_filename,
    con,
    eor,
    fast_download,
    get_string,
)
from . import humanbytes as hb
from . import inline_mention, is_url_ok, mediainfo, ultroid_cmd

@ultroid_cmd(pattern="tt(?: |$)(.*)")
async def _(event):
    xxnx = event.pattern_match.group(1)
    if xxnx:
        d_link = xxnx
    elif event.is_reply:
        d_link = await event.get_reply_message()
    else:
        return await eod(
            event,
            "**Berikan Link Tiktok Pesan atau Reply Link Tiktok Untuk di Download**",
        )
    xx = await eor(event, "`Video Sedang Diproses...`")
    chat = "@thisvidbot"
    async with event.client.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        await event.client.send_file(event.chat_id, video)
        await event.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id, text.id]
        )
        await xx.delete()
