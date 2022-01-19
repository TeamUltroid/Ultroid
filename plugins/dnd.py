# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

Do Not Disturb - As it says, activating this in your group will kick new users who joins the group.

• `{i}dnd`
    To activate.

• `{i}deldnd`
    To deactivate.
"""


from pyUltroid.dB.dnd_db import add_dnd, chat_in_dnd, del_dnd, get_dnd_chats
from telethon.events import ChatAction

from . import LOGS, asst, ultroid_bot, ultroid_cmd


@ultroid_bot.on(ChatAction)
@asst.on(ChatAction)
async def _(event):
    if int(event.chat_id) in get_dnd_chats() and event.user_joined:
        for user in event.users:
            try:
                await event.client.kick_participant(event.chat_id, user)
            except Exception as ex:
                LOGS.error("Error in DND:\n" + str(ex))
        await event.delete()


@ultroid_cmd(pattern="dnd$", manager=True, admins_only=True, groups_only=True)
async def _(event):
    if chat_in_dnd(event.chat_id):
        return await event.eor("`Chat already in do not disturb mode.`", time=3)
    add_dnd(event.chat_id)
    await event.eor("`Do not disturb mode activated for this chat.`", time=3)


@ultroid_cmd(pattern="deldnd$", manager=True, admins_only=True, groups_only=True)
async def _(event):
    if not chat_in_dnd(event.chat_id):
        return await event.eor("`Chat is not in do not disturb mode.`", time=3)
    del_dnd(event.chat_id)
    await event.eor("`Do not disturb mode deactivated for this chat.`", time=3)
