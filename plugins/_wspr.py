# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from telethon import Button
from telethon.errors.rpcerrorlist import BotInlineDisabledError as dis
from telethon.errors.rpcerrorlist import BotResponseTimeoutError as rep
from telethon.errors.rpcerrorlist import MessageNotModifiedError as np
from telethon.tl.functions.users import GetFullUserRequest as gu
from telethon.tl.types import UserStatusEmpty as mt
from telethon.tl.types import UserStatusLastMonth as lm
from telethon.tl.types import UserStatusLastWeek as lw
from telethon.tl.types import UserStatusOffline as off
from telethon.tl.types import UserStatusOnline as on
from telethon.tl.types import UserStatusRecently as rec

from . import *

snap = {}
buddhhu = {}


@ultroid_cmd(
    pattern="wspr ?(.*)",
)
async def _(e):
    if e.reply_to_msg_id:
        okk = (await e.get_reply_message()).sender_id
        try:
            put = okk
        except ValueError as ex:
            return await eor(e, str(ex))
        except AttributeError:
            return await eor(e, "No username of replied user was found.")
    else:
        put = e.pattern_match.group(1)
    if put:
        try:
            results = await e.client.inline_query(asst.me.username, f"msg {put}")
        except rep:
            return await eor(
                e,
                get_string("help_2").format(HNDLR),
            )
        except dis:
            return await eor(e, get_string("help_3"))
        await results[0].click(e.chat_id, reply_to=e.reply_to_msg_id, hide_via=True)
        await e.delete()
    else:
        await eor(e, "Add some id or username too")


@in_pattern("msg")
@in_owner
async def _(e):
    vvv = e.text
    zzz = vvv.split(" ", maxsplit=1)
    try:
        ggg = zzz[1]
        sed = ggg.split(" wspr ", maxsplit=1)
        query = sed[0].replace(" ", "")
        if query.isdigit():
            query = int(query)
    except IndexError:
        return
    iuser = e.query.user_id
    try:
        desc = sed[1]
    except IndexError:
        desc = "Touch me"
    if "wspr" not in vvv:
        try:
            logi = await ultroid_bot(gu(id=query))
            name = logi.user.first_name
            ids = logi.user.id
            username = logi.user.username
            mention = f"[{name}](tg://user?id={ids})"
            x = logi.user.status
            bio = logi.about
            if isinstance(x, on):
                status = "Online"
            if isinstance(x, off):
                status = "Offline"
            if isinstance(x, rec):
                status = "Last Seen Recently"
            if isinstance(x, lm):
                status = "Last seen months ago"
            if isinstance(x, lw):
                status = "Last seen weeks ago"
            if isinstance(x, mt):
                status = "Can't Tell"
            text = f"**Name:**    `{name}`\n"
            text += f"**Id:**    `{ids}`\n"
            if username:
                text += f"**Username:**    `{username}`\n"
                url = f"https://t.me/{username}"
            else:
                text += f"**Mention:**    `{mention}`\n"
                url = f"tg://user?id={ids}"
            text += f"**Status:**    `{status}`\n"
            text += f"**About:**    `{bio}`"
            button = [
                Button.url("Private", url=url),
                Button.switch_inline(
                    "Secret msg",
                    query=f"msg {query} wspr Hello 👋",
                    same_peer=True,
                ),
            ]
            sur = e.builder.article(
                title=f"{name}",
                description=desc,
                text=text,
                buttons=button,
            )
        except BaseException:
            name = f"User {query} Not Found\nSearch Again"
            sur = e.builder.article(
                title=name,
                text=name,
            )
    else:
        try:
            logi = await ultroid_bot.get_entity(query)
            button = [
                Button.inline("Secret Msg", data=f"dd_{e.id}"),
                Button.inline("Delete Msg", data=f"del_{e.id}"),
            ]
            us = logi.username
            sur = e.builder.article(
                title=f"{logi.first_name}",
                description=desc,
                text=get_string("wspr_1").format(us),
                buttons=button,
            )
            buddhhu.update({e.id: [logi.id, iuser]})
            snap.update({e.id: desc})
        except ValueError:
            sur = e.builder.article(
                title="Type ur msg", text="You Didn't Type Your Msg"
            )
    await e.answer([sur])


@callback(
    re.compile(
        "dd_(.*)",
    ),
)
async def _(e):
    ids = int(e.pattern_match.group(1).decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            await e.answer(snap[ids], alert=True)
        else:
            await e.answer("Not For You", alert=True)
    else:
        await e.answer("Message Deleted", alert=True)


@callback(re.compile("del_(.*)"))
async def _(e):
    ids = int(e.pattern_match.group(1).decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            buddhhu.pop(ids)
            snap.pop(ids)
            try:
                await e.edit(get_string("wspr_2"))
            except np:
                pass
    else:
        await e.answer("You Can't do this", alert=True)
