# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}promote <reply to user/userid/username>`
• `{i}demote`
    Promote/Demote the user in the chat.

• `{i}ban <reply to user/userid/username> <reason>`
• `{i}unban`
    Ban/Unban the user from the chat.

• `{i}kick <reply to user/userid/username> <reason>`
    Kick the user from the chat.

• `{i}pin <reply to message>`
    Pin the message in the chat
    for silent pin use ({i}pin silent).

• `{i}unpin (all) <reply to message>`
    Unpin the messages in the chat.

• `{i}pinned`
   Get pinned message in the current chat.

• `{i}autodelete <24h/7d/off>`
   Enable Auto Delete Messages in Chat.

• `{i}listpinned`
   Get all pinned messages in current chat.

• `{i}purge <reply to message>`
    Purge all messages from the replied message.

• `{i}purgeme <reply to message>`
    Purge Only your messages from the replied message.

• `{i}purgeall`
    Delete all msgs of replied user.
"""

import asyncio

from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import ChatNotModifiedError, UserIdInvalidError
from telethon.tl.functions.channels import DeleteUserHistoryRequest, EditAdminRequest
from telethon.tl.functions.channels import ExportMessageLinkRequest as ExpLink
from telethon.tl.functions.messages import SetHistoryTTLRequest
from telethon.tl.types import ChatAdminRights, InputMessagesFilterPinned

from . import *


@ultroid_cmd(
    pattern="promote ?(.*)",
    groups_only=True,
    admins_only=True,
)
async def prmte(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Admin"
    if not user:
        return await xx.edit("`Reply to a user to promote him!`")
    try:
        await ultroid_bot(
            EditAdminRequest(
                ult.chat_id,
                user.id,
                ChatAdminRights(
                    add_admins=False,
                    invite_users=True,
                    change_info=False,
                    ban_users=True,
                    delete_messages=True,
                    pin_messages=True,
                ),
                rank,
            ),
        )
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `is now an admin in {ult.chat.title} with title {rank}.`",
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to promote you.`")
    await asyncio.sleep(5)
    await xx.delete()


@ultroid_cmd(
    pattern="demote ?(.*)",
    groups_only=True,
    admins_only=True,
)
async def dmote(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, rank = await get_user_info(ult)
    if not rank:
        rank = "Not Admin"
    if not user:
        return await xx.edit("`Reply to a user to demote him!`")
    try:
        await ultroid_bot(
            EditAdminRequest(
                ult.chat_id,
                user.id,
                ChatAdminRights(
                    add_admins=None,
                    invite_users=None,
                    change_info=None,
                    ban_users=None,
                    delete_messages=None,
                    pin_messages=None,
                ),
                rank,
            ),
        )
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `is no longer an admin in {ult.chat.title}`",
        )
    except BadRequestError:
        return await xx.edit("`I don't have the right to demote you.`")
    await asyncio.sleep(5)
    await xx.delete()


@ultroid_cmd(
    pattern="ban ?(.*)",
    groups_only=True,
    admins_only=True,
)
async def bban(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to ban him!`")
    if str(user.id) in DEVLIST:
        return await xx.edit(" `LoL, I can't Ban my Developer 😂`")
    try:
        await ultroid_bot.edit_permissions(ult.chat_id, user.id, view_messages=False)
    except BadRequestError:
        return await xx.edit("`I don't have the right to ban a user.`")
    except UserIdInvalidError:
        await xx.edit("`I couldn't get who he is!`")
    try:
        reply = await ult.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`\n**Messages Deleted**: `False`",
        )
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`",
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was banned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`",
        )


@ultroid_cmd(
    pattern="unban ?(.*)",
    groups_only=True,
    admins_only=True,
)
async def uunban(ult):
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Reply to a user or give username to unban him!`")
    try:
        await ultroid_bot.edit_permissions(ult.chat_id, user.id, view_messages=True)
    except BadRequestError:
        return await xx.edit("`I don't have the right to unban a user.`")
    except UserIdInvalidError:
        await xx.edit("`I couldn't get who he is!`")
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was unbanned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`\n**Reason**: `{reason}`",
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **was unbanned by** [{OWNER_NAME}](tg://user?id={OWNER_ID}) **in** `{ult.chat.title}`",
        )


@ultroid_cmd(
    pattern="kick ?(.*)",
    groups_only=True,
    admins_only=True,
)
async def kck(ult):
    if ult.text == f"{HNDLR}kickme":
        return
    xx = await eor(ult, get_string("com_1"))
    await ult.get_chat()
    user, reason = await get_user_info(ult)
    if not user:
        return await xx.edit("`Kick? Whom? I couldn't get his info...`")
    if str(user.id) in DEVLIST:
        return await xx.edit(" `Lol, I can't Kick my Developer`😂")
    if user.id == ultroid_bot.uid:
        return await xx.edit("`You Can't kick urself`")
    try:
        await ultroid_bot.kick_participant(ult.chat_id, user.id)
        await asyncio.sleep(0.5)
    except BadRequestError:
        return await xx.edit("`I don't have the right to kick a user.`")
    except Exception as e:
        return await xx.edit(
            f"`I don't have the right to kick a user.`\n\n**ERROR**:\n`{str(e)}`",
        )
    if reason:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id})` was kicked by` [{OWNER_NAME}](tg://user?id={OWNER_ID}) `in {ult.chat.title}`\n**Reason**: `{reason}`",
        )
    else:
        await xx.edit(
            f"[{user.first_name}](tg://user?id={user.id})` was kicked by` [{OWNER_NAME}](tg://user?id={OWNER_ID}) `in {ult.chat.title}`",
        )


@ultroid_cmd(
    pattern="pin ?(.*)",
)
async def pin(msg):
    mss = "`Pinned.`"
    xx = msg.reply_to_msg_id
    tt = msg.text
    try:
        kk = tt[4]
        if kk:
            return
    except BaseException:
        pass
    if not msg.is_reply:
        return
    if not msg.is_private:
        link = (await ultroid_bot(ExpLink(msg.chat_id, xx))).link
        mss = f"`Pinned` [This Message]({link})"
    ch = msg.pattern_match.group(1)
    if ch != "silent":
        slnt = True
        try:
            await ultroid_bot.pin_message(msg.chat_id, xx, notify=slnt)
        except BadRequestError:
            return await eor(msg, "`Hmm.. Guess I have no rights here!`")
        except Exception as e:
            return await eor(msg, f"**ERROR:**`{str(e)}`")
        await eor(msg, mss)
    else:
        try:
            await ultroid_bot.pin_message(msg.chat_id, xx, notify=False)
        except BadRequestError:
            return await eor(msg, "`Hmm.. Guess I have no rights here!`")
        except Exception as e:
            return await eor(msg, f"**ERROR:**`{str(e)}`")
        try:
            await msg.delete()
        except BaseException:
            pass


@ultroid_cmd(
    pattern="unpin($| (.*))",
)
async def unp(ult):
    xx = await eor(ult, get_string("com_1"))
    if not ult.is_private:
        # for (un)pin(s) in private messages
        await ult.get_chat()
    ch = (ult.pattern_match.group(1)).strip()
    msg = ult.reply_to_msg_id
    if msg and not ch:
        try:
            await ultroid_bot.unpin_message(ult.chat_id, msg)
        except BadRequestError:
            return await xx.edit("`Hmm.. Guess I have no rights here!`")
        except Exception as e:
            return await xx.edit(f"**ERROR:**\n`{str(e)}`")
    elif ch == "all":
        try:
            await ultroid_bot.unpin_message(ult.chat_id)
        except BadRequestError:
            return await xx.edit("`Hmm.. Guess I have no rights here!`")
        except Exception as e:
            return await xx.edit(f"**ERROR:**`{str(e)}`")
    else:
        return await xx.edit(f"Either reply to a message, or, use `{hndlr}unpin all`")
    if not msg and ch != "all":
        return await xx.edit(f"Either reply to a message, or, use `{hndlr}unpin all`")
    await xx.edit("`Unpinned!`")


@ultroid_cmd(
    pattern="purge ?(.*)",
)
async def fastpurger(purg):
    chat = await purg.get_input_chat()
    match = purg.pattern_match.group(1)
    try:
        ABC = purg.text[6]
    except IndexError:
        ABC = None
    if ABC and purg.text[6] in ["m", "a"]:
        return
    if match and not purg.is_reply:
        p = 0
        async for msg in ultroid_bot.iter_messages(purg.chat_id, limit=int(match)):
            await msg.delete()
            p += 0
        return await eod(purg, f"Purged {p} Messages! ")
    msgs = []
    count = 0
    if not (purg.reply_to_msg_id or match):
        return await eod(purg, "`Reply to a message to purge from.`", time=10)
    async for msg in ultroid_bot.iter_messages(chat, min_id=purg.reply_to_msg_id):
        msgs.append(msg)
        count = count + 1
        msgs.append(purg.reply_to_msg_id)
        if len(msgs) == 100:
            await ultroid_bot.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await ultroid_bot.delete_messages(chat, msgs)
    done = await ultroid_bot.send_message(
        purg.chat_id,
        "__Fast purge complete!__\n**Purged** `"
        + str(len(msgs))
        + "` **of** `"
        + str(count)
        + "` **messages.**",
    )
    await asyncio.sleep(5)
    await done.delete()


@ultroid_cmd(
    pattern="purgeme ?(.*)",
)
async def fastpurgerme(purg):
    num = purg.pattern_match.group(1)
    if num and not purg.is_reply:
        try:
            nnt = int(num)
        except BaseException:
            await eod(purg, "`Give a Valid Input.. `")
            return
        mp = 0
        async for mm in ultroid_bot.iter_messages(
            purg.chat_id, limit=nnt, from_user="me"
        ):
            await mm.delete()
            mp += 1
        await eod(purg, f"Purged {mp} Messages!")
        return
    chat = await purg.get_input_chat()
    msgs = []
    count = 0
    if not (purg.reply_to_msg_id or num):
        return await eod(
            purg,
            "`Reply to a message to purge from or use it like ``purgeme <num>`",
            time=10,
        )
    async for msg in ultroid_bot.iter_messages(
        chat,
        from_user="me",
        min_id=purg.reply_to_msg_id,
    ):
        msgs.append(msg)
        count = count + 1
        msgs.append(purg.reply_to_msg_id)
        if len(msgs) == 100:
            await ultroid_bot.delete_messages(chat, msgs)
            msgs = []

    if msgs:
        await ultroid_bot.delete_messages(chat, msgs)
    done = await ultroid_bot.send_message(
        purg.chat_id,
        "__Fast purge complete!__\n**Purged** `" + str(count) + "` **messages.**",
    )
    await asyncio.sleep(5)
    await done.delete()


@ultroid_cmd(
    pattern="purgeall$",
)
async def _(e):
    xx = await eor(e, get_string("com_1"))
    if e.reply_to_msg_id:
        input = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(input)).first_name
        try:
            await ultroid_bot(DeleteUserHistoryRequest(e.chat_id, input))
            await eod(e, f"Successfully Purged All Messages from {name}")
        except Exception as er:
            return await eod(xx, str(er), time=5)
    else:
        return await eod(
            xx,
            "`Reply to someone's msg to delete.`",
            time=5,
        )


@ultroid_cmd(pattern="pinned")
async def get_pinned(event):
    x = await eor(event, get_string("com_1"))
    chat_id = (str(event.chat_id)).replace("-100", "")
    chat_name = "This Chat"
    if not event.is_private:
        chat_name = (await event.get_chat()).title
    tem = ""
    c = 0

    async for i in ultroid.iter_messages(
        event.chat_id, filter=InputMessagesFilterPinned
    ):
        c += 1
        tem += f"The pinned message in {chat_name} can be found <a href=https://t.me/c/{chat_id}/{i.id}>here.</a>"
        if c == 1:
            return await x.edit(tem, parse_mode="html")

    if tem == "":
        return await eod(x, "There is no pinned message in chat!", time=5)


@ultroid_cmd(pattern="listpinned")
async def get_all_pinned(event):
    x = await eor(event, get_string("com_1"))
    chat_id = (str(event.chat_id)).replace("-100", "")
    chat_name = (await event.get_chat()).title
    a = ""
    c = 1
    async for i in ultroid.iter_messages(
        event.chat_id, filter=InputMessagesFilterPinned
    ):
        a += f"{c}. <a href=https://t.me/c/{chat_id}/{i.id}>Go to message.</a>\n"
        c += 1

    if c == 1:
        m = f"<b>The pinned message in {chat_name}:</b>\n\n"
    else:
        m = f"<b>List of pinned message(s) in {chat_name}:</b>\n\n"

    if a == "":
        return await eod(x, "There is no message pinned in this group!", time=5)

    await x.edit(m + a, parse_mode="html")


@ultroid_cmd(pattern="autodelete ?(.*)", groups_only=True, admins_only=True)
async def autodelte(ult):  # Tg Feature
    match = ult.pattern_match.group(1)
    if not match or match not in ["24h", "7d", "off"]:
        return await eod(ult, "`Please Use Proper Format..`")
    if match == "24h":
        tt = 3600 * 24
    elif match == "7d":
        tt = 3600 * 24 * 7
    else:
        tt = 0
    try:
        await ultroid_bot(SetHistoryTTLRequest(ult.chat_id, period=tt))
    except ChatNotModifiedError:
        return await eod(ult, f"Auto Delete Setting is Already same to `{match}`")
    await eor(ult, f"Auto Delete Status Changed to {match} !")
