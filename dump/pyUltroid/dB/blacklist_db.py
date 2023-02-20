# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def get_stuff():
    return udB.get_key("BLACKLIST_DB") or {}


def add_blacklist(chat, word):
    ok = get_stuff()
    if ok.get(chat):
        for z in word.split():
            if z not in ok[chat]:
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
