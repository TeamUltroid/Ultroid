# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


"""
✘ Commands Available -

At Night it will turn off everyone permission to send message in  an all groups which you added via `{i}addnight`
And Turn On auto at morning

• `{i}addnm`
   Add NightMode
   To Add Group To Auto Night Mode.

• `{i}remnm`
   Remove NightMode
   To remove Group From Auto Night Mode

• `{i}listnm`
   List NightMode
   To Get All List of Groups where NightMode Active.

• `{i}nmtime <close hour> <close min> <open hour> <open min>
   NightMode Time
   By Default Its close 00:00 , open 07:00
   Use 24hr format
   Ex- `nmtime 01 00 06 30`
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyUltroid.functions.night_db import *
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

from . import *


@ultroid_cmd(pattern="nmtime ?(.*)")
async def set_time(e):
    if not e.pattern_match.group(1):
        return await eor(e, "Give Time in correct format")
    try:
        ok = e.text.split(maxsplit=1)[1].split()
        if len(ok) != 4:
            return await eor(e, "Give Time in correct format")
        tm = [int(x) for x in ok]
        udB.set("NIGHT_TIME", str(tm))
        await eor(e, "Setted time successfully")
    except BaseException:
        await eor(e, "Give Time in correct format")


@ultroid_cmd(pattern="addnm ?(.*)")
async def add_grp(e):
    pat = e.pattern_match.group(1)
    if pat:
        try:
            add_night((await bot.get_entity(pat)).id)
            return await eor(e, f"Done, Added {pat} To Night Mode.")
        except BaseException:
            return await eor(e, "Something Went Wrong", time=5)
    add_night(e.chat_id)
    await eor(e, "Done, Added Current Chat To Night Mode")


@ultroid_cmd(pattern="remnm ?(.*)")
async def rem_grp(e):
    pat = e.pattern_match.group(1)
    if pat:
        try:
            rem_night((await bot.get_entity(pat)).id)
            return await eor(e, f"Done, Removed {pat} To Night Mode.")
        except BaseException:
            return await eor(e, "Something Went Wrong", time=5)
    rem_night(e.chat_id)
    await eor(e, "Done, Removed Current Chat from Night Mode")


@ultroid_cmd(pattern="listnm$")
async def rem_grp(e):
    chats = night_grps()
    name = "NightMode Groups Are-:\n\n"
    for x in chats:
        try:
            ok = await ultroid_bot.get_entity(x)
            name += "@" + ok.username if ok.username else ok.title
        except BaseException:
            name += str(x)
    await eor(e, name)


async def open_grp():
    chats = night_grps()
    for chat in chats:
        try:
            await ultroid_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=False,
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        send_polls=False,
                    ),
                )
            )
            await ultroid_bot.send_message(chat, "**NightMode Off**\n\nGroup Opened 🥳.")
        except Exception as er:
            LOGS.info(er)


async def close_grp():
    chats = night_grps()
    h1, m1, h2, m2 = 0, 0, 7, 0
    if udB.get("NIGHT_TIME"):
        h1, m1, h2, m2 = eval(udB["NIGHT_TIME"])
    for chat in chats:
        try:
            await ultroid_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=True,
                    ),
                )
            )
            await ultroid_bot.send_message(
                chat, f"**NightMode : Group Closed**\n\nGroup Will Open At `{h2}:{m2}`"
            )
        except Exception as er:
            LOGS.info(er)


if night_grps():
    try:
        h1, m1, h2, m2 = 0, 0, 7, 0
        if udB.get("NIGHT_TIME"):
            h1, m1, h2, m2 = eval(udB["NIGHT_TIME"])
        sch = AsyncIOScheduler()
        sch.add_job(close_grp, trigger="cron", hour=h1, minute=m1)
        sch.add_job(open_grp, trigger="cron", hour=h2, minute=m2)
        sch.start()
    except Exception as er:
        LOGS.info(er)
