# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("echo")


from telethon.utils import get_display_name

from . import inline_mention, udB, ultroid_cmd


@ultroid_cmd(pattern="addecho( (.*)|$)")
async def echo(e):
    r = await e.get_reply_message()
    if r:
        user = r.sender_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await e.eor("Reply To A user.", time=5)
    if check_echo(e.chat_id, user):
        return await e.eor("Echo already activated for this user.", time=5)
    add_echo(e.chat_id, user)
    ok = await e.client.get_entity(user)
    user = inline_mention(ok)
    await e.eor(f"Activated Echo For {user}.")


@ultroid_cmd(pattern="remecho( (.*)|$)")
async def rm(e):
    r = await e.get_reply_message()
    if r:
        user = r.sender_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await e.eor("Reply To A User.", time=5)
    if check_echo(e.chat_id, user):
        rem_echo(e.chat_id, user)
        ok = await e.client.get_entity(user)
        user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
        return await e.eor(f"Deactivated Echo For {user}.")
    await e.eor("Echo not activated for this user")


@ultroid_cmd(pattern="listecho$")
async def lstecho(e):
    if k := list_echo(e.chat_id):
        user = "**Activated Echo For Users:**\n\n"
        for x in k:
            ok = await e.client.get_entity(int(x))
            kk = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
            user += f"•{kk}" + "\n"
        await e.eor(user)
    else:
        await e.eor("`List is Empty, For echo`", time=5)


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
