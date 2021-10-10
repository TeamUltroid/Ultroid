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

buddhhu = {}


@ultroid_cmd(
    pattern="wspr ?(.*)",
)
async def _(e):
    if e.reply_to_msg_id:
        okk = await e.get_reply_message()
        if okk.sender.username:
            put = f"@{okk.sender.username}"
        put = okk.sender_id
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
        return await e.delete()
    await eor(e, get_string("wspr_3"))


@in_pattern("wspr", owner=True)
async def _(e):
    iuser = e.query.user_id
    zzz = e.text.split(maxsplit=2)
    try:
        query = zzz[1]
        if query.isdigit():
            query = int(query)
        logi = await ultroid_bot.get_entity(query)
    except IndexError:
        sur = e.builder.article(
            title="Give Username",
            description="You Didn't Type Username or id.",
            text="You Didn't Type Username or id.",
        )
        return await e.answer([sur])
    except ValueError:
        sur = e.builder.article(
            title="User Not Found",
            description="Make sure username or id is correct.",
            text="Make sure username or id is correct.",
        )
        return await e.answer([sur])
    try:
        desc = zzz[2]
    except IndexError:
        sur = e.builder.article(title="Type ur msg", text="You Didn't Type Your Msg")
        return await e.answer([sur])
    button = [
        Button.inline("Secret Msg", data=f"dd_{e.id}"),
        Button.inline("Delete Msg", data=f"del_{e.id}"),
    ]
    us = logi.username or logi.first_name
    sur = e.builder.article(
        title=f"{logi.first_name}",
        description=desc,
        text=get_string("wspr_1").format(us),
        buttons=button,
    )
    buddhhu.update({e.id: [logi.id, iuser, desc]})
    await e.answer([sur])


@in_pattern("msg", owner=True)
async def _(e):
    zzz = e.text.split(maxsplit=1)
    desc = "Touch me"
    try:
        query = zzz[1]
        if query.isdigit():
            query = int(query)
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
                query=f"wspr {query} Hello 👋",
                same_peer=True,
            ),
        ]
        sur = e.builder.article(
            title=f"{name}",
            description=desc,
            text=text,
            buttons=button,
        )
    except IndexError:
        sur = e.builder.article(
            title="Give Username",
            description="You Didn't Type Username or id.",
            text="You Didn't Type Username or id.",
        )
    except BaseException:
        name = get_string("wspr_4").format(query)
        sur = e.builder.article(
            title=name,
            text=name,
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
            await e.answer(buddhhu[ids][-1], alert=True)
        else:
            await e.answer("Not For You", alert=True)
    else:
        await e.answer(get_string("wspr_2"), alert=True)


@callback(re.compile("del_(.*)"))
async def _(e):
    ids = int(e.pattern_match.group(1).decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            buddhhu.pop(ids)
            try:
                await e.edit(get_string("wspr_2"))
            except np:
                pass
        else:
            await e.answer(get_string("wspr_5"), alert=True)
