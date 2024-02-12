# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_fileshare")

import os

from pyUltroid.dB.filestore_db import del_stored, get_stored_msg, list_all_stored_msgs
from pyUltroid.fns.tools import get_file_link

from . import HNDLR, asst, get_string, in_pattern, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="store$")
async def filestoreplg(event):
    msg = await event.get_reply_message()
    if not msg:
        return await event.eor(get_string("fsh_3"), time=10)
    # allow storing both messages and media.
    filehash = await get_file_link(msg)
    link_to_file = f"https://t.me/{asst.me.username}?start={filehash}"
    await event.eor(
        get_string("fsh_2").format(link_to_file),
        link_preview=False,
    )


@ultroid_cmd("delstored ?(.*)")
async def _(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.eor("`Give stored film's link to delete.`", time=5)
    match = match.split("?start=")
    botusername = match[0].split("/")[-1]
    if botusername != asst.me.username:
        return await event.eor(
            "`Message/Media of provided link was not stored by this bot.`", time=5
        )
    msg_id = get_stored_msg(match[1])
    if not msg_id:
        return await event.eor(
            "`Message/Media of provided link was already deleted.`", time=5
        )
    del_stored(match[1])
    await ultroid_bot.delete_messages(udB.get_key("LOG_CHANNEL"), int(msg_id))
    await event.eor("__Deleted__")


@ultroid_cmd("liststored$")
async def liststored(event):
    files = list_all_stored_msgs()
    if not files:
        return await event.eor(get_string("fsh_4"), time=5)
    msg = "**Stored files:**\n"
    for c, i in enumerate(files, start=1):
        msg += f"`{c}`. https://t.me/{asst.me.username}?start={i}\n"
    if len(msg) > 4095:
        with open("liststored.txt", "w") as f:
            f.write(msg.replace("**", "").replace("`", ""))
        await event.reply(get_string("fsh_1"), file="liststored.txt")
        os.remove("liststored.txt")
        return
    await event.eor(msg, link_preview=False)


@in_pattern("filestore", owner=True)
async def file_short(event):
    all_ = list_all_stored_msgs()
    res = []
    if all_:
        LOG_CHA = udB.get_key("LOG_CHANNEL")
        for msg in all_[:50]:
            m_id = get_stored_msg(msg)
            if not m_id:
                continue
            message = await asst.get_messages(LOG_CHA, ids=m_id)
            if not message:
                continue
            if message.media:
                res.append(await event.builder.document(title=msg, file=message.media))
            elif message.text:
                res.append(
                    await event.builder.article(title=message.text, text=message.text)
                )
    if not res:
        title = "You have no stored file :("
        text = f"{title}\n\nRead `{HNDLR}help fileshare` to know how to store."
        return await event.answer([await event.builder.article(title=title, text=text)])
    await event.answer(res, switch_pm="• File Store •", switch_pm_param="start")
