# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

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
            chat = int("-100" + str((await vcClient.get_entity(chat)).id))
        except Exception as e:
            return await eor(event, "**ERROR:**\n{}".format(str(e)))
    else:
        chat = event.chat_id
    ultSongs = Player(chat, event)
    if not ultSongs.group_call.is_connected:
        await ultSongs.vc_joiner()


@vc_asst("(leavevc|stopvc)")
async def leaver(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        if not chat.startswith("@"):
            chat = int(chat)
        try:
            chat = int("-100" + str((await vcClient.get_entity(chat)).id))
        except Exception as e:
            return await eor(event, "**ERROR:**\n{}".format(str(e)))
    else:
        chat = event.chat_id
    ultSongs = Player(chat)
    await ultSongs.group_call.stop()
    if CLIENTS.get(chat):
        del CLIENTS[chat]
    if VIDEO_ON.get(chat):
        del VIDEO_ON[chat]
    await eor(event, "`Left the voice chat.`")


@vc_asst("rejoin")
async def rejoiner(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        if not chat.startswith("@"):
            chat = int(chat)
        try:
            chat = int("-100" + str((await vcClient.get_entity(chat)).id))
        except Exception as e:
            return await eor(event, "**ERROR:**\n{}".format(str(e)))
    else:
        chat = event.chat_id
    ultSongs = Player(chat)
    try:
        await ultSongs.group_call.reconnect()
    except NotConnectedError:
        return await eor(event, "You haven't connected to a voice chat!")
    await eor(event, "`Re-joining this voice chat.`")
