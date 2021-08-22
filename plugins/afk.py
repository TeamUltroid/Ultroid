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


from pyUltroid.functions.afk_db import *
from pyUltroid.functions.pmpermit_db import *
from telegraph import upload_file as uf
from telethon import events

from . import *

old_afk_msg = []


@ultroid_cmd(pattern="afk ?(.*)", fullsudo=True)
async def set_afk(event):
    if event.client._bot:
        await eor(event, "Master, I am a Bot, I cant go AFK..")
    elif is_afk():
        return
    text, media, media_type = None, None, None
    if event.pattern_match.group(1):
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
                media = f"https://telegra.ph{iurl[0]}"
            elif "sticker" in media_type:
                media = reply.file.id
            else:
                return await eor(event, "`Unsupported media`", time=5)
    add_afk(text, media_type, media)
    await eor(event, "`Done`")
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
        msg1 = await ultroid_bot.send_message(
            event.chat_id, get_string("afk_5").format(text)
        )
    else:
        msg1 = await ultroid_bot.send_message(event.chat_id, get_string("afk_6"))
    old_afk_msg.append(msg1)
    if msg2:
        old_afk_msg.append(msg2)
        return await asst.send_message(LOG_CHANNEL, msg2.text)
    await asst.send_message(LOG_CHANNEL, msg1.text)


@ultroid_bot.on(events.MessageEdited(outgoing=True))
async def remove_afk(event):
    if (
        event.is_private
        and Redis("PMSETTING") == "True"
        and not is_approved(event.chat_id)
        and "afk" in event.text
    ):
        return
    if is_afk():
        _, _, _, afk_time = is_afk()
        del_afk()
        await event.reply(get_string("afk_1").format(afk_time))
        await asst.send_message(LOG_CHANNEL, get_string("afk_2").format(afk_time))
        for x in old_afk_msg:
            try:
                await x.delete()
            except BaseException:
                pass


@ultroid_bot.on(
    events.NewMessage(incoming=True, func=lambda e: bool(e.mentioned or e.is_private)),
)
async def on_afk(event):
    if (
        event.is_private
        and Redis("PMSETTING") == "True"
        and not is_approved(event.chat_id)
        or not is_afk()
        or "afk" in event.text
    ):
        return
    if event.chat_id in NOSPAM_CHAT:
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
