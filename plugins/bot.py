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
    s - soft restart
    To restart your bot.

• `{i}logs`
    Get the last 100 lines from heroku logs.

• `{i}usage`
    Get app usage details.

• `{i}shutdown`
    Turn off your bot.
"""

import math
import shutil
import time
from datetime import datetime as dt
from platform import python_version as pyver

import heroku3
import psutil
import requests
from git import Repo
from pyUltroid import __version__ as UltVer
from search_engine_parser.core.utils import get_rand_user_agent as grua
from telethon import __version__
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError

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
    uptime = grt(time.time() - start_time)
    header = udB.get("ALIVE_TEXT") if udB.get("ALIVE_TEXT") else "Hey,  I am alive."
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    als = (get_string("alive_1")).format(
        header,
        OWNER_NAME,
        ultroid_version,
        UltVer,
        uptime,
        pyver(),
        __version__,
        kk,
    )
    if pic is None:
        return await eor(ult, als)
    elif pic is not None and "telegra" in pic:
        try:
            await ult.reply(als, file=pic)
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als)
    else:
        try:
            await ultroid_bot.send_message(ult.chat_id, file=pic)
            await ultroid_bot.send_message(ult.chat_id, als)
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als)


@ultroid_cmd(
    pattern="ping$",
)
async def _(event):
    start = dt.now()
    x = await eor(event, "`Pong !`")
    end = dt.now()
    ms = (end - start).microseconds / 1000
    uptime = grt(time.time() - start_time)
    await x.edit(get_string("ping").format(ms, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event)


@ultroid_cmd(
    pattern="restart$",
)
async def restartbt(ult):
    if not Var.HEROKU_API:
        await eor(ult, "`Restarting..`")
        await bash("pkill python3 && python3 -m pyUltroid")
    else:
        await restart(ult)


@ultroid_cmd(
    pattern="logs$",
)
async def _(ult):
    xx = await eor(ult, "`Processing...`")
    with open("ultroid.log") as f:
        k = f.read()
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": k})
        .json()
        .get("result")
        .get("key")
    )
    url = f"https://nekobin.com/{key}"
    await ultroid.send_file(
        ult.chat_id,
        file="ultroid.log",
        thumb="resources/extras/logo_rdm.png",
        caption=f"**Ultroid Logs.**\nPasted [here](https://nekobin.com/{key}) too!",
    )
    await xx.edit("Done")
    await xx.delete()


@ultroid_cmd(
    pattern="usage$",
)
async def dyno_usage(dyno):
    if not HEROKU_API and HEROKU_APP_NAME:
        return
    dyn = await eor(dyno, "`Processing...`")
    useragent = grua()
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
            "`Error: something bad happened`\n\n" f">.`{r.reason}`\n",
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
        get_string("usage").format(
            Var.HEROKU_APP_NAME,
            AppHours,
            AppMinutes,
            AppPercentage,
            hours,
            minutes,
            percentage,
            TOTAL,
            USED,
            FREE,
            upload,
            down,
            cpuUsage,
            memory,
            disk,
        ),
    )


@ultroid_cmd(
    pattern="shutdown$",
)
async def shht(event):
    await eor(event, get_string("shutdown").format(OWNER_NAME))
    await ultroid_bot.disconnect()


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
