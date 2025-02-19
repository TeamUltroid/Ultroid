# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def get_stuff():
    return udB.get_key("WARNS") or {}


def add_warn(chat, user, count, reason):
    x = get_stuff()
    try:
        x[chat].update({user: [count, reason]})
    except BaseException:
        x.update({chat: {user: [count, reason]}})
    return udB.set_key("WARNS", x)


def warns(chat, user):
    x = get_stuff()
    try:
        count, reason = x[chat][user][0], x[chat][user][1]
        return count, reason
    except BaseException:
        return 0, None


def reset_warn(chat, user):
    x = get_stuff()
    try:
        x[chat].pop(user)
        return udB.set_key("WARNS", x)
    except BaseException:
        return
