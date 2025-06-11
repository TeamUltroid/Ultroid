# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_fileshare")

import os, secrets

from pyUltroid.fns.tools import get_file_link

from . import HNDLR, asst, get_string, in_pattern, udB, ultroid_bot, ultroid_cmd, LOGS


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


def get_stored():
    return udB.get_key("FILE_STORE") or {}


def store_msg(hash, msg_id):
    all = get_stored()
    all.update({hash: msg_id})
    return udB.set_key("FILE_STORE", all)


def list_all_stored_msgs():
    all = get_stored()
    return list(all.keys())


def get_stored_msg(hash):
    all = get_stored()
    if all.get(hash):
        return all[hash]


def del_stored(hash):
    all = get_stored()
    all.pop(hash)
    return udB.set_key("FILE_STORE", all)


async def get_file_link(msg):
    from .. import udB

    msg_id = await msg.forward_to(udB.get_key("LOG_CHANNEL"))
    await msg_id.reply(
        "**Message has been stored to generate a shareable link. Do not delete it.**"
    )
    msg_id = msg_id.id
    msg_hash = secrets.token_hex(nbytes=8)
    store_msg(msg_hash, msg_id)
    return msg_hash


async def get_stored_file(event, hash):
    from .. import udB, asst

    msg_id = get_stored_msg(hash)
    if not msg_id:
        return
    try:
        msg = await asst.get_messages(udB.get_key("LOG_CHANNEL"), ids=msg_id)
    except Exception as er:
        LOGS.warning(f"FileStore, Error: {er}")
        return
    if not msg_id:
        return await asst.send_message(
            event.chat_id, "__Message was deleted by owner!__", reply_to=event.id
        )
    await asst.send_message(event.chat_id, msg.text, file=msg.media, reply_to=event.id)
