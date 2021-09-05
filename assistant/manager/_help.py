# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@ultroid_cmd(pattern="help", type="manager")
async def helpish(event):
    if str(event.sender_id) in owner_and_sudos():
        return
    await event.reply("Manager Help")
