# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available
"""

import os

from . import *


@vc_asst("vidstream")
async def video_c(ult):
    try:
        match = ult.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eor(ult, "`Give link to play...`")
    ultSongs = Player(ult.chat_id, ult, True)
    if not (await ultSongs.vc_joiner()):
        return
    await ultSongs.group_call.start_video(match)
    await eor(ult, f"Playing {match}")
