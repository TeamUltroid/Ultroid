# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}volume <number>`
   Put number between 1 to 100
"""

from . import *


@vc_asst("volume")
async def volume_setter(event):
    if len(event.text.split()) > 1:
        inp = event.text.split()
        if inp[1].startswith("@"):
            chat = inp[1]
            vol = int(inp[2])
            try:
                chat = int("-100" + str((await vcClient.get_entity(chat)).id))
            except Exception as e:
                return await eor(event, "**ERROR:**\n{}".format(str(e)))
        elif inp[1].startswith("-"):
            chat = int(inp[1])
            vol = int(inp[2])
            try:
                chat = int("-100" + str((await vcClient.get_entity(chat)).id))
            except Exception as e:
                return await eor(event, "**ERROR:**\n{}".format(str(e)))
        elif inp[1].isdigit() and len(inp) == 2:
            vol = int(inp[1])
            chat = event.chat_id
    else:
        return await eor(event, "`Please specify a volume from 1 to 200!`")
    ultSongs = Player(chat)
    if vol:
        await ultSongs.group_call.set_my_volume(int(vol))
        if vol > 200:
            vol = 200
        elif vol < 1:
            vol = 1
        return await eor(event, "• Volume Changed to `{}%` •".format(vol))
