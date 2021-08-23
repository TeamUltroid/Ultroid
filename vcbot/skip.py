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
    chat = (
        event.chat_id
        if str(event.chat_id).startswith("-100")
        else int("-100" + str(event.chat_id))
    )
    try:
        remove(ultSongs.group_call._GroupCallFile__input_filename)
    except BaseException:
        pass

    await play_from_queue(chat)
