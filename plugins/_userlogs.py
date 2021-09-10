# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import re

from pyUltroid.functions.botchat_db import tag_add, who_tag
from telethon.errors.rpcerrorlist import (
    ChatWriteForbiddenError,
    MediaEmptyError,
    PeerIdInvalidError,
    UserNotParticipantError,
)
from telethon.utils import get_display_name

from . import *

CACHE_SPAM = {}


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: (e.mentioned),
    ),
)
async def all_messages_catcher(e):
    if not udB.get("TAG_LOG"):
        return
    try:
        NEEDTOLOG = int(udB.get("TAG_LOG"))
    except Exception:
        return LOGS.info("you given Wrong Grp/Channel ID in TAG_LOG.")
    x = await e.get_sender()
    if isinstance(x, types.User) and (x.bot or x.verified):
        return
    y = e.chat
    where_n = get_display_name(y)
    who_n = get_display_name(x)
    where_l = e.message.message_link
    buttons = [[Button.url(where_n, where_l)]]
    if x.username:
        who_l = f"https://t.me/{x.username}"
        buttons.append([Button.url(who_n, who_l)])
    else:
        buttons.append([Button.inline(who_n, data=f"who{x.id}")])
    try:
        sent = await asst.send_message(NEEDTOLOG, e.message, buttons=buttons)
        tag_add(sent.id, e.chat_id, e.id)
    except MediaEmptyError:
        try:
            msg = await asst.get_messages(e.chat_id, ids=e.id)
            sent = await asst.send_message(NEEDTOLOG, msg, buttons=buttons)
            tag_add(sent.id, e.chat_id, e.id)
        except Exception as me:
            LOGS.info(me)
            if e.photo or e.sticker or e.gif:
                try:
                    media = await e.download_media()
                    await asst.send_message(
                        NEEDTOLOG, e.message.text, file=media, buttons=buttons
                    )
                    return os.remove(media)
                except Exception as er:
                    LOGS.info(er)
            await asst.send_message(NEEDTOLOG, "`Unsupported Media`", buttons=buttons)
    except (PeerIdInvalidError, ValueError):
        await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            "The Chat Id You Set In Tag Logger Is Wrong , Please Correct It",
        )
    except ChatWriteForbiddenError:
        try:
            await asst.get_permissions(NEEDTOLOG, "me")
            MSG = "Your Asst Cant Send Messages in Tag Log Chat."
            MSG += "\n\nPlease Review the case or you can off"
            MSG += "Your TagLogger, if you dont want to use it"
        except UserNotParticipantError:
            MSG = "Add me to Your Tag Logger Chat to Log Tags"
        try:
            CACHE_SPAM[NEEDTOLOG]
        except KeyError:
            await asst.send_message(LOG_CHANNEL, MSG)
            CACHE_SPAM.update({NEEDTOLOG: True})
    except Exception as er:
        LOGS.info(str(er))


if udB.get("TAG_LOG"):

    @ultroid_bot.on(
        events.NewMessage(
            outgoing=True, chats=[int(udB["TAG_LOG"])], func=lambda e: e.reply_to
        )
    )
    async def idk(e):
        id = e.reply_to_msg_id
        chat, msg = who_tag(id)
        if chat and msg:
            try:
                await ultroid_bot.send_message(chat, e.message, reply_to=msg)
            except BaseException:
                pass


@callback(re.compile("who(.*)"))
async def _(e):
    wah = e.pattern_match.group(1).decode("UTF-8")
    y = await ultroid_bot.get_entity(int(wah))
    who = f"[{get_display_name(y)}](tg://user?id={y.id})"
    x = await e.reply(f"Mention By user : {who}")
    await asyncio.sleep(6)
    await x.delete()


# log for assistant
@asst.on(events.ChatAction)
async def when_asst_added_to_chat(event):
    if not event.user_added:
        return
    user = await event.get_user()
    chat = await event.get_chat()
    if chat.username:
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    if user and user.is_self:
        tmp = event.added_by
        buttons = Button.inline("Leave Chat", data=f"leave_ch_{event.chat_id}|bot")
        return await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#ADD_LOG\n\n[{tmp.first_name}](tg://user?id={tmp.id}) added [{user.first_name}](tg://user?id={user.id}) to {chat}.",
            buttons=buttons,
        )


# log for user's new joins


@ultroid.on(events.ChatAction)
async def when_ultd_added_to_chat(event):
    user = await event.get_user()
    chat = await event.get_chat()
    if not (user and user.is_self):
        return
    if chat.username:
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    buttons = Button.inline("Leave Chat", data=f"leave_ch_{event.chat_id}|user")
    if event.user_added:
        tmp = event.added_by
        text = f"#ADD_LOG\n\n{inline_mention(tmp)} just added {inline_mention(user)} to {chat}."
    elif event.user_joined:
        text = f"#JOIN_LOG\n\n[{user.first_name}](tg://user?id={user.id}) just joined {chat}."
    else:
        return
    await asst.send_message(int(udB["LOG_CHANNEL"]), text, buttons=buttons)


@callback(
    re.compile(
        "leave_ch_(.*)",
    ),
)
@owner
async def leave_ch_at(event):
    cht = event.data_match.group(1).decode("UTF-8")
    ch_id, client = cht.split("|")
    if client == "bot":
        name = (await asst.get_entity(int(ch_id))).title
        await asst.delete_dialog(int(ch_id))
    elif client == "user":
        name = (await ultroid_bot.get_entity(int(ch_id))).title
        await ultroid_bot.delete_dialog(int(ch_id))
    await event.edit(f"Left `{name}`")
