# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}play <song name/song url/reply to file>`
   Play the song in voice chat, or add the song to queue.
"""

from datetime import datetime as dt

from . import *


@vc_asst("play")
async def play_music_(event):
    xx = await eor(event, "`Processing...`")
    chat = event.chat_id
    from_user = event.sender_id
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        if input.split()[0].startswith(("@", "-")):
            chat = int(f"-100{await get_user_id(input)}")
            try:
                song = input.split(maxsplit=1)[1]
            except IndexError:
                pass
        else:
            song = input
    if not (reply or song):
        return await eor(
            xx, "Please specify a song name or reply to a audio file !", time=5
        )
    await eor(xx, "`Downloading and converting...`")
    ts = dt.now().strftime("%H_%M_%S")
    if reply and (reply.audio or reply.video or reply.document):
        song, thumb, song_name, duration = await file_download(reply, chat, ts)
    else:
        song, thumb, song_name, duration = await download(event, song, chat, ts)
    ultSongs = Player(chat)
    if not ultSongs.group_call.is_connected:
        # check if vc_Client is in call
        done = await vc_joiner(event, chat)
        if not done:
            return
        await xx.reply(
            "🎸 **Now playing:** `{}`\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** `{}`".format(
                song_name, time_formatter(duration * 1000), chat, from_user
            ),
            file=thumb,
        )

        ultSongs.group_call.input_filename = song
        await xx.delete()
        if thumb:
            remove(thumb)
    else:
        add_to_queue(chat, song, song_name, thumb, from_user, duration)
        return await eor(
            xx,
            f"▶ Added 🎵 **{song_name}** to queue at #{list(VC_QUEUE[chat].keys())[-1]}.",
        )
