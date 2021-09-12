# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}queue`
   List the songs in queue.
"""

from . import *


@vc_asst("queue")
async def queue(event):
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
    q = list_queue(chat)
    if not q:
        return await eor(event, "• Nothing in queue!")
    await eor(event, "• <strong>Queue:</strong>\n\n{}".format(q), parse_mode="html")
