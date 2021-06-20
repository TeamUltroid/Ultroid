# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
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

• `{i}nologpm`
    To stop logging from that user.

• `{i}logpm`
    Start logging again from that user.

• `{i}startarchive`
    Will start adding new PMs to archive.

• `{i}stoparchive`
    Will stop adding new PMs to archive.

• `{i}cleararchive`
    Unarchive all chats.
"""

import re

from pyUltroid.functions.logusers_db import *
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
    PMPIC = "resources/extras/teamultroid.jpg"

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

_not_approved = {}
# =================================================================


@ultroid_cmd(
    pattern="logpm$",
)
async def _(e):
    if not e.is_private:
        return await eod(e, "`Use me in Private.`", time=3)
    if is_logger(str(e.chat_id)):
        nolog_user(str(e.chat_id))
        return await eod(e, "`Now I Will log msgs from here.`", time=3)
    else:
        return await eod(e, "`Wasn't logging msgs from here.`", time=3)


@ultroid_cmd(
    pattern="nologpm$",
)
async def _(e):
    if not e.is_private:
        return await eod(e, "`Use me in Private.`", time=3)
    if not is_logger(str(e.chat_id)):
        log_user(str(e.chat_id))
        return await eod(e, "`Now I Won't log msgs from here.`", time=3)
    else:
        return await eod(e, "`Wasn't logging msgs from here.`", time=3)


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: e.is_private,
    ),
)
async def permitpm(event):
    user = await event.get_chat()
    if user.bot or user.is_self or user.verified:
        return
    if is_logger(user.id):
        return
    if Redis("PMLOG") == "True":
        pl = udB.get("PMLOGGROUP")
        if pl is not None:
            return await event.forward_to(int(pl))
        await event.forward_to(int(udB.get("LOG_CHANNEL")))


sett = Redis("PMSETTING")
if sett is None:
    sett = True
if sett == "True":

    @ultroid_bot.on(
        events.NewMessage(
            outgoing=True,
            func=lambda e: e.is_private,
        ),
    )
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
            try:
                await ultroid_bot.edit_folder(e.chat_id, folder=0)
            except BaseException:
                pass
            name = await e.client.get_entity(e.chat_id)
            name0 = str(name.first_name)
            await asst.send_message(
                int(udB.get("LOG_CHANNEL")),
                f"#AutoApproved\n**OutGoing Message.**\nUser - [{name0}](tg://user?id={e.chat_id})",
            )

    @ultroid_bot.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private,
        ),
    )
    async def permitpm(event):
        user = await event.get_chat()
        if user.bot or user.is_self or user.verified:
            return
        if str(user.id) in DEVLIST:
            return
        apprv = is_approved(user.id)
        if not apprv and event.text != UND:
            if Redis("MOVE_ARCHIVE") == "True":
                try:
                    await ultroid.edit_folder(user.id, folder=1)
                except BaseException:
                    pass
            if event.media:
                await event.delete()
            name = user.first_name
            if user.last_name:
                fullname = f"{name} {user.last_name}"
            else:
                fullname = name
            username = f"@{user.username}"
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            count = len(get_approved())
            try:
                wrn = COUNT_PM[user.id] + 1
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"Incoming PM from {mention} with {wrn}/{WARNS} warning!",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block PM", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    int(udB.get("LOG_CHANNEL")),
                    f"Incoming PM from {mention} with 1/{WARNS} warning!",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block PM", data=f"block_{user.id}"),
                    ],
                )
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    if "PMSecurity" in event.text:
                        return
                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UND,
                    ):
                        await message.delete()

                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UNS,
                    ):
                        await message.delete()
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    await ultroid.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                elif event.text == prevmsg:
                    async for message in ultroid.iter_messages(
                        user.id,
                        search=UND,
                    ):
                        await message.delete()
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    await ultroid.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                LASTMSG.update({user.id: event.text})
            else:
                async for message in ultroid.iter_messages(user.id, search=UND):
                    await message.delete()
                message_ = UNAPPROVED_MSG.format(
                    ON=OWNER_NAME,
                    warn=wrn,
                    twarn=WARNS,
                    UND=UND,
                    name=name,
                    fullname=fullname,
                    username=username,
                    count=count,
                    mention=mention,
                )
                await ultroid.send_file(
                    user.id,
                    PMPIC,
                    caption=message_,
                )
                LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= WARNS:
                async for message in ultroid.iter_messages(user.id, search=UND):
                    await message.delete()
                await event.respond(UNS)
                try:
                    del COUNT_PM[user.id]
                    del LASTMSG[user.id]
                except KeyError:
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        "PMPermit is messed! Pls restart the bot!!",
                    )
                    return LOGS.info("COUNT_PM is messed.")
                await ultroid(BlockRequest(user.id))
                await ultroid(ReportSpamRequest(peer=user.id))
                name = await ultroid.get_entity(user.id)
                name0 = str(name.first_name)
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"[{name0}](tg://user?id={user.id}) was Blocked for spamming.",
                )

    @ultroid_cmd(
        pattern="(start|stop|clear)archive$",
    )
    async def _(e):
        x = e.pattern_match.group(1)
        if x == "start":
            udB.set("MOVE_ARCHIVE", "True")
            await eod(e, "Now I will move new Unapproved DM's to archive")
        elif x == "stop":
            udB.set("MOVE_ARCHIVE", "False")
            await eod(e, "Now I won't move new Unapproved DM's to archive")
        elif x == "clear":
            try:
                await e.client.edit_folder(unpack=1)
                await eod(e, "Unarchived all chats")
            except Exception as mm:
                await eod(e, str(mm))

    @ultroid_cmd(
        pattern="(a|approve)(?: |$)",
    )
    async def approvepm(apprvpm):
        if apprvpm.reply_to_msg_id:
            reply = await apprvpm.get_reply_message()
            replied_user = await apprvpm.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    apprvpm,
                    "Lol, He is my Developer\nHe is auto Approved",
                )
            name0 = str(replied_user.first_name)
            uid = replied_user.id
            if not is_approved(uid):
                approve_user(uid)
                try:
                    await apprvpm.client.edit_folder(uid, folder=0)
                except BaseException:
                    pass
                await eod(apprvpm, f"[{name0}](tg://user?id={uid}) `approved to PM!`")
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[uid],
                    f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                    buttons=[
                        Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                        Button.inline("Block", data=f"block_{uid}"),
                    ],
                )
            else:
                await eod(apprvpm, "`User may already be approved.`")
        elif apprvpm.is_private:
            user = await apprvpm.get_chat()
            aname = await apprvpm.client.get_entity(user.id)
            if str(user.id) in DEVLIST:
                return await eor(
                    apprvpm,
                    "Lol, He is my Developer\nHe is auto Approved",
                )
            name0 = str(aname.first_name)
            uid = user.id
            if not is_approved(uid):
                approve_user(uid)
                try:
                    await apprvpm.client.edit_folder(uid, folder=0)
                except BaseException:
                    pass
                await eod(apprvpm, f"[{name0}](tg://user?id={uid}) `approved to PM!`")
                async for message in apprvpm.client.iter_messages(user.id, search=UND):
                    await message.delete()
                async for message in apprvpm.client.iter_messages(user.id, search=UNS):
                    await message.delete()
                try:
                    await asst.edit_message(
                        int(udB.get("LOG_CHANNEL")),
                        _not_approved[uid],
                        f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                        buttons=[
                            Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                            Button.inline("Block", data=f"block_{uid}"),
                        ],
                    )
                except KeyError:
                    _not_approved[uid] = await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"#APPROVED\n\n`User: `[{name0}](tg://user?id={uid})",
                        buttons=[
                            Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                            Button.inline("Block", data=f"block_{uid}"),
                        ],
                    )
            else:
                await eod(apprvpm, "`User may already be approved.`")
        else:
            await apprvpm.edit(NO_REPLY)

    @ultroid_cmd(
        pattern="(da|disapprove)(?: |$)",
    )
    async def disapprovepm(e):
        if e.reply_to_msg_id:
            reply = await e.get_reply_message()
            replied_user = await e.client.get_entity(reply.sender_id)
            aname = replied_user.id
            if str(aname) in DEVLIST:
                return await eor(
                    e,
                    "`Lol, He is my Developer\nHe Can't Be DisApproved.`",
                )
            name0 = str(replied_user.first_name)
            if is_approved(aname):
                disapprove_user(aname)
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) `Disaproved to PM!`",
                )
                await asyncio.sleep(5)
                await e.delete()
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[aname],
                    f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `was disapproved to PM you.`",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{aname}"),
                        Button.inline("Block", data=f"block_{aname}"),
                    ],
                )
            else:
                await e.edit(
                    f"[{name0}](tg://user?id={replied_user.id}) was never approved!",
                )
                await asyncio.sleep(5)
                await e.delete()
        elif e.is_private:
            bbb = await e.get_chat()
            aname = await e.client.get_entity(bbb.id)
            if str(bbb.id) in DEVLIST:
                return await eor(
                    e,
                    "`Lol, He is my Developer\nHe Can't Be DisApproved.`",
                )
            name0 = str(aname.first_name)
            if is_approved(bbb.id):
                disapprove_user(bbb.id)
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) `Disaproved to PM!`")
                await asyncio.sleep(5)
                await e.delete()
                try:
                    await asst.edit_message(
                        int(udB.get("LOG_CHANNEL")),
                        _not_approved[bbb.id],
                        f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `was disapproved to PM you.`",
                        buttons=[
                            Button.inline("Approve PM", data=f"approve_{bbb.id}"),
                            Button.inline("Block", data=f"block_{bbb.id}"),
                        ],
                    )
                except KeyError:
                    _not_approved[bbb.id] = await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"#DISAPPROVED\n\n[{name0}](tg://user?id={bbb.id}) `was disapproved to PM you.`",
                        buttons=[
                            Button.inline("Approve PM", data=f"approve_{bbb.id}"),
                            Button.inline("Block", data=f"block_{bbb.id}"),
                        ],
                    )
            else:
                await e.edit(f"[{name0}](tg://user?id={bbb.id}) was never approved!")
                await asyncio.sleep(5)
                await e.delete()
        else:
            await e.edit(NO_REPLY)


@ultroid_cmd(
    pattern="block ?(.*)",
)
async def blockpm(block):
    match = block.pattern_match.group(1)
    if block.is_reply:
        reply = await block.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match)
    elif block.is_private:
        user = block.chat_id
    else:
        return await eod(block, NO_REPLY)
    if str(user) in DEVLIST:
        return await eor(
            block,
            "`Lol, He is my Developer\nHe Can't Be Blocked`",
        )
    await block.client(BlockRequest(user))
    aname = await block.client.get_entity(user)
    await eor(block, f"`{aname.first_name} has been blocked!`")
    try:
        disapprove_user(user)
    except AttributeError:
        pass
    try:
        await asst.edit_message(
            int(udB.get("LOG_CHANNEL")),
            _not_approved[user],
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) has been **blocked**.",
            buttons=Button.inline("UnBlock", data=f"unblock_{user}"),
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) has been **blocked**.",
            buttons=Button.inline("UnBlock", data=f"unblock_{user}"),
        )


@ultroid_cmd(
    pattern="unblock ?(.*)",
)
async def unblockpm(unblock):
    match = unblock.pattern_match.group(1)
    if unblock.is_reply:
        reply = await unblock.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match)
    else:
        return await eod(unblock, NO_REPLY)
    try:
        await unblock.client(UnblockRequest(user))
        aname = await unblock.client.get_entity(user)
        await eor(unblock, f"`{aname.first_name} has been UnBlocked!`")
    except Exception as et:
        await eod(unblock, f"ERROR - {str(et)}")
    try:
        await asst.edit_message(
            int(udB.get("LOG_CHANNEL")),
            _not_approved[user],
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) has been **unblocked**.",
            buttons=[
                Button.inline("Block", data=f"block_{user}"),
                Button.inline("Close", data="deletedissht"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) has been **unblocked**.",
            buttons=[
                Button.inline("Block", data=f"block_{user}"),
                Button.inline("Close", data="deletedissht"),
            ],
        )


@callback(
    re.compile(
        b"approve_(.*)",
    ),
)
@owner
async def apr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if str(uid) in DEVLIST:
        await event.edit("It's a dev! Approved!")
    if not is_approved(uid):
        approve_user(uid)
        try:
            await ultroid_bot.edit_folder(uid, folder=0)
        except BaseException:
            pass
        try:
            user_name = (await ultroid.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#APPROVED\n\n[{user_name}](tg://user?id={uid}) `approved to PM!`",
            buttons=[
                Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                Button.inline("Block", data=f"block_{uid}"),
            ],
        )
        async for message in ultroid.iter_messages(uid, search=UND):
            await message.delete()
        async for message in ultroid.iter_messages(uid, search=UNS):
            await message.delete()
        await event.answer("Approved.")
        x = await ultroid.send_message(uid, "You have been approved to PM me!")
        await asyncio.sleep(5)
        await x.delete()
    else:
        await event.edit(
            "`User may already be approved.`",
            buttons=[
                Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                Button.inline("Block", data=f"block_{uid}"),
            ],
        )


@callback(
    re.compile(
        b"disapprove_(.*)",
    ),
)
@owner
async def disapr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if is_approved(uid):
        disapprove_user(uid)
        try:
            user_name = (await ultroid.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#DISAPPROVED\n\n[{user_name}](tg://user?id={uid}) `disapproved from PMs!`",
            buttons=[
                Button.inline("Approve PM", data=f"approve_{uid}"),
                Button.inline("Block", data=f"block_{uid}"),
            ],
        )
        await event.answer("DisApproved.")
        x = await ultroid.send_message(uid, "You have been disapproved from PMing me!")
        await asyncio.sleep(5)
        await x.delete()
    else:
        await event.edit(
            "`User was never approved!`",
            buttons=[
                Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                Button.inline("Block", data=f"block_{uid}"),
            ],
        )


@callback(
    re.compile(
        b"block_(.*)",
    ),
)
@owner
async def blck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid(BlockRequest(uid))
    try:
        user_name = (await ultroid.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("Blocked.")
    await event.edit(
        f"#BLOCKED\n\n[{user_name}](tg://user?id={uid}) has been **blocked!**",
        buttons=Button.inline("UnBlock", data=f"unblock_{uid}"),
    )


@callback(
    re.compile(
        b"unblock_(.*)",
    ),
)
@owner
async def unblck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid(UnblockRequest(uid))
    try:
        user_name = (await ultroid.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("UnBlocked.")
    await event.edit(
        f"#UNBLOCKED\n\n[{user_name}](tg://user?id={uid}) has been **unblocked!**",
        buttons=[
            Button.inline("Block", data=f"block_{uid}"),
            Button.inline("Close", data="deletedissht"),
        ],
    )


@callback("deletedissht")
async def ytfuxist(e):
    await e.answer("Deleted.")
    await e.delete()
