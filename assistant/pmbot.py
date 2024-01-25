# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/incoming.py

# --------------------------------------- Imports -------------------------------------------- #

import asyncio
import logging
import os

from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

from pyUltroid.dB.base import KeyManager
from pyUltroid.dB.botchat_db import *
from pyUltroid.fns.helper import inline_mention

from . import *

botb = KeyManager("BOTBLS", cast=list)
FSUB = Keys.PMBOT_FSUB
PMBOTGROUP = Keys.LOG_CHANNEL
CACHE = {}
SUDOS = Keys.SUDOS
PMUSERS = [OWNER_ID, SUDOS]
logging.basicConfig(
    format="%(asctime)s | %(name)s [%(levelname)s] : %(message)s",
    level=logging.INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
logger = logging.getLogger("DEBUGGING")

# --------------------------------------- Functions -------------------------------------------- #


async def forward_to_multiple(event, *user_ids):
    results = []
    tasks = []

    for user_id in user_ids:
        task = asyncio.create_task(event.forward_to(user_id))
        tasks.append(task)

    for task in tasks:
        try:
            result = await task
            results.append(result)
        except Exception as e:
            results.append(str(e))

    return results


async def check_reply_from_bot(event):
    if (event.is_private and event.is_reply) or (
        event.chat_id == PMBOTGROUP and event.is_reply and event.reply_to_msg_id
    ):
        if event.chat_id == PMBOTGROUP:
            replied_message = await event.client.get_messages(
                event.chat_id, ids=event.reply_to_msg_id
            )
            if replied_message.from_id:
                entity = replied_message.from_id.user_id
            else:
                return False
            return entity == 6176247391
        else:
            # For private messages, no need to check the entity, as it's
            # already a reply
            return True
    return False


# --------------------------------------- Incoming -------------------------------------------- #


@asst_cmd(
    load=AST_PLUGINS,
    incoming=True,
    func=lambda e: e.is_private and not botb.contains(e.sender_id),
)
async def on_new_mssg(event):
    who = event.sender_id
    if event.text.startswith("/") or who == OWNER_ID:
        return
    if FSUB:
        MSG = ""
        BTTS = []
        for chat in FSUB:
            try:
                await event.client.get_permissions(chat, event.sender_id)
            except UserNotParticipantError:
                if not MSG:
                    MSG += get_string("pmbot_1")
                try:
                    uri = ""
                    TAHC_ = await event.client.get_entity(chat)
                    if hasattr(TAHC_, "username") and TAHC_.username:
                        uri = f"t.me/{TAHC_.username}"
                    elif CACHE.get(chat):
                        uri = CACHE[chat]
                    else:
                        if isinstance(TAHC_, Channel):
                            FUGB = await event.client(GetFullChannelRequest(chat))
                        elif isinstance(TAHC_, Chat):
                            FUGB = await event.client(GetFullChatRequest(chat))
                        else:
                            return
                        if FUGB.full_chat.exported_invite:
                            CACHE[chat] = FUGB.full_chat.exported_invite.link
                            uri = CACHE[chat]
                    BTTS.append(Button.url(get_display_name(TAHC_), uri))
                except Exception as er:
                    LOGS.exception(f"Error On PmBot Force Sub!\n - {chat} \n{er}")
        if MSG and BTTS:
            return await event.reply(MSG, buttons=BTTS)
    xx = await event.forward_to(OWNER_ID)
    zz = await event.forward_to(PMBOTGROUP)
    if event.fwd_from:
        await xx.reply(f"From {inline_mention(event.sender)} [`{event.sender_id}`]")
        await zz.reply(f"From {inline_mention(event.sender)} [`{event.sender_id}`]")
    add_stuff(xx.id, who)
    add_stuff(zz.id, who)


# --------------------------------------- Outgoing -------------------------------------------- #


@asst_cmd(
    load=AST_PLUGINS,
    from_users=PMUSERS,
    incoming=True,
    func=check_reply_from_bot,
)
async def on_out_mssg(event):
    x = event.reply_to_msg_id
    logger.info(f"msg_id: {x}")
    if event.chat_id == PMBOTGROUP:
        group_to_user = get_who(x)
    else:
        to_user = get_who(x)

    if event.reply_to_msg_id:
        replied_message = await event.client.get_messages(
            event.chat_id, ids=event.reply_to_msg_id
        )
        if (
            replied_message
            and replied_message.fwd_from
            and replied_message.fwd_from.from_id
            and replied_message.fwd_from.from_id.user_id != 6176247391
        ):
            return
    if event.text.startswith("/who"):
        try:
            if event.is_private and to_user:
                k = await asst.get_entity(to_user)
                photu = await event.client.download_profile_photo(k.id)
                await event.reply(
                    f"• **Name :** {get_display_name(k)}\n• **ID :** `{k.id}`\n• **Link :** {inline_mention(k)}",
                    file=photu,
                )
                if photu:
                    os.remove(photu)
                return
            elif event.chat_id == PMBOTGROUP and group_to_user:
                k = await asst.get_entity(group_to_user)
                photu = await event.client.download_profile_photo(k.id)
                await event.reply(
                    f"• **Name :** {get_display_name(k)}\n• **ID :** `{k.id}`\n• **Link :** {inline_mention(k)}",
                    file=photu,
                )
                if photu:
                    os.remove(photu)
                return
            else:
                return await event.reply(
                    "Unable to determine the user. Please reply to a specific message."
                )
        except BaseException as er:
            return await event.reply(f"**ERROR : **{str(er)}")
    elif event.text.startswith("/"):
        return

    if event.chat_id == PMBOTGROUP:
        if group_to_user:
            await asst.send_message(group_to_user, event.message)
        else:
            return await event.reply(
                "Unable to determine the user. Please reply to a specific message."
            )
    elif event.sender_id in PMUSERS:
        if to_user:
            await asst.send_message(to_user, event.message)
        else:
            return await event.reply(
                "Unable to determine the user. Please reply to a specific message."
            )


# --------------------------------------- Ban/Unban -------------------------------------------- #


@asst_cmd(
    pattern="ban",
    load=AST_PLUGINS,
    from_users=[OWNER_ID],
    func=lambda x: x.is_private,
)
async def banhammer(event):
    if not event.is_reply:
        return await event.reply(get_string("pmbot_2"))
    target = get_who(event.reply_to_msg_id)
    if botb.contains(target):
        return await event.reply(get_string("pmbot_3"))

    botb.add(target)
    await event.reply(f"#BAN\nUser : {target}")
    await asst.send_message(target, get_string("pmbot_4"))


@asst_cmd(
    pattern="unban",
    load=AST_PLUGINS,
    from_users=[OWNER_ID],
    func=lambda x: x.is_private,
)
async def unbanhammer(event):
    if not event.is_reply:
        return await event.reply(get_string("pmbot_5"))
    target = get_who(event.reply_to_msg_id)
    if not botb.contains(target):
        return await event.reply(get_string("pmbot_6"))

    botb.remove(target)
    await event.reply(f"#UNBAN\nUser : {target}")
    await asst.send_message(target, get_string("pmbot_7"))


# --------------------------------------- END -------------------------------------------- #
