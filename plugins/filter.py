# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addfilter <word><reply to a message>`
    add the used word as filter relating to replied message.

• `{i}remfilter <word>`
    Remove the filtered user..

• `{i}listfilter`
    list all filters.
"""

import os
import re

from pyUltroid.functions.filter_db import *
from telegraph import upload_file as uf
from telethon.tl.types import User
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addfilter ?(.*)")
async def af(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await eor(e, "`Use this command word to set as filter and reply...`")
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            variable = uf(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eor(x, "`Unsupported Media`", time=5)
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            add_filter(int(chat), wrd, wt.text, m)
        else:
            add_filter(int(chat), wrd, None, m)
    else:
        add_filter(int(chat), wrd, wt.text, None)
    await eor(e, f"Done : Filter `{wrd}` Saved.")


@ultroid_cmd(pattern="remfilter ?(.*)")
async def rf(e):
    wrd = (e.pattern_match.group(1)).lower()
    chat = e.chat_id
    if not wrd:
        return await eor(e, "`Give the filter to remove..`")
    rem_filter(int(chat), wrd)
    await eor(e, f"Done : Filter `{wrd}` Removed.")


@ultroid_cmd(pattern="listfilter$")
async def lsnote(e):
    x = list_filter(e.chat_id)
    if x:
        sd = "Filters Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Filters Found Here")


@ultroid_bot.on(events.NewMessage())
async def fl(e):
    if isinstance(e.sender, User) and e.sender.bot:
        return
    xx = (e.text).lower()
    chat = e.chat_id
    x = get_filter(chat)
    if x:
        for c in x:
            pat = r"( |^|[^\w])" + re.escape(c) + r"( |$|[^\w])"
            if re.search(pat, xx):
                k = x.get(c)
                if k:
                    msg = k["msg"]
                    media = k["media"]
                    await e.reply(msg, file=media)
