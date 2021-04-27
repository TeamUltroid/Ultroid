# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
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
import random

from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.messages import GetWebPagePreviewRequest as getweb
from . import *


@ultroid_cmd(pattern="autopic ?(.*)")
async def autopic(e):
    search = e.pattern_match.group(1)
    if not search:
        return await eor(e, get_string("autopic_1"))
    clls = autopicsearch(search)
    if len(clls) == 0:
        return await eor(e, get_string("autopic_2").format(search))
    title = page["title"]
    await eor(e, get_string("autopic_3").format(search))
    udB.set("AUTOPIC", "True")
    while True:
        ge = udB.get("AUTOPIC")
        if not ge == "True":
            return
        for lie in clls:
            au ='https://unsplash.com' + lie['href']
            et = await ultroid_bot(getweb(au))
            kar = await ultroid_bot.download_media(et.webpage.photo)
            file = await ultroid_bot.upload_file(kar)
            await ultroid_bot(UploadProfilePhotoRequest(file))
            os.remove(kar)
            await asyncio.sleep(1100)


@ultroid_cmd(pattern="stoppic$")
async def stoppo(ult):
    gt = udB.get("AUTOPIC")
    if not gt == "True":
        return await eor(ult, "`AUTOPIC was not in used !!`")
    udB.set("AUTOPIC", "None")
    await eor(ult, "`AUTOPIC Stopped !!`")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
