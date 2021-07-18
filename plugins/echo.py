# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

•`{i}addecho <reply to anyone>`
   Start Auto Echo message of Replied user.

•`{i}remecho <reply to anyone>`
   Turn It off

•`{i}listecho <reply to anyone>`
   To Get list.

"""

from pyUltroid.functions.echo_db import *
from telethon.utils import get_display_name

from . import *


@ultroid_cmd(pattern="addecho ?(.*)")
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
            return await eod(e, "Reply To A user.")
    if check_echo(e.chat_id, user):
        return await eod(e, "Echo already activated for this user.")
    add_echo(e.chat_id, user)
    ok = await e.client.get_entity(user)
    user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
    await eor(e, f"Activated Echo For {user}.")


@ultroid_cmd(pattern="remecho ?(.*)")
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
            return await eod(e, "Reply To A User.")
    if check_echo(e.chat_id, user):
        rem_echo(e.chat_id, user)
        ok = await e.client.get_entity(user)
        user = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
        return await eor(e, f"Deactivated Echo For {user}.")
    await eor(e, "Echo not activated for this user")


@ultroid_bot.on(events.NewMessage(incoming=True))
async def okk(e):
    if check_echo(e.chat_id, e.sender_id):
        try:
            ok = await e.client.get_messages(e.chat_id, ids=e.id)
            return await e.client.send_message(e.chat_id, ok)
        except Exception as er:
            LOGS.info(er)


@ultroid_cmd(pattern="listecho$")
async def lstecho(e):
    k = list_echo(e.chat_id)
    if k:
        user = "**Activated Echo For Users:**\n\n"
        for x in k:
            ok = await e.client.get_entity(int(x))
            kk = f"[{get_display_name(ok)}](tg://user?id={ok.id})"
            user += "•" + kk + "\n"
        await eor(e, user)
    else:
        await eod(e, "`List is Empty, For echo`")
