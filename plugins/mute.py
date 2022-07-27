# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}mute <reply to msg/ user id>`
    Mute user in current chat.

• `{i}unmute <reply to msg/ user id>`
    Unmute user in current chat.

• `{i}dmute <reply to msg/ user id>`
    Mute user in current chat by deleting msgs.

• `{i}undmute <reply to msg/ use id>`
    Unmute dmuted user in current chat.

• `{i}tmute <time> <reply to msg/ use id>`
    s- seconds
    m- minutes
    h- hours
    d- days
    Mute user in current chat with time.
"""
from telethon import events
from telethon.utils import get_display_name

from pyUltroid.dB.mute_db import is_muted, mute, unmute
from pyUltroid.functions.admins import ban_time

from . import asst, eod, get_string, inline_mention, ultroid_bot, ultroid_cmd


@ultroid_bot.on(events.NewMessage(incoming=True))
async def watcher(event):
    if is_muted(event.chat_id, event.sender_id):
        await event.delete()
    if event.via_bot and is_muted(event.chat_id, event.via_bot_id):
        await event.delete()


@ultroid_cmd(
    pattern="dmute( (.*)|$)",
)
async def startmute(event):
    xx = await event.eor("`Muting...`")
    if input_ := event.pattern_match.group(1).strip():
        try:
            userid = await event.client.parse_id(input_)
        except Exception as x:
            return await xx.edit(str(x))
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        userid = reply.sender_id
        if reply.out or userid in [ultroid_bot.me.id, asst.me.id]:
            return await xx.eor("`You cannot mute yourself or your assistant bot.`")
    elif event.is_private:
        userid = event.chat_id
    else:
        return await xx.eor("`Reply to a user or add their userid.`", time=5)
    chat = await event.get_chat()
    if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
        if not chat.admin_rights.delete_messages:
            return await xx.eor("`No proper admin rights...`", time=5)
    elif "creator" not in vars(chat) and not event.is_private:
        return await xx.eor("`No proper admin rights...`", time=5)
    if is_muted(event.chat_id, userid):
        return await xx.eor("`This user is already muted in this chat.`", time=5)
    mute(event.chat_id, userid)
    await xx.eor("`Successfully muted...`", time=3)


@ultroid_cmd(
    pattern="undmute( (.*)|$)",
)
async def endmute(event):
    xx = await event.eor("`Unmuting...`")
    if input_ := event.pattern_match.group(1).strip():
        try:
            userid = await event.client.parse_id(input_)
        except Exception as x:
            return await xx.edit(str(x))
    elif event.reply_to_msg_id:
        userid = (await event.get_reply_message()).sender_id
    elif event.is_private:
        userid = event.chat_id
    else:
        return await xx.eor("`Reply to a user or add their userid.`", time=5)
    if not is_muted(event.chat_id, userid):
        return await xx.eor("`This user is not muted in this chat.`", time=3)
    unmute(event.chat_id, userid)
    await xx.eor("`Successfully unmuted...`", time=3)


@ultroid_cmd(
    pattern="tmute",
    groups_only=True,
    manager=True,
)
async def _(e):
    xx = await e.eor("`Muting...`")
    huh = e.text.split()
    try:
        tme = huh[1]
    except IndexError:
        return await xx.eor("`Time till mute?`", time=5)
    try:
        input = huh[2]
    except IndexError:
        pass
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        reply = await e.get_reply_message()
        userid = reply.sender_id
        name = (await reply.get_sender()).first_name
    elif input:
        userid = await e.client.parse_id(input)
        name = (await e.client.get_entity(userid)).first_name
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    if userid == ultroid_bot.uid:
        return await xx.eor("`I can't mute myself.`", time=3)
    try:
        bun = ban_time(tme)
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=bun,
            send_messages=False,
        )
        await eod(
            xx,
            f"`Successfully Muted` [{name}](tg://user?id={userid}) `in {chat.title} for {tme}`",
            time=5,
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)


@ultroid_cmd(
    pattern="unmute( (.*)|$)",
    admins_only=True,
    manager=True,
)
async def _(e):
    xx = await e.eor("`Unmuting...`")
    input = e.pattern_match.group(1).strip()
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        reply = await e.get_reply_message()
        userid = reply.sender_id
        name = (await reply.get_sender()).first_name
    elif input:
        userid = await e.client.parse_id(input)
        name = (await e.client.get_entity(userid)).first_name
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=True,
        )
        await eod(
            xx,
            f"`Successfully Unmuted` [{name}](tg://user?id={userid}) `in {chat.title}`",
            time=5,
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)


@ultroid_cmd(
    pattern="mute( (.*)|$)", admins_only=True, manager=True, require="ban_users"
)
async def _(e):
    xx = await e.eor("`Muting...`")
    input = e.pattern_match.group(1).strip()
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = get_display_name(await e.client.get_entity(userid))
    elif input:
        try:
            userid = await e.client.parse_id(input)
            name = inline_mention(await e.client.get_entity(userid))
        except Exception as x:
            return await xx.edit(str(x))
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    if userid == ultroid_bot.uid:
        return await xx.eor("`I can't mute myself.`", time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=False,
        )
        await eod(
            xx,
            f"`Successfully Muted` {name} `in {chat.title}`",
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)
