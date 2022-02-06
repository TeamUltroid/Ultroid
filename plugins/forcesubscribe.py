# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}fsub <chat username><id>`
    Enable ForceSub in Used Chat !

• `{i}checkfsub`
    Check/Get Active ForceSub Setting of Used Chat.

• `{i}remfsub`
    Remove ForceSub from Used Chat !

    Note - You Need to be Admin in Both Channel/Chats
        in order to Use ForceSubscribe.
"""

import re

from pyUltroid.dB.forcesub_db import add_forcesub, get_forcesetting, rem_forcesub
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, UserNotParticipantError
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import (
    Channel,
    ChannelParticipantBanned,
    ChannelParticipantLeft,
    User,
)

from . import (
    LOGS,
    asst,
    callback,
    events,
    get_string,
    in_pattern,
    inline_mention,
    udB,
    ultroid_bot,
    ultroid_cmd,
)

CACHE = {}


@ultroid_cmd(pattern="fsub( (.*)|$)", admins_only=True, groups_only=True)
async def addfor(e):
    match = e.pattern_match.group(1).strip()
    if not match:
        return await e.eor(get_string("fsub_1"), time=5)
    try:
        match = await e.client.parse_id(match)
    except BaseException:
        return await e.eor(get_string("fsub_2"), time=5)
    add_forcesub(e.chat_id, match)
    await e.eor("Added ForceSub in This Chat !")
    ultroid_bot.add_handler(force_sub, events.NewMessage(incoming=True))


@ultroid_cmd(pattern="remfsub$")
async def remor(e):
    res = rem_forcesub(e.chat_id)
    if not res:
        return await e.eor(get_string("fsub_3"), time=5)
    await e.eor("Removed ForceSub...")


@ultroid_cmd(pattern="checkfsub$")
async def getfsr(e):
    res = get_forcesetting(e.chat_id)
    if not res:
        return await e.eor("ForceSub is Not Active In This Chat !", time=5)
    cha = await e.client.get_entity(int(res))
    await e.eor(f"**ForceSub Status** : `Active`\n- **{cha.title}** `({res})`")


@in_pattern("fsub( (.*)|$)", owner=True)
async def fcall(e):
    match = e.pattern_match.group(1).strip()
    spli = match.split("_")
    user = await ultroid_bot.get_entity(int(spli[0]))
    cl = await ultroid_bot.get_entity(int(spli[1]))
    text = f"Hi [{inline_mention(user)}), You Need to Join"
    text += f" {cl.title} in order to Chat in this Group."
    if not cl.username:
        el = (await ultroid_bot(ExportChatInviteRequest(cl))).link
    else:
        el = "https://t.me/" + cl.username
    res = [
        await e.builder.article(
            title="forcesub",
            text=text,
            buttons=[
                [Button.url(text=get_string("fsub_4"), url=el)],
                [Button.inline(get_string("fsub_5"), data=f"unm_{match}")],
            ],
        )
    ]
    await e.answer(res)


@callback(re.compile("unm_(.*)"))
async def diesoon(e):
    match = (e.data_match.group(1)).decode("UTF-8")
    spli = match.split("_")
    if e.sender_id != int(spli[0]):
        return await e.answer(get_string("fsub_7"), alert=True)
    try:
        values = await ultroid_bot(GetParticipantRequest(int(spli[1]), int(spli[0])))
        if isinstance(values.participant, ChannelParticipantLeft) or (
            isinstance(values.participant, ChannelParticipantBanned) and values.left
        ):
            raise UserNotParticipantError("")
    except UserNotParticipantError:
        return await e.answer(
            "Please Join That Channel !\nThen Click This Button !", alert=True
        )
    await ultroid_bot.edit_permissions(
        e.chat_id, int(spli[0]), send_messages=True, until_date=None
    )
    await e.edit(get_string("fsub_8"))


async def force_sub(ult):
    if not udB.get_key("FORCESUB"):
        return

    user = await ult.get_sender()
    joinchat = get_forcesetting(ult.chat_id)
    if (not joinchat) or (isinstance(user, User) and user.bot):
        return
    if CACHE.get(ult.chat_id):
        if CACHE[ult.chat_id].get(user.id):
            CACHE[ult.chat_id].update({user.id: CACHE[ult.chat_id][user.id] + 1})
        else:
            CACHE[ult.chat_id].update({user.id: 1})
    else:
        CACHE.update({ult.chat_id: {user.id: 1}})
    count = CACHE[ult.chat_id][user.id]
    if count == 11:
        CACHE[ult.chat_id][user.id].update(1)
        return
    if count in range(2, 11):
        return
    try:
        await ultroid_bot.get_permissions(int(joinchat), user.id)
        return
    except UserNotParticipantError:
        pass
    if isinstance(user, Channel):
        try:
            await ultroid_bot.edit_permissions(
                ult.chat_id, user.id, view_messages=False
            )
            return
        except BaseException as er:
            LOGS.exception(er)
    try:
        await ultroid_bot.edit_permissions(ult.chat_id, user.id, send_messages=False)
    except ChatAdminRequiredError:
        return
    except Exception as e:
        LOGS.info(e)
    res = await ultroid_bot.inline_query(asst.me.username, f"fsub {user.id}_{joinchat}")
    await res[0].click(ult.chat_id, reply_to=ult.id)


if udB.get_key("FORCESUB"):
    ultroid_bot.add_handler(force_sub, events.NewMessage(incoming=True))
