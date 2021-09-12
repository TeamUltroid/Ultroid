# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}alive` | `{i}ialive`
    Check if your bot is working.

• `{i}ping`
    Check Ultroid's response time.

• `{i}cmds`
    View all plugin names.

• `{i}restart`
    To restart your bot.

• `{i}logs (sys)`
    Get the full terminal logs.

• `{i}logs heroku`
   Get the latest 100 lines of heroku logs.

• `{i}shutdown`
    Turn off your bot.
"""
import os
import sys
import time
from datetime import datetime as dt
from platform import python_version as pyver

from git import Repo
from pyUltroid.version import __version__ as UltVer
from telethon import __version__
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError
from telethon.utils import resolve_bot_file_id

from . import *

# Will move to strings
alive_txt = """
The Ultroid Userbot

  ◍ Version - {}
  ◍ Py-Ultroid - {}
  ◍ Telethon - {}
"""


@callback("alive")
async def alive(event):
    text = alive_txt.format(ultroid_version, UltVer, __version__)
    await event.answer(text, alert=True)


@ultroid_cmd(
    pattern="alive$",
)
async def lol(ult):
    pic = udB.get("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get("ALIVE_TEXT") or "Hey,  I am alive."
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    als = (get_string("alive_1")).format(
        header,
        OWNER_NAME,
        ultroid_version,
        UltVer,
        uptime,
        pyver(),
        __version__,
        kk,
    )
    if pic is None:
        await eor(ult, als)
    elif "telegra" in pic:
        try:
            await ult.reply(als, file=pic, link_preview=False)
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als, link_preview=False)
    else:
        try:
            await ult.reply(file=pic)
            await ult.reply(als, link_preview=False)
            await ult.delete()
        except ChatSendMediaForbiddenError:
            await eor(ult, als, link_preview=False)


@ultroid_cmd(
    pattern="ialive$",
)
async def is_on(ult):
    if not ult.client._bot:
        await ult.delete()
        try:
            res = await ult.client.inline_query(asst.me.username, "alive")
            return await res[0].click(ult.chat_id)
        except Exception as er:
            LOGS.info(er)
        return
    pic = udB.get("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get("ALIVE_TEXT") or "Hey,  I am alive."
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    als = (get_string("alive_1")).format(
        header,
        OWNER_NAME,
        ultroid_version,
        UltVer,
        uptime,
        pyver(),
        __version__,
        kk,
    )
    buttons = [
        Button.inline("Stats", "alive"),
        [
            Button.url("Repo", "https://github.com/TeamUltroid/Ultroid"),
            Button.url("Support", "t.me/UltroidSupport"),
        ],
    ]
    await ult.client.send_message(ult.chat_id, als, file=pic, buttons=buttons)


@ultroid_cmd(
    pattern="ping$",
    chats=[],
)
async def _(event):
    start = dt.now()
    x = await eor(event, "`Pong !`")
    end = dt.now()
    ms = (end - start).microseconds / 1000
    uptime = time_formatter((time.time() - start_time) * 1000)
    await x.edit(get_string("ping").format(ms, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event)


heroku_api = Var.HEROKU_API


@ultroid_cmd(
    pattern="restart$",
    fullsudo=True,
)
async def restartbt(ult):
    ok = await eor(ult, "• `Restarting...`")
    call_back()
    if heroku_api:
        return await restart(ok)
    await bash("git pull && pip3 install -r requirements.txt")
    os.execl(sys.executable, sys.executable, "-m", "pyUltroid")


@ultroid_cmd(
    pattern="shutdown$",
    fullsudo=True,
)
async def shutdownbot(ult):
    await shutdown(ult)


@ultroid_cmd(
    pattern="logs ?(|heroku|sys)",
    chats=[],
)
async def _(event):
    opt = event.pattern_match.group(1)
    if opt == "heroku":
        await heroku_logs(event)
    else:
        await def_logs(event)


@in_pattern("alive")
@in_owner
async def inline_alive(ult):
    pic = udB.get("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get("ALIVE_TEXT") or "Hey,  I am alive."
    y = Repo().active_branch
    xx = Repo().remotes[0].config_reader.get("url")
    rep = xx.replace(".git", f"/tree/{y}")
    kk = f" `[{y}]({rep})` "
    als = (get_string("alive_1")).format(
        header,
        OWNER_NAME,
        ultroid_version,
        UltVer,
        uptime,
        pyver(),
        __version__,
        kk,
    )
    buttons = [
        [
            Button.url("Repo", "https://github.com/TeamUltroid/Ultroid"),
            Button.url("Support", "t.me/UltroidSupport"),
        ]
    ]
    builder = ult.builder
    if pic:
        try:
            if ".jpg" in pic:
                results = [await builder.photo(pic, text=als, buttons=buttons)]
            else:
                _pic = resolve_bot_file_id(pic)
                if _pic:
                    pic = _pic
                    buttons.insert(0, [Button.inline("Stats", data="alive")])
                results = [
                    await builder.document(
                        pic,
                        title="Inline Alive",
                        description="@TheUltroid",
                        buttons=buttons,
                    )
                ]
            return await ult.answer(results)
        except BaseException as er:
            LOGS.info(er)
    result = [
        await builder.article("Alive", text=als, link_preview=False, buttons=buttons)
    ]
    await ult.answer(result)
