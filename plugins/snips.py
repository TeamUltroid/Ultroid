# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

from pyUltroid.functions.snips_db import *
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addsnip ?(.*)")
async def an(e):
    wrd = e.pattern_match.group(1)
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await eor(e, "fuk off bici")
    if "$" in wrd:
        wrd = wrd.replace("$", "")
    try:
        rem_snip(int(chat), wrd)
    except:
        pass
    if wt.media:
        ok = pack_bot_file_id(wt.media)
        add_snip(wrd, ok)
    else:
        add_snip(wrd, wt.text)
    await eor(e, "done")


@ultroid_cmd(pattern="remsnip ?(.*)")
async def rs(e):
    wrd = e.pattern_match.group(1)
    if not wrd:
        return await eor(e, "fuk off bici")
    if wrd.startswith("$"):
        wrd = wrd.replace("$", "")
    rem_snip(wrd)
    await eor(e, "done")


@ultroid_cmd(pattern="listsnip")
async def lsnote(e):
    x = list_snip()
    if x:
        sd = "SNIPS Found In This Chats Are\n\n"
        await eor(e, sd + x)
    else:
        await eor(e, "No Snips Found Here")


@ultroid_bot.on(events.NewMessage(outgoing=True))
async def notes(e):
    xx = e.text
    if not xx.startswith("$"):
        return
    xx = xx.replace("$", "")
    x = get_snips()
    if x:
        if " " in xx:
            xx = xx.split(" ")[0]
        k = get_reply(xx)
        if k:
            try:
                await e.delete()
                await ultroid_bot.send_file(e.chat_id, k)
            except:
                await e.delete()
                await ultroid_bot.send_message(e.chat_id, k)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
