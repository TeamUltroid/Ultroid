# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def _get() -> dict:
    return udB.get_key("RSSFEEDS") or {}


def get_rss_urls(chat):
    cont = _get().get(chat)
    if cont:
        return cont.keys()


def add_rss(chat, url, format=""):
    cont = _get()
    if cont.get(chat):
        if url in cont[chat].keys():
            cont[chat]["format"] = format
        else:
            cont[chat].update({url: format})
    else:
        cont[chat] = {url: format}
    udB.set_key("RSSFEEDS", cont)


def remove_rss(chat):
    cont = _get()
    if cont.get(chat):
        del cont[chat]
        udB.set_key("RSSFEEDS", cont)
