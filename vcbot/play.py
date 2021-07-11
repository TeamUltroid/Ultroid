# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os

from . import *

J_CACHE = {}


@asst.on_message(
    filters.command(["play", f"play@{vcusername}"])
    & filters.user(AUTH)
    & ~filters.edited
    & filters.group
)
async def startup(_, message):
    msg = await eor(message, "`Processing..`")
    song = message.text.split(" ", maxsplit=1)
    reply = message.reply_to_message

    if len(song) >= 1 and song[0].startswith("@" or "-"):
        song = song.split(" ", maxsplit=1)
        chat = await Client.get_chat(song[0])
    else:
        chat = message.chat
    try:
        if reply.audio:
            med = reply.audio
        elif reply.video:
            med = reply.video
        elif reply.voice:
            med = reply.voice
        song_name = med.file_name
    except BaseException:
        med = None
        if song:
            song_name = song[1]
        else:
            song_name = ""

    TS = dt.now().strftime("%H:%M:%S")
    if not reply and len(song) > 1:
        song = await download(song[1], chat.id, TS)
    elif not reply and len(song) == 1:
        return await msg.edit_text("Pls Give me Something to Play...")
    elif not (reply.audio or reply.voice or reply.video):
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    else:
        dl = await reply.download()
        song = f"VCSONG_{chat.id}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
        os.remove(dl)
        if med and med.thumbs:
            dll = med.thumbs[0].file_id
            th = await asst.download_media(dll)
            try:
                CallsClient.active_calls[chat.id]
            except KeyError:
                await msg.delete()
                msg = await message.reply_photo(
                    th,
                    caption=f"**Playing :** {song_name}\n**Requested By :** {message.from_user.mention}",
                    disable_web_page_preview=True,
                )
            os.remove(th)
    from_user = message.from_user.mention
    if chat.id in CallsClient.active_calls.keys():
        add_to_queue(chat, song, song_name, from_user)
        return await msg.edit(f"Added to queue at #{list(QUEUE[chat.id].keys())[-1]}")
    CallsClient.join_group_call(chat, song)
    CH = await asst.send_message(
        LOG_CHANNEL, f"Joined Voice Call in {chat.title} [`{chat.id}`]"
    )
    J_CACHE.update({chat: CH.message_id})
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Pause", callback_data=f"vcp_{chat.id}")]]
    )
    await msg.edit_reply_markup(reply_markup)


@Client.on_message(
    filters.me & filters.command(["play"], HNDLR) & ~filters.edited
)
async def cstartup(_, message):
    await startup(_, message)


@CallsClient.on_stream_end()
async def streamhandler(chat_id: int):
    try:
        song, title, from_user = get_from_queue(chat_id)
        CallsClient.leave_group_call(chat_id)
        CallsClient.join_group_call(chat_id, song)
        await asst.send_message(
            chat_id, f"**Playing :** {title}\n**Requested by**: {from_user}"
        )
        try:
            pos = list(QUEUE[int(chat_id)])[0]
            del QUEUE[chat_id][pos]
        except BaseException as ap:
            await asst.send_message(chat_id, f"`{str(ap)}`")
    except BaseException:
        CallsClient.leave_group_call(chat_id)
        Cyanide = J_CACHE[chat_id]
        await asst.delete_messages(LOG_CHANNEL, Cyanide)
        J_CACHE.pop(chat_id)
