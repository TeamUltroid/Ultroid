# Ultroid - UserBot
# Copyright (C) 2021 Gladiator-007
#
# This file is a part of < https://github.com/Gladiator-007/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/Gladiator-007/Ultroid/blob/main/LICENSE/>.
from telethon.errors import ChatSendInlineForbiddenError
from telethon.errors.rpcerrorlist import BotMethodInvalidError as bmi

from . import *

REPOMSG = """
• **ULTROID USERBOT** •\n
• Repo - [Click Here](https://github.com/Gladiator-007/Ultroid)
• Addons - [Click Here](https://github.com/Gladiator-007/UltroidAddons)
• Support - @UltroidSupport
"""


@ultroid_cmd(pattern="repo$", type=["official", "manager"], ignore_dualmode=True)
async def repify(e):
    try:
        q = await e.client.inline_query(asst.me.username, "repo")
        await q[0].click(e.chat_id)
        if e.out:
            await e.delete()
    except (ChatSendInlineForbiddenError, bmi):
        await eor(e, REPOMSG)
