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
    x = await e.get_sender()
    if isinstance(x, types.User) and (x.bot or x.verified):
        return
    if not udB.get_key("TAG_LOG"):
        return
    try:
        NEEDTOLOG = int(udB.get_key("TAG_LOG"))
    except Exception:
        return LOGS.info(get_string("userlogs_1"))
    y = e.chat
    where_n, who_n = get_display_name(y), get_display_name(x)
    where_l = e.message_link
    buttons = [[Button.url(where_n, where_l)]]
    if isinstance(x, types.User) and x.username:
        try:
            buttons.append(
                [Button.mention(who_n, await asst.get_input_entity(x.username))]
            )
        except Exception as er:
            LOGS.exception(er)
            buttons.append([Button.url(who_n, f"t.me/{x.username}")])
    elif getattr(x, "username"):
        buttons.append([Button.url(who_n, f"t.me/{x.username}")])
    else:
        buttons.append([Button.url(who_n, where_l)])
    try:
        sent = await asst.send_message(NEEDTOLOG, e.message, buttons=buttons)
        tag_add(sent.id, e.chat_id, e.id)
    except MediaEmptyError:
        try:
            msg = await asst.get_messages(e.chat_id, ids=e.id)
            sent = await asst.send_message(NEEDTOLOG, msg, buttons=buttons)
            tag_add(sent.id, e.chat_id, e.id)
        except Exception as me:
            if not isinstance(me, (PeerIdInvalidError, ValueError)):
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
                int(udB.get_key("LOG_CHANNEL")), get_string("userlogs_1")
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
        LOGS.exception(er)


@ultroid_bot.on(
        events.NewMessage(
            outgoing=True,
            chats=[udB.get_key("TAG_LOG")],
            func=lambda e: e.reply_to,
    )
)
async def idk(e):
    id = e.reply_to_msg_id
    chat, msg = who_tag(id)
    if chat and msg:
        try:
            await ultroid_bot.send_message(chat, e.message, reply_to=msg)
        except BaseException as er:
            LOGS.exception(er)


# log for assistant/user joins/add


async def when_added_or_joined(event):
    user = await event.get_user()
    chat = await event.get_chat()
    if not (user and user.is_self):
        return
    if getattr(chat, "username", None):
        chat = f"[{chat.title}](https://t.me/{chat.username}/{event.action_message.id})"
    else:
        chat = f"[{chat.title}](https://t.me/c/{chat.id}/{event.action_message.id})"
    key = "bot" if event.client._bot else "user"
    buttons = Button.inline(
        get_string("userlogs_3"), data=f"leave_ch_{event.chat_id}|{key}"
    )
    if event.user_added:
        tmp = event.added_by
        text = f"#ADD_LOG\n\n{inline_mention(tmp)} just added {inline_mention(user)} to {chat}."
    elif event.from_request:
        text = f"#APPROVAL_LOG\n\n{inline_mention(user)} just got Chat Join Approval to {chat}."
    else:
        text = f"#JOIN_LOG\n\n{inline_mention(user)} just joined {chat}."
    await asst.send_message(int(udB.get_key("LOG_CHANNEL")), text, buttons=buttons)


asst.add_event_handler(
    when_added_or_joined, events.ChatAction(func=lambda x: x.user_added)
)
ultroid_bot.add_event_handler(
    when_added_or_joined,
    events.ChatAction(func=lambda x: x.user_added or x.user_joined),
)

_client = {"bot": asst, "user": ultroid_bot}


@callback(
    re.compile(
        "leave_ch_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def leave_ch_at(event):
    cht = event.data_match.group(1).decode("UTF-8")
    ch_id, client = cht.split("|")
    try:
        client = _client[client]
    except KeyError:
        return
    name = (await client.get_entity(int(ch_id))).title
    await client.delete_dialog(int(ch_id))
    await event.edit(get_string("userlogs_5").format(name))


@callback("do_nothing")
async def _(event):
    await event.answer()
