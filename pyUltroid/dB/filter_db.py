# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def get_stuff():
    return udB.get_key("FILTERS") or {}


def add_filter(chat, word, msg, media, button):
    ok = get_stuff()
    if ok.get(chat):
        ok[chat].update({word: {"msg": msg, "media": media, "button": button}})
    else:
        ok.update({chat: {word: {"msg": msg, "media": media, "button": button}}})
    udB.set_key("FILTERS", ok)


def rem_filter(chat, word):
    ok = get_stuff()
    if ok.get(chat) and ok[chat].get(word):
        ok[chat].pop(word)
        udB.set_key("FILTERS", ok)


def rem_all_filter(chat):
    ok = get_stuff()
    if ok.get(chat):
        ok.pop(chat)
        udB.set_key("FILTERS", ok)


def get_filter(chat):
    ok = get_stuff()
    if ok.get(chat):
        return ok[chat]


def list_filter(chat):
    ok = get_stuff()
    if ok.get(chat):
        return "".join(f"👉 `{z}`\n" for z in ok[chat])
