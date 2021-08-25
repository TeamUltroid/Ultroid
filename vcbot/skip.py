# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}skip`
   Skip the current song and play the next in queue, if any.
"""

from . import *


@vc_asst("skip")
async def skipper(event):
    spli = event.text.split(" ", 1)
    try:
        chat = int(f"-100{await get_user_id(spli[1])}")
    except IndexError:
        chat = event.chat_id
    ultSongs = Player(chat)
    try:
        remove(ultSongs.group_call._GroupCallFile__input_filename)
    except BaseException:
        pass
    await play_from_queue(chat)
