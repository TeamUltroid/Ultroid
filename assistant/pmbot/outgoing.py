# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/outgoing.py

from telethon import events
from telethon.utils import pack_bot_file_id

from . import *

# outgoing

@asst.on(events.NewMessage(func=lambda e: e.is_private))
async def on_out_mssg(event):
    x = await event.get_reply_message()
    if x is None:
        return
    to_send = event.raw_text
    who = event.sender_id
    if who == OWNER_ID:
        if to_send.startswith("/"):
            return
        to_user = udB.get(str(x.id))
        if event.text is not None and event.media:
            # if sending media
            bot_api_file_id = pack_bot_file_id(event.media)
            await asst.send_file(
                to_user,
                file=bot_api_file_id,
                caption=event.text
            )
        else:
            await asst.send_message(to_user, to_send)
