# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_blacklist")


from pyUltroid.dB.blacklist_db import (
    add_blacklist,
    get_blacklist,
    list_blacklist,
    rem_blacklist,
)

from . import events, get_string, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="blacklist( (.*)|$)", admins_only=True)
async def af(e):
    wrd = e.pattern_match.group(1).strip()
    chat = e.chat_id
    if not (wrd):
        return await e.eor(get_string("blk_1"), time=5)
    wrd = e.text[11:]
    heh = wrd.split(" ")
    for z in heh:
        add_blacklist(int(chat), z.lower())
    ultroid_bot.add_handler(blacklist, events.NewMessage(incoming=True))
    await e.eor(get_string("blk_2").format(wrd))


@ultroid_cmd(pattern="remblacklist( (.*)|$)", admins_only=True)
async def rf(e):
    wrd = e.pattern_match.group(1).strip()
    chat = e.chat_id
    if not wrd:
        return await e.eor(get_string("blk_3"), time=5)
    wrd = e.text[14:]
    heh = wrd.split(" ")
    for z in heh:
        rem_blacklist(int(chat), z.lower())
    await e.eor(get_string("blk_4").format(wrd))


@ultroid_cmd(pattern="listblacklist$", admins_only=True)
async def lsnote(e):
    if x := list_blacklist(e.chat_id):
        sd = get_string("blk_5")
        return await e.eor(sd + x)
    await e.eor(get_string("blk_6"))


async def blacklist(e):
    if x := get_blacklist(e.chat_id):
        for z in e.text.lower().split():
            for zz in x:
                if z == zz:
                    try:
                        await e.delete()
                        break
                    except BaseException:
                        break


if udB.get_key("BLACKLIST_DB"):
    ultroid_bot.add_handler(blacklist, events.NewMessage(incoming=True))
