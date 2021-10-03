# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

from pyUltroid.dB.blacklist_db import (
    add_blacklist,
    get_blacklist,
    list_blacklist,
    rem_blacklist,
)

from . import eor, events, get_string, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="blacklist ?(.*)", admins_only=True)
async def af(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not (wrd):
        return await eor(e, get_string("blk_1"), time=5)
    wrd = e.text[11:]
    heh = wrd.split(" ")
    for z in heh:
        add_blacklist(int(chat), z.lower())
    await eor(e, get_string("blk_2").format(wrd))


@ultroid_cmd(pattern="remblacklist ?(.*)", admins_only=True)
async def rf(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return await eor(e, get_string("blk_3"), time=5)
    wrd = e.text[14:]
    heh = wrd.split(" ")
    for z in heh:
        rem_blacklist(int(chat), z.lower())
    await eor(e, get_string("blk_4").format(wrd))


@ultroid_cmd(pattern="listblacklist$", admins_only=True)
async def lsnote(e):
    x = list_blacklist(e.chat_id)
    if x:
        sd = get_string("blk_5")
        return await eor(e, sd + x)
    await eor(e, get_string("blk_6"))


@ultroid_bot.on(events.NewMessage(incoming=True))
async def bl(e):
    x = get_blacklist(e.chat_id)
    if x:
        for z in e.text.lower().split():
            for zz in x:
                if z == zz:
                    try:
                        await e.delete()
                        break
                    except BaseException:
                        break
