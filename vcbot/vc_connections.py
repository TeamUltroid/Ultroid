# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}joinvc <optional chat id/username>`
   Join the voice chat.

• `{i}leavevc`
   Leave the voice chat.

• `{i}rejoin`
   Re-join the voice chat, incase of errors.
"""

from pytgcalls.exceptions import NotConnectedError

from . import *


@vc_asst("joinvc")
async def join_(event):
    txt = event.text.split(" ", 1)
    try:
        chat = txt[1]
    except IndexError:
        chat = event.chat_id
    try:
        chat = int(chat)
    except ValueError:
        try:
            chat = (await vcClient.get_entity(chat)).id
        except Exception as e:
            return await eor(event, "**ERROR:**\n{}".format(str(e)))
    await vc_joiner(event, chat)


@vc_asst("leavevc")
async def leaver(event):
    await ultSongs.group_call.stop()
    await eor(event, "`Left the voice chat.`")


@vc_asst("rejoin")
async def rejoiner(event):
    try:
        await ultSongs.group_call.reconnect()
    except NotConnectedError:
        return await eor(event, "You haven't connected to a voice chat!")
    await eor(event, "`Re-joining this voice chat.`")
