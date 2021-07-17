# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["radio", f"radio@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def radio(client, message):
    radio = message.text.split(" ", maxsplit=1)
    if not len(radio) >= 1:
        return await eor(message, "Are You Kidding Me?\nWhat to Play?")
    elif len(radio) >= 1 and radio[1].startswith("@" or "-"):
        ko = radio[1].split(" ", maxsplit=1)
        chat = await client.get_chat(ko[0])
        chat = chat.id
    else:
        chat = message.chat.id
        ko = radio
    file = f"VCRADIO_{chat}.raw"
    if re.search("youtube", ko[1]) or re.search("youtu", ko[1]):
        is_live_vid = (await bash(f'youtube-dl -j "{ko[1]}" | jq ".is_live"'))[0]
        if is_live_vid == "true":
            the_input = (await bash(f"youtube-dl -x -g {ko[1]}"))[0]
        else:
            return await eor(
                message, f"Only Live Youtube Urls/m3u8 Urls supported!\n{ko}"
            )
    else:
        the_input = ko[1]
    process = (
        ffmpeg.input(the_input)
        .output(
            file,
            format="s16le",
            acodec="pcm_s16le",
            ac=1,
            ar="48000",
            loglevel="error",
        )
        .overwrite_output()
        .run_async()
    )
    CallsClient.join_group_call(chat, file, stream_type=StreamType().live_stream)
    await eor(message, "• Started Radio Stream •", reply_markup=reply_markup(chat))


@Client.on_message(filters.me & filters.command("radio", HNDLR) & ~filters.edited)
async def rplay(_, message):
    await radio(_, message)
