# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}autokick <on/off>`
    on - To enable.
    off - To disable.
    Automatically kick new joined users from the group.

• `{i}cban`
    Enable/Disable autobanning send as channel in used chat.

• `{i}addwl <Username>`
   Add Channel to channelban whitelist.

• `{i}remwl <Username>`
   Remove Channel from channelban whitelist.

• `{i}listwl` : List all whitelist channels.
"""


from pyUltroid.dB import autoban_db, dnd_db
from pyUltroid.functions.admins import get_update_linked_chat
from telethon import events
from telethon.tl.types import Channel

from . import LOGS, asst, get_string, inline_mention, ultroid_bot, ultroid_cmd


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


async def channel_del(event):
    if not autoban_db.is_autoban_enabled(event.chat_id):
        return
    if autoban_db.is_whitelisted(event.chat_id, event.sender_id):
        return
    linked = await get_update_linked_chat(event)
    if linked == event.sender.id:
        return
    if event.chat.creator or event.chat.admin_rights.ban_users:
        try:
            await event.client.edit_permissions(
                event.chat_id, event.sender_id, view_messages=False
            )
        except Exception as er:
            LOGS.exception(er)
    await event.try_delete()


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


@ultroid_cmd(pattern="cban$", admins_only=True)
async def ban_cha(ult):
    if autoban_db.is_autoban_enabled(ult.chat_id):
        autoban_db.del_channel(ult.chat_id)
        return await ult.eor("`Disabled Auto ChannelBan...`")
    if not (
        ult.chat.creator
        or (ult.chat.admin_rights.delete_messages or ult.chat.admin_rights.ban_users)
    ):
        return await ult.eor(
            "You are missing required admin rights!\nYou can't use ChannelBan without Ban/del privilege..`"
        )
    autoban_db.add_channel(ult.chat_id)
    await ult.eor("`Enabled Auto ChannelBan Successfully!`")
    ult.client.add_handler(
        channel_del,
        events.NewMessage(
            func=lambda x: not x.is_private and isinstance(x.sender, Channel)
        ),
    )


@ultroid_cmd(pattern="(list|add|rem)wl( (.*)|$)")
async def do_magic(event):
    match = event.pattern_match.group(1)
    msg = await event.eor(get_string("com_1"))
    if match == "list":
        cha = autoban_db.get_whitelisted_channels(event.chat_id)
        if not cha:
            return await msg.edit("`No Whitelisted channels for current chat.`")
        Msg = "**Whitelist Channels in Current Chat**\n\n"
        for ch in cha:
            Msg += f"(`{ch}`) "
            try:
                Msg += inline_mention(await event.client.get_entity(ch))
            except Exception:
                Msg += "\n"
        return await msg.edit(Msg)
    usea = event.pattern_match.group(2).strip()
    if not usea:
        return await Msg.edit(
            "`Please provide a channel username/id to add/remove to/from whitelist..`"
        )
    try:
        u_id = await event.client.parse_id(usea)
        cha = await event.client.get_entity(u_id)
    except Exception as er:
        LOGS.exception(er)
        return await msg.edit(f"Error Broke Out!\n`{er}`")
    if match == "add":
        autoban_db.add_to_whitelist(event.chat_id, u_id)
        return await msg.edit(f"`Added` {inline_mention(cha)} `to WhiteList..`")
    autoban_db.del_from_whitelist(event.chat_id, u_id)
    await msg.edit(f"`Removed` {inline_mention(cha)} `from WhiteList.`")


if dnd_db.get_dnd_chats():
    ultroid_bot.add_handler(dnd_func, events.ChatAction(func=lambda x: x.user_joined))
    asst.add_handler(dnd_func, events.ChatAction(func=lambda x: x.user_joined))

if autoban_db.get_all_channels():
    ultroid_bot.add_handler(
        channel_del,
        events.NewMessage(
            func=lambda x: not x.is_private and isinstance(x.sender, Channel)
        ),
    )
