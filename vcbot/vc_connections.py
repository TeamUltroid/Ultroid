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
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        if not chat.startswith("@"):
            chat = int(chat)
        try:
            chat = (await event.client.get_entity(chat)).id
        except Exception as e:
            return await eor(event, "**ERROR:**\n{}".format(str(e)))
    else:
        chat = event.chat_id
    await vc_joiner(event, chat)


@vc_asst("leavevc")
async def leaver(event):
    try:
        chat = event.text.split(maxsplit=1)[1]
        chat = int(f"-100{await get_user_id(chat)}")
    except IndexError:
        chat = event.chat_id
    ultSongs = Player(chat)
    await ultSongs.group_call.stop()
    await eor(event, "`Left the voice chat.`")


@vc_asst("rejoin")
async def rejoiner(event):
    ultSongs = Player(event.chat_id)
    try:
        await ultSongs.group_call.reconnect()
    except NotConnectedError:
        return await eor(event, "You haven't connected to a voice chat!")
    await eor(event, "`Re-joining this voice chat.`")
