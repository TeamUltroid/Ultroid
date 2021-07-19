# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import os
import random

from . import *


@asst.on_message(
    filters.command(["play", f"play@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
    & filters.group
)
async def startup(_, message):
    msg = await eor(message, "`Processing..`")
    song = message.text.split(" ", maxsplit=1)
    reply = message.reply_to_message

    if len(song) > 1 and song[1].startswith("@" or "-"):
        song = song[1].split(" ", maxsplit=1)
        chat = await Client.get_chat(song[0])
    else:
        chat = message.chat

    thumb, med, song_name = None, None, ""
    if reply:
        if reply.audio:
            med = reply.audio
            song_name = med.title
        elif reply.video or reply.audio:
            med = reply.video or reply.audio
            song_name = med.file_name
        if med and med.thumbs:
            dll = med.thumbs[0].file_id
            thumb = await asst.download_media(dll)
    TS = dt.now().strftime("%H:%M:%S")
    if not reply and len(song) > 1:
        song, thumb, song_name, duration = await download(msg, song[1], chat.id, TS)
    elif not reply and len(song) == 1:
        return await msg.edit_text("Pls Give me Something to Play...")
    elif not (reply.audio or reply.voice or reply.video):
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    else:
        dl = await reply.download()
        duration = med.duration
        song = f"VCSONG_{chat.id}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
    from_user = message.from_user.mention
    if chat.id in CallsClient.active_calls.keys():
        add_to_queue(chat.id, song, song_name, from_user, duration)
        return await msg.edit(
            f"Added **{song_name}** to queue at #{list(QUEUE[chat.id].keys())[-1]}"
        )
    che = await vc_check(chat.id, chat.type)
    if not che:
        try:
            Up = await Client.send(
                functions.phone.CreateGroupCall(
                    peer=await Client.resolve_peer(chat.id),
                    random_id=random.randrange(1, 100),
                )
            )
        except Exception as E:
            return await msg.edit_text(str(E))
    if thumb:
        await msg.delete()
        msg = await message.reply_photo(
            thumb,
            caption=f"🎸 **Playing :** {song_name}\n**☘ Duration :** {time_formatter(duration*1000)}\n👤 **Requested By :** {from_user}",
            reply_markup=reply_markup(chat.id),
        )
        if os.path.exists(thumb):
            os.remove(thumb)
    try:
        CallsClient.join_group_call(chat.id, song)
    except Exception as E:
        return await msg.edit_text(str(E))
    CH = await asst.send_message(
        LOG_CHANNEL, f"Joined Voice Call in {chat.title} [`{chat.id}`]"
    )
    await asyncio.sleep(duration)
    os.remove(song)
    await msg.delete()
    await CH.delete()


@Client.on_message(filters.me & filters.command(["play"], HNDLR) & ~filters.edited)
async def cstartup(_, message):
    await startup(_, message)


async def queue_func(chat_id: int):
    try:
        song, title, from_user, pos, dur = get_from_queue(chat_id)
        CallsClient.change_stream(chat_id, song)
       #CallsClient._add_active_call(chat_id)
        xx = await asst.send_message(
            chat_id,
            f"**Playing :** {title}\n**Duration** : {time_formatter(dur*1000)}\n**Requested by**: {from_user}",
            reply_markup=reply_markup(chat_id),
        )
        QUEUE[chat_id].pop(pos)
        if not QUEUE[chat_id]:
            QUEUE.pop(chat_id)
        await asyncio.sleep(dur + 5)
     #   CallsClient._remove_active_call(chat_id)
        await xx.delete()
    except (IndexError, KeyError):
        CallsClient.leave_group_call(chat_id)
    except Exception as ap:
        await asst.send_message(chat_id, f"`{str(ap)}`")


@CallsClient.on_stream_end()
async def streamhandler(chat_id: int):
    await queue_func(chat_id)
