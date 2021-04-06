# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
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

from pyUltroid.functions.notes_db import *
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addnote ?(.*)")
async def an(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You Are Not Admin Here.", time=5)
    wrd = e.pattern_match.group(1)
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await eod(e, "`Use this Command with Reply and word to use a note.`")
    if "#" in wrd:
        wrd = wrd.replace("#", "")
    try:
        rem_note(int(chat), wrd)
    except:
        pass
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await bot.download_media(wt.media)
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eod(x, "`Unsupported Media`")
            else:
                dl = await bot.download_media(wt.media)
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
    await eor(e, f"Done Note : `#{wrd}` saved.")


@ultroid_cmd(pattern="remnote ?(.*)")
async def rn(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You Are Not Admin Here.", time=5)
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return await eod(e, "`Give me the note handler which you want to remove.`")
    if wrd.startswith("#"):
        wrd = wrd.replace("#", "")
    rem_note(int(chat), wrd)
    await eor(e, f"Done Note: `#{wrd}` Removed.")


@ultroid_cmd(pattern="listnote$")
async def lsnote(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You Are Not Admin Here.", time=5)
    x = list_note(e.chat_id)
    if x:
        sd = "Notes Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Notes Found Here")


@ultroid_bot.on(events.NewMessage())
async def notes(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return
    xx = e.text
    if not xx.startswith("#"):
        return
    xx = xx.replace("#", "")
    chat = e.chat_id
    x = get_notes(int(chat))
    if x:
        if " " in xx:
            xx = xx.split(" ")[0]
        k = get_reply(chat, xx)
        if k:
            msg = k["msg"]
            media = k["media"]
            await e.reply(msg, file=media)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
