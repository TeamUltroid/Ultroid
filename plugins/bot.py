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

• `{i}update`
    See changelogs if any update is available.

• `{i}cmds`
    View all plugin names.

• `{i}restart`
    To restart your bot.

• `{i}logs (sys)`
    Get the full terminal logs.
• `{i}logs carbon`
    Get the carbonized sys logs.
• `{i}logs heroku`
   Get the latest 100 lines of heroku logs.

• `{i}shutdown`
    Turn off your bot.
"""
import os
import sys
import time
from platform import python_version as pyver
from random import choice

from git import Repo
from pyUltroid.version import __version__ as UltVer
from telethon import __version__
from telethon.errors.rpcerrorlist import ChatSendMediaForbiddenError
from telethon.utils import resolve_bot_file_id

from . import (
    ATRA_COL,
    INLINE_PIC,
    LOGS,
    OWNER_NAME,
    ULTROID_IMAGES,
    Button,
    Carbon,
    Telegraph,
    Var,
    allcmds,
    asst,
    bash,
    call_back,
    callback,
    def_logs,
    eor,
    get_string,
    heroku_logs,
    in_pattern,
    restart,
    shutdown,
    start_time,
    time_formatter,
    udB,
    ultroid_cmd,
    ultroid_version,
    updater
)

ULTPIC = INLINE_PIC or choice(ULTROID_IMAGES)

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
    pic = udB.get_key("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
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
            await res[0].click(ult.chat_id)
        except Exception as er:
            LOGS.info(er)
        return
    pic = udB.get_key("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
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
        [Button.inline(get_string("bot_2"), "alive")],
        [
            Button.url(get_string("bot_3"), "https://github.com/TeamUltroid/Ultroid"),
            Button.url(get_string("bot_4"), "t.me/UltroidSupport"),
        ],
    ]
    await ult.client.send_message(
        ult.chat_id, als, file=pic, buttons=buttons, link_preview=False
    )


@ultroid_cmd(pattern="ping$", chats=[], type=["official", "assistant"])
async def _(event):
    start = time.time()
    x = await eor(event, "Pong !")
    end = round((time.time() - start) * 1000)
    uptime = time_formatter((time.time() - start_time) * 1000)
    await x.edit(get_string("ping").format(end, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event, Telegraph)


heroku_api = Var.HEROKU_API


@ultroid_cmd(
    pattern="restart$",
    fullsudo=True,
)
async def restartbt(ult):
    ok = await eor(ult, get_string("bot_5"))
    call_back()
    if heroku_api:
        return await restart(ok)
    await bash("git pull && pip3 install -r requirements.txt")
    if len(sys.argv) > 1:
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")


@ultroid_cmd(
    pattern="shutdown$",
    fullsudo=True,
)
async def shutdownbot(ult):
    await shutdown(ult)


@ultroid_cmd(
    pattern="logs ?(.*)",
    chats=[],
)
async def _(event):
    opt = event.pattern_match.group(1)
    file = "ultroid.log"
    if len(sys.argv) > 1:
        file = f"ultroid{sys.argv[-1]}.log"
    if opt == "heroku":
        await heroku_logs(event)
    elif opt == "carbon" and Carbon:
        event = await eor(event, get_string("com_1"))
        code = open(file, "r").read()[-2500:]
        file = await Carbon(
            file_name="ultroid-logs",
            code=code,
            backgroundColor=choice(ATRA_COL),
        )
        await event.reply("**Ultroid Logs.**", file=file)
    elif opt == "open":
        file = open("ultroid.log", "r").read()[-4000:]
        return await eor(event, f"`{file}`")
    else:
        await def_logs(event, file)
    await event.delete()


@in_pattern("alive", owner=True)
async def inline_alive(ult):
    pic = udB.get_key("ALIVE_PIC")
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
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
            Button.url(get_string("bot_3"), "https://github.com/TeamUltroid/Ultroid"),
            Button.url(get_string("bot_4"), "t.me/UltroidSupport"),
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
                    buttons.insert(
                        0, [Button.inline(get_string("bot_2"), data="alive")]
                    )
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


@ultroid_cmd(pattern="update ?(.*)")
async def _(e):
    xx = await eor(e, get_string("upd_1"))
    if e.pattern_match.group(1) and (
        "fast" in e.pattern_match.group(1) or "soft" in e.pattern_match.group(1)
    ):
        await bash("git pull -f && pip3 install -r requirements.txt")
        call_back()
        await xx.edit(get_string("upd_7"))
        os.execl(sys.executable, "python3", "-m", "pyUltroid")
        return
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await asst.send_file(
            udB.get_key("LOG_CHANNEL"),
            ULTPIC,
            caption="• **Update Available** •",
            force_document=False,
            buttons=Button.inline("Changelogs", data="changes"),
        )
        Link = x.message_link
        await xx.edit(
            f'<strong><a href="{Link}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await xx.edit(
            f'<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong><a href="https://github.com/TeamUltroid/Ultroid/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail", owner=True)
async def updava(event):
    await event.delete()
    await asst.send_file(
        udB.get_key("LOG_CHANNEL"),
        ULTPIC,
        caption="• **Update Available** •",
        force_document=False,
        buttons=Button.inline("Changelogs", data="changes"),
    )
