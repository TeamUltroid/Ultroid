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

from pyUltroid.dB.snips_db import *
from pyUltroid.functions.tools import create_tl_btn, format_btn, get_msg_button
from pyUltroid.misc import sudoers
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *
from ._builder import something


@ultroid_cmd(pattern="addsnip ?(.*)")
async def an(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await eor(e, "Give word to set as snip and reply to a message.")
    if "$" in wrd:
        wrd = wrd.replace("$", "")
    if wt.buttons:
        btn = format_btn(wt.buttons)
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eor(x, get_string("com_4"), time=5)
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            txt = wt.text
            if not btn:
                txt, btn = get_msg_button(wt.text)
            add_snip(wrd, txt, m, btn)
        else:
            add_snip(wrd, None, m, btn)
    else:
        txt = wt.text
        if not btn:
            txt, btn = get_msg_button(wt.text)
        add_snip(wrd, txt, None, btn)
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
    if not e.out and str(e.sender_id) not in sudoers():
        return
    xx = (e.text).lower()
    if not xx.startswith("$"):
        return
    xx = xx.replace("$", "").split()
    for z in xx:
        k = get_snips(z)
        if k:
            msg = k["msg"]
            media = k["media"]
            rep = await e.get_reply_message()
            if rep:
                if k.get("button"):
                    btn = create_tl_btn(k["button"])
                    return await something(k, msg, media, btn)
                await rep.reply(msg, file=media)
            else:
                await e.delete()
                if k.get("button"):
                    btn = create_tl_btn(k["button"])
                    return await something(k, msg, media, btn, reply=None)
                await ultroid_bot.send_message(e.chat_id, msg, file=media)
