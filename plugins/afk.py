# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_afk")


import asyncio

from telegraph import upload_file as uf
from telethon import events

from pyUltroid.dB.afk_db import add_afk, del_afk, is_afk
from pyUltroid.dB.base import KeyManager

from . import (
    LOG_CHANNEL,
    NOSPAM_CHAT,
    Redis,
    asst,
    get_string,
    mediainfo,
    udB,
    ultroid_bot,
    ultroid_cmd,
)

old_afk_msg = []

is_approved = KeyManager("PMPERMIT", cast=list).contains


@ultroid_cmd(pattern="afk( (.*)|$)", owner_only=True)
async def set_afk(event):
    if event.client._bot or is_afk():
        return
    text, media, media_type = None, None, None
    if event.pattern_match.group(1).strip():
        text = event.text.split(maxsplit=1)[1]
    reply = await event.get_reply_message()
    if reply:
        if reply.text and not text:
            text = reply.text
        if reply.media:
            media_type = mediainfo(reply.media)
            if media_type.startswith(("pic", "gif")):
                file = await event.client.download_media(reply.media)
                iurl = uf(file)
                media = f"https://graph.org{iurl[0]}"
            else:
                media = reply.file.id
    await event.eor("`Done`", time=2)
    add_afk(text, media_type, media)
    ultroid_bot.add_handler(remove_afk, events.NewMessage(outgoing=True))
    ultroid_bot.add_handler(
        on_afk,
        events.NewMessage(
            incoming=True, func=lambda e: bool(e.mentioned or e.is_private)
        ),
    )
    msg1, msg2 = None, None
    if text and media:
        if "sticker" in media_type:
            msg1 = await ultroid_bot.send_file(event.chat_id, file=media)
            msg2 = await ultroid_bot.send_message(
                event.chat_id, get_string("afk_5").format(text)
            )
        else:
            msg1 = await ultroid_bot.send_message(
                event.chat_id, get_string("afk_5").format(text), file=media
            )
    elif media:
        if "sticker" in media_type:
            msg1 = await ultroid_bot.send_file(event.chat_id, file=media)
            msg2 = await ultroid_bot.send_message(event.chat_id, get_string("afk_6"))
        else:
            msg1 = await ultroid_bot.send_message(
                event.chat_id, get_string("afk_6"), file=media
            )
    elif text:
        msg1 = await event.respond(get_string("afk_5").format(text))
    else:
        msg1 = await event.respond(get_string("afk_6"))
    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)
        return await asst.send_message(LOG_CHANNEL, msg2.text)
    await asst.send_message(LOG_CHANNEL, msg1.text)


async def remove_afk(event):
    if event.is_private and udB.get_key("PMSETTING") and not is_approved(event.chat_id):
        return
    elif "afk" in event.text.lower():
        return
    elif event.chat_id in NOSPAM_CHAT:
        return
    if is_afk():
        _, _, _, afk_time = is_afk()
        del_afk()
        off = await event.reply(get_string("afk_1").format(afk_time))
        await asst.send_message(LOG_CHANNEL, get_string("afk_2").format(afk_time))
        for x in old_afk_msg:
            try:
                await x.delete()
            except BaseException:
                pass
        await asyncio.sleep(10)
        await off.delete()


async def on_afk(event):
    if event.is_private and Redis("PMSETTING") and not is_approved(event.chat_id):
        return
    elif "afk" in event.text.lower():
        return
    elif not is_afk():
        return
    if event.chat_id in NOSPAM_CHAT:
        return
    sender = await event.get_sender()
    if sender.bot or sender.verified:
        return
    text, media_type, media, afk_time = is_afk()
    msg1, msg2 = None, None
    if text and media:
        if "sticker" in media_type:
            msg1 = await event.reply(file=media)
            msg2 = await event.reply(get_string("afk_3").format(afk_time, text))
        else:
            msg1 = await event.reply(
                get_string("afk_3").format(afk_time, text), file=media
            )
    elif media:
        if "sticker" in media_type:
            msg1 = await event.reply(file=media)
            msg2 = await event.reply(get_string("afk_4").format(afk_time))
        else:
            msg1 = await event.reply(get_string("afk_4").format(afk_time), file=media)
    elif text:
        msg1 = await event.reply(get_string("afk_3").format(afk_time, text))
    else:
        msg1 = await event.reply(get_string("afk_4").format(afk_time))
    for x in old_afk_msg:
        try:
            await x.delete()
        except BaseException:
            pass
    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)


if udB.get_key("AFK_DB"):
    ultroid_bot.add_handler(remove_afk, events.NewMessage(outgoing=True))
    ultroid_bot.add_handler(
        on_afk,
        events.NewMessage(
            incoming=True, func=lambda e: bool(e.mentioned or e.is_private)
        ),
    )
