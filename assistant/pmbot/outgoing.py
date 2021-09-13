# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/outgoing.py

from telethon import events

from . import *

# outgoing


@asst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def on_out_mssg(event):
    x = await event.get_reply_message()
    if not x:
        return
    who = event.sender_id
    if who == OWNER_ID:
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
            await asst.send_message(to_user, event.message)
