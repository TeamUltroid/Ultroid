# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/incoming.py

# --------------------------------------- Imports -------------------------------------------- #

# TODO: fix imports

import os

from pyUltroid.dB.asst_fns import *
from pyUltroid.dB.botchat_db import *
from pyUltroid.fns.helper import inline_mention
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import Channel, Chat
from telethon.utils import get_display_name

FSUB = udB.get_key("PMBOT_FSUB")
CACHE = {}
# --------------------------------------- Incoming -------------------------------------------- #


@asst_cmd(
    load=AST_PLUGINS,
    incoming=True,
    func=lambda e: e.is_private and not is_blacklisted(e.sender_id),
)
async def on_new_mssg(event):
    who = event.sender_id
    # doesn't reply to that user anymore
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
    if event.fwd_from:
        await xx.reply(f"From {inline_mention(event.sender)} [`{event.sender_id}`]")
    add_stuff(xx.id, who)


# --------------------------------------- Outgoing -------------------------------------------- #


@asst_cmd(
    load=AST_PLUGINS,
    from_users=[OWNER_ID],
    incoming=True,
    func=lambda e: e.is_private and e.is_reply,
)
async def on_out_mssg(event):
    x = event.reply_to_msg_id
    to_user = get_who(x)
    if event.text.startswith("/who"):
        try:
            k = await asst.get_entity(to_user)
            photu = await event.client.download_profile_photo(k.id)
            await event.reply(
                f"• **Name :** {get_display_name(k)}\n• **ID :** `{k.id}`\n• **Link :** {inline_mention(k)}",
                file=photu,
            )
            if photu:
                os.remove(photu)
            return
        except BaseException as er:
            return await event.reply(f"**ERROR : **{str(er)}")
    elif event.text.startswith("/"):
        return
    if to_user:
        await asst.send_message(to_user, event.message)


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
    if is_blacklisted(target):
        return await event.reply(get_string("pmbot_3"))

    blacklist_user(target)
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
    if not is_blacklisted(target):
        return await event.reply(get_string("pmbot_6"))

    rem_blacklist(target)
    await event.reply(f"#UNBAN\nUser : {target}")
    await asst.send_message(target, get_string("pmbot_7"))


# --------------------------------------- END -------------------------------------------- #
