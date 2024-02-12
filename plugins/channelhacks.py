# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
from . import get_help

__doc__ = get_help("help_channelhacks")


import asyncio
import io

from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.utils import get_display_name, get_peer_id

from pyUltroid.dB.base import KeyManager

from . import LOGS, asst, eor, events, get_string, udB, ultroid_bot, ultroid_cmd

ERROR = {}
SourceM = KeyManager("CH_SOURCE", cast=list)
DestiM = KeyManager("CH_DESTINATIONS", cast=list)


async def autopost_func(e):
    if not udB.get_key("AUTOPOST"):
        return
    x = SourceM.get()
    th = await e.get_chat()
    if get_peer_id(th) not in x:
        return
    y = DestiM.get()
    for ys in y:
        try:
            await e.client.send_message(int(ys), e.message)
        except Exception as ex:
            try:
                ERROR[str(ex)]
            except KeyError:
                ERROR.update({str(ex): ex})
                Error = f"**Error on AUTOPOST**\n\n`{ex}`"
                await asst.send_message(udB.get_key("LOG_CHANNEL"), Error)


@ultroid_cmd(pattern="shift (.*)")
async def _(e):
    x = e.pattern_match.group(1).strip()
    z = await e.eor(get_string("com_1"))
    a, b = x.split("|")
    try:
        c = await e.client.parse_id(a)
    except Exception:
        await z.edit(get_string("cha_1"))
        return
    try:
        d = await e.client.parse_id(b)
    except Exception as er:
        LOGS.exception(er)
        await z.edit(get_string("cha_1"))
        return
    async for msg in e.client.iter_messages(int(c), reverse=True):
        try:
            await asyncio.sleep(2)
            await e.client.send_message(int(d), msg)
        except FloodWaitError as er:
            await asyncio.sleep(er.seconds + 5)
            await e.client.send_message(int(d), msg)
        except BaseException as er:
            LOGS.exception(er)
    await z.edit("Done")


@ultroid_cmd(pattern="asource (.*)")
async def source(e):
    if x := e.pattern_match.group(1).strip():
        try:
            y = await e.client.parse_id(x)
        except Exception as er:
            LOGS.exception(er)
            return
    else:
        y = e.chat_id
    if not SourceM.contains(y):
        SourceM.add(y)
        await e.eor(get_string("cha_2"))
        ultroid_bot.add_handler(autopost_func, events.NewMessage())
    else:
        await e.eor(get_string("cha_3"))


@ultroid_cmd(pattern="dsource( (.*)|$)")
async def dd(event):
    chat_id = event.pattern_match.group(1).strip()
    x = await event.eor(get_string("com_1"))
    if chat_id == "all":
        await x.edit(get_string("bd_8"))
        udB.del_key("CH_SOURCE")
        await x.edit(get_string("cha_4"))
        return
    if chat_id:
        try:
            y = await event.client.parse_id(chat_id)
        except Exception as er:
            LOGS.exception(er)
            return
    else:
        y = event.chat_id
    if SourceM.contains(y):
        SourceM.remove(y)
        await eor(x, get_string("cha_5"), time=5)
    else:
        await eor(x, "Source channel is already removed from database. ", time=3)


@ultroid_cmd(pattern="listsource")
async def list_all(event):
    x = await event.eor(get_string("com_1"))
    num = SourceM.count()
    if not num:
        return await eor(x, "No chats were added.", time=5)
    msg = get_string("cha_8")
    channels = SourceM.get()
    for channel in channels:
        name = ""
        try:
            name = get_display_name(await event.client.get_entity(int(channel)))
        except BaseException:
            name = ""
        msg += f"\n=> **{name}** [`{channel}`]"
    msg += f"\nTotal {num} channels."
    if len(msg) > 4096:
        MSG = msg.replace("*", "").replace("`", "")
        with io.BytesIO(str.encode(MSG)) as out_file:
            out_file.name = "channels.txt"
            await event.reply(
                "Channels in database",
                file=out_file,
                force_document=True,
                allow_cache=False,
            )
            await x.delete()
    else:
        await x.edit(msg)


@ultroid_cmd(pattern="adest (.*)")
async def destination(e):
    if x := e.pattern_match.group(1).strip():
        try:
            y = await e.client.parse_id(x)
        except Exception as er:
            LOGS.exception(er)
            return
    else:
        y = e.chat_id
    if not DestiM.contains(y):
        DestiM.add(y)
        await e.eor("Destination added succesfully")
    else:
        await e.eor("Destination channel already added")


@ultroid_cmd(pattern="ddest( (.*)|$)")
async def dd(event):
    chat_id = event.pattern_match.group(1).strip()
    x = await event.eor(get_string("com_1"))
    if chat_id == "all":
        await x.edit(get_string("bd_8"))
        udB.del_key("CH_DESTINATION")
        await x.edit("Destinations database cleared.")
        return
    if chat_id:
        try:
            y = await event.client.parse_id(chat_id)
        except Exception as er:
            LOGS.exception(er)
            return
    else:
        y = event.chat_id
    if DestiM.contains(y):
        DestiM.remove(y)
        await eor(x, "Destination removed from database")
    else:
        await eor(x, "Destination channel is already removed from database. ", time=5)


@ultroid_cmd(pattern="listdest")
async def list_all(event):
    ultroid_bot = event.client
    x = await event.eor(get_string("com_1"))
    channels = DestiM.get()
    num = len(channels)
    if not num:
        return await eor(x, "No chats were added.", time=5)
    msg = get_string("cha_7")
    for channel in channels:
        name = ""
        try:
            name = get_display_name(await ultroid_bot.get_entity(int(channel)))
        except BaseException:
            name = ""
        msg += f"\n=> **{name}** [`{channel}`]"
    msg += f"\nTotal {num} channels."
    if len(msg) > 4096:
        MSG = msg.replace("*", "").replace("`", "")
        with io.BytesIO(str.encode(MSG)) as out_file:
            out_file.name = "channels.txt"
            await ultroid_bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Destination channels in database",
                reply_to=event,
            )
            await x.delete()
    else:
        await x.edit(msg)


if udB.get_key("AUTOPOST"):
    ultroid_bot.add_handler(autopost_func, events.NewMessage())
