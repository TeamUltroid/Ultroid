# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@vc_asst("volume")
async def volume_setter(event):
    text = event.text.split(" ", 1)
    try:
        vol = int(text[1])
    except (IndexError, ValueError):
        return await eor(event, "`Please specify a volume from 1 to 200!`")
    await ultSongs.group_call.set_my_volume(vol)
    await eor(event, "Set volume to {}".format(vol))
