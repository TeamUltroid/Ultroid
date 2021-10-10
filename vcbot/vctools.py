# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}mutevc`
   Mute playback.

• `{i}unmutevc`
   UnMute playback.

• `{i}pausevc`
   Pause playback.

• `{i}resumevc`
   Resume playback.

• `{i}replay`
   Re-play the current song from the beginning.
"""
from . import *


@vc_asst("mutevc")
async def mute(event):
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
    await ultSongs.group_call.set_is_mute(True)
    await eor(event, get_string('vcbot_12'))


@vc_asst("unmutevc")
async def unmute(event):
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
    await ultSongs.group_call.set_is_mute(False)
    await eor(event, "`UnMuted playback in this chat.`")


@vc_asst("pausevc")
async def pauser(event):
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
    await ultSongs.group_call.set_pause(True)
    await eor(event, get_string('vcbot_14'))


@vc_asst("resumevc")
async def resumer(event):
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
    await ultSongs.group_call.set_pause(False)
    await eor(event, get_string('vcbot_13'))


@vc_asst("replay")
async def replayer(event):
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
    ultSongs.group_call.restart_playout()
    await eor(event, "`Re-playing the current song.`")
