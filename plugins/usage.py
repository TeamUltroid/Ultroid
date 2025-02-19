# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
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

• `{i}usage db`
   Get database storage usage.
"""

import math
import shutil
from random import choice

from pyUltroid.fns import some_random_headers

from . import (
    HOSTED_ON,
    LOGS,
    Var,
    async_searcher,
    get_string,
    humanbytes,
    udB,
    ultroid_cmd,
)

HEROKU_API = None
HEROKU_APP_NAME = None

if HOSTED_ON == "heroku":
    heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME
    try:
        if heroku_api and app_name:
            import heroku3

            Heroku = heroku3.from_key(heroku_api)
            app = Heroku.app(app_name)
            HEROKU_API = heroku_api
            HEROKU_APP_NAME = app_name
    except BaseException as er:
        LOGS.exception(er)


@ultroid_cmd(pattern="usage")
async def usage_finder(event):
    x = await event.eor(get_string("com_1"))
    try:
        opt = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await x.edit(simple_usage())

    if opt == "db":
        await x.edit(db_usage())
    elif opt == "heroku":
        is_hk, hk = await heroku_usage()
        await x.edit(hk)
    else:
        await x.edit(await get_full_usage())


def simple_usage():
    try:
        import psutil
    except ImportError:
        return "Install 'psutil' to use this..."
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


async def heroku_usage():
    try:
        import psutil
    except ImportError:
        return (
            False,
            "'psutil' not installed!\nPlease Install it to use this.\n`pip3 install psutil`",
        )
    if not (HEROKU_API and HEROKU_APP_NAME):
        if HOSTED_ON == "heroku":
            return False, "Please fill `HEROKU_API` and `HEROKU_APP_NAME`"
        return (
            False,
            f"`This command is only for Heroku Users, You are using {HOSTED_ON}`",
        )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": choice(some_random_headers),
        "Authorization": f"Bearer {heroku_api}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    her_url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    try:
        result = await async_searcher(her_url, headers=headers, re_json=True)
    except Exception as er:
        return False, str(er)
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
    _ = shutil.disk_usage("/")
    disk = _.used / _.total * 100
    cpuUsage = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
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


def db_usage():
    if udB.name == "Mongo":
        total = 512
    elif udB.name == "Redis":
        total = 30
    elif udB.name == "SQL":
        total = 20
    total = total * (2**20)
    used = udB.usage
    a = f"{humanbytes(used)}/{humanbytes(total)}"
    b = f"{str(round((used / total) * 100, 2))}%"
    return f"**{udB.name}**\n\n**Storage Used**: `{a}`\n**Usage percentage**: **{b}**"


async def get_full_usage():
    is_hk, hk = await heroku_usage()
    her = hk if is_hk else ""
    rd = db_usage()
    return her + "\n\n" + rd
