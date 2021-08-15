# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import aiohttp

from . import *


@ultroid_cmd(pattern="echo ?(.*)", type=["manager"])
async def oqha(e):
    match = e.pattern_match.group(1)
    if match:
        text = match
        reply_to = e
    elif e.is_reply:
        text = (await e.get_reply_message()).text
        reply_to = e.reply_to_msg_id
    else:
        return await eod(e, "What to Echo?")
    await e.client.send_message(e.chat_id, text, reply_to=reply_to)


@ultroid_cmd(pattern="kickme", type=["manager"], allow_all=True)
async def doit(e):
    try:
        await e.client.kick_participant(e.chat_id, e.sender_id)
    except Exception as e:
        return await eod(e, str(e))
    await eod(e, "Yes, You are right, get out.")


@ultroid_cmd(pattern="joke$", type=["manager"])
async def do_joke(e):
    e = await e.get_reply_message() if e.is_reply else e
    link = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"
    async with aiohttp.ClientSession() as ses:
        async with ses.get(link) as out:
            out = await out.json()
    await e.reply(out["joke"])
