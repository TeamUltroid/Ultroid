# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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

from core.decorators import get_sudos as sudoers
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id
from utilities.tools import create_tl_btn, format_btn, get_msg_button

from ..basic._inline import something
from . import events, get_string, mediainfo, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="addsnip( (.*)|$)")
async def an(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await e.eor(get_string("snip_1"))
    if "$" in wrd:
        wrd = wrd.replace("$", "")
    btn = format_btn(wt.buttons) if wt.buttons else None
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await e.eor(get_string("com_4"), time=5)
            dl = await wt.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
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
    await e.eor(f"Done : snip `${wrd}` Saved.")
    ultroid_bot.add_handler(add_snips, events.NewMessage())


@ultroid_cmd(pattern="remsnip( (.*)|$)")
async def rs(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    if not wrd:
        return await e.eor(get_string("snip_2"))
    if wrd.startswith("$"):
        wrd = wrd.replace("$", "")
    rem_snip(wrd)
    await e.eor(f"Done : snip `${wrd}` Removed.")


@ultroid_cmd(pattern="listsnip")
async def lsnote(e):
    if x := list_snip():
        sd = "SNIPS Found :\n\n"
        return await e.eor(sd + x)
    await e.eor("No Snips Found Here")


async def add_snips(e):
    if not e.out and e.sender_id not in sudoers():
        return
    xx = [z.replace("$", "")
          for z in e.text.lower().split() if z.startswith("$")]
    for z in xx:
        if k := get_snips(z):
            msg = k["msg"]
            media = k["media"]
            rep = await e.get_reply_message()
            if rep:
                if k.get("button"):
                    btn = create_tl_btn(k["button"])
                    return await something(rep, msg, media, btn)
                await rep.reply(msg, file=media)
            else:
                await e.delete()
                if k.get("button"):
                    btn = create_tl_btn(k["button"])
                    return await something(e, msg, media, btn, reply=None)
                await ultroid_bot.send_message(e.chat_id, msg, file=media)


def get_all_snips():
    return udB.get_key("SNIP") or {}


def add_snip(word, msg, media, button):
    ok = get_all_snips()
    ok.update({word: {"msg": msg, "media": media, "button": button}})
    udB.set_key("SNIP", ok)


def rem_snip(word):
    ok = get_all_snips()
    if ok.get(word):
        ok.pop(word)
        udB.set_key("SNIP", ok)


def get_snips(word):
    ok = get_all_snips()
    if ok.get(word):
        return ok[word]
    return False


def list_snip():
    return "".join(f"👉 ${z}\n" for z in get_all_snips())


if udB.get_key("SNIP"):
    ultroid_bot.add_handler(add_snips, events.NewMessage())
