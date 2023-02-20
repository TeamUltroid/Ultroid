# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_autoban")

from telethon import events

from pyUltroid.dB.base import KeyManager

from . import LOGS, asst, ultroid_bot, ultroid_cmd

Keym = KeyManager("DND_CHATS", cast=list)


def join_func(e):
    return e.user_joined and Keym.contains(e.chat_id)


async def dnd_func(event):
    for user in event.users:
        try:
            await (await event.client.kick_participant(event.chat_id, user)).delete()
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
        if Keym.contains(event.chat_id):
            return await event.eor("`Chat already in do not disturb mode.`", time=3)
        Keym.add(event.chat_id)
        event.client.add_handler(dnd_func, events.ChatAction(func=join_func))
        await event.eor("`Do not disturb mode activated for this chat.`", time=3)
    elif match == "off":
        if not Keym.contains(event.chat_id):
            return await event.eor("`Chat is not in do not disturb mode.`", time=3)
        Keym.remove(event.chat_id)
        await event.eor("`Do not disturb mode deactivated for this chat.`", time=3)


if Keym.get():
    ultroid_bot.add_handler(dnd_func, events.ChatAction(func=join_func))
    asst.add_handler(dnd_func, events.ChatAction(func=join_func))
