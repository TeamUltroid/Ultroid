# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

•`{i}addnsfw <ban/mute/kick>`
   If someone sends 18+ content it will be deleted and action will be taken.

•`{i}remnsfw`
   Remove Chat from nsfw filtering.
"""

import os

import requests
from ProfanityDetector import detector
from pyUltroid.dB.nsfw_db import is_nsfw, nsfw_chat, rem_nsfw

from . import HNDLR, eor, events, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="addnsfw ?(.*)", admins_only=True)
async def addnsfw(e):
    if not udB.get("DEEP_API"):
        return await eor(
            e, f"Get Api from deepai.org and Add It `{HNDLR}setredis DEEP_API your-api`"
        )
    action = e.pattern_match.group(1)
    if not action or ("ban" or "kick" or "mute") not in action:
        action = "mute"
    nsfw_chat(e.chat_id, action)
    await eor(e, "Added This Chat To Nsfw Filter")


@ultroid_cmd(pattern="remnsfw", admins_only=True)
async def remnsfw(e):
    rem_nsfw(e.chat_id)
    await eor(e, "Removed This Chat from Nsfw Filter.")


NWARN = {}


@ultroid_bot.on(events.NewMessage(incoming=True))
async def checknsfw(e):
    chat = e.chat_id
    action = is_nsfw(chat)
    if action and udB.get("DEEP_API") and e.media:
        pic, name, nsfw = "", "", 0
        try:
            pic = await e.download_media(thumb=-1)
        except BaseException:
            pass
        if e.file:
            name = e.file.name
        if name:
            x, y = detector(name)
            if y:
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
            if NWARN.get(e.sender_id):
                count = NWARN[e.sender_id] + 1
                if count < 3:
                    NWARN.update({e.sender_id: count})
                    return await ultroid_bot.send_message(
                        chat,
                        f"**NSFW Warn {count}/3** To [{e.sender.first_name}](tg://user?id={e.sender_id})\nDon't Send NSFW stuffs Here Or You will Be Get {action}",
                    )
                if "mute" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            chat, e.sender_id, until_date=None, send_messages=False
                        )
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Action Taken** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nCan't Able to {action}.",
                        )
                elif "ban" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            chat, e.sender_id, view_messages=False
                        )
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Action Taken** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nCan't Able to {action}.",
                        )
                elif "kick" in action:
                    try:
                        await ultroid_bot.kick_participant(chat, e.sender_id)
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Action Taken** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW Warn 3/3 to [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nCan't Able to {action}.",
                        )
                NWARN.pop(e.sender_id)
            else:
                NWARN.update({e.sender_id: 1})
                return await ultroid_bot.send_message(
                    chat,
                    f"**NSFW Warn 1/3** To [{e.sender.first_name}](tg://user?id={e.sender_id})\nDon't Send NSFW stuffs Here Or You will Be Get {action}",
                )
