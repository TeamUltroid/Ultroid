# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
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
import shutil, psutil
from random import choice

from utilities import some_random_headers
from utilities.helper import humanbytes, async_searcher
from core.config import HOSTED_ON,  Var
from .. import ultroid_cmd, udB, LOGS, get_string

HEROKU_API = None
HEROKU_APP_NAME = None


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



def db_usage():
    if udB.name == "Mongo":
        total = 512
    elif udB.name == "Redis":
        total = 30
    elif udB.name == "SQL":
        total = 20
    else:
        return ''
    total *= (2**20)
    used = udB.usage
    a = f"{humanbytes(used)}/{humanbytes(total)}"
    b = f"{str(round((used / total) * 100, 2))}%"
    return f"**{udB.name}**\n\n**Storage Used**: `{a}`\n**Usage percentage**: **{b}**"


async def get_full_usage():
    is_hk, hk = await heroku_usage()
    her = hk if is_hk else ""
    rd = db_usage()
    return her + "\n\n" + rd
