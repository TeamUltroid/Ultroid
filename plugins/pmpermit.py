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

• `{i}unblock` | `{i}unblock all`
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

• `{i}listapproved`
   List all approved PMs.
"""

import asyncio
import re
from os import remove

from pyUltroid.dB import DEVLIST
from pyUltroid.dB.logusers_db import *
from pyUltroid.dB.pmpermit_db import *
from tabulate import tabulate
from telethon import events
from telethon.tl.functions.contacts import (
    BlockRequest,
    GetBlockedRequest,
    UnblockRequest,
)
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.utils import get_display_name, resolve_bot_file_id

from . import *

# ========================= CONSTANTS =============================

COUNT_PM = {}
LASTMSG = {}
WARN_MSGS = {}
U_WARNS = {}
PMPIC = Redis("PMPIC") or None
UND = get_string("pmperm_1")

if not Redis("PM_TEXT"):
    UNAPPROVED_MSG = (
        "**PMSecurity of {ON}!**\n\n{UND}\n\nYou have {warn}/{twarn} warnings!"
    )
else:
    UNAPPROVED_MSG = (
        "**PMSecurity of {ON}!**\n\n"
        + Redis("PM_TEXT")
        + "\n\nYou have {warn}/{twarn} warnings!"
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
    f"{HNDLR}a",
    f"{HNDLR}approve",
    f"{HNDLR}da",
    f"{HNDLR}disapprove",
    f"{HNDLR}block",
    f"{HNDLR}unblock",
]

_not_approved = {}
_to_delete = {}

sett = Redis("PMSETTING") or "False"

my_bot = asst.me.username


def update_pm(userid, message, warns_given):
    try:
        WARN_MSGS.update({userid: message})
    except KeyError:
        pass
    try:
        U_WARNS.update({userid: warns_given})
    except KeyError:
        pass


async def delete_pm_warn_msgs(chat: int):
    try:
        await _to_delete[chat].delete()
    except KeyError:
        pass


# =================================================================


@ultroid_cmd(
    pattern="logpm$",
)
async def _(e):
    if not e.is_private:
        return await eor(e, "`Use me in Private.`", time=3)
    if not is_logger(str(e.chat_id)):
        return await eor(e, "`Wasn't logging msgs from here.`", time=3)

    nolog_user(str(e.chat_id))
    return await eor(e, "`Now I Will log msgs from here.`", time=3)


@ultroid_cmd(
    pattern="nologpm$",
)
async def _(e):
    if not e.is_private:
        return await eor(e, "`Use me in Private.`", time=3)
    if is_logger(str(e.chat_id)):
        return await eor(e, "`Wasn't logging msgs from here.`", time=3)

    log_user(str(e.chat_id))
    return await eor(e, "`Now I Won't log msgs from here.`", time=3)


@ultroid_bot.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: e.is_private,
    ),
)
async def permitpm(event):
    user = await event.get_sender()
    if user.bot or user.is_self or user.verified or is_logger(user.id):
        return
    if Redis("PMLOG") == "True":
        pl = udB.get("PMLOGGROUP")
        if pl:
            return await event.forward_to(int(pl))
        await event.forward_to(int(udB.get("LOG_CHANNEL")))


if sett == "True":

    @ultroid_bot.on(
        events.NewMessage(
            outgoing=True,
            func=lambda e: e.is_private and e.out,
        ),
    )
    async def autoappr(e):
        miss = await e.get_chat()
        if miss.bot or miss.is_self or miss.verified or Redis("AUTOAPPROVE") != "True":
            return
        if miss.id in DEVLIST:
            return
        # do not approve if outgoing is a command.
        if e.text.startswith(HNDLR):
            return
        if is_approved(miss.id):
            return
        approve_user(miss.id)
        await delete_pm_warn_msgs(miss.id)
        try:
            await ultroid_bot.edit_folder(miss.id, folder=0)
        except BaseException:
            pass
        name = get_display_name(e.chat)
        try:
            await asst.edit_message(
                int(udB.get("LOG_CHANNEL")),
                _not_approved[miss.id],
                f"#AutoApproved : **OutGoing Message.**\nUser : **[{miss.first_name}](tg://user?id={miss.id})** [`{miss.id}`]",
            )
        except KeyError:
            await asst.send_message(
                int(udB.get("LOG_CHANNEL")),
                f"#AutoApproved\n**OutGoing Message.**\nUser - [{name}](tg://user?id={miss.id}) [`{miss.id}`]",
            )

    @ultroid_bot.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private and not e.out,
        ),
    )
    async def permitpm(event):
        inline_pm = False
        if Redis("INLINE_PM") and Redis("INLINE_PM") == "True":
            inline_pm = not inline_pm
        user = await event.get_sender()
        if user.bot or user.is_self or user.verified:
            return
        if user.id in DEVLIST:
            return
        if not is_approved(user.id) and event.text != UND:
            if Redis("MOVE_ARCHIVE") == "True":
                try:
                    await ultroid_bot.edit_folder(user.id, folder=1)
                except BaseException as er:
                    LOGS.info(er)
            if event.media:
                await event.delete()
            name = user.first_name
            fullname = get_display_name(user)
            username = f"@{user.username}"
            mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
            count = len(get_approved())
            try:
                wrn = COUNT_PM[user.id] + 1
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"Incoming PM from **{mention}** [`{user.id}`] with **{wrn}/{WARNS}** warning!",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block PM", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    int(udB.get("LOG_CHANNEL")),
                    f"Incoming PM from **{mention}** [`{user.id}`] with **1/{WARNS}** warning!",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block PM", data=f"block_{user.id}"),
                    ],
                )
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    if "PMSecurity" in event.text or "**PMSecurity" in event.text:
                        return
                    await delete_pm_warn_msgs(user.id)
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
                    update_pm(user.id, message_, wrn)
                    if inline_pm:
                        results = await ultroid_bot.inline_query(
                            my_bot, f"ip_{user.id}"
                        )
                        try:
                            _to_delete[user.id] = await results[0].click(
                                user.id, reply_to=event.id, hide_via=True
                            )
                        except Exception as e:
                            LOGS.info(str(e))
                    elif PMPIC:
                        _to_delete[user.id] = await ultroid_bot.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await ultroid_bot.send_message(
                            user.id, message_
                        )

                else:
                    await delete_pm_warn_msgs(user.id)
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
                    update_pm(user.id, message_, wrn)
                    if inline_pm:
                        try:
                            results = await ultroid_bot.inline_query(
                                my_bot, f"ip_{user.id}"
                            )
                            _to_delete[user.id] = await results[0].click(
                                user.id, reply_to=event.id, hide_via=True
                            )
                        except Exception as e:
                            LOGS.info(str(e))
                    elif PMPIC:
                        _to_delete[user.id] = await ultroid_bot.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await ultroid_bot.send_message(
                            user.id, message_
                        )
                LASTMSG.update({user.id: event.text})
            else:
                await delete_pm_warn_msgs(user.id)
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
                update_pm(user.id, message_, wrn)
                if inline_pm:
                    try:
                        results = await ultroid_bot.inline_query(
                            my_bot, f"ip_{user.id}"
                        )
                        _to_delete[user.id] = await results[0].click(
                            user.id, reply_to=event.id, hide_via=True
                        )
                    except Exception as e:
                        LOGS.info(str(e))
                elif PMPIC:
                    _to_delete[user.id] = await ultroid_bot.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                else:
                    _to_delete[user.id] = await ultroid_bot.send_message(
                        user.id, message_
                    )
            LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= WARNS:
                await delete_pm_warn_msgs(user.id)
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
                await ultroid_bot(BlockRequest(user.id))
                await ultroid_bot(ReportSpamRequest(peer=user.id))
                name = await ultroid_bot.get_entity(user.id)
                name0 = str(name.first_name)
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"**[{name0}](tg://user?id={user.id})** [`{user.id}`] was Blocked for spamming.",
                )

    @ultroid_cmd(
        pattern="(start|stop|clear)archive$",
    )
    async def _(e):
        x = e.pattern_match.group(1)
        if x == "start":
            udB.set("MOVE_ARCHIVE", "True")
            await eor(e, "Now I will move new Unapproved DM's to archive", time=5)
        elif x == "stop":
            udB.set("MOVE_ARCHIVE", "False")
            await eor(e, "Now I won't move new Unapproved DM's to archive", time=5)
        elif x == "clear":
            try:
                await e.client.edit_folder(unpack=1)
                await eor(e, "Unarchived all chats", time=5)
            except Exception as mm:
                await eor(e, str(mm), time=5)

    @ultroid_cmd(
        pattern="(a|approve)(?: |$)",
    )
    async def approvepm(apprvpm):
        if apprvpm.reply_to_msg_id:
            user = (await apprvpm.get_reply_message()).sender
        elif apprvpm.is_private:
            user = await apprvpm.get_chat()
        else:
            return await apprvpm.edit(NO_REPLY)
        if user.id in DEVLIST:
            return await eor(
                apprvpm,
                "Lol, He is my Developer\nHe is auto Approved",
            )
        if not is_approved(user.id):
            approve_user(user.id)
            try:
                await delete_pm_warn_msgs(user.id)
                await apprvpm.client.edit_folder(user.id, folder=0)
            except BaseException:
                pass
            await eod(
                apprvpm,
                f"[{user.first_name}](tg://user?id={user.id}) `approved to PM!`",
            )
            try:
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"#APPROVED\n\n`User: `[{user.first_name}](tg://user?id={user.id}) [`{user.id}`]",
                    buttons=[
                        Button.inline("Disapprove PM", data=f"disapprove_{user.id}"),
                        Button.inline("Block", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    int(udB.get("LOG_CHANNEL")),
                    f"#APPROVED\n\n`User: `[{user.first_name}](tg://user?id={user.id}) [`{user.id}`]",
                    buttons=[
                        Button.inline("Disapprove PM", data=f"disapprove_{user.id}"),
                        Button.inline("Block", data=f"block_{user.id}"),
                    ],
                )
        else:
            await eor(apprvpm, "`User may already be approved.`", time=5)

    @ultroid_cmd(
        pattern="(da|disapprove)(?: |$)",
    )
    async def disapprovepm(e):
        if e.reply_to_msg_id:
            user = (await e.get_reply_message()).sender
        elif e.is_private:
            user = await e.get_chat()
        else:
            return await e.edit(NO_REPLY)
        if user.id in DEVLIST:
            return await eor(
                e,
                "`Lol, He is my Developer\nHe Can't Be DisApproved.`",
            )
        if is_approved(user.id):
            disapprove_user(user.id)
            await eod(
                e, f"[{user.first_name}](tg://user?id={user.id}) `Disapproved to PM!`"
            )
            try:
                await asst.edit_message(
                    int(udB.get("LOG_CHANNEL")),
                    _not_approved[user.id],
                    f"#DISAPPROVED\n\n[{user.first_name}](tg://user?id={user.id}) [{user.id}] `was disapproved to PM you.`",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    int(udB.get("LOG_CHANNEL")),
                    f"#DISAPPROVED\n\n[{user.first_name}](tg://user?id={user.id}) [`{user.id}`] `was disapproved to PM you.`",
                    buttons=[
                        Button.inline("Approve PM", data=f"approve_{user.id}"),
                        Button.inline("Block", data=f"block_{user.id}"),
                    ],
                )
        else:
            await eod(
                e, f"[{user.first_name}](tg://user?id={user.id}) was never approved!"
            )


@ultroid_cmd(pattern="block ?(.*)", fullsudo=True)
async def blockpm(block):
    match = block.pattern_match.group(1)
    if block.reply_to_msg_id:
        reply = await block.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match)
    elif block.is_private:
        user = block.chat_id
    else:
        return await eor(block, NO_REPLY, time=10)
    if user in DEVLIST:
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
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) [`{user}`] has been **blocked**.",
            buttons=[
                Button.inline("UnBlock", data=f"unblock_{user}"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#BLOCKED\n\n[{aname.first_name}](tg://user?id={user}) [`{user}`] has been **blocked**.",
            buttons=[
                Button.inline("UnBlock", data=f"unblock_{user}"),
            ],
        )


@ultroid_cmd(pattern="unblock ?(.*)")
async def unblockpm(unblock):
    match = unblock.pattern_match.group(1)
    if unblock.is_reply:
        reply = await unblock.get_reply_message()
        user = reply.sender_id
    elif match:
        user = await get_user_id(match) if match != "all" else None
    else:
        return await eor(unblock, NO_REPLY, time=5)
    if match == "all":
        msg = await eor(unblock, get_string("com_1"))
        u_s = await unblock.client(GetBlockedRequest(0, 0))
        count = len(u_s.users)
        if not count:
            return await eor(msg, "__You have not blocked Anyone...__")
        for user in u_s.users:
            await asyncio.sleep(1.5)
            await unblock.client(UnblockRequest(user.id))
        # GetBlockedRequest return 20 users at most.
        if count < 20:
            return await eor(msg, f"__Unblocked {count} Users!__")
        while u_s.users:
            u_s = await unblock.client(GetBlockedRequest(0, 0))
            for user in u_s.users:
                await asyncio.sleep(1.5)
                await unblock.client(UnblockRequest(user.id))
            count += len(u_s.users)
        return await eor(msg, f"__Unblocked {count} users.__")
    try:
        await unblock.client(UnblockRequest(user))
        aname = await unblock.client.get_entity(user)
        await eor(unblock, f"`{aname.first_name} has been UnBlocked!`")
    except Exception as et:
        return await eor(unblock, f"ERROR - {et}", time=5)
    try:
        await asst.edit_message(
            int(udB.get("LOG_CHANNEL")),
            _not_approved[user],
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) [`{user}`] has been **unblocked**.",
            buttons=[
                Button.inline("Block", data=f"block_{user}"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            int(udB.get("LOG_CHANNEL")),
            f"#UNBLOCKED\n\n[{aname.first_name}](tg://user?id={user}) [`{user}`] has been **unblocked**.",
            buttons=[
                Button.inline("Block", data=f"block_{user}"),
            ],
        )


@ultroid_cmd(pattern="listapproved")
async def list_approved(event):
    xx = await eor(event, get_string("com_1"))
    all = get_approved()
    if not all:
        return await eor(xx, "`You haven't approved anyone yet!`", time=5)
    users = []
    for i in all:
        try:
            name = (await ultroid_bot.get_entity(i)).first_name
        except BaseException:
            name = ""
        users.append([name.strip(), str(i)])
    with open("approved_pms.txt", "w") as list_appr:
        list_appr.write(
            tabulate(users, headers=["UserName", "UserID"], showindex="always")
        )
    await event.reply(
        "List of users approved by [{}](tg://user?id={})".format(OWNER_NAME, OWNER_ID),
        file="approved_pms.txt",
    )
    await xx.delete()
    remove("approved_pms.txt")


@callback(
    re.compile(
        b"approve_(.*)",
    ),
    owner=True,
)
async def apr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid in DEVLIST:
        await event.edit("It's a dev! Approved!")
    if not is_approved(uid):
        approve_user(uid)
        try:
            await ultroid_bot.edit_folder(uid, folder=0)
        except BaseException:
            pass
        try:
            user_name = (await ultroid_bot.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#APPROVED\n\n[{user_name}](tg://user?id={uid}) [`{uid}`] `approved to PM!`",
            buttons=[
                [
                    Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                    Button.inline("Block", data=f"block_{uid}"),
                ],
            ],
        )
        await delete_pm_warn_msgs(uid)
        await event.answer("Approved.")
    else:
        await event.edit(
            "`User may already be approved.`",
            buttons=[
                [
                    Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                    Button.inline("Block", data=f"block_{uid}"),
                ],
            ],
        )


@callback(
    re.compile(
        b"disapprove_(.*)",
    ),
    owner=True,
)
async def disapr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if is_approved(uid):
        disapprove_user(uid)
        try:
            user_name = (await ultroid_bot.get_entity(uid)).first_name
        except BaseException:
            user_name = ""
        await event.edit(
            f"#DISAPPROVED\n\n**[{user_name}](tg://user?id={uid})** [`{uid}`] `disapproved from PMs!`",
            buttons=[
                [
                    Button.inline("Approve PM", data=f"approve_{uid}"),
                    Button.inline("Block", data=f"block_{uid}"),
                ],
            ],
        )
        await event.answer("DisApproved.")
    else:
        await event.edit(
            "`User was never approved!`",
            buttons=[
                [
                    Button.inline("Disapprove PM", data=f"disapprove_{uid}"),
                    Button.inline("Block", data=f"block_{uid}"),
                ],
            ],
        )


@callback(
    re.compile(
        b"block_(.*)",
    ),
    owner=True,
)
async def blck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid_bot(BlockRequest(uid))
    try:
        user_name = (await ultroid_bot.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("Blocked.")
    await event.edit(
        f"#BLOCKED\n\n[{user_name}](tg://user?id={uid}) [`{uid}`] has been **blocked!**",
        buttons=[
            Button.inline("UnBlock", data=f"unblock_{uid}"),
        ],
    )


@callback(
    re.compile(
        b"unblock_(.*)",
    ),
    owner=True,
)
async def unblck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    await ultroid_bot(UnblockRequest(uid))
    try:
        user_name = (await ultroid_bot.get_entity(uid)).first_name
    except BaseException:
        user_name = ""
    await event.answer("UnBlocked.")
    await event.edit(
        f"#UNBLOCKED\n\n[{user_name}](tg://user?id={uid}) has been **unblocked!**",
        buttons=[
            Button.inline("Block", data=f"block_{uid}"),
        ],
    )


@callback("deletedissht")
async def ytfuxist(e):
    try:
        await e.answer("Deleted.")
        await e.delete()
    except BaseException:
        await ultroid_bot.delete_messages(e.chat_id, e.id)


@in_pattern(re.compile("ip_(.*)"), owner=True)
async def in_pm_ans(event):
    from_user = int(event.pattern_match.group(1))
    try:
        warns = U_WARNS[from_user]
    except Exception as e:
        LOGS.info(e)
        warns = "?"
    try:
        msg_ = WARN_MSGS[from_user]
    except KeyError:
        msg_ = "**PMSecurity of {OWNER_NAME}**"
    wrns = f"{warns}/{WARNS}"
    buttons = [
        [
            Button.inline("Warns", data=f"admin_only{from_user}"),
            Button.inline(wrns, data=f"don_{wrns}"),
        ]
    ]
    include_media = True
    mime_type, res = None, None
    cont = None
    try:
        ext = PMPIC.split(".")[-1].lower()
    except (AttributeError, IndexError):
        ext = None
    if ext in ["img", "jpg", "png"]:
        _type = "photo"
        mime_type = "image/jpg"
    elif ext in ["mp4", "mkv", "gif"]:
        mime_type = "video/mp4"
        _type = "gif"
    else:
        try:
            res = resolve_bot_file_id(PMPIC)
        except ValueError:
            pass
        if res:
            res = [
                await event.builder.document(
                    res,
                    title="Inline PmPermit",
                    description="~ @TheUltroid",
                    text=msg_,
                    buttons=buttons,
                    link_preview=False,
                )
            ]
        else:
            _type = "article"
            include_media = False
    if not res:
        if include_media:
            cont = types.InputWebDocument(PMPIC, 0, mime_type, [])
        res = [
            event.builder.article(
                title="Inline PMPermit.",
                type=_type,
                text=msg_,
                description="@TeamUltroid",
                include_media=include_media,
                buttons=buttons,
                thumb=cont,
                content=cont,
            )
        ]
    await event.answer(res, switch_pm="• Ultroid •", switch_pm_param="start")


@callback(re.compile("admin_only(.*)"), owner=True)
async def _admin_tools(event):
    chat = int(event.pattern_match.group(1))
    await event.edit(
        buttons=[
            [
                Button.inline("Approve PM", data=f"approve_{chat}"),
                Button.inline("Block PM", data=f"block_{chat}"),
            ],
            [Button.inline("« Back", data=f"pmbk_{chat}")],
        ],
    )


@callback(re.compile("don_(.*)"))
async def _mejik(e):
    data = e.pattern_match.group(1).decode("utf-8").split("/")
    text = "👮‍♂ Warn Count : " + data[0]
    text += "\n🤖 Total Warn Count : " + data[1]
    await e.answer(text, alert=True)


@callback(re.compile("pmbk_(.*)"))
async def edt(event):
    from_user = int(event.pattern_match.group(1))
    try:
        warns = U_WARNS[from_user]
    except Exception as e:
        LOGS.info(str(e))
        warns = "0"
    wrns = f"{warns}/{WARNS}"
    await event.edit(
        buttons=[
            [
                Button.inline("Warns", data=f"admin_only{from_user}"),
                Button.inline(wrns, data=f"don_{wrns}"),
            ]
        ],
    )
