# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_autoban")

from telethon import events

from pyUltroid.dB import dnd_db

from . import LOGS, asst, ultroid_bot, ultroid_cmd


async def dnd_func(event):
    if event.chat_id in dnd_db.get_dnd_chats():
        for user in event.users:
            try:
                await (
                    await event.client.kick_participant(event.chat_id, user)
                ).delete()
            except Exception as ex:
                LOGS.error("Error in DND:")
                LOGS.exception(ex)
        await event.delete()


@ultroid_cmd(
    pattern="autokick (on|off)$",
    admins_only=True,
    manager=True,
    require="ban_users",
    fullsudo=True,
)
async def _(event):
    match = event.pattern_match.group(1)
    if match == "on":
        if dnd_db.chat_in_dnd(event.chat_id):
            return await event.eor("`Chat already in do not disturb mode.`", time=3)
        dnd_db.add_dnd(event.chat_id)
        event.client.add_handler(
            dnd_func, events.ChatAction(func=lambda x: x.user_joined)
        )
        await event.eor("`Do not disturb mode activated for this chat.`", time=3)
    elif match == "off":
        if not dnd_db.chat_in_dnd(event.chat_id):
            return await event.eor("`Chat is not in do not disturb mode.`", time=3)
        dnd_db.del_dnd(event.chat_id)
        await event.eor("`Do not disturb mode deactivated for this chat.`", time=3)


if dnd_db.get_dnd_chats():
    ultroid_bot.add_handler(dnd_func, events.ChatAction(func=lambda x: x.user_joined))
    asst.add_handler(dnd_func, events.ChatAction(func=lambda x: x.user_joined))
