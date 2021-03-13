# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}a` or `{i}approve`
    To Approve Someone In PM.

• `{i}da` or `{i}disapprove`
    To Disapprove Someone In PM.

• `{i}block`
    To Block Someone in PM.

• `{i}unblock`
    To Unblock Someone in PM.
"""

from pyUltroid.functions.pmpermit_db import *
from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.utils import get_display_name

from . import *

# ========================= CONSTANTS =============================
COUNT_PM = {}
LASTMSG = {}
if Redis("PMPIC"):
    PMPIC = Redis("PMPIC")
else:
    PMPIC = "https://telegra.ph/file/94f6a4aeb21ce2d58dd41.jpg"

UND = get_string("pmperm_1")

if not Redis("PM_TEXT"):
    UNAPPROVED_MSG = """
**PMSecurity of {ON}!**

{UND}

You have {warn}/{twarn} warnings!"""
else:
    UNAPPROVED_MSG = (
        """
**PMSecurity of {ON}!**"""
        f"""

{Redis("PM_TEXT")}
"""
        """

{UND}

You have {warn}/{twarn} warnings!"""
    )

UNS = get_string("pmperm_2")
# 1
if Redis("PMWARNS"):
    try:
        WARNS = int(Redis("PMWARNS"))
    except BaseException:
        WARNS = 4
else:
    WARNS = 4
NO_REPLY = get_string("pmperm_3")
PMCMDS = [
    f"{hndlr}a",
    f"{hndlr}approve",
    f"{hndlr}da",
    f"{hndlr}disapprove",
    f"{hndlr}block",
    f"{hndlr}unblock",
]
# =================================================================


@ultroid_bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def permitpm(event):
    user = await event.get_chat()
    if user.bot or user.is_self:
        return
    if Redis("PMLOG") == "True":
        pl = udB.get("PMLOGGROUP")
        if pl is not None:
            return await event.forward_to(pl)
        await event.forward_to(Var.LOG_CHANNEL)


sett = Redis("PMSETTING")
if sett is None:
    sett = True
if sett == "True" and sett != "False":

    @ultroid_bot.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
    async def autoappr(e):
        miss = await e.get_chat()
        if miss.bot or miss.is_self or miss.verified or Redis("AUTOAPPROVE") != "True":
            return
        if str(miss.id) in DEVLIST:
            return
        mssg = e.text
        if mssg.startswith(HNDLR):  # do not approve if outgoing is a command.
            return
        if not is_approved(e.chat_id):
            approve_user(e.chat_id)
            async for message in e.client.iter_messages(e.chat_id, search=UND):
                await message.delete()
            async for message in e.client.iter_messages(e.chat_id, search=UNS):
                await message.delete()
            if Var.LOG_CHANNEL:
                name = await e.client.get_entity(e.chat_id)
                name0 = str(name.first_name)
                await e.client.send_message(
                    Var.LOG_CHANNEL,
                    f"#AutoApproved\nßecoz of outgoing msg\nUser - [{name0}](tg://user?id={e.chat_id})",
                )

    @ultroid_bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def permitpm(event):
        user = await event.get_chat()
        if user.bot or user.is_self or user.verified:
            return
        if str(user.id) in DEVLIST:
            return
        apprv = is_approved(user.id)
        if not apprv and event.text != UND:
            name = user.first_name
            fullname = (user.first_name, user.last_name)
            username = user.username
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            count = len(get_approved())
            try:
                wrn = COUNT_PM[user.id] + 1
            except KeyError:
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    async for message in event.client.iter_messages(
                        user.id, search=UND
                    ):
                        await message.delete()

                    async for message in event.client.iter_messages(
                        user.id, search=UNS
                    ):
                        await message.delete()
                    await event.client.send_file(
                        user.id,
                        PMPIC,
                        caption=UNAPPROVED_MSG.format(
                            ON=OWNER_NAME,
                            warn=wrn,
                            twarn=WARNS,
                            UND=UND,
                            name=name,
                            fullname=fullname,
                            username=username,
                            count=count,
                            mention=mention,
                        ),
                    )
                elif event.text == prevmsg:
                    async for message in event.client.iter_messages(
                        user.id, search=UND
                    ):
                        await message.delete()
                    await event.client.send_file(
                        user.id,
                        PMPIC,
                        caption=UNAPPROVED_MSG.format(
                            ON=OWNER_NAME,
                            warn=wrn,
                            twarn=WARNS,
                            UND=UND,
                            name=name,
                            fullname=fullname,
                            username=username,
                            count=count,
                            mention=mention,
                        ),
                    )
                LASTMSG.update({user.id: event.text})
            else:
                async for message in event.client.iter_messages(user.id, search=UND):
                    await message.delete()
                await event.client.send_file(
                    user.id,
                    PMPIC,
                    caption=UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    ),
                )
                LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= WARNS:
                async for message in event.client.iter_messages(user.id, search=UND):
                    await message.delete()
                await event.respond(UNS)
                try:
                    del COUNT_PM[user.id]
                    del LASTMSG[user.id]
                except KeyError:
                    if Var.LOG_CHANNEL:
                        await event.client.send_message(
                            Var.LOG_CHANNEL,
                            "PMPermit is messed! Pls restart the bot!!",
                        )
                        return LOGS.info("COUNT_PM is messed.")
                await event.client(BlockRequest(user.id))
                await event.client(ReportSpamRequest(peer=user.id))
                if Var.LOG_CHANNEL:
                    name = await event.client.get_entity(user.id)
                    name0 = str(name.first_name)
                    await event.client.send_message(
                        Var.LOG_CHANNEL,
                        f"[{name0}](tg://user?id={user.id}) was blocked for spamming.",
                    )

    @ultroid_cmd(pattern="(a|approve)(?: |$)")
    async def approvepm(apprvpm):
        if apprvpm.reply_to_msg_id:
            reply = await apprvpm.get_reply_message()
            replied_user = await apprvpm.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    apprvpm, "Lol, He is my Developer\nHe is auto Approved"
                )
            name0 = str(replied_user.first_name)
            uid = replied_user.id
            if not is_approved(uid):
                approve_user(uid)
                await apprvpm.edit(f"[{name0}](tg://user?id={uid}) `approved to PM!`")
                await asyncio.sleep(3)
                await apprvpm.delete()
            else:
                await apprvpm.edit("`User may already be approved.`")
                await asyncio.sleep(5)
                await apprvpm.delete()
        elif apprvpm.is_private:
            user = await apprvpm.get_chat()
            aname = await apprvpm.client.get_entity(user.id)
            if str(user.id) in DEVLIST:
                return await eor(
                    apprvpm, "Lol, He is my Developer\nHe is auto Approved"
                )
            name0 = str(aname.first_name)
            uid = user.id
            if not is_approved(uid):
                approve_user(uid)
                await apprvpm.edit(f"[{name0}](tg://user?id={uid}) `approved to PM!`")
                async for message in apprvpm.client.iter_messages(user.id, search=UND):

                    await message.delete()
                async for message in apprvpm.client.iter_messages(user.id, search=UNS):
                    await message.delete()
                await asyncio.sleep(3)
                await apprvpm.delete()
                if Var.LOG_CHANNEL:
                    await apprvpm.client.send_message(
                        Var.LOG_CHANNEL,
                        f"#APPROVED\nUser: [{name0}](tg://user?id={uid})",
                    )
            else:
                await apprvpm.edit("`User may already be approved.`")
                await asyncio.sleep(5)
                await apprvpm.delete()
                if Var.LOG_CHANNEL:
                    await apprvpm.client.send_message(
                        Var.LOG_CHANNEL,
                        f"#APPROVED\nUser: [{name0}](tg://user?id={uid})",
                    )
        else:
            await apprvpm.edit(NO_REPLY)

    @ultroid_cmd(pattern="(da|disapprove)(?: |$)")
    async def disapprovepm(e):
        if e.reply_to_msg_id:
            reply = await e.get_reply_message()
            replied_user = await e.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    e, "`Lol, He is my Developer\nHe Can't Be DisApproved.`"
                )
            name0 = str(replied_user.first_name)
            if is_approved(replied_user.id):
                disapprove_user(replied_user.id)
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) `Disaproved to PM!`"
                )
                await asyncio.sleep(5)
                await e.delete()
            else:
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) was never approved!"
                )
                await asyncio.sleep(5)
                await e.delete()
        elif e.is_private:
            bbb = await e.get_chat()
            aname = await e.client.get_entity(bbb.id)
            if str(bbb.id) in DEVLIST:
                return await eor(
                    e, "`Lol, He is my Developer\nHe Can't Be DisApproved.`"
                )
            name0 = str(aname.first_name)
            if is_approved(bbb.id):
                disapprove_user(bbb.id)
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) `Disaproved to PM!`")
                await asyncio.sleep(5)
                await e.delete()
                if Var.LOG_CHANNEL:
                    await e.client.send_message(
                        Var.LOG_CHANNEL,
                        f"[{name0}](tg://user?id={bbb.id}) was disapproved to PM you.",
                    )
            else:
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) was never approved!")
                await asyncio.sleep(5)
                await e.delete()
        else:
            await e.edit(NO_REPLY)

    @ultroid_cmd(pattern="block$")
    async def blockpm(block):
        if block.reply_to_msg_id:
            reply = await block.get_reply_message()
            replied_user = await block.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    block, "`Lol, He is my Developer\nHe Can't Be Blocked`"
                )
            name0 = str(replied_user.first_name)
            await block.client(BlockRequest(replied_user.id))
            await block.edit("`You've been blocked!`")
            uid = replied_user.id
        elif block.is_private:
            bbb = await block.get_chat()
            if str(bbb.id) in DEVLIST:
                return await eor(
                    block, "`Lol, He is my Developer\nHe Can't Be Blocked`"
                )
            await block.client(BlockRequest(bbb.id))
            aname = await block.client.get_entity(bbb.id)
            await block.edit("`You've been blocked!`")
            name0 = str(aname.first_name)
            uid = bbb.id
        else:
            await block.edit(NO_REPLY)
        try:
            disapprove_user(uid)
        except AttributeError:
            pass
        if Var.LOG_CHANNEL:
            await block.client.send_message(
                Var.LOG_CHANNEL, f"#BLOCKED\nUser: [{name0}](tg://user?id={uid})"
            )

    @ultroid_cmd(pattern="unblock$")
    async def unblockpm(unblock):
        if unblock.reply_to_msg_id:
            reply = await unblock.get_reply_message()
            replied_user = await unblock.client.get_entity(reply.sender_id)
            name0 = str(replied_user.first_name)
            await unblock.client(UnblockRequest(replied_user.id))
            await unblock.edit("`You have been unblocked.`")
        else:
            await unblock.edit(NO_REPLY)
        if Var.LOG_CHANNEL:
            await unblock.client.send_message(
                Var.LOG_CHANNEL,
                f"[{name0}](tg://user?id={replied_user.id}) was unblocked!.",
            )


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
