# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}autopic <search query>`
    Will change your profile pic at defined intervals with pics related to the given topic.

• `{i}autopic` : stop autopic if active.
"""
import asyncio
import os
import random
from glob import glob
from random import shuffle

from pyUltroid.functions.google_image import googleimagesdownload
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from . import LOGS, get_string, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="autopic( (.*)|$)")
async def autopic(e):
    search = e.pattern_match.group(1).strip()
    if udB.get_key("AUTOPIC") and not search:
        udB.del_key("AUTOPIC")
        return await e.eor(get_string("autopic_5"))
    if not search:
        return await e.eor(get_string("autopic_1"), time=5)
    e = await e.eor(get_string("com_1"))
    gi = googleimagesdownload()
    args = {
        "keywords": search,
        "limit": 50,
        "format": "jpg",
        "output_directory": "./resources/downloads/",
    }
    try:
        pth = await gi.download(args)
        ok = pth[0][search]
    except Exception as er:
        LOGS.exception(er)
        return await e.eor(str(er))
    if not ok:
        return await e.eor(get_string("autopic_2").format(search), time=5)
    await e.eor(get_string("autopic_3").format(search))
    udB.set_key("AUTOPIC", search)
    SLEEP_TIME = udB.get_key("SLEEP_TIME") or 1221
    while True:
        for lie in ok:
            if udB.get_key("AUTOPIC") != search:
                return
            file = await e.client.upload_file(lie)
            await e.client(UploadProfilePhotoRequest(file))
            await asyncio.sleep(SLEEP_TIME)
        shuffle(ok)


if search := udB.get_key("AUTOPIC"):
    gi = googleimagesdownload()
    args = {
        "keywords": search,
        "limit": 50,
        "format": "jpg",
        "output_directory": "./resources/downloads/",
    }
    images = []
    if os.path.exists(f"./resources/downloads/{search}"):
        images = glob(f"resources/downloads/{search}/*")
    sleep = udB.get_key("SLEEP_TIME") or 1221

    async def autopic_func():
        if udB.get_key("AUTOPIC") != search:
            return
        if not images:
            try:
                pth = await gi.download(args)
                ok = pth[0][search]
                images.extend(ok)
            except Exception as er:
                LOGS.exception(er)
                return
        else:
            ok = images
        img = random.choice(ok)
        file = await ultroid_bot.upload_file(img)
        await ultroid_bot(UploadProfilePhotoRequest(file))
        shuffle(ok)

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        schedule = AsyncIOScheduler()
        schedule.add_job(autopic_func, "interval", seconds=sleep)
        schedule.start()
    except ModuleNotFoundError as er:
        LOGS.error(f"autopic: '{er.name}' not installed.")
