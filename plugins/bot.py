# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}alive`
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
import time
from datetime import datetime as dt
from platform import python_version as pyver

from git import Repo
from pyUltroid.version import __version__ as UltVer
from telethon import __version__, events
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError

from . import *


@ultroid_cmd(
    pattern="alive$",
)
async def lol(ult):
    pic = udB.get("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get("ALIVE_TEXT") if udB.get("ALIVE_TEXT") else "Hey,  I am alive."
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
        return await eor(ult, als)
    elif pic is not None and "telegra" in pic:
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


@ultroid_bot.on(events.NewMessage(pattern=f"\\{HNDLR}ping$"))
async def _(event):
    if event.fwd_from:
        return
    if not event.out and not is_sudo(event.sender_id):
        return
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


@ultroid_cmd(
    pattern="restart$",
)
async def restartbt(ult):
    ok = await eor(ult, "`Restarting...`")
    if Var.HEROKU_API:
        await restart(ok)
    else:
        await bash("pkill python3 && python3 -m pyUltroid")


@ultroid_cmd(pattern="shutdown$")
async def shutdownbot(ult):
    if not ult.out and not is_fullsudo(ult.sender_id):
        return await eod(ult, "`This Command Is Sudo Restricted.`")
    await shutdown(ult)


@ultroid_bot.on(events.NewMessage(pattern=f"\\{HNDLR}logs ?(.*)"))
@asst.on(events.NewMessage(pattern="^/{HNDLR}logs ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    if not event.out and not is_sudo(event.sender_id):
        return
    try:
        opt = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await def_logs(event)
    if opt == "heroku":
        await heroku_logs(event)
    else:
        await def_logs(event)
    if event.out:
        await event.delete()
