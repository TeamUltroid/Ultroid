# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

from pyUltroid.functions.forcesub_db import *
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, UserNotParticipantError
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import ExportChatInviteRequest

from . import *

CACHE = {}


@ultroid_cmd(pattern="fsub ?(.*)", admins_only=True, groups_only=True)
async def addfor(e):
    match = e.pattern_match.group(1)
    if not match:
        return await eor(e, "Give Channel where you want User to Join !", time=5)
    if match.startswith("@"):
        ch = match
    else:
        try:
            ch = int(match)
        except BaseException:
            return await eor(e, "Give Correct Channel Username or id", time=5)
    try:
        match = (await e.client.get_entity(ch)).id
    except BaseException:
        return await eor(e, "Give Correct Channel Username or id", time=5)
    if not str(match).startswith("-100"):
        match = int("-100" + str(match))
    add_forcesub(e.chat_id, match)
    await eor(e, "Added ForceSub in This Chat !")


@ultroid_cmd(pattern="remfsub$")
async def remor(e):
    res = rem_forcesub(e.chat_id)
    if not res:
        return await eor(e, "ForceSub was not Active in this Chat !", time=5)
    await eor(e, "Removed ForceSub...")


@ultroid_cmd(pattern="checkfsub$")
async def getfsr(e):
    res = get_forcesetting(e.chat_id)
    if not res:
        return await eor(e, "ForceSub is Not Active In This Chat !", time=5)
    cha = await e.client.get_entity(int(res))
    await eor(e, f"**ForceSub Status** : `Active`\n- **{cha.title}** `({res})`")


@in_pattern("fsub ?(.*)")
@in_owner
async def fcall(e):
    match = e.pattern_match.group(1)
    spli = match.split("_")
    user = await ultroid_bot.get_entity(int(spli[0]))
    cl = await ultroid_bot.get_entity(int(spli[1]))
    text = f"Hi [{user.first_name}](tg://user?id={user.id}), You Need to Join"
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
                [Button.url(text="Join Channel", url=el)],
                [Button.inline("Unmute Me", data=f"unm_{match}")],
            ],
        )
    ]
    await e.answer(res)


@callback(re.compile("unm_(.*)"))
async def diesoon(e):
    match = (e.data_match.group(1)).decode("UTF-8")
    spli = match.split("_")
    if e.sender_id != int(spli[0]):
        return await e.answer("This Message is Not for You", alert=True)
    try:
        await ultroid_bot(GetParticipantRequest(int(spli[1]), int(spli[0])))
    except UserNotParticipantError:
        return await e.answer(
            "Please Join That Channel !\nThen Click This Button !", alert=True
        )
    await ultroid_bot.edit_permissions(
        e.chat_id, int(spli[0]), send_messages=True, until_date=None
    )
    await e.edit("Thanks For Joining ! ")


@ultroid_bot.on(events.NewMessage(incoming=True))
async def cacheahs(ult):
    if udB.get("FORCESUB"):
        user = await ult.get_sender()
        joinchat = get_forcesetting(ult.chat_id)
        if not joinchat or user.bot:
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
        try:
            await ultroid_bot.edit_permissions(
                ult.chat_id, user.id, send_messages=False
            )
        except ChatAdminRequiredError:
            return
        except Exception as e:
            LOGS.info(e)
        res = await ultroid_bot.inline_query(
            asst.me.username, f"fsub {user.id}_{joinchat}"
        )
        await res[0].click(ult.chat_id, reply_to=ult.id)
