# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available


🔹 `{i}shift <from channel> | <to channel>`
     This will transfer all old post from channel A to channel B.
      (u can use username or id of channel too)
      example : `{i}shift @abc | @xyz`
      [note - this (" | ") sign is nessesary]

🔹 For auto-posting/forwarding all new message from any source channel to any destination channel.

   * `asource <channel username or id>`
      This add source channel to database
   * `dsource <channel username or id>`
      This remove source channels from database
   * `listsource <channel username or id>`
      Show list of source channels


   * `{i}adest <channel username or id>`
      This add Ur channels to database
   * `{i}ddest <channel username or id>`
      This Remove Ur channels from database
   * `{i}listdest <channel username or id>`
      Show List of Ur channels

   'you can set many channels in database'
   'For activating auto-post use `{i}setredis AUTOPOST True` '
"""

import asyncio

from pyUltroid.functions.ch_db import *

from . import *


@ultroid_bot.on(events.NewMessage())
async def _(e):
    if not udB.get("AUTOPOST") == "True":
        return
    x = get_source_channels()
    th = await e.get_chat()
    if str(th.id) not in x:
        return
    y = get_destinations()
    for ys in y:
        try:
            if e.text and not e.media:
                await ultroid_bot.send_message(int(ys), e.text)
            elif e.media and e.text:
                await ultroid_bot.send_file(int(ys), e.media, caption=e.text)
            else:
                await ultroid_bot.send_file(int(ys), e.media)
        except Exception as e:
            await ultroid_bot.send_message(bot.me.id, str(e))


@ultroid_cmd(pattern="shift (.*)")
async def _(e):
    x = e.pattern_match.group(1)
    z = await eor(e, "`processing..`")
    a, b = x.split("|")
    try:
        c = int(a)
    except Exception:
        try:
            c = (await e.client.get_entity(a)).id
        except Exception:
            await z.edit("invalid Channel given")
            return
    try:
        d = int(b)
    except Exception:
        try:
            d = (await e.client.get_entity(b)).id
        except Exception:
            await z.edit("invalid Channel given")
            return
    async for msg in e.client.iter_messages(int(c), reverse=True):
        try:
            await asyncio.sleep(2)
            await e.client.send_message(int(d), msg)
        except BaseException:
            pass
    await z.edit("Done")


@ultroid_cmd(pattern="asource (.*)")
async def source(e):
    x = e.pattern_match.group(1)
    try:
        y = int(x)
    except Exception:
        try:
            y = int((await bot.get_entity(x)).id)
        except Exception as es:
            print(es)
            return
    if not is_source_channel_added(y):
        add_source_channel(y)
        await eor(e, "Source added succesfully")
    elif is_source_channel_added(y):
        await eor(e, "Source channel already added")


@ultroid_cmd(pattern="dsource ?(.*)")
async def dd(event):
    chat_id = event.pattern_match.group(1)
    x = await eor(event, "`Processing..`")
    if chat_id == "all":
        await x.edit("`Removing...`")
        udB.delete("CH_SOURCE")
        await x.edit("Source database cleared.")
        return
    try:
        y = int(chat_id)
    except Exception:
        try:
            y = int((await event.client.get_entity(chat_id)).id)
        except Exception as es:
            print(es)
            return
    if is_source_channel_added(y):
        rem_source_channel(y)
        await eod(x, "Source removed from database", time=3)
    elif is_source_channel_added(y):
        rem_source_channel(y)
        await eod(x, "Source removed from database")
    elif not is_source_channel_added(y):
        await eod(x, "Source channel is already removed from database. ", time=3)


@ultroid_cmd(pattern="listsource")
async def list_all(event):
    x = await eor(event, "`Calculating...`")
    channels = get_source_channels()
    num = get_no_source_channels()
    if num == 0:
        return await eod(x, "No chats were added.", time=5)
    msg = "Source channels in database:\n"
    for channel in channels:
        name = ""
        try:
            name = (await event.client.get_entity(int(channel))).title
        except BaseException:
            name = ""
        msg += f"=> **{name}** [`{channel}`]\n"
    msg += f"\nTotal {get_no_source_channels()} channels."
    if len(msg) > 4096:
        MSG = msg.replace("*", "").replace("`", "")
        with io.BytesIO(str.encode(MSG)) as out_file:
            out_file.name = "channels.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Channels in database",
                reply_to=event,
            )
            await x.delete()
    else:
        await x.edit(msg)


@ultroid_cmd(pattern="adest (.*)")
async def destination(e):
    x = e.pattern_match.group(1)
    try:
        y = int(x)
    except Exception:
        try:
            y = int((await e.client.get_entity(x)).id)
        except Exception as es:
            print(es)
            return
    if not is_destination_added(y):
        add_destination(y)
        await eor(e, "Destination added succesfully")
    elif is_destination_added(y):
        await eor(e, "Destination channel already added")


@ultroid_cmd(pattern="ddest ?(.*)")
async def dd(event):
    chat_id = event.pattern_match.group(1)
    x = await eor(event, "processing")
    if chat_id == "all":
        await x.edit("`Removing...`")
        udB.delete("CH_DESTINATION")
        await x.edit("Destinations database cleared.")
        return
    try:
        y = int(chat_id)
    except Exception:
        try:
            y = int((await event.client.get_entity(chat_id)).id)
        except Exception as es:
            print(es)
            return
    if is_destination_added(y):
        rem_destination(y)
        await eor(x, "Destination removed from database")
    elif is_destination_added(y):
        rem_destination(y)
        await eod(x, "Destination removed from database")
    elif not is_destination_added(y):
        await eod(x, "Destination channel is already removed from database. ")


@ultroid_cmd(pattern="listdest")
async def list_all(event):
    ultroid_bot = event.client
    x = await eor(event, "`Calculating...`")
    channels = get_destinations()
    num = get_no_destinations()
    if num == 0:
        return await eod(x, "No chats were added.", time=5)
    msg = "Destination channels in database:\n"
    for channel in channels:
        name = ""
        try:
            name = (await ultroid.get_entity(int(channel))).title
        except BaseException:
            name = ""
        msg += f"=> **{name}** [`{channel}`]\n"
    msg += f"\nTotal {get_no_destinations()} channels."
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
