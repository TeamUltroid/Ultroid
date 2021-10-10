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

from pyUltroid.dB.asstcmd_db import *
from pyUltroid.functions.tools import create_tl_btn, format_btn, get_msg_button
from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id

from . import asst_cmd, eor, get_string, mediainfo, ultroid_cmd


@ultroid_cmd(pattern="addcmd ?(.*)")
async def ac(e):
    wrd = (e.pattern_match.group(1)).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await eor(e, get_string("asstcmd_1"), time=5)
    if "/" in wrd:
        wrd = wrd.replace("/", "")
    btn = format_btn(wt.buttons) if wt.buttons else None
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await e.client.download_media(wt.media)
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await eor(e, get_string("com_4"), time=5)
            dl = await e.client.download_media(wt.media)
            variable = uf(dl)
            os.remove(dl)
            m = "https://telegra.ph" + variable[0]
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            txt = wt.text
            if not btn:
                txt, btn = get_msg_button(wt.text)
            add_cmd(wrd, txt, m, btn)
        else:
            add_cmd(wrd, None, m)
    else:
        txt = wt.text
        if not btn:
            txt, btn = get_msg_button(wt.text)
        add_cmd(wrd, txt, None, btn)
    await eor(e, get_string("asstcmd_4").format(wrd))


@ultroid_cmd(pattern="remcmd ?(.*)")
async def rc(e):
    wrd = (e.pattern_match.group(1)).lower()
    if not wrd:
        return await eor(e, get_string("asstcmd_2"), time=5)
    wrd = wrd.replace("/", "")
    rem_cmd(wrd)
    await eor(e, get_string("asstcmd_3").format(wrd))


@ultroid_cmd(pattern="listcmd$")
async def lscmd(e):
    if list_cmds():
        ok = get_string("asstcmd_6")
        for x in list_cmds():
            ok += "/" + x + "\n"
        return await eor(e, ok)
    return await eor(e, get_string("asstcmd_5"))


@asst_cmd(func=lambda x: x.text.startswith("/") and x.text[1:] in list(list_cmds()))
async def ascmds(e):
    xx = (e.text.replace("/", "")).lower().split()[0]
    if cmd_reply(xx):
        msg, media, bt = cmd_reply(xx)
        if bt:
            bt = create_tl_btn(bt)
        await e.reply(msg, file=media, buttons=bt)
