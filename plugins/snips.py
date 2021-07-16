# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}addsnip <word><reply to a message>`
    add the used word as snip relating to replied message.

• `{i}remsnip <word>`
    Remove the snip word..

• `{i}listsnip`
    list all snips.

• Use :
    type `$(ur snip word)` get setted reply.
"""
import os

from pyUltroid.functions.snips_db import *
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addsnip ?(.*)")
async def an(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await eor(e, "Give word to set as snip and reply to a message.")
    if "$" in wrd:
        wrd = wrd.replace("$", "")
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eod(x, "`Unsupported Media`")
            else:
                dl = await wt.download_media()
                variable = uf(dl)
                os.remove(dl)
                m = "https://telegra.ph" + variable[0]
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            add_snip(wrd, wt.text, m)
        else:
            add_snip(wrd, None, m)
    else:
        add_snip(wrd, wt.text, None)
    await eor(e, f"Done : snip `${wrd}` Saved.")


@ultroid_cmd(pattern="remsnip ?(.*)")
async def rs(e):
    wrd = (e.pattern_match.group(1)).lower()
    if not wrd:
        return await eor(e, "Give the word to remove...")
    if wrd.startswith("$"):
        wrd = wrd.replace("$", "")
    rem_snip(wrd)
    await eor(e, f"Done : snip `${wrd}` Removed.")


@ultroid_cmd(pattern="listsnip")
async def lsnote(e):
    x = list_snip()
    if x:
        sd = "SNIPS Found :\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Snips Found Here")


@ultroid_bot.on(events.NewMessage())
async def notes(e):
    if not e.out and not str(e.sender_id) in sudoers():
        return
    xx = (e.text).lower()
    if not xx.startswith("$"):
        return
    xx = xx.replace("$", "")
    x = get_snips()
    if x:
        if " " in xx:
            xx = xx.split(" ")[0]
        k = get_reply(xx)
        if k:
            msg = k["msg"]
            media = k["media"]
            rep = await e.get_reply_message()
            if rep:
                await rep.reply(msg, file=media)
            else:
                await ultroid_bot.send_message(e.chat_id, msg, file=media)
                await e.delete()
