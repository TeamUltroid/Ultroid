# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@vc_asst("volume")
async def volume_setter(event):
    ultSongs = Player(event.chat_id)
    if len(event.text.split()) > 1:
        vol = event.text.split()[1]
        if vol.isdigit():
            await ultSongs.group_call.set_my_volume(int(vol))
            if int(vol) > 200:
                vol = 200
            elif int(vol) < 1:
                vol = 1
            return await eor(event, "• Volume Changed to `{}%` •".format(vol))
    await eor(event, "`Please specify a volume from 1 to 200!`")
