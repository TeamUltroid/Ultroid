# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import random

import aiohttp

from pyUltroid.dB import DEVLIST
from pyUltroid.functions.admins import admin_check

from . import *


@asst_cmd(pattern="decide")
async def dheh(e):
    text = ["Yes", "NoU", "Maybe", "IDK"]
    text = random.choice(text)
    ri = e.reply_to_msg_id or e.id
    await e.client.send_message(e.chat_id, text, reply_to=ri)


@asst_cmd(pattern="echo( (.*)|$)")
async def oqha(e):
    if not await admin_check(e):
        return
    if match := e.pattern_match.group(1).strip():
        text = match
        reply_to = e
    elif e.is_reply:
        text = (await e.get_reply_message()).text
        reply_to = e.reply_to_msg_id
    else:
        return await e.eor("What to Echo?", time=5)
    try:
        await e.delete()
    except BaseException as ex:
        LOGS.error(ex)
    await e.client.send_message(e.chat_id, text, reply_to=reply_to)


@asst_cmd(pattern="kickme$")
async def doit(e):
    if e.sender_id in DEVLIST:
        return await eod(e, "`I will Not Kick You, my Developer..`")
    try:
        await e.client.kick_participant(e.chat_id, e.sender_id)
    except Exception as Fe:
        return await e.eor(str(Fe), time=5)
    await e.eor("Yes, You are right, get out.", time=5)


@asst_cmd(pattern="joke$")
async def do_joke(e):
    e = await e.get_reply_message() if e.is_reply else e
    link = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"
    async with aiohttp.ClientSession() as ses:
        async with ses.get(link) as out:
            out = await out.json()
    await e.reply(out["joke"])
