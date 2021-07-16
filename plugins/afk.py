# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}afk <optional reason>`
    AFK means away from keyboard,

    After u active this if Someone tag or msg u then It auto Reply Him/her,
    (Note : By Reply To any media U can set media afk too).

"""

import asyncio
from datetime import datetime

from pyUltroid.functions.pmpermit_db import *
from telethon import events
from telethon.tl.functions.account import GetPrivacyRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, PrivacyValueAllowAll

from . import *

global USER_AFK
global afk_time
global last_afk_message
global last_afk_msg
global afk_start
global afk_end
USER_AFK = {}
afk_time = None
last_afk_message = {}
last_afk_msg = {}
afk_start = {}

LOG = int(udB.get("LOG_CHANNEL"))


@ultroid_bot.on(events.NewMessage(outgoing=True))
@ultroid_bot.on(events.MessageEdited(outgoing=True))
async def set_not_afk(event):
    if event.is_private:
        if Redis("PMSETTING") == "True":
            if not is_approved(event.chat_id):
                return
    global USER_AFK
    global afk_time
    global last_afk_message
    global afk_start
    global afk_end
    back_alive = datetime.now()
    afk_end = back_alive.replace(microsecond=0)
    if afk_start != {}:
        total_afk_time = str(afk_end - afk_start)
    current_message = event.message.message
    if "afk" not in current_message and "yes" in USER_AFK:
        try:
            if pic.endswith((".tgs", ".webp")):
                shite = await ultroid_bot.send_message(event.chat_id, file=pic)
                shites = await ultroid_bot.send_message(
                    event.chat_id,
                    get_string("afk_1").format(total_afk_time),
                )
            else:
                shite = await ultroid_bot.send_message(
                    event.chat_id,
                    get_string("afk_1").format(total_afk_time),
                    file=pic,
                )
        except BaseException:
            shite = await ultroid_bot.send_message(
                event.chat_id,
                get_string("afk_1").format(total_afk_time),
            )
        try:
            try:
                if pic.endswith((".tgs", ".webp")):
                    await ultroid_bot.send_message(LOG, file=pic)
                    await ultroid_bot.send_message(
                        LOG,
                        get_string("afk_2").format(total_afk_time),
                    )
                else:
                    await ultroid_bot.send_message(
                        LOG,
                        get_string("afk_2").format(total_afk_time),
                        file=pic,
                    )
            except BaseException:
                await ultroid_bot.send_message(
                    LOG,
                    get_string("afk_2").format(total_afk_time),
                )
        except BaseException:
            pass
        await asyncio.sleep(3)
        await shite.delete()
        try:
            await shites.delete()
        except BaseException:
            pass
        USER_AFK = {}
        afk_time = None


@ultroid_bot.on(
    events.NewMessage(incoming=True, func=lambda e: bool(e.mentioned or e.is_private)),
)
async def on_afk(event):
    if event.is_private:
        if Redis("PMSETTING") == "True":
            if not is_approved(event.chat_id):
                return
    global USER_AFK
    global afk_time
    global last_afk_message
    global afk_start
    global afk_end
    back_alivee = datetime.now()
    afk_end = back_alivee.replace(microsecond=0)
    if afk_start != {}:
        total_afk_time = str(afk_end - afk_start)
    current_message_text = event.message.message.lower()
    if "afk" in current_message_text:
        return False
    sender = await event.get_sender()
    if USER_AFK and not (sender.bot or sender.verified):
        msg = None
        if reason:
            message_to_reply = get_string("afk_3").format(total_afk_time, reason)
        else:
            message_to_reply = get_string("afk_4").format(total_afk_time)
        try:
            if pic.endswith((".tgs", ".webp")):
                msg = await event.reply(file=pic)
                msgs = await event.reply(message_to_reply)
            else:
                msg = await event.reply(message_to_reply, file=pic)
        except BaseException:
            msg = await event.reply(message_to_reply)
        await asyncio.sleep(2.5)
        if event.chat_id in last_afk_message:
            await last_afk_message[event.chat_id].delete()
        try:
            if event.chat_id in last_afk_msg:
                await last_afk_msg[event.chat_id].delete()
        except BaseException:
            pass
        last_afk_message[event.chat_id] = msg
        try:
            if msgs:
                last_afk_msg[event.chat_id] = msgs
        except BaseException:
            pass


@ultroid_cmd(pattern=r"afk ?(.*)")
async def _(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Full Sudo Restricted.`")
    reply = await event.get_reply_message()
    if event.client._bot:
        return await eor(event, "Master, I am a Bot, I cant go AFK..")
    global USER_AFK
    global afk_time
    global last_afk_message
    global last_afk_msg
    global afk_start
    global afk_end
    global reason
    global pic
    USER_AFK = {}
    afk_time = None
    last_afk_message = {}
    last_afk_msg = {}
    afk_end = {}
    start_1 = datetime.now()
    afk_start = start_1.replace(microsecond=0)
    reason = event.pattern_match.group(1)
    if reply:
        pic = await event.client.download_media(reply)
    else:
        pic = None
    if not USER_AFK:
        last_seen_status = await ultroid_bot(
            GetPrivacyRequest(InputPrivacyKeyStatusTimestamp()),
        )
        if isinstance(last_seen_status.rules, PrivacyValueAllowAll):
            afk_time = datetime.datetime.now()
        USER_AFK = f"yes: {reason} {pic}"
        if reason:
            try:
                if pic.endswith((".tgs", ".webp")):
                    await ultroid_bot.send_message(event.chat_id, file=pic)
                    await ultroid_bot.send_message(
                        event.chat_id,
                        get_string("afk_5").format(reason),
                    )
                else:
                    await ultroid_bot.send_message(
                        event.chat_id,
                        get_string("afk_5").format(reason),
                        file=pic,
                    )
            except BaseException:
                await ultroid_bot.send_message(
                    event.chat_id,
                    get_string("afk_5").format(reason),
                )
        else:
            try:
                if pic.endswith((".tgs", ".webp")):
                    await ultroid_bot.send_message(event.chat_id, file=pic)
                    await ultroid_bot.send_message(event.chat_id, get_string("afk_6"))
                else:
                    await ultroid_bot.send_message(
                        event.chat_id,
                        get_string("afk_6"),
                        file=pic,
                    )
            except BaseException:
                await ultroid_bot.send_message(event.chat_id, get_string("afk_6"))
        await event.delete()
        try:
            if reason and pic:
                if pic.endswith((".tgs", ".webp")):
                    await ultroid_bot.send_message(LOG, file=pic)
                    await ultroid_bot.send_message(
                        LOG,
                        get_string("afk_7").format(reason),
                    )
                else:
                    await ultroid_bot.send_message(
                        LOG,
                        get_string("afk_7").format(reason),
                        file=pic,
                    )
            elif reason:
                await ultroid_bot.send_message(LOG, get_string("afk_7").format(reason))
            elif pic:
                if pic.endswith((".tgs", ".webp")):
                    await ultroid_bot.send_message(LOG, file=pic)
                    await ultroid_bot.send_message(LOG, get_string("afk_8"))
                else:
                    await ultroid_bot.send_message(LOG, get_string("afk_8"), file=pic)
            else:
                await ultroid_bot.send_message(LOG, get_string("afk_8"))
        except BaseException:
            pass
