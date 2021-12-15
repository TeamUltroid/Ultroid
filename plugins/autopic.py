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

• `{i}autopic` : stop autopic if active.
"""
import asyncio
import os
from random import shuffle

from pyUltroid.functions.misc import unsplashsearch
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from . import download_file, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="autopic ?(.*)")
async def autopic(e):
    search = e.pattern_match.group(1)
    if udB.get_key("AUTOPIC") and not search:
        udB.del_key("AUTOPIC")
        return await e.eor(get_string("autopic_5"))
    if not search:
        return await e.eor(get_string("autopic_1"), time=5)
    e = await e.eor(get_string("com_1"))
    clls = await unsplashsearch(search, limit=50)
    if not clls:
        return await e.eor(get_string("autopic_2").format(search), time=5)
    await e.eor(get_string("autopic_3").format(search))
    udB.set_key("AUTOPIC", "True")
    SLEEP_TIME = udB.get_key("SLEEP_TIME") or 1221
    while True:
        for lie in clls:
            if udB.get_key("AUTOPIC") is not True:
                return
            kar = await download_file(lie, "autopic.png")
            file = await e.client.upload_file(kar)
            await e.client(UploadProfilePhotoRequest(file))
            os.remove(kar)
            await asyncio.sleep(SLEEP_TIME)
        shuffle(clls)
