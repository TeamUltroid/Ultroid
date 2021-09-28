# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import re

from pyUltroid.dB.botchat_db import tag_add, who_tag
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
        return LOGS.info(get_string("userlogs_1"))
    x = await e.get_sender()
    if isinstance(x, types.User) and (x.bot or x.verified):
        return
    y = e.chat
    where_n = get_display_name(y)
    who_n = get_display_name(x)
    where_l = e.message.message_link
    buttons = [[Button.url(where_n, where_l)]]
    if hasattr(x, "username") and x.username:
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
            await asst.send_message(NEEDTOLOG, get_string("com_4"), buttons=buttons)
    except (PeerIdInvalidError, ValueError):
        try:
            CACHE_SPAM[NEEDTOLOG]
        except KeyError:
            await asst.send_message(
                int(udB.get("LOG_CHANNEL")), get_string("userlogs_1")
            )
            CACHE_SPAM.update({NEEDTOLOG: True})
    except ChatWriteForbiddenError:
        try:
            await asst.get_permissions(NEEDTOLOG, "me")
            MSG = get_string("userlogs_4")
        except UserNotParticipantError:
            MSG = get_string("userlogs_2")
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
    if hasattr(chat, "username") and chat.username:
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    if not (user and user.is_self):
        return
    tmp = event.added_by
    buttons = Button.inline(
        get_string("userlogs_3"), data=f"leave_ch_{event.chat_id}|bot"
    )
    await asst.send_message(
        int(udB.get("LOG_CHANNEL")),
        f"#ADD_LOG\n\n[{tmp.first_name}](tg://user?id={tmp.id}) added [{user.first_name}](tg://user?id={user.id}) to {chat}.",
        buttons=buttons,
    )


# log for user's new joins


@ultroid_bot.on(events.ChatAction)
async def when_ultd_added_to_chat(event):
    user = await event.get_user()
    chat = await event.get_chat()
    if not (user and user.is_self):
        return
    if hasattr(chat, "username") and chat.username:
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    buttons = Button.inline(
        get_string("userlogs_3"), data=f"leave_ch_{event.chat_id}|user"
    )
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
    owner=True,
)
async def leave_ch_at(event):
    cht = event.data_match.group(1).decode("UTF-8")
    ch_id, client = cht.split("|")
    if client == "bot":
        client = asst
    elif client == "user":
        client = ultroid_bot
    else:
        return
    name = (await client.get_entity(int(ch_id))).title
    await client.delete_dialog(int(ch_id))
    await event.edit(get_string("userlogs_5").format(name))
