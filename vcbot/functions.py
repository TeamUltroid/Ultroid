# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}mutevc`
   Mute playback.

• `{i}unmutevc`
   UnMute playback.

• `{i}pausevc`
   Pause playback.

• `{i}resumevc`
   Resume playback.

• `{i}stopvc`
   Stop the playback and leave the voice chat.

• `{i}replay`
   Re-play the current song from the beginning.
"""
from . import *


@vc_asst("mutevc")
async def mute(event):
    ultSongs = Player(event.chat_id)
    await ultSongs.group_call.set_is_mute(True)
    await eor(event, "`Muted playback in this chat.`")


@vc_asst("unmutevc")
async def unmute(event):
    ultSongs = Player(event.chat_id)
    await ultSongs.group_call.set_is_mute(False)
    await eor(event, "`UnMuted playback in this chat.`")


@vc_asst("pausevc")
async def pauser(event):
    ultSongs = Player(event.chat_id)
    ultSongs.group_call.pause_playout()
    await eor(event, "`Paused playback in this chat.`")


@vc_asst("resumevc")
async def resumer(event):
    ultSongs = Player(event.chat_id)
    ultSongs.group_call.resume_playout()
    await eor(event, "`Resumed playback in this chat.`")


@vc_asst("stopvc")
async def stopper(event):
    ultSongs = Player(event.chat_id)
    ultSongs.group_call.stop_playout()
    await eor(event, "`Stopped playback in this chat.`")
    try:
        remove(ultSongs.group_call._GroupCallFile__input_filename)
    except BaseException:
        pass


@vc_asst("replay")
async def replayer(event):
    ultSongs = Player(event.chat_id)
    ultSongs.group_call.restart_playout()
    await eor(event, "`Re-playing the current song.`")
