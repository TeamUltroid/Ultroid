# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

•`{i}addcmd <new cmd> <reply>`
   It will set new cmd for your assistant bot with that reply message.

•`{i}remcmd <cmd name>`
   It will remove your cmd.

•`{i}listcmd`
   To Get list of all your custom cmd.
"""
import os

from pyUltroid.functions.asstcmd_db import *
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import *


@ultroid_cmd(pattern="addcmd ?(.*)")
async def ac(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await eod(e, "`Use this Command with Reply and word to use a command.`")
    if "/" in wrd:
        wrd = wrd.replace("/", "")
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await e.client.download_media(wt.media)
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eod(x, "`Unsupported Media`")
            else:
                dl = await e.client.download_media(wt.media)
                variable = uf(dl)
                os.remove(dl)
                m = "https://telegra.ph" + variable[0]
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            add_cmd(wrd, wt.text, m)
        else:
            add_cmd(wrd, None, m)
    else:
        add_cmd(wrd, wt.text, None)
    await eor(e, f"Done Command : `/{wrd}` saved.")


@ultroid_cmd(pattern="remcmd ?(.*)")
async def rc(e):
    wrd = (e.pattern_match.group(1)).lower()
    if not wrd:
        return await eod(e, "`Give me the command which you want to remove.`")
    if wrd.startswith("/"):
        wrd = wrd.replace("/", "")
    rem_cmd(wrd)
    await eor(e, f"Done Command: `/{wrd}` Removed.")


@ultroid_cmd(pattern="listcmd$")
async def lscmd(e):
    if list_cmds():
        ok = "**ALL ASSISTANT CMDS**\n\n"
        for x in list_cmds():
            ok += "/" + x + "\n"
        return await eor(e, ok)
    return await eor(e, "No commands found")


@asst.on(events.NewMessage())
async def ascmds(e):
    xx = e.text
    if not xx.startswith("/"):
        return
    xx = (xx.replace("/", "")).lower()
    if " " in xx:
        xx = xx.split(" ")[0]
    if cmd_reply(xx):
        msg, media = cmd_reply(xx)
        await e.reply(msg, file=media)
