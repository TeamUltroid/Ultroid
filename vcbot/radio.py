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


@vc_asst("(radio|live|ytlive)")
async def r_l(e):
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
    if re.search("youtube", song) or re.search("youtu", song):
        is_live_vid = (await bash(f'youtube-dl -j "{song}" | jq ".is_live"'))[0]
        if is_live_vid == "true":
            song, _ = await bash(f"youtube-dl -x -g {song}")
        else:
            return await eor(e, f"Only Live Youtube Urls/m3u8 Urls supported!\n{song}")
    raw_converter(song, file)
    await asyncio.sleep(2)
    if not os.path.exists(file):
        return await eor(e, f"`{song}`\n\nNot a playable link.🥱")
    ultSongs = Player(chat)
    if not ultSongs.group_call.is_connected:
        if not (await vc_joiner(e, chat)):
            return
    await eor(e, "• Started Radio 📻")
    ultSongs.group_call.input_filename = file
