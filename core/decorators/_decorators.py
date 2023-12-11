# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import re
import sys
import traceback
from functools import wraps
from html import escape
from time import gmtime, strftime
from traceback import format_exc

from telethon import Button
from telethon import __version__ as telever
from telethon import events
from telethon.errors.common import AlreadyInConversationError
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    BotInlineDisabledError,
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserIsBotError,
)
from telethon.events import MessageEdited, NewMessage
from telethon.tl.custom import Message
from telethon.utils import get_display_name

from core import *
from core.version import version as ult_ver
from database._core import LIST

# from core import _ignore_eval
from database.helpers import DEVLIST
from localization import get_string
from utilities.admins import admin_check
from utilities.helper import bash, check_update
from utilities.helper import time_formatter as tf

from . import fullsudos, owner_and_sudos
from . import should_allow_sudos as allow_sudo
from ._wrappers import eod

MANAGER = udB.get_key("MANAGER")
TAKE_EDITS = udB.get_key("TAKE_EDITS")
black_list_chats = udB.get_key("BLACKLIST_CHATS")


_ignore_eval = []


def compile_pattern(data, hndlr):
    if data.startswith("^"):
        data = data[1:]
    if data.startswith("."):
        data = data[1:]
    if hndlr in [" ", "NO_HNDLR"]:
        # No Hndlr Feature
        return re.compile(f"^{data}")
    return re.compile("\\" + hndlr + data)


def ultroid_cmd(pattern=None, manager=False, asst=asst, **kwargs):
    reply_req = kwargs.get("replied", False)
    owner_only = kwargs.get("owner_only", False)
    groups_only = kwargs.get("groups_only", False)
    admins_only = kwargs.get("admins_only", False)
    fullsudo = kwargs.get("fullsudo", False)
    only_devs = kwargs.get("only_devs", False)
    #    cmd_key = kwargs.get("cmds_key")
    func = kwargs.get("func", lambda e: not e.via_bot_id)

    def decor(dec):
        @wraps(dec)
        async def wrapp(ult: Message):
            if not ult.out:
                if owner_only:
                    return
                if ult.sender_id not in owner_and_sudos():
                    return
                if ult.sender_id in _ignore_eval:
                    return await eod(
                        ult,
                        get_string("py_d1"),
                    )
                if fullsudo and ult.sender_id not in fullsudos():
                    return await eod(ult, get_string("py_d2"), time=15)
            if reply_req and not (await ult.get_reply_message()):
                return await eod(ult, "Reply to a message.")
            chat = ult.chat
            if (
                hasattr(chat, "title")
                and "#noub" in chat.title.lower()
                and not chat.admin_rights
                and not chat.creator
                and ult.sender_id not in DEVLIST
            ):
                return
            if ult.is_private and (groups_only or admins_only):
                return await eod(ult, get_string("py_d3"))
            elif admins_only and not chat.admin_rights and not chat.creator:
                return await eod(ult, get_string("py_d5"))
            if only_devs and not udB.get_key("I_DEV"):
                return await eod(
                    ult,
                    get_string("py_d4").format(HNDLR),
                    time=10,
                )
            try:
                await dec(ult)
            except FloodWaitError as fwerr:
                await asst.send_message(
                    udB.get_config("LOG_CHANNEL"),
                    f"`FloodWaitError:\n{str(fwerr)}\n\nSleeping for {tf((fwerr.seconds + 10)*1000)}`",
                )
                time.sleep(fwerr.seconds + 10)
                await ultroid_bot.connect()
                await asst.send_message(
                    udB.get_config("LOG_CHANNEL"),
                    "`Bot is working again`",
                )
                return
            except ChatSendInlineForbiddenError:
                return await eod(ult, "`Inline Locked In This Chat.`")
            except (ChatSendMediaForbiddenError, ChatSendStickersForbiddenError):
                return await eod(ult, get_string("py_d8"))
            except (BotMethodInvalidError, UserIsBotError):
                return await eod(ult, get_string("py_d6"))
            except AlreadyInConversationError:
                return await eod(
                    ult,
                    get_string("py_d7"),
                )
            except (BotInlineDisabledError, ConnectionError) as er:
                return await eod(ult, f"`{er}`")
            except (
                MessageIdInvalidError,
                MessageNotModifiedError,
                MessageDeleteForbiddenError,
            ) as er:
                LOGS.exception(er)
            except AuthKeyDuplicatedError as er:
                LOGS.exception(er)
                await asst.send_message(
                    udB.get_config("LOG_CHANNEL"),
                    "Session String expired, create new session from 👇",
                    buttons=[
                        Button.url("Bot", "t.me/SessionGeneratorBot?start="),
                        Button.url(
                            "Repl",
                            "https://replit.com/@TheUltroid/UltroidStringSession",
                        ),
                    ],
                )
                sys.exit()
            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except Exception:
                date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                naam = get_display_name(chat)
                chat_username = getattr(ult.chat, "username", None)
                sender = await ult.get_sender()
                replied = await ult.get_reply_message()
                stdout, stderr = await bash('git log --pretty=format:"%an: %s" -5')
                result = stdout + (stderr or "")
                result = "".join(
                    [f"<li>{escape(line)}</li>" for line in result.split("\n")]
                )
                MakeHtml = f"""
<img src='https://graph.org/file/957d8142c369e1d31547f.jpg'/>
<a href='https://UltroidSupportChat.t.me'>Report Error</a>
<br /><br />
<ul>
<li>Version: {ult_ver} - &nbsp;[{HOSTED_ON}]</li>
{'<li>Update Available: <i>True</i></li>' if check_update() else ''}
<li>Telethon: {telever}</li>
<li>Date: {date}</li>
<li>Group: {f'<a href="https://t.me/{chat_username}">@{chat_username}</a>' if chat_username else f'<code>{ult.chat_id}</code>'} [{escape(naam)}]</li>
<li>Sender: <a href='{sender.username or ""}'>{escape(get_display_name(sender))}</a>&nbsp;<code>{ult.sender_id}</code></li>
<li>Replied: &nbsp;{f'<a href="{replied.message_link}">This message</a>' if replied else '<code>False</code>'}</li>
</ul><br />
<h4>Trigger:</h4>
<pre>{escape(ult.text)}</pre>
<br />
<h4>Traceback:</h4>
<pre>{escape(format_exc())}</pre>
<br />
<h4>Last 5 Commits: </h4>
<ul>{result}</ul>
"""
                try:
                    ultr = getattr(ult, "_eor", None) or ult
                    if ultr.out:
                        await ultr.edit(get_string("py_d9"))
                    with rm.get("graph", helper=True, dispose=True) as mod:
                        graphLink = await mod.make_html_telegraph(
                            "Ultroid Error", MakeHtml
                        )
                    msg = f"<a href='tg://user?id={ultroid_bot.me.id}'>\xad</a><b><a href={graphLink}>[An error occurred]</a></b>"

                    Msg = await asst.send_message(
                        udB.get_config("LOG_CHANNEL"),
                        msg,
                        parse_mode="html",
                    )
                    await ultr.edit(
                        f"<b><a href={Msg.message_link}>[An error occurred]</a></b>",
                        parse_mode="html",
                    )
                except Exception as er:
                    LOGS.error(f"Error while pasting exception on graph: {er}")
                    LOGS.exception(er)

        cmd = None
        chats = None
        blacklist_chats = bool(black_list_chats)
        if black_list_chats:
            chats = black_list_chats

        _add_new = allow_sudo() and HNDLR != SUDO_HNDLR
        if _add_new:
            if pattern:
                cmd = compile_pattern(pattern, SUDO_HNDLR)
            ultroid_bot.add_event_handler(
                wrapp,
                NewMessage(
                    pattern=cmd,
                    incoming=True,
                    forwards=False,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if pattern:
            cmd = compile_pattern(pattern, HNDLR)
        ultroid_bot.add_event_handler(
            wrapp,
            NewMessage(
                outgoing=True if _add_new else None,
                pattern=cmd,
                forwards=False,
                func=func,
                chats=chats,
                blacklist_chats=blacklist_chats,
            ),
        )
        if TAKE_EDITS:

            def func_(x):
                return (
                    (x.out or x.sender_id == ultroid_bot.me.id)
                    and not x.via_bot_id
                    and not (x.is_channel and x.chat.broadcast)
                )

            ultroid_bot.add_handler(
                wrapp,
                MessageEdited(
                    pattern=cmd,
                    forwards=False,
                    func=func_,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if manager and MANAGER:
            allow_all = kwargs.get("allow_all", False)
            allow_pm = kwargs.get("allow_pm", False)
            require = kwargs.get("require")

            async def manager_cmd(ult):
                if not allow_all and not (await admin_check(ult, require=require)):
                    return
                if not allow_pm and ult.is_private:
                    return
                try:
                    await dec(ult)
                except Exception as er:
                    if chat := udB.get_key("MANAGER_LOG"):
                        text = f"**#MANAGER_LOG\n\nChat:** `{get_display_name(ult.chat)}` `{ult.chat_id}`"
                        text += f"\n**Replied :** `{ult.is_reply}`\n**Command :** {ult.text}\n\n**Error :** `{er}`"
                        try:
                            return await asst.send_message(
                                chat, text, link_preview=False
                            )
                        except Exception as err:
                            LOGS.exception(err)
                    LOGS.info(f"• MANAGER [{ult.chat_id}]:")
                    LOGS.exception(er)

            if pattern:
                cmd = compile_pattern(pattern, "/")
                _event = NewMessage(
                    pattern=cmd,
                    forwards=False,
                    incoming=True,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                )
            _event.manager = True
            asst.add_handler(manager_cmd, _event)
        if DUAL_MODE and not (manager and DUAL_HNDLR == "/"):
            if pattern:
                cmd = compile_pattern(pattern, DUAL_HNDLR)
            asst.add_handler(
                wrapp,
                NewMessage(
                    pattern=cmd,
                    incoming=True,
                    forwards=False,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )

        if pattern:
            file = os.path.basename(traceback.extract_stack(limit=2)[0].filename)[:-3]
            if LIST.get(file) is None:
                LIST[file] = []
            LIST[file].append(pattern)
        return wrapp

    return decor
