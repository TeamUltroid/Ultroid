# Ultroid - UserBot
# Copyright (C) 2021 Gladiator-007
#
# This file is a part of < https://github.com/Gladiator-007/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/Gladiator-007/Ultroid/blob/main/LICENSE/>.

# https://github.com/xditya/TeleBot/blob/master/telebot/plugins/mybot/pmbot/incoming.py
"""
Incoming Message(s) forwarder.
"""

from telethon import events

from . import *

# if incoming


@asst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def on_new_mssg(event):
    incoming = event.raw_text
    who = event.sender_id
    if is_blacklisted(who):
        return
    # doesn't reply to that user anymore
    if incoming.startswith("/"):
        pass
    elif who == OWNER_ID:
        return
    else:
        xx = await event.forward_to(OWNER_ID)
        add_stuff(xx.id, who)
