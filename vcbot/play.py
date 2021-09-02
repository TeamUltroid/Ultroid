# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}play <song name/song url/reply to file>`
   Play the song in voice chat, or add the song to queue.
"""

import os

from . import *


@vc_asst("play")
async def play_music_(event):
    if "playfrom" in event.text.split()[0]:
        return  # For PlayFrom Conflict
    xx = await eor(event, get_string("com_1"))
    chat = event.chat_id
    from_user = inline_mention(event.sender)
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        tiny_input = input.split()[0]
        if tiny_input.startswith("@"):
            try:
                chat = int(f"-100{await get_user_id(tiny_input, client=vcClient)}")
                song = input.split(maxsplit=1)[1]
            except IndexError:
                pass
            except Exception as e:
                return await eor(event, str(e))
        elif tiny_input.startswith("-"):
            chat = int(f"-100{await get_user_id(int(tiny_input), client=vcClient)}")
            try:
                song = input.split(maxsplit=1)[1]
            except BaseException:
                pass
        else:
            song = input
    if not (reply or song):
        return await eor(
            xx, "Please specify a song name or reply to a audio file !", time=5
        )
    await eor(xx, "`Downloading and converting...`")
    ts = str(time()).split(".")[0]
    if reply and reply.media and mediainfo(reply.media).startswith(("audio", "video")):
        song, thumb, song_name, duration = await file_download(xx, reply, chat, ts)
    else:
        song, thumb, song_name, duration = await download(song, chat, ts)
    ultSongs = Player(chat, event)
    if len(song_name) > 37:
        song_name = song_name[:35] + "..."
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
        ultSongs.group_call.input_filename = song
        await xx.reply(
            "🎸 **Now playing:** `{}`\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
                song_name, duration, chat, from_user
            ),
            file=thumb,
        )
        await xx.delete()
        if thumb and os.path.exists(thumb):
            remove(thumb)
    else:
        add_to_queue(chat, song, song_name, thumb, from_user, duration)
        return await eor(
            xx,
            f"▶ Added 🎵 **{song_name}** to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
        )


@vc_asst("playfrom")
async def play_music_(event):
    msg = await eor(event, get_string("com_1"))
    chat = event.chat_id
    limit = 10
    from_user = inline_mention(event.sender)
    if not len(event.text.split()) > 1:
        return await msg.edit(
            "Use in Proper Format\n`.playfrom <channel username> ; <limit>`"
        )
    input = event.text.split(maxsplit=1)[1]
    if ";" in input:
        try:
            limit = input.split(";")
            input = limit[0]
            limit = int(limit[1])
        except IndexError:
            pass
    try:
        fromchat = (await event.client.get_entity(input)).id
    except Exception as er:
        return await eor(msg, str(er))
    await eor(msg, "`• Starting Playing from Channel....`")
    send_message = True
    ultSongs = Player(chat, event)
    async for song in event.client.iter_messages(
        fromchat, limit=limit, wait_for=10, filter=types.InputMessagesFilterMusic
    ):
        song, thumb, song_name, duration = await file_download(
            msg, song, chat, ts, str(time()).split(".")[0]
        )
        if len(song_name) > 37:
            song_name = song_name[:35] + "..."
        if not ultSongs.group_call.is_connected:
            if not (await ultSongs.vc_joiner()):
                return
            ultSongs.group_call.input_filename = song
            await msg.reply(
                "🎸 **Now playing:** `{}`\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
                    song_name, duration, chat, from_user
                ),
                file=thumb,
            )
            if thumb and os.path.exists(thumb):
                remove(thumb)
        else:
            add_to_queue(chat, song, song_name, thumb, from_user, duration)
            if send_message:
                await eor(
                    msg,
                    f"▶ Added 🎵 **{song_name}** to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
                )
                send_message = False
