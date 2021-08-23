# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *
from pytgcalls.exceptions import NotConnectedError


@vc_asst("joinvc")
async def join_(event):
    await vc_joiner(event, event.chat_id)


@vc_asst("leavevc")
async def leaver(event):
    ultSongs.group_call.stop()
    await eor(event, "`Left the voice chat.`")


@vc_asst("rejoin")
async def rejoiner(event):
    try:
        await ultSongs.group_call.reconnect()
    except NotConnectedError:
        return await eor(event, "You haven't connected to a voice chat!")
    await eor(event, "`Re-joining this voice chat.`")
