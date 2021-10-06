# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/incoming.py

# --------------------------------------- Imports -------------------------------------------- #

from pyUltroid.dB.asst_fns import *
from pyUltroid.dB.botchat_db import *
from pyUltroid.functions.helper import inline_mention
from pyUltroid.misc import owner_and_sudos
from telethon import events

from . import *

# --------------------------------------- Incoming -------------------------------------------- #


@asst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def on_new_mssg(event):
    who = event.sender_id
    if is_blacklisted(who):
        return
    # doesn't reply to that user anymore
    if event.text.startswith("/") or who == OWNER_ID:
        return
    xx = await event.forward_to(OWNER_ID)
    if event.fwd_from:
        await xx.reply(f"From **{inline_mention(event.sender)}** [`{event.sender_id}`]")
    add_stuff(xx.id, who)


# --------------------------------------- Outgoing -------------------------------------------- #


@asst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.is_reply))
async def on_out_mssg(event):
    x = await event.get_reply_message()
    who = event.sender_id
    if who != OWNER_ID:
        return
    to_user = get_who(x.id)
    if event.text.startswith("/who"):
        try:
            k = await asst.get_entity(to_user)
            return await event.reply(f"[{k.first_name}](tg://user?id={k.id})")
        except BaseException:
            return
    elif event.text.startswith("/"):
        return
    if to_user:
        await asst.send_message(to_user, event)


# --------------------------------------- Ban/Unban -------------------------------------------- #


@asst_cmd(pattern="ban", from_users=owner_and_sudos(castint=True))
async def banhammer(event):
    if not event.is_private:
        return
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please reply to someone to ban him.")
    target = get_who(x.id)
    if is_blacklisted(target):
        return await asst.send_message(event.chat_id, "User is already banned!")

    blacklist_user(target)
    await asst.send_message(event.chat_id, f"#BAN\nUser - {target}")
    await asst.send_message(
        target,
        "`GoodBye! You have been banned.`\n**Further messages you send will not be forwarded.**",
    )


@asst_cmd(
    pattern="unban",
    from_users=owner_and_sudos(castint=True),
    func=lambda x: x.is_private and x.is_reply,
)
async def unbanhammer(event):
    x = await event.get_reply_message()
    if x is None:
        return await event.edit("Please reply to someone to Unban him.")
    target = get_who(x.id)
    if not is_blacklisted(target):
        return await asst.send_message(event.chat_id, "User was never banned!")

    rem_blacklist(target)
    await asst.send_message(event.chat_id, f"#UNBAN\nUser - {target}")
    await asst.send_message(target, "`Congrats! You have been unbanned.`")


# --------------------------------------- END -------------------------------------------- #
