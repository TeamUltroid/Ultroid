# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/incoming.py
"""
Incoming Message(s) forwarder.
"""

from telethon import events
from pyUltroid.functions.helper import inline_mention
from . import *

# if incoming


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
