# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}alive`
    Check if your bot is working.

• `{i}ping`
    Check Ultroid's response time.

• `{i}cmds`
    View all plugin names.

• `{i}restart`
    To restart your bot.

• `{i}logs`
    Get the last 100 lines from heroku logs.

• `{i}usage`
    Get app usage details.

• `{i}shutdown`
    Turn off your bot.
"""

import asyncio
import math
import os
import shutil
import time
from datetime import datetime as dt
from platform import python_version as pyver

import heroku3
import psutil
import requests
from git import Repo
from telethon import __version__

from . import *

HEROKU_API = None
HEROKU_APP_NAME = None

try:
    if Var.HEROKU_API and Var.HEROKU_APP_NAME:
        HEROKU_API = Var.HEROKU_API
        HEROKU_APP_NAME = Var.HEROKU_APP_NAME
        Heroku = heroku3.from_key(Var.HEROKU_API)
        heroku_api = "https://api.heroku.com"
        app = Heroku.app(Var.HEROKU_APP_NAME)
except BaseException:
    HEROKU_API = None
    HEROKU_APP_NAME = None


@ultroid_cmd(
    pattern="alive$",
)
async def lol(ult):
    pic = udB.get("ALIVE_PIC")
    uptime = grt((time.time() - start_time))
    header = udB.get("ALIVE_TEXT") if udB.get("ALIVE_TEXT") else "Hey,  I am alive."
    als = """
**The Ultroid Userbot...**

**{}**

┏━━━━━━━━━━━━━━━━━━━━━
┣ **Owner** - `{}`
┣ **Version** - `{}`
┣ **UpTime** - `{}`
┣ **Python** - `{}`
┣ **Telethon** - `{}`
┣ **Branch** - `{}`
┗━━━━━━━━━━━━━━━━━━━━━
""".format(
        header,
        OWNER_NAME,
        ultroid_version,
        uptime,
        pyver(),
        __version__,
        Repo().active_branch,
    )
    if pic is None:
        await ult.edit(als)
    elif pic is not None and "telegra" in pic:
        await ult.delete()
        await ult.reply(als, file=pic)
    else:
        await ult.delete()
        await ultroid_bot.send_message(ult.chat_id, file=pic)
        await ultroid_bot.send_message(ult.chat_id, als)


@ultroid_cmd(
    pattern="ping$",
)
async def _(event):
    start = dt.now()
    x = await eor(event, "`Pong !`")
    if event.fwd_from:
        return
    end = dt.now()
    ms = (end - start).microseconds / 1000
    uptime = grt((time.time() - start_time))
    await x.edit(f"**Pong !!** `{ms}ms`\n**Uptime** - `{uptime}`")


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event)


@ultroid_cmd(
    pattern="restart$",
)
async def restartbt(ult):
    await restart(ult)


@ultroid_cmd(
    pattern="logs$",
)
async def _(ult):
    xx = await eor(ult, "`Processing...`")
    if HEROKU_API is None and HEROKU_APP_NAME is None:
        return await xx.edit("Please set `HEROKU_APP_NAME` and `HEROKU_API` in vars.")
    await xx.edit("`Downloading Logs...`")
    with open("logs-ultroid.txt", "w") as log:
        log.write(app.get_log())
    ok = app.get_log()
    message = ok
    url = "https://del.dog/documents"
    r = requests.post(url, data=message.encode("UTF-8")).json()
    url = f"https://del.dog/{r['key']}"
    await ult.client.send_file(
        ult.chat_id,
        "logs-ultroid.txt",
        reply_to=ult.id,
        caption=f"**Heroku** Ultroid Logs.\nPasted [here]({url}) too!",
    )
    await xx.edit("`Uploading...`")
    await asyncio.sleep(1)
    await xx.delete()
    return os.remove("logs-ultroid.txt")


@ultroid_cmd(
    pattern="usage$",
)
async def dyno_usage(dyno):
    dyn = await eor(dyno, "`Processing...`")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {Var.HEROKU_API}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit(
            "`Error: something bad happened`\n\n" f">.`{r.reason}`\n"
        )
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    total, used, free = shutil.disk_usage(".")
    cpuUsage = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    upload = humanbytes(psutil.net_io_counters().bytes_sent)
    down = humanbytes(psutil.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return await eod(
        dyn,
        "**⚙️ Dyno Usage ⚙️**:\n\n"
        + f" -> `Dyno usage for`  **{Var.HEROKU_APP_NAME}**:\n"
        + f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
        + f"**|**  [`{AppPercentage}`**%**]"
        + "\n\n"
        + " -> `Dyno hours quota remaining this month`:\n"
        + f"     •  `{hours}`**h**  `{minutes}`**m**  "
        + f"**|**  [`{percentage}`**%**]\n\n"
        + f"**Total Disk Space: {TOTAL}\n\n**"
        + f"**Used: {USED}  Free: {FREE}\n\n**"
        + f"**📊Data Usage📊\n\nUpload: {upload}\nDown: {down}\n\n**"
        + f"**CPU: {cpuUsage}%\nRAM: {memory}%\nDISK: {disk}%**",
    )


@ultroid_cmd(
    pattern="shutdown$",
)
async def shht(event):
    await eor(event, "GoodBye {}.\n`Shutting down...`".format(OWNER_NAME))
    await ultroid_bot.disconnect()


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=Var.HNDLR)}"})
