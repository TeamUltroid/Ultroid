# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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
import os

from pyUltroid.dB.notes_db import *
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addnote ?(.*)", admins_only=True)
async def an(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await eor(e, get_string("notes_1"), time=5)
    if "#" in wrd:
        wrd = wrd.replace("#", "")
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
            add_note(int(chat), wrd, wt.text, m)
        else:
            add_note(int(chat), wrd, None, m)
    else:
        add_note(int(chat), wrd, wt.text, None)
    await eor(e, get_string("notes_2").format(wrd))


@ultroid_cmd(pattern="remnote ?(.*)", admins_only=True)
async def rn(e):
    wrd = (e.pattern_match.group(1)).lower()
    chat = e.chat_id
    if not wrd:
        return await eor(e, get_string("notes_3"), time=5)
    if wrd.startswith("#"):
        wrd = wrd.replace("#", "")
    rem_note(int(chat), wrd)
    await eor(e, f"Done Note: `#{wrd}` Removed.")


@ultroid_cmd(pattern="listnote$", admins_only=True)
async def lsnote(e):
    x = list_note(e.chat_id)
    if x:
        sd = "Notes Found In This Chats Are\n\n"
        return await eor(e, sd + x)
    await eor(e, get_string("notes_5"))


@ultroid_bot.on(events.NewMessage(pattern="^#(.*)"))
async def notes(e):
    xx = e.text
    xx = (xx.replace("#", "")).lower().split()
    chat = e.chat_id
    for word in xx:
        k = get_notes(chat, word)
        if k:
            msg = k["msg"]
            media = k["media"]
            await e.reply(msg, file=media)
