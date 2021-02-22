# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon import custom, events
from telethon.tl.types import Channel
from telethon.utils import get_display_name

from . import *


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: (e.mentioned),
    )
)
async def all_messages_catcher(event):
    if udB.get("TAG_LOG") is not None:
        NEEDTOLOG = int(udB.get("TAG_LOG"))
        await event.forward_to(NEEDTOLOG)
        ammoca_message = ""
        who_ = await event.client.get_entity(event.sender_id)
        if who_.bot or who_.verified or who_.support:
            return
        who_m = f"[{get_display_name(who_)}](tg://user?id={who_.id})"
        where_ = await event.client.get_entity(event.chat_id)
        where_m = get_display_name(where_)
        button_text = "📨 Go to Message  "
        if isinstance(where_, Channel):
            message_link = f"https://t.me/c/{where_.id}/{event.id}"
            chat_link = f"https://t.me/c/{where_.id}"
        else:
            message_link = f"tg://openmessage?chat_id={where_.id}&message_id={event.id}"
            chat_link = f"tg://openmessage?chat_id={where_.id}"
        ammoca_message += f"{who_m} tagged you in [{where_m}]({chat_link})"
        try:
            await asst.send_message(
                entity=NEEDTOLOG,
                message=ammoca_message,
                link_preview=False,
                buttons=[[custom.Button.url(button_text, message_link)]],
                silent=True,
            )
        except BaseException:
            pass
    else:
        return
