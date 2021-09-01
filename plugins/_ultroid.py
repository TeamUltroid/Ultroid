# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon.errors import ChatSendInlineForbiddenError
from pyUltroid.misc._assistant import callback
from assistant.initial import STRINGS

from . import *

REPOMSG = """
• **ULTROID USERBOT** •\n
• Repo - [Click Here](https://github.com/TeamUltroid/Ultroid)
• Addons - [Click Here](https://github.com/TeamUltroid/UltroidAddons)
• Support - @UltroidSupport
"""

RP_BUTTONS = [
    [
        Button.url("Repo", "https://github.com/TeamUltroid/Ultroid"),
        Button.url("Addons", "https://github.com/TeamUltroid/UltroidAddons"),
    ],
    [Button.url("Support Group", "t.me/ultroidsupport")],
]


@ultroid_cmd(
    pattern="repo$",
    type=["official", "manager"],
)
async def repify(e):
    if e.client._bot:
        return await e.reply("• **Ultroid Userbot** •", buttons=RP_BUTTONS)
    try:
        q = await e.client.inline_query(asst.me.username, "repo")
        await q[0].click(e.chat_id)
        if e.out:
            await e.delete()
    except (ChatSendInlineForbiddenError):
        await eor(e, REPOMSG)


@ultroid_cmd(pattern="ultroid")
async def useUltroid(rs):
    button = Button.inline("Start >>", "initft_2")
    msg = await asst.send_message(LOG_CHANNEL, STRINGS[1], buttons=button)
    await eor(rs, f"[Click Here]({msg.message_link})")
