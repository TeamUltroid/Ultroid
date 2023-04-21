# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import get_help

__doc__ = get_help("help_broadcast")

import asyncio
import io

from core.helpers._base import KeyManager
from telethon.utils import get_display_name

from . import HNDLR, LOGS, eor, get_string, udB, ultroid_bot, ultroid_cmd

KeyM = KeyManager("BROADCAST", cast=list)


@ultroid_cmd(
    pattern="addch( (.*)|$)",
    allow_sudo=False,
)
async def broadcast_adder(event):
    msgg = event.pattern_match.group(1).strip()
    x = await event.eor(get_string("bd_1"))
    if msgg == "all":
        await x.edit(get_string("bd_2"))
        chats = [
            e.entity
            for e in await event.client.get_dialogs()
            if (e.is_group or e.is_channel)
        ]
        new = 0
        for i in chats:
            try:
                if (
                    i.broadcast
                    and (i.creator or i.admin_rights)
                    and not KeyM.contains(i.id)
                ):
                    new += 1
                    cid = f"-100{i.id}"
                    KeyM.add(int(cid))
            except Exception as Ex:
                LOGS.exception(Ex)
        await x.edit(get_string("bd_3").format(KeyM.count(), new))
        return
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        raw_text = previous_message.text
        lines = raw_text.split("\n")
        length = len(lines)
        for line_number in range(1, length - 2):
            channel_id = lines[line_number][4:-1]
            if not KeyM.contains(channel_id):
                KeyM.add(channel_id)
        await x.edit(get_string("bd_4"))
        await asyncio.sleep(3)
        await event.delete()
        return
    chat_id = event.chat_id
    if chat_id == udB.get_key("LOG_CHANNEL"):
        return
    if KeyM.contains(chat_id):
        await x.edit(get_string("bd_6"))
    elif xx := KeyM.add(chat_id):
        await x.edit(get_string("bd_5"))
    else:
        await x.edit(get_string("sf_8"))
    await asyncio.sleep(3)
    await x.delete()


@ultroid_cmd(
    pattern="remch( (.*)|$)",
    allow_sudo=False,
)
async def broadcast_remover(event):
    chat_id = event.pattern_match.group(1).strip() or event.chat_id
    x = await event.eor(get_string("com_1"))
    if chat_id == "all":
        await x.edit(get_string("bd_8"))
        udB.del_key("BROADCAST")
        await x.edit("Database cleared.")
        return
    if KeyM.contains(chat_id):
        KeyM.remove(chat_id)
        await x.edit(get_string("bd_7"))
    else:
        await x.edit(get_string("bd_9"))
    await asyncio.sleep(3)
    await x.delete()


@ultroid_cmd(
    pattern="listchannels$",
)
async def list_all(event):
    x = await event.eor(get_string("com_1"))
    channels = KeyM.get()
    num = KeyM.count()
    if not channels:
        return await eor(x, "No chats were added.", time=5)
    msg = "Channels in database:\n"
    for channel in channels:
        name = ""
        try:
            name = get_display_name(await event.client.get_entity(channel))
        except ValueError:
            name = ""
        msg += f"=> **{name}** [`{channel}`]\n"
    msg += f"\nTotal {num} channels."
    if len(msg) > 4096:
        MSG = msg.replace("*", "").replace("`", "")
        with io.BytesIO(str.encode(MSG)) as out_file:
            out_file.name = "channels.txt"
            await event.reply(
                "Channels in Database",
                file=out_file,
                force_document=True,
                allow_cache=False,
            )
            await x.delete()
    else:
        await x.edit(msg)


@ultroid_cmd(
    pattern="forward$",
    allow_sudo=False,
)
async def forw(event):
    if not event.is_reply:
        return await event.eor(get_string("ex_1"))
    ultroid_bot = event.client
    channels = KeyM.get()
    x = await event.eor("Sending...")
    if not channels:
        return await x.edit(f"Please add channels by using `{HNDLR}add` in them.")
    error_count = 0
    sent_count = 0
    previous_message = await event.get_reply_message()
    error_count = 0
    for channel in channels:
        try:
            await ultroid_bot.forward_messages(channel, previous_message)
            sent_count += 1
            await x.edit(
                f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
            )
        except Exception:
            try:
                await ultroid_bot.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"Error in sending at {channel}.",
                )
            except Exception as Em:
                LOGS.info(Em)
            error_count += 1
            await x.edit(
                f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
            )
    await x.edit(f"{sent_count} messages sent with {error_count} errors.")
    if error_count > 0:
        await ultroid_bot.send_message(
            udB.get_key("LOG_CHANNEL"), f"{error_count} Errors"
        )


@ultroid_cmd(
    pattern="broadcast( (.*)|$)",
    allow_sudo=False,
)
async def sending(event):
    x = await event.eor(get_string("com_1"))
    if not event.is_reply:
        return await x.edit(get_string("ex_1"))
    channels = KeyM.get()
    if not channels:
        return await x.edit(f"Please add channels by using `{HNDLR}add` in them.")
    await x.edit("Sending....")
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.poll:
            return await x.edit(f"Reply `{HNDLR}forward` for polls.")
        if previous_message:
            error_count = 0
            sent_count = 0
            for channel in channels:
                try:
                    await ultroid_bot.send_message(channel, previous_message)
                    sent_count += 1
                    await x.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
                except Exception as error:
                    await ultroid_bot.send_message(
                        udB.get_key("LOG_CHANNEL"),
                        f"Error in sending at {channel}.\n\n{error}",
                    )
                    error_count += 1
                    await x.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
            await x.edit(f"{sent_count} messages sent with {error_count} errors.")
            if error_count > 0:
                await ultroid_bot.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"{error_count} Errors",
                )
