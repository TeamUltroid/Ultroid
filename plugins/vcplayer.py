import os

from vcbot import *

from . import *


@ultroid_cmd(pattern="play")
async def playic(event):
    if not udB.get("VC_SESSION"):
        return await eor(event, "Fill A `VC_SESSION` in redis to play in Vc")
    msg = await eor(event, "`Processing...`")
    song = event.text.split(" ", maxsplit=1)
    reply = await event.get_reply_message()
    if len(song) > 1 and song[0].startswith("@" or "-"):
        song = song[1].split(" ", maxsplit=1)
        chat = await Client.get_chat(song[0])
    # Mixing Up Pyro & Tele bcoz not much difference
    else:
        chat = event.chat
    LOG_CHANNEL = udB.get("LOG_CHANNEL")
    TS = dt.now().strftime("%H:%M:%S")
    if not reply and len(song) > 1:
        song = await download(song[1], chat.id, TS)
    elif not reply and len(song) == 1:
        return await msg.edit("Pls Give me Something to Play...")
    from_user = inline_mention(event.sender)
    if chat in CallsClient.active_calls.keys():
        add_to_queue(chat, song, song_name, from_user)
        return await msg.edit(f"Added to queue at #{list(QUEUE[chat].keys())[-1]}")
    if reply and reply.file:
        dl = await reply.download_media()
        song = f"VCSONG_{chat.id}_{TS}.raw"
        await bash(
            f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y'
        )
        os.remove(dl)
        thumb = await reply.download_media(thumb=-1)
        if thumb:
            await msg.delete()
            msg = await asst.send_photo(chat.id, caption=f"`Playing {song_name}...`")
            os.remove(thumb)
    await asst.send_message(
        LOG_CHANNEL, f"Joined Voice Call in {chat.title} [`{chat.id}`]"
    )
    CallsClient.join_group_call(chat.id, song)
