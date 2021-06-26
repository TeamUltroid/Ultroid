# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["play", "cplay", f"play@{vcusername}", f"cplay@{vcusername}"])
    & filters.user(AUTH)
    & ~filters.edited
    & filters.group
)
async def startup(_, message):
    msg = await eor(message, "`Processing..`")
    song = message.text.split(" ", maxsplit=1)
    reply = message.reply_to_message
    ChatPlay = None
    if message.text[1] != "c":
        chat = message.chat.id
    else:
        ChatPlay = True
        try:
            song = song[1].split(" ", maxsplit=1)
        except IndexError:
            if not reply:
                return await msg.edit_text(
                    "Please Give a Channel Username/Id to Play There or use /play to play in current Chat."
                )
        chat = song[0]
    try:
        song_name = reply.audio.file_name
    except BaseException:
        if song:
            song_name = song[1]
        else:
            song_name = ""
    if ChatPlay:
        Chat = await Client.get_chat(chat)
        chat = Chat.id
    TS = dt.now().strftime("%H:%M:%S")
    if not reply and len(song) > 1:
        song = await download(song[1], message.chat.id, TS)
    elif not reply and len(song) == 1:
        return await msg.edit_text("Pls Give me Something to Play...")
    elif not (reply.audio or reply.voice):
        return await msg.edit_text("Pls Reply to Audio File or Give Search Query...")
    else:
        dl = await reply.download()
        song = f"VCSONG_{chat}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
        if reply.audio and reply.audio.thumbs:
            dll = reply.audio.thumbs[0].file_id
            th = await asst.download_media(dll)
            try:
                CallsClient.active_calls[chat]
            except KeyError:
                await msg.delete()
                msg = await message.reply_photo(th, caption=f"`Playing {song_name}...`")
            os.remove(th)
    from_user = message.from_user.first_name
    if chat in CallsClient.active_calls.keys():
        add_to_queue(chat, song, song_name, from_user)
        return await msg.edit(f"Added to queue at #{list(QUEUE[chat].keys())[-1]}")
    chattitle = message.chat.title
    if ChatPlay:
        chattitle = Chat.title
    await asst.send_message(LOG_CHANNEL, f"Joined Voice Call in {chattitle} [`{chat}`]")
    CallsClient.join_group_call(chat, song)
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Pause", callback_data=f"vcp_{chat}")]]
    )
    await msg.edit_reply_markup(reply_markup)


@Client.on_message(filters.me & filters.command("play", HNDLR) & ~filters.edited)
async def cstartup(_, message):
    await startup(_, message)


@CallsClient.on_stream_end()
async def streamhandler(chat_id: int):
    try:
        song, title, from_user = get_from_queue(chat_id)
        CallsClient.change_stream(chat_id, song)
        await asst.send_message(chat_id, f"Playing {title}\nRequested by: {from_user}")
        try:
            pos = list(QUEUE[int(chat_id)])[0]
            del QUEUE[chat_id][pos]
        except BaseException as ap:
            await asst.send_message(chat_id, f"`{str(ap)}`")
    except BaseException:
        CallsClient.leave_group_call(chat_id)
