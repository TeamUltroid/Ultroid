# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}setgpic <reply to Photo><chat username>`
    Set Profile photo of Group.

• `{i}delgpic <chat username -optional>`
    Delete Profile photo of Group.

• `{i}unbanall`
    Unban all Members of a group.

• `{i}rmusers`
    Remove users specifically.
"""
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import (
    ChannelParticipantsKicked,
    ChatBannedRights,
    UserStatusEmpty,
    UserStatusLastMonth,
    UserStatusLastWeek,
    UserStatusOffline,
    UserStatusOnline,
    UserStatusRecently,
)

from . import *


@ultroid_cmd(
    pattern="setgpic ?(.*)",
    groups_only=True,
    admins_only=True,
    type=["official", "manager"],
)
async def _(ult):
    if not ult.is_reply:
        return await eor(ult, "`Reply to a Media..`", time=5)
    match = ult.pattern_match.group(1)
    if not ult.client._bot and match:
        try:
            chat = await get_user_id(match)
        except Exception as ok:
            return await eor(ult, str(ok))
    else:
        chat = ult.chat_id
    reply_message = await ult.get_reply_message()
    if reply_message.media:
        replfile = await reply_message.download_media()
    else:
        return await eor(ult, "Reply to a Photo or Video..")
    file = await ult.client.upload_file(replfile)
    mediain = mediainfo(reply_message.media)
    try:
        if "pic" not in mediain:
            file = types.InputChatUploadedPhoto(video=file)
        await ult.client(EditPhotoRequest(chat, file))
        await eor(ult, "`Group Photo has Successfully Changed !`", time=5)
    except Exception as ex:
        await eor(ult, "Error occured.\n`{}`".format(str(ex)), time=5)
    os.remove(replfile)


@ultroid_cmd(
    pattern="delgpic ?(.*)",
    groups_only=True,
    admins_only=True,
    type=["official", "manager"],
)
async def _(ult):
    match = ult.pattern_match.group(1)
    chat = ult.chat_id
    if not ult.client._bot and match:
        chat = match
    try:
        await ult.client(EditPhotoRequest(chat, types.InputChatPhotoEmpty()))
        text = "`Removed Chat Photo..`"
    except Exception as E:
        text = str(E)
    return await eor(ult, text, time=5)


@ultroid_cmd(
    pattern="unbanall$",
    groups_only=True,
)
async def _(event):
    xx = await eor(event, "Searching Participant Lists.")
    p = 0
    title = (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id,
        filter=ChannelParticipantsKicked,
        aggressive=True,
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except BaseException:
            pass
    await eor(xx, f"{title}: {p} unbanned", time=5)


@ultroid_cmd(
    pattern="rmusers ?(.*)",
    groups_only=True,
    admins_only=True,
    fullsudo=True,
)
async def _(event):
    xx = await eor(event, "Searching Participant Lists.")
    input_str = event.pattern_match.group(1)
    p, b, c, d, m, n, y, w, o, q, r = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    async for i in event.client.iter_participants(event.chat_id):
        p += 1
        if isinstance(i.status, UserStatusEmpty):
            y += 1
            if "empty" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    y -= 1
                except BaseException:
                    pass
        if isinstance(i.status, UserStatusLastMonth):
            m += 1
            if "month" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    m -= 1
                except BaseException:
                    pass
        if isinstance(i.status, UserStatusLastWeek):
            w += 1
            if "week" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    w -= 1
                except BaseException:
                    pass
        if isinstance(i.status, UserStatusOffline):
            o += 1
            if "offline" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    o -= 1
                except BaseException:
                    pass
        if isinstance(i.status, UserStatusOnline):
            q += 1
            if "online" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    q -= 1
                except BaseException:
                    pass
        if isinstance(i.status, UserStatusRecently):
            r += 1
            if "recently" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    r -= 1
                except BaseException:
                    pass
        if i.bot:
            b += 1
            if "bot" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    b -= 1
                except BaseException:
                    pass
        elif i.deleted:
            d += 1
            if "deleted" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    d -= 1
                except BaseException:
                    pass
        elif i.status is None:
            n += 1
            if "none" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                    n -= 1
                except BaseException:
                    pass
    if input_str:
        required_string = f"**>> Kicked** `{c} / {p}` **users**\n\n"
    else:
        required_string = f"**>> Total** `{p}` **users**\n\n"
    required_string += f"  `{HNDLR}rmusers deleted`  **••**  `{d}`\n"
    required_string += f"  `{HNDLR}rmusers empty`  **••**  `{y}`\n"
    required_string += f"  `{HNDLR}rmusers month`  **••**  `{m}`\n"
    required_string += f"  `{HNDLR}rmusers week`  **••**  `{w}`\n"
    required_string += f"  `{HNDLR}rmusers offline`  **••**  `{o}`\n"
    required_string += f"  `{HNDLR}rmusers online`  **••**  `{q}`\n"
    required_string += f"  `{HNDLR}rmusers recently`  **••**  `{r}`\n"
    required_string += f"  `{HNDLR}rmusers bot`  **••**  `{b}`\n"
    required_string += f"  `{HNDLR}rmusers none`  **••**  `{n}`"
    await eor(xx, required_string)
