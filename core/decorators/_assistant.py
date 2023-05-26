# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import inspect
import re
from html import escape
from traceback import format_exc, extract_stack
from pathlib import Path

from telethon import Button
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery, NewMessage
from telethon.tl.types import InputWebDocument

from core import LOGS, asst, udB, ultroid_bot
from core.remote import rm
from database._core import InlinePlugin, InlinePaths
from utilities.admins import admin_check

from . import owner_and_sudos

OWNER = ultroid_bot.full_name
CWD = Path.cwd()

MSG = f"""
**Ultroid - UserBot**
➖➖➖➖➖➖➖➖➖➖
**Owner**: [{OWNER}](tg://user?id={ultroid_bot.uid})
**Support**: @TeamUltroid
➖➖➖➖➖➖➖➖➖➖
"""


# decorator for assistant


def asst_cmd(pattern=None, load=None, owner=False, **kwargs):
    """Decorator for assistant's command"""
    inspect.stack()[1].filename.split("/")[-1].replace(".py", "")
    kwargs["forwards"] = False
    if pattern:
        kwargs["pattern"] = re.compile(f"^/{pattern}")

    def ult(func):
        async def handler(event):
            if owner and event.sender_id not in owner_and_sudos():
                return
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(handler, NewMessage(**kwargs))

    return ult


def callback(data=None, from_users=[], admins=False, owner=False, **kwargs):
    """Assistant's callback decorator"""
    if "me" in from_users:
        from_users.remove("me")
        from_users.append(ultroid_bot.me.id)

    def ultr(func):
        async def wrapper(event):
            if admins and not await admin_check(event):
                return
            if from_users and event.sender_id not in from_users:
                return await event.answer("Not for You!", alert=True)
            if owner and event.sender_id not in owner_and_sudos():
                return await event.answer(f"This is {OWNER}'s bot!!")
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(wrapper, CallbackQuery(data=data, **kwargs))

    return ultr


def in_pattern(pattern=None, owner=False, button=None, **kwargs):
    """Assistant's inline decorator."""

    def don(func):
        async def wrapper(event):
            if owner and event.sender_id not in owner_and_sudos():
                IN_BTTS = [
                    [
                        Button.url(
                            "Repository",
                            url="https://github.com/TeamUltroid/Ultroid",
                        ),
                        Button.url("Support", url="https://t.me/UltroidSupportChat"),
                    ]
                ]

                res = [
                    await event.builder.article(
                        title="Ultroid Userbot",
                        url="https://t.me/TeamUltroid",
                        description="(c) TeamUltroid",
                        text=MSG,
                        thumb=InputWebDocument(
                            "https://graph.org/file/dde85d441fa051a0d7d1d.jpg",
                            0,
                            "image/jpeg",
                            [],
                        ),
                        buttons=IN_BTTS,
                    )
                ]
                return await event.answer(
                    res,
                    switch_pm=f"🤖: Assistant of {OWNER}",
                    switch_pm_param="start",
                )
            try:
                await func(event)
            except QueryIdInvalidError:
                pass
            except Exception:
                err = format_exc()
                MakeHtml = f"""
Bot: <a href='https://{asst.me.username}.t.me'>@{asst.me.username}</a>
<h3>Query:</h3><br />
<pre>{escape(pattern or '')}</pre><br />
<h3><b>Traceback:</b></h3><br />
<pre>{escape(err)}</pre>
"""
                try:
                    with rm.get("graph", helper=True, dispose=True) as mod:
                        graphLink = await mod.make_html_telegraph(
                            "Inline Error", MakeHtml
                        )
                except Exception as er:
                    LOGS.exception(f"Error while pasting inline error: {er}")
                    LOGS.exception(err)
                    return
                try:
                    await event.answer(
                        [
                            await event.builder.article(
                                title="Unhandled Exception has Occured!",
                                text=graphLink,
                                buttons=Button.url(
                                    "Report", "https://t.me/UltroidSupportChat"
                                ),
                            )
                        ]
                    )
                except QueryIdInvalidError:
                    msg = f"<b><a href={graphLink}>[An error occurred]</a></b>"
                    await asst.send_message(udB.get_config("LOG_CHANNEL"), msg)
                except Exception as er:
                    LOGS.exception(err)
                    LOGS.exception(er)

        asst.add_event_handler(wrapper, InlineQuery(pattern=pattern, **kwargs))

    if button:
        InlinePlugin.update(button)
        if kwargs.get("add_help") is not False:
            _path = extract_stack(limit=2)[0].filename[:-3][len(str(CWD)) + 1 :]
            InlinePaths.append(_path.replace("/", "."))
    return don
