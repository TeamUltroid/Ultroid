# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from datetime import datetime as dt

from pyUltroid.functions.helper import inline_mention, time_formatter
from telethon.events import NewMessage
from telethon.tl.types import Message, User, MessageEntityMentionCode, MessageEntityMention
from telethon.utils import get_display_name

from . import asst, asst_cmd

AFK = {}


@asst_cmd(pattern="afk", func=lambda x: not x.is_private)
async def go_afk(event):
    sender = await event.get_sender()
    if (not isinstance(sender, User)) or sender.bot:
        return
    try:
        reason = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        reason = None
    if event.is_reply:
        replied = await event.get_reply_message()
        if not reason and replied.text and not replied.media:
            reason = replied.text
        else:
            reason = replied
    time_ = dt.now()
    if AFK.get(event.chat_id):
        AFk[event.chat_id].update({event.sender_id: {"reason": reason, "time": time_}})
    else:
        AFK.update(
            {event.chat_id: {event.sender_id: {"reason": reason, "time": time_}}}
        )
    mention = inline_mention(sender)
    msg = f"**{mention} went AFK Now!**"
    if reason and not isinstance(reason, str):
        await event.reply(reason)
    else:
        msg += f"\n\n**Reason : ** {reason}"
    await event.reply(msg)


@asst.on(NewMessage(func=lambda x: AFK.get(x.chat_id) and not x.is_private))
async def make_change(event):
    chat_ = AFK[event.chat_id]
    dont_send = None
    if event.sender_id in chat_.keys() and not event.text.startswith("/afk"):
        name = get_display_name(event.sender)
        cha_send = chat_[event.sender_id]
        time_ = time_formatter((cha_send["time"] - dt.now()).microseconds)
        msg = f"**{name}** is No Longer AFK!\n**Was AFK for** {time_}"
        await event.reply(msg)
        del chat_[event.sender_id]
        if not chat_:
            del AFK[event.chat_id]
        return
    if event.is_reply:
        replied = await event.get_reply_message()
        name = get_display_name(replied.sender)
        if replied.sender_id in chat_.keys():
            s_der = chat_[replied.sender_id]
            res_ = s_der["reason"]
            time_ = time_formatter((s_der["time"] - dt.now()).microseconds)
            msg = f"**{name}** is AFK Currently!\n**From :** {time_}"
            if res_ and isinstance(res_, str):
                msg += f"\n**Reason :** {res_}"
            elif res_ and isinstance(res_, Message):
                await event.reply(res)
                dont_send = True
            if not dont_send:
                await event.reply(msg)
        return
    ST_SPAM = []
    for ent, text in event.get_entities_text():
        dont_send, entity = None, None
        if isinstance(ent, MessageEntityMentionCode):
            c_id = en.user_id
        elif isinstance(ent, MessageEntityMention):
            c_id = text
        else:
            c_id = None
        if c_id:
            entity = await event.client.get_entity(c_id)
        if entity and entity.id in chat_.keys() and entity.id not in ST_SPAM:
            ST_SPAM.append(entity.id)
            s_der = chat_[entity.id]
            name = get_display_name(entity)
            res_ = s_der["reason"]
            time_ = time_formatter((s_der["time"] - dt.now()).microseconds)
            msg = f"**{name}** is AFK Currently!\n**From :** {time_}"
            if res_ and isinstance(res_, str):
                msg += f"\n**Reason :** {res_}"
            elif res_ and isinstance(res_, Message):
                await event.reply(res)
                dont_send = True
            if not dont_send:
                await event.reply(msg)
