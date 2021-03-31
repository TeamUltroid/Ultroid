# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

from pyUltroid.functions.filter_db import *
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addfilter ?(.*)")
async def af(e):
    wrd = e.pattern_match.group(1)
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await eor(e, "fuk off bici")
    try:
        rem_filter(int(chat), wrd)
    except:
        pass
    if wt.media:
        ok = pack_bot_file_id(wt.media)
        add_filter(int(chat), wrd, ok)
    else:
        add_filter(int(chat), wrd, wt.text)
    await eor(e, "done")


@ultroid_cmd(pattern="remfilter ?(.*)")
async def rf(e):
    wrd = e.pattern_match.group(1)
    chat = e.chat_id
    if not wrd:
        return await eor(e, "fuk off bici")
    rem_filter(int(chat), wrd)
    await eor(e, "done")


@ultroid_cmd(pattern="listfilter")
async def lsnote(e):
    x = list_filter(e.chat_id)
    if x:
        sd = "Filters Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Filters Found Here")


@ultroid_bot.on(events.NewMessage())
async def fl(e):
    xx = e.text
    chat = e.chat_id
    x = get_filter(int(chat))
    if x:
        if " " in xx:
            xx = xx.split(" ")
            for c in xx:
                if c in x:
                    k = get_reply(int(chat), c)
                    if k:
                        kk = k
            try:
                await ultroid_bot.send_file(int(chat), kk)
            except:
                try:
                    await ultroid_bot.send_message(int(chat), kk)
                except:
                    pass
        else:
            k = get_reply(chat, xx)
            if k:
                try:
                    await ultroid_bot.send_file(int(chat), k)
                except:
                    await ultroid_bot.send_message(int(chat), k)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
