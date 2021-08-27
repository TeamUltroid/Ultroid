# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}radio <link>`
   Stream Live Radio.

• `{i}ytlive <link>`
   Stream Live YouTube.
"""

import os

from . import *


@vc_asst("radio")
async def radio_mirchi(e):
    xx = await eor(e, get_string("com_1"))
    if not len(e.text.split()) > 1:
        return await eor(e, "Are You Kidding Me?\nWhat to Play?")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        chat = int(f"-100{(await vcClient.get_entity(input[1])).id}")
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    file = f"VCRADIO_{chat}.raw"
    raw_converter(song, file)
    await asyncio.sleep(2)
    if not os.path.exists(file):
        return await eor(e, f"`{song}`\n\nNot a playable link.🥱")
    ultSongs = Player(chat)
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
    ultSongs.group_call.input_filename = file
    await xx.reply(
        f"• Started Radio 📻\n\n• Channel : `{song}`",
        file="https://telegra.ph/file/419bd79c53cca22ec24f0.jpg",
    )
    await xx.delete()


@vc_asst("(live|ytlive)")
async def live_stream(e):
    xx = await eor(e, get_string("com_1"))
    if not len(e.text.split()) > 1:
        return await eor(e, "Are You Kidding Me?\nWhat to Play?")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        chat = int(f"-100{(await vcClient.get_entity(input[1])).id}")
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    file = f"VCRADIO_{chat}.raw"
    is_live_vid = False
    if re.search("youtube", song) or re.search("youtu", song):
        is_live_vid = (await bash(f'youtube-dl -j "{song}" | jq ".is_live"'))[0]
    if is_live_vid != "true":
        return await eor(e, f"Only Live Youtube Urls supported!\n{song}")
    thumb, title, duration = await live_dl(song, file)
    await asyncio.sleep(2)
    if not os.path.exists(file):
        return await eor(e, f"`{song}`\n\nNot a playable link.🥱")
    ultSongs = Player(chat)
    if not ultSongs.group_call.is_connected:
        if not (await ultSongs.vc_joiner()):
            return
    from_user = inline_mention(e.sender)
    await xx.reply(
        "🎸 **Now playing:** `{}`\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
            title, duration, chat, from_user
        ),
        file=thumb,
    )
    await xx.delete()
    ultSongs.group_call.input_filename = file
