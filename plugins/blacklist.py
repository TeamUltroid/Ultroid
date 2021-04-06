# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}blacklist <word/all words with a space>`
    blacklist the choosen word in that chat.

• `{i}remblacklist <word>`
    Remove the word from blacklist..

• `{i}listblacklist`
    list all blacklisted words.

  'if a person uses blacklist Word his/her msg will be deleted'
  'And u Must be Admin in that Chat'
"""

import re

from pyUltroid.functions.blacklist_db import *
from telethon.tl.types import ChannelParticipantsAdmins

from . import *


@ultroid_cmd(pattern="blacklist ?(.*)")
async def af(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You are Not Admin Here`")
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not (wrd):
        return await eod(e, "`Give the word to blacklist..`")
    wrd = e.text[10:]
    add_blacklist(int(chat), wrd)
    await eor(e, f"Done : `{wrd}` Blacklisted here.")


@ultroid_cmd(pattern="remblacklist ?(.*)")
async def rf(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You are Not Admin Here`")
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return await eod(e, "`Give the word to remove from blacklist..`")
    rem_blacklist(int(chat), wrd)
    await eor(e, f"Done : `{wrd}` Removed from Blacklist.")


@ultroid_cmd(pattern="listblacklist")
async def lsnote(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return await eod(e, "`You are Not Admin Here`")
    x = list_blacklist(e.chat_id)
    if x:
        sd = "Blacklist Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Blacklist word Found Here")


@ultroid_bot.on(events.NewMessage(incoming=True))
async def bl(e):
    if e.is_group:
        if not e._chat.admin_rights:
            return
    xx = e.text
    chat = e.chat_id
    x = get_blacklist(int(chat))
    if x and xx:
        if " " in xx:
            xx = xx.split(" ")
            kk = ""
            for c in xx:
                kk = re.search(str(c), str(x), flags=re.IGNORECASE)
            if kk:
                async for l in ultroid_bot.iter_participants(
                    e.chat_id, filter=ChannelParticipantsAdmins
                ):
                    if l.id == e.sender_id:
                        return
                await e.delete()
        else:
            k = re.search(xx, x, flags=re.IGNORECASE)
            if k:
                async for l in ultroid_bot.iter_participants(
                    e.chat_id, filter=ChannelParticipantsAdmins
                ):
                    if l.id == e.sender_id:
                        return
                await e.delete()


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
