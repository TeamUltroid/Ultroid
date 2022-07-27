# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def night_grps():
    return udB.get_key("NIGHT_CHATS") or []


def add_night(chat):
    chats = night_grps()
    if chat not in chats:
        chats.append(chat)
        return udB.set_key("NIGHT_CHATS", chats)
    return


def rem_night(chat):
    chats = night_grps()
    if chat in chats:
        chats.remove(chat)
        return udB.set_key("NIGHT_CHATS", chats)
