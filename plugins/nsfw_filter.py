# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

import os

import requests

from . import *


@ultroid_cmd(pattern="addnsfw ?(.*)", admins_only=True)
async def addnsfw(e):
    action = e.pattern_match.group(1)
    if not action:
        action = "mute"
    nsfw_chat(e.chat_id, action)
    await eor(e, "Added This Chat To Nsfw Filter")


@ultroid_cmd(pattern="remnsfw", admins_only=True)
async def remnsfw(e):
    rem_nsfw(e.chat_id)
    await eor(e, "Removed This Chat from Nsfw Filter.")


@ultroid_bot.on(events.NewMessage(incoming=True))
async def checknsfw(e):
    chat = e.chat_id
    action = is_nsfw(chat)
    if action and udB.get("DEEP_API") and e.media:
        pic, name, nsfw = "", "", 0
        try:
            pic = await ultroid_bot.download_media(e.media, thumb=-1)
        except BaseException:
            pass
        if e.file:
            name = e.file.name
        if name:
            if check_profanity(name):
                nsfw += 1
        if pic and not nsfw:
            r = requests.post(
                "https://api.deepai.org/api/nsfw-detector",
                files={
                    "image": open(pic, "rb"),
                },
                headers={"api-key": udB["DEEP_API"]},
            )
            k = float((r.json()["output"]["nsfw_score"]))
            score = int(k * 100)
            if score > 45:
                nsfw += 1
            os.remove(pic)
        if nsfw:
            await e.delete()
            take(action)
