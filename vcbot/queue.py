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

• `{i}clearqueue`
   Clear all queue in chat.
"""

from . import *


@vc_asst("queue")
async def lstqueue(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        if not chat.startswith("@"):
            chat = int(chat)
        try:
            chat = int("-100" + str((await vcClient.get_entity(chat)).id))
        except Exception as e:
            return await eor(event, get_string("vcbot_2").format(str(e)))
    else:
        chat = event.chat_id
    q = list_queue(chat)
    if not q:
        return await eor(event, get_string('vcbot_21'))
    await eor(event, "• <strong>Queue:</strong>\n\n{}".format(q), parse_mode="html")

@vc_asst("clearqueue")
async def clean_queue(event):
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
    if VC_QUEUE.get(chat):
        VC_QUEUE.pop(chat)
    await eor(event, get_string('vcbot_22'), time=5)
