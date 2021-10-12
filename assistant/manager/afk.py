# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import time
from . import asst_cmd, asst
from telethon.events import NewMessage, ChatAction
from telethon.tl.types import User
from telethon.utils import get_display_name
from pyUltroid.functions.helper import inline_mention

AFK = {}

@asst_cmd(pattern="afk", func=lambda x: not x.is_private)
async def go_afk(event):
  sender = await event.get_sender()
  if not isinstance(sender, User):
    return
  try:
    reason = event.text.split(" ", maxsplit=1)[1]
  except IndexError:
    reason = None
  if event.is_reply:
    replied = await event.get_reply_message()
    if not reason and replied.text:
      reason = replied.text
  time_ = time.time()
  if AFK.get(e.chat_id):
    AFk[event.chat_id].update({event.sender_id:{"reason":reason,"time":time_}})
  else:
    AFK.update({event.chat_id:{event.sender_id:{"reason":reason,"time":time_}}})
  mention = inline_mention(sender)
  msg = f"**{mention} went AFK Now!**"
  if reason and not isinstance(reason, str):
    await event.reply(reason)
  else:
    msg +=f"\n\n**Reason : ** {reason}"
  await event.reply(msg)

  
@asst.on(NewMessage(func=lambda x: AFK.get(x.chat_id)))
async def make_change(event):
  chat_ = AFK[event.chat_id]
  name = get_display_name(event.sender)
  if event.sender_id in chat_.keys():
    cha_send = chat_[event.sender_id]
    reason = cha_send["reason"]
    msg = f"**{name}** is No Longer AFK!\n**Was AFK for {time_formatter(cha_send['time']-time.time())}"
    await event.reply(msg)
    del chat_[event.sender_id]
    if not chat_:
      del AFK[event.chat_id]
    return
  
