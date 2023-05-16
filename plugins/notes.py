
import os

from telegraph import upload_file as uf
from telethon import events
from telethon.utils import pack_bot_file_id
from utilities.tools import create_tl_btn, format_btn, get_msg_button

from ..basic._inline import something
from . import get_string, mediainfo, udB, ultroid_bot, ultroid_cmd


def get_stuff():
    return udB.get_key("NOTE") or {}


def add_note(chat, word, msg, media, button):
    ok = get_stuff()
    if ok.get(int(chat)):
        ok[int(chat)].update(
            {word: {"msg": msg, "media": media, "button": button}})
    else:
        ok.update(
            {int(chat): {word: {"msg": msg, "media": media, "button": button}}})
    udB.set_key("NOTE", ok)


def rem_note(chat, word):
    ok = get_stuff()
    if ok.get(int(chat)) and ok[int(chat)].get(word):
        ok[int(chat)].pop(word)
        return udB.set_key("NOTE", ok)


def rem_all_note(chat):
    ok = get_stuff()
    if ok.get(int(chat)):
        ok.pop(int(chat))
        return udB.set_key("NOTE", ok)


def get_notes(chat, word):
    ok = get_stuff()
    if ok.get(int(chat)) and ok[int(chat)].get(word):
        return ok[int(chat)][word]


def list_note(chat):
    ok = get_stuff()
    if ok.get(int(chat)):
        return "".join(f"👉 #{z}\n" for z in ok[chat])


# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}addnote <word><reply to a message>`
    add note in the used chat with replied message and choosen word.

• `{i}remnote <word>`
    Remove the note from used chat.

• `{i}listnote`
    list all notes.

• Use :
   set notes in group so all can use it.
   type `#(Keyword of note)` to get it
"""


@ultroid_cmd(pattern="addnote( (.*)|$)", admins_only=True)
async def an(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await e.eor(get_string("notes_1"), time=5)
    if "#" in wrd:
        wrd = wrd.replace("#", "")
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
            add_note(chat, wrd, txt, m, btn)
        else:
            add_note(chat, wrd, None, m, btn)
    else:
        txt = wt.text
        if not btn:
            txt, btn = get_msg_button(wt.text)
        add_note(chat, wrd, txt, None, btn)
    await e.eor(get_string("notes_2").format(wrd))
    ultroid_bot.add_handler(notes, events.NewMessage())


@ultroid_cmd(pattern="remnote( (.*)|$)", admins_only=True)
async def rn(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    chat = e.chat_id
    if not wrd:
        return await e.eor(get_string("notes_3"), time=5)
    if wrd.startswith("#"):
        wrd = wrd.replace("#", "")
    rem_note(int(chat), wrd)
    await e.eor(f"Done Note: `#{wrd}` Removed.")


@ultroid_cmd(pattern="listnote$", admins_only=True)
async def lsnote(e):
    if x := list_note(e.chat_id):
        sd = "Notes Found In This Chats Are\n\n"
        return await e.eor(sd + x)
    await e.eor(get_string("notes_5"))


async def notes(e):
    xx = [z.replace("#", "")
          for z in e.text.lower().split() if z.startswith("#")]
    for word in xx:
        if k := get_notes(e.chat_id, word):
            msg = k["msg"]
            media = k["media"]
            if k.get("button"):
                btn = create_tl_btn(k["button"])
                return await something(e, msg, media, btn)
            await e.client.send_message(
                e.chat_id, msg, file=media, reply_to=e.reply_to_msg_id or e.id
            )


if udB.get_key("NOTE"):
    ultroid_bot.add_handler(notes, events.NewMessage())


def get_stuff():
    return udB.get_key("NOTE") or {}


def add_note(chat, word, msg, media, button):
    ok = get_stuff()
    if ok.get(int(chat)):
        ok[int(chat)].update(
            {word: {"msg": msg, "media": media, "button": button}})
    else:
        ok.update(
            {int(chat): {word: {"msg": msg, "media": media, "button": button}}})
    udB.set_key("NOTE", ok)


def rem_note(chat, word):
    ok = get_stuff()
    if ok.get(int(chat)) and ok[int(chat)].get(word):
        ok[int(chat)].pop(word)
        return udB.set_key("NOTE", ok)


def rem_all_note(chat):
    ok = get_stuff()
    if ok.get(int(chat)):
        ok.pop(int(chat))
        return udB.set_key("NOTE", ok)


def get_notes(chat, word):
    ok = get_stuff()
    if ok.get(int(chat)) and ok[int(chat)].get(word):
        return ok[int(chat)][word]


def list_note(chat):
    ok = get_stuff()
    if ok.get(int(chat)):
        return "".join(f"👉 #{z}\n" for z in ok[chat])
