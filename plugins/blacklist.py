# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("blacklist")

from telethon import events

from . import get_string, udB, ultroid_bot, ultroid_cmd


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
        text = e.text.lower().split()
        if any((z in text) for z in x):
            try:
                await e.delete()
            except BaseException:
                pass


def get_stuff():
    return udB.get_key("BLACKLIST_DB") or {}


def add_blacklist(chat, word):
    ok = get_stuff()
    if ok.get(chat):
        for z in filter(lambda z: z not in ok[chat], word.split()):
            ok[chat].append(z)
    else:
        ok.update({chat: [word]})
    return udB.set_key("BLACKLIST_DB", ok)


def rem_blacklist(chat, word):
    ok = get_stuff()
    if ok.get(chat) and word in ok[chat]:
        ok[chat].remove(word)
        return udB.set_key("BLACKLIST_DB", ok)


def list_blacklist(chat):
    ok = get_stuff()
    if ok.get(chat):
        txt = "".join(f"👉`{z}`\n" for z in ok[chat])
        if txt:
            return txt


def get_blacklist(chat):
    ok = get_stuff()
    if ok.get(chat):
        return ok[chat]


if udB.get_key("BLACKLIST_DB"):
    ultroid_bot.add_handler(blacklist, events.NewMessage(incoming=True))
