# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}autopic <search query>`
    Will change your profile pic at defined intervals with pics related to the given topic.

• `{i}stoppic`
    Stop the AutoPic command.

"""
import asyncio
import os

import requests as r
from bs4 import BeautifulSoup as bs
from pyUltroid.functions.misc import unsplashsearch
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from . import *


@ultroid_cmd(pattern="autopic ?(.*)")
async def autopic(e):
    search = e.pattern_match.group(1)
    if not search:
        return await eor(e, get_string("autopic_1"), time=5)
    clls = await unsplashsearch(search)
    if len(clls) == 0:
        return await eor(e, get_string("autopic_2").format(search), time=5)
    await eor(e, get_string("autopic_3").format(search))
    udB.set("AUTOPIC", "True")
    ST = udB.get("SLEEP_TIME")
    SLEEP_TIME = int(ST) if ST else 1221
    while True:
        for lie in clls:
            if udB.get("AUTOPIC") != "True":
                return
            kar = await download_file(lie, kar)
            file = await e.client.upload_file(kar)
            await e.client(UploadProfilePhotoRequest(file))
            os.remove(kar)
            await asyncio.sleep(SLEEP_TIME)


@ultroid_cmd(pattern="stoppic$")
async def stoppo(ult):
    gt = udB.get("AUTOPIC")
    if gt != "True":
        return await eor(ult, get_string("autopic_4"), time=5)
    udB.set("AUTOPIC", "None")
    await eor(ult, get_string("autopic_5"), time=5)
