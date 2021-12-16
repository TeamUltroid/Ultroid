# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}webupload`
    Upload files on another server.
"""

import os

from pyUltroid.functions.tools import _webupload_cache

from . import asst, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="webupload ?(.*)",
)
async def _(event):
    xx = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1)
    if match:
        if not os.path.exists(match):
            return await xx.eor("`File doesn't exist.`")
        _webupload_cache[event.chat_id][event.id] = match
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply.photo:
            file = await event.client.download_media("resources/downloads/")
            _webupload_cache[event.chat_id][event.id] = file
        else:
            file, _ = await event.client.fast_downloader(
                reply.document, reply.file.name, show_progress=True, event=xx
            )
            _webupload_cache[event.chat_id][event.id] = file.name
    else:
        return await xx.eor("`Reply to file or give file path...`")
    results = await event.client.inline_query(
        asst.me.username, f"fl2lnk {event.chat_id}:{event.id}"
    )
    await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
    await xx.delete()
