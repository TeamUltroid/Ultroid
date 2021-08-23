# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

""" 
• `{i}queue`
   List the songs in queue.
"""

from . import *


@vc_asst("queue")
async def queue(event):
    chat = (
        event.chat_id
        if str(event.chat_id).startswith("-100")
        else int("-100" + str(event.chat_id))
    )

    q = list_queue(chat)

    if q == "":
        return await eor(event, "Nothing in queue!")

    await eor(event, "**Queue:**\n\n{}".format(q))
