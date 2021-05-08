# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import functools
from telethon import events
from .. import *
from ..utils import *
from ._decorators import sed
from telethon.tl.types import InputWebDocument
from telethon.utils import get_display_name

OWNER_NAME = ultroid_bot.me.first_name
OWNER_ID = ultroid_bot.me.id
ULTROID_PIC = "https://telegra.ph/file/d16ced174be071190818b.png"
MSG = f"""
**RYNO - UserBot**
➖➖➖➖➖➖➖➖➖➖
**Owner**: [{get_display_name(ultroid_bot.me)}](tg://user?id={ultroid_bot.me.id})
**Support**: @OFFICIALRYNO
➖➖➖➖➖➖➖➖➖➖
"""

# decorator for assistant


def inline_owner():
    def decorator(function):
        @functools.wraps(function)
        async def wrapper(event):
            if event.sender_id in sed:
                try:
                    await function(event)
                except BaseException:
                    pass
            else:
                try:
                    builder = event.builder
                    sur = builder.article(
                        title="RYNO Userbot",
                        url="https://t.me/OFFICIALRYNO",
                        description="(c) OFFICIALRYNO",
                        text=MSG,
                        thumb=InputWebDocument(ULTROID_PIC, 0, "image/jpeg", []),
                        buttons=[
                            [
                                Button.url(
                                    "Repository",
                                    url="https://github.com/RYNO-X/RYNO",
                                ),
                                Button.url(
                                    "Support", url="https://t.me/OFFICIALRYNO"
                                ),
                            ]
                        ],
                    )
                    await event.answer(
                        [sur],
                        switch_pm=f"🤖: Assistant of {OWNER_NAME}",
                        switch_pm_param="start",
                    )
                except BaseException:
                    pass

        return wrapper

    return decorator


def asst_cmd(dec):
    def ult(func):
        pattern = "^/" + dec  # todo - handlers for assistant?
        ultroid_bot.asst.add_event_handler(
            func, events.NewMessage(incoming=True, pattern=pattern)
        )

    return ult


def callback(sed):
    def ultr(func):
        data = sed
        ultroid_bot.asst.add_event_handler(
            func, events.callbackquery.CallbackQuery(data=data)
        )

    return ultr


def inline():
    def ultr(func):
        ultroid_bot.asst.add_event_handler(func, events.InlineQuery)

    return ultr


def in_pattern(pat):
    def don(func):
        pattern = pat
        ultroid_bot.asst.add_event_handler(func, events.InlineQuery(pattern=pattern))

    return don


# check for owner
def owner():
    def decorator(function):
        @functools.wraps(function)
        async def wrapper(event):
            if event.sender_id in sed:
                await function(event)
            else:
                try:
                    await event.answer(f"This is {OWNER_NAME}'s bot!!")
                except BaseException:
                    pass

        return wrapper

    return decorator
