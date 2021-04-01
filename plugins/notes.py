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
"""

from pyUltroid.functions.notes_db import *
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addnote ?(.*)")
async def an(e):
    wrd = e.pattern_match.group(1)
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await eor(e, "`Use this Command with Reply and word to use a note.`")
    if "#" in wrd:
        wrd = wrd.replace("#", "")
    try:
        rem_note(int(chat), wrd)
    except:
        pass
    if wt.media:
        ok = pack_bot_file_id(wt.media)
        add_note(int(chat), wrd, ok)
    else:
        add_note(int(chat), wrd, wt.text)
    await eor(e, "done")


@ultroid_cmd(pattern="remnote ?(.*)")
async def rn(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return await eor(e, "`Give me the note handler which you want to remove.`")
    if wrd.startswith("#"):
        wrd = wrd.replace("#", "")
    rem_note(int(chat), wrd)
    await eor(e, "done")


@ultroid_cmd(pattern="listnote$")
async def lsnote(e):
    x = list_note(e.chat_id)
    if x:
        sd = "Notes Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Notes Found Here")


@ultroid_bot.on(events.NewMessage())
async def notes(e):
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
            try:
                await ultroid_bot.send_file(int(chat), k)
            except:
                await ultroid_bot.send_message(int(chat), k)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
