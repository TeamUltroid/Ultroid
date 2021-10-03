# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}usage`
    Get overall usage.

• `{i}usage heroku`
   Get heroku stats.

• `{i}usage redis`
   Get redis usage.
"""

import math
import shutil
from random import choice

import heroku3
import psutil
import requests
from pyUltroid.functions import some_random_headers

from . import Var, eor, get_string, humanbytes, udB, ultroid_cmd

HEROKU_API = None
HEROKU_APP_NAME = None
heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME
try:
    if heroku_api and app_name:
        HEROKU_API = heroku_api
        HEROKU_APP_NAME = app_name
        Heroku = heroku3.from_key(heroku_api)
        app = Heroku.app(app_name)
except BaseException:
    HEROKU_API = None
    HEROKU_APP_NAME = None


@ultroid_cmd(pattern="usage")
async def usage_finder(event):
    x = await eor(event, get_string("com_1"))
    try:
        opt = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await x.edit(simple_usage())

    if opt == "redis":
        await x.edit(redis_usage())
    elif opt == "heroku":
        is_hk, hk = heroku_usage()
        await x.edit(hk)
    elif opt == "full":
        await x.edit(get_full_usage())
    else:
        await eor(x, "`The what?`", time=5)


def simple_usage():
    total, used, free = shutil.disk_usage(".")
    cpuUsage = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    upload = humanbytes(psutil.net_io_counters().bytes_sent)
    down = humanbytes(psutil.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return get_string("usage_simple").format(
        TOTAL,
        USED,
        FREE,
        upload,
        down,
        cpuUsage,
        memory,
        disk,
    )


def heroku_usage():
    if HEROKU_API is None and HEROKU_APP_NAME is None:
        return False, "You do not use heroku, bruh!"
    user_id = Heroku.account().id
    headers = {
        "User-Agent": choice(some_random_headers),
        "Authorization": f"Bearer {heroku_api}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    her_url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    r = requests.get(her_url, headers=headers)
    if r.status_code != 200:
        return (
            True,
            f"**ERROR**\n`{r.reason}`",
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
    return True, get_string("usage").format(
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
    )


def redis_usage():
    x = 30 * 1024 * 1024
    z = sum(udB.memory_usage(n) for n in udB.keys())
    a = humanbytes(z) + "/" + humanbytes(x)
    b = str(round(z / x * 100, 3)) + "%"
    return f"**REDIS**\n\n**Storage Used**: {a}\n**Usage percentage**: {b}"


def get_full_usage():
    is_hk, hk = heroku_usage()
    her = "" if is_hk is False else hk
    rd = redis_usage()
    return her + "\n\n" + rd
