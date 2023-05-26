
# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_asstcmd")

import os

from core.remote import rm
from telethon import events, utils
from utilities.tools import create_tl_btn, format_btn, get_msg_button

from . import asst, get_string, mediainfo, udB, ultroid_cmd


@ultroid_cmd(pattern="addcmd( (.*)|$)")
async def ac(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    wt = await e.get_reply_message()
    if not (wt and wrd):
        return await e.eor(get_string("asstcmd_1"), time=5)
    if "/" in wrd:
        wrd = wrd.replace("/", "")
    btn = format_btn(wt.buttons) if wt.buttons else None
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await e.client.download_media(wt.media)
            with rm.get("graph", helper=True, dispose=True) as mod:
                client = mod.get_client()
                variable = client.upload_file(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await e.eor(get_string("com_4"), time=5)
            dl = await e.client.download_media(wt.media)
            with rm.get("graph", helper=True, dispose=True) as mod:
                client = mod.get_client()
                variable = client.upload_file(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        else:
            m = utils.pack_bot_file_id(wt.media)
        if wt.text:
            txt = wt.text
            if not btn:
                txt, btn = get_msg_button(wt.text)
            add_cmd(wrd, txt, m, btn)
        else:
            add_cmd(wrd, None, m, btn)
    else:
        txt = wt.text
        if not btn:
            txt, btn = get_msg_button(wt.text)
        add_cmd(wrd, txt, None, btn)
    asst.add_handler(
        astcmds,
        events.NewMessage(
            func=lambda x: x.text.startswith(
                "/") and x.text[1:] in list(list_cmds())
        ),
    )
    await e.eor(get_string("asstcmd_4").format(wrd))


@ultroid_cmd(pattern="remcmd( (.*)|$)")
async def rc(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    if not wrd:
        return await e.eor(get_string("asstcmd_2"), time=5)
    wrd = wrd.replace("/", "")
    rem_cmd(wrd)
    await e.eor(get_string("asstcmd_3").format(wrd))


@ultroid_cmd(pattern="listcmd$")
async def lscmd(e):
    if list_cmds():
        ok = get_string("asstcmd_6")
        for x in list_cmds():
            ok += f"/{x}" + "\n"
        return await e.eor(ok)
    return await e.eor(get_string("asstcmd_5"))


async def astcmds(e):
    xx = (e.text.replace("/", "")).lower().split()[0]
    if x := cmd_reply(xx):
        msg, media, bt = x
        if bt:
            bt = create_tl_btn(bt)
        await e.reply(msg, file=media, buttons=bt)


if udB.get_key("ASST_CMDS"):
    asst.add_handler(
        astcmds,
        events.NewMessage(
            func=lambda x: x.text.startswith(
                "/") and x.text[1:] in list(list_cmds())
        ),
    )


def get_stuff():
    return udB.get_key("ASST_CMDS") or {}


def add_cmd(cmd, msg, media, button):
    ok = get_stuff()
    ok.update({cmd: {"msg": msg, "media": media, "button": button}})
    return udB.set_key("ASST_CMDS", ok)


def rem_cmd(cmd):
    ok = get_stuff()
    if ok.get(cmd):
        ok.pop(cmd)
        return udB.set_key("ASST_CMDS", ok)


def cmd_reply(cmd):
    ok = get_stuff()
    if ok.get(cmd):
        okk = ok[cmd]
        return okk["msg"], okk["media"], okk["button"] if ok.get(
            "button") else None
    return


def list_cmds():
    ok = get_stuff()
    return ok.keys()
