# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from .. import udB


def get_stuff():
    return udB.get_key("ECHO") or {}


def add_echo(chat, user):
    x = get_stuff()
    if k := x.get(int(chat)):
        if user not in k:
            k.append(int(user))
        x.update({int(chat): k})
    else:
        x.update({int(chat): [int(user)]})
    return udB.set_key("ECHO", x)


def rem_echo(chat, user):
    x = get_stuff()
    if k := x.get(int(chat)):
        if user in k:
            k.remove(int(user))
        x.update({int(chat): k})
    return udB.set_key("ECHO", x)


def check_echo(chat, user):
    x = get_stuff()
    if (k := x.get(int(chat))) and int(user) in k:
        return True


def list_echo(chat):
    x = get_stuff()
    return x.get(int(chat))
