# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ftyping <time/in secs>`
    `Show Fake Typing in current chat. `

• `{i}faudio <time/in secs>`
    `Show Fake Recording Action in current chat. `

• `{i}fvideo <time/in secs>`
    `Show Fake video action in current chat. `

• `{i}fgame <time/in secs>`
    `Show Fake Game Playing Action in current chat. `

• `{i}fround <time/in secs>`
    `Show Fake video message action in current chat. `

• `{i}fphoto <time/in secs>`
    `Show Fake sending photo in current chat. `

• `{i}fdocument <time/in secs>`
    `Show Fake sending photo in current chat. `

• `{i}flocation <time/in secs>`
    `Show Fake share location in current chat. `

• `{i}fcontact <time/in secs>`
    `Show Fake share contact in current chat. `

• `{i}stopaction`
   `Stop any ongoing Chat Action going in Chat.`
"""

from . import *


@ultroid_cmd(pattern="ftyping ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake Typing For {t} sec.")
    async with e.client.action(e.chat_id, "typing"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="faudio ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake audio recording For {t} sec.")
    async with e.client.action(e.chat_id, "record-audio"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fvideo ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake video recording For {t} sec.")
    async with e.client.action(e.chat_id, "record-video"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fgame ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake Game Playing For {t} sec.")
    async with e.client.action(e.chat_id, "game"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fround ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake video message recording For {t} sec.")
    async with e.client.action(e.chat_id, "record-round"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fphoto ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Start Fake Sending Photos For {t} sec.")
    async with e.client.action(e.chat_id, "photo"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fdocument ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake sending document For {t} sec.")
    async with e.client.action(e.chat_id, "document"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="flocation ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake share location For {t} sec.")
    async with e.client.action(e.chat_id, "location"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="fcontact ?(.*)")
async def _(e):
    t = e.pattern_match.group(1)
    if not (t or t.isdigit()):
        t = 100
    else:
        try:
            t = int(t)
        except BaseException:
            try:
                t = await ban_time(e, t)
            except BaseException:
                return await eod(e, "`Incorrect Format`")
    await eod(e, f"Starting Fake share contact For {t} sec.")
    async with e.client.action(e.chat_id, "contact"):
        await asyncio.sleep(t)


@ultroid_cmd(pattern="stopaction")
async def do_it(e):
    async with e.client.action(e.chat_id, "cancel"):
        pass
    await e.reply("Fake Action Stopped.")
