# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

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
        if not len(ok) == 4:
            return await eor(e, "Give Time in correct format")
        tm = []
        for x in ok:
            tm.append(int(x))
        udB.set("NIGHT_TIME", str(tm))
        await eor(e, "Setted time successfully")
    except BaseException:
        await eor(e, "Give Time in correct format")


@ultroid_cmd(pattern="addnight")
async def add_grp(e):
    add_night(e.chat_id)
    await eor(e, "Done, Added Current Chat To Night Mode")


@ultroid_cmd(pattern="remnight")
async def rem_grp(e):
    rem_night(e.chat_id)
    await eor(e, "Done, Added Current Chat To Night Mode")


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
            await ultroid_bot.send_message(chat, "Group Opened")
        except Exception as er:
            LOGS.info(er)


async def close_grp():
    chats = night_grps()
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
            await ultroid_bot.send_message(chat, "Group Opened")
        except Exception as er:
            LOGS.info(er)


if night_grps():
    h1, m1, h2, m2 = 0, 0, 7, 0
    if udB.get("NIGHT_TIME"):
        h1, m1, h2, m2 = eval(udB["NIGHT_TIME"])
    sch = AsyncIOScheduler()
    sch.add_job(close_grp, trigger="cron", hour=h1, minute=m1)
    sch.add_job(open_grp, trigger="cron", hour=h2, minute=m2)
    sch.start()
