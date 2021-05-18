import re
from . import *
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.custom import Button
from pyUltroid.functions.forcesub_db import *


@ultroid_bot.on(events.ChatAction())
async def forcesub(ult):
        if not udB.get('FORCESUB'):
            return
        if not ( ult.user_joined or ult.user_added):
            return
        if not get_forcesetting(ult.chat_id):
            return
        user = await ult.get_user()
        if user.bot : return
        joinchat = get_forcesetting(ult.chat_id)
        try:
            await ultroid_bot(GetParticipantRequest(int(joinchat), user.id))
        except UserNotParticipantError:
            await ultroid_bot.edit_permissions(ult.chat_id, user.id, send_messages=False)
            res = await ultroid_bot.inline_query(asst.me.username, f"fsub {user.id}_{joinchat}")
            await res[0].click(ult.chat_id, reply_to=ult.action_message.id)


@ultroid_cmd(pattern="forcesub ?(.*)",
admins_only=True,
groups_only=True)
async def addfor(e):
    match = e.pattern_match.group(1)      
    if not match:
        return await eod(e, "Give Channel where you want User to Join !")  
    if not match.isdigit():
        match = (await ultroid_bot.get_entity(match)).id
        if not str(match).startswith('-100'):
         match = int('-100' + str(match))
    ad = add_forcesub(e.chat_id, match)
    if ad:
        await eor(e, "Added ForceSub in This Chat !")


@ultroid_cmd(pattern="remforcesub$")
async def remor(e):
    res = rem_forcesub(e.chat_id)
    if res == False or not res:
        return await eor(e, "ForceSub was not Active in this Chat !")
    await eor(e, "Removed ForceSub...")

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
    res = [await e.builder.article(title="forcesub",text=text,buttons=[[Button.url(text="Join Channel",url=el)],[Button.inline("Unmute Me",data=f"unm_{match}")]])]
    await e.answer(res)


@callback(re.compile("unm_(.*)"))
async def diesoon(e):
    match = (e.data_match.group(1)).decode('UTF-8')
    spli = match.split("_")
    if not e.sender_id == int(spli[0]):
        return await e.answer("This Message is Not for You", alert=True)
    try:
        await ultroid_bot(GetParticipantRequest(int(spli[1]), int(spli[0])))
    except UserNotParticipantError:
        return await e.answer("Please Join That Channel !\nThen Click This Button !", alert=True)
    await ultroid_bot.edit_permissions(e.chat_id, int(spli[0]), send_messages=True, until_date=None)
    await e.edit('Thanks For Joining ! ')
